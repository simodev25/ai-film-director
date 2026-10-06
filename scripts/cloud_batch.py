#!/usr/bin/env python3
"""Batch helper for OpenRouter Studio cloud jobs (Seedream/Nano Banana image, Veo/Wan video).

Offline only: no HTTP, no ComfyUI/MCP call, no generation. It prepares
separate graph copies through ``prepare_cloud_workflow``, writes per-job
approvals bound to explicit user consent, reserves+claims in the project
``CloudLedger`` and records outcomes with actual costs read (read-only) from
the OpenRouter Studio job database. Submission stays caller-owned via
comfy-mcp ``run_workflow(wait=false, confirm_spend=false)``.

  prepare  --project P --batch BATCH.yaml [--out DIR]
  uploads-refresh --batch-dir D (--descriptor NODES_GET.json | --choices-from UPLOAD_RESULT.json)
  validations --batch-dir D --from VALIDATE_RESULTS.json
  approve  --batch-dir D --consent-verbatim TXT --question TXT --ceiling-per-job X
  record   --batch-dir D --results results.json
  status   --project P
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from budget import require_budget_review  # noqa: E402
from cloud_policy import DEFAULT_CONFIG, file_sha256, load_cloud_policy  # noqa: E402
from comfyui.cloud_adapters import (  # noqa: E402
    ROUTES, CloudAdapterError, CloudBinding, ReferenceInput, _input_specs,
    authorize_cloud_job, prepare_cloud_workflow, sha256_document,
)
from comfyui.cloud_ledger import CloudLedger, LedgerError, _json as ledger_key  # noqa: E402
from comfyui.cloud_targets import ProjectScope, exploratory_target_evidence  # noqa: E402

DEFAULT_STUDIO_DB = Path(os.environ.get(
    "OPENROUTER_STUDIO_JOBS_DB",
    "/Users/mbensass/ComfyUI-Installs/simo/ComfyUI/user/__openrouter_studio/jobs.sqlite3"))
# Project-relative, validated scaffolds of la-pomme (overridable in batch.yaml).
DEFAULT_TEMPLATES = {
    "image": {"graph": "workflows/cloud/preparation/scene-01-shots/shot_la_pomme_01_03/prepared.api.json",
              "bindings": "workflows/cloud/preparation/scene-01-shots/shot_la_pomme_01_03/bindings.json"},
    "video_first": {"graph": "workflows/cloud/preparation/scene-01-video/scaffold-first-only.api.json",
                    "evidence": "workflows/cloud/preparation/scene-01-video/route-evidence.json"},
    "video_first_last": {"graph": "workflows/cloud/preparation/scene-01-video/scaffold.api.json",
                         "evidence": "workflows/cloud/preparation/scene-01-video/route-evidence.json"},
}
DEFAULT_CATALOGS = {
    "image": "workflows/cloud/preparation/scene-01-shots/node-catalog.selected.live.json",
    "video": "workflows/cloud/preparation/scene-01-video/node-catalog.selected.live.json",
}
# Model-specific scaffolds/catalogs (live-validated 2026-10-05). A template is
# only usable when its paid-node inputs match the model's live branch exactly.
MODEL_DEFAULTS = {
    "google/gemini-3.1-flash-image": {
        "templates": {"image": {
            "graph": "workflows/cloud/tests/scene-01-shots/scaffold-gemini-3.1-flash-image.api.json",
            "bindings": "workflows/cloud/tests/scene-01-shots/scaffold-gemini-3.1-flash-image.bindings.json"}},
        "catalogs": {"image": "workflows/cloud/tests/scene-01-shots/node-catalog.selected.live.json"}},
    "alibaba/wan-3.0": {
        "templates": {"video_first": {
            "graph": "workflows/cloud/tests/scene-01-video/scaffold-first-only.wan-3.0.api.json",
            "evidence": "workflows/cloud/tests/scene-01-video/route-evidence.wan-3.0.json"},
            "video_first_last": None}},  # live branch has no last_frame input
}
REQUIRED_CLASSES = {"image": ("OpenRouterStudioImage", "LoadImage", "SaveImage"),
                    "video": ("OpenRouterStudioVideo", "LoadImage", "SaveVideo")}
CLASS_FOR = {"image": "OpenRouterStudioImage", "video": "OpenRouterStudioVideo"}
NEGATIVE_INPUT = "model.special__negativePrompt"
# Model-specific live negative-prompt inputs (Veo camelCase, Kling/Wan 2.6 snake_case).
NEGATIVE_INPUTS = (NEGATIVE_INPUT, "model.special__negative_prompt")
FOLD_HEADER = "Contraintes d’exclusion (negative_prompt canonique):"
SLUG = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,80}$")
SEMANTICS = ("prompt", "seed", "width", "height", "frames", "fps", "image_input", "audio_input")


class BatchError(RuntimeError):
    pass


# ----------------------------------------------------------------- helpers
def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if re.search(r"sk-or-|Bearer\s+[A-Za-z0-9]", text):
        raise BatchError(f"Credential-like value refused in {path}")
    Path(path).write_text(text, encoding="utf-8")


def bytes_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel_inside(project, value, what):
    path = (project / value).resolve()
    if not path.is_relative_to(project) or not path.is_file():
        raise BatchError(f"{what} must be an existing project-relative file: {value}")
    return path


def dotted(data, key):
    current = data
    for part in key.split("."):
        if isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise BatchError(f"Key {key!r} missing in prompt file")
    return current


def safe_label(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")[:40] or "ref"


def upload_name(prefix, label, sha, suffix):
    """Deterministic, content-addressed Comfy input filename."""
    return f"{safe_label(prefix)}_{safe_label(label)}_{sha[:16]}{suffix.lower()}"


def load_catalog(project, batch, modality, batch_dir, model=None):
    defaults = {**DEFAULT_CATALOGS, **MODEL_DEFAULTS.get(model, {}).get("catalogs", {})}
    rel = (batch.get("node_catalogs") or {}).get(modality, defaults[modality])
    path = rel_inside(project, rel, "live node catalog")
    if not path.is_file():
        raise BatchError(
            f"Live node catalog missing: {rel}. Save comfy-mcp nodes(action='get') descriptors "
            f"for {', '.join(REQUIRED_CLASSES[modality])} as {{class: descriptor}} there.")
    catalog = read_json(path)
    overrides = sorted((batch_dir / "live-descriptors").glob("*.json"))
    for extra in overrides:  # fresh nodes(get) outputs, e.g. LoadImage after upload
        data = read_json(extra)
        items = {data.get("name", data.get("id")): data} if "inputs" in data else data
        catalog.update(items)
    missing = [name for name in REQUIRED_CLASSES[modality] if name not in catalog]
    if missing:
        raise BatchError(f"Catalog {rel} lacks live descriptors for {missing}")
    return catalog, {"catalog": rel, "catalog_sha256": bytes_sha256(path),
                     "live_overrides": [str(p.relative_to(batch_dir)) for p in overrides]}


def ledger_attempt(project, job):
    """Next attempt for the ledger target key; refuses in-flight priors."""
    parts = [job["modality"], job.get("job_kind", "shot_render"),
             job.get("entity_type"), job.get("entity_id", job.get("shot_id"))]
    if job.get("segment_id") is not None:
        parts.append({"segment_id": job["segment_id"]})
    target = ledger_key(parts)
    path = project / "budget/cloud-ledger.sqlite3"
    if not path.exists():
        return 1
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        rows = db.execute("SELECT attempt, status FROM jobs WHERE target=? ORDER BY attempt",
                          (target,)).fetchall()
    if rows and rows[-1][1] not in ("completed", "failed", "ambiguous"):
        raise BatchError(f"Prior attempt {rows[-1][0]} still {rows[-1][1]}; record its outcome first")
    return (rows[-1][0] if rows else 0) + 1


def estimate(profile, modality, params, refs):
    pricing = profile["pricing"]
    if modality == "image":
        count = sum(r["role"] == "reference" for r in refs)
        value = Decimal(str(pricing["output_per_image"])) + count * Decimal(str(pricing.get("input_per_reference", 0)))
    else:
        if "duration" not in params:
            raise BatchError("Video job requires parameters.duration (no implicit duration)")
        seconds = Decimal(params["duration"])
        value = seconds * Decimal(str(pricing["output_per_second"]))
        audio = params.get("generate_audio", "true" if profile.get("defaults", {}).get("audio") else "false")
        if audio in ("true", "on"):
            if "audio_per_second" not in pricing:
                raise BatchError("Native video audio has no configured price for this model; unknown pricing blocks")
            value += seconds * Decimal(str(pricing["audio_per_second"]))
    if value <= 0:
        raise BatchError("Unknown/zero estimate blocks preparation")
    return float(value)


# ----------------------------------------------------------------- graphs
def template_for(project, batch, modality, roles, model=None):
    templates = {**DEFAULT_TEMPLATES, **MODEL_DEFAULTS.get(model, {}).get("templates", {}),
                 **(batch.get("templates") or {})}
    if modality == "image":
        spec = templates["image"]
        graph_path = rel_inside(project, spec["graph"], "image template")
        bindings = read_json(rel_inside(project, spec["bindings"], "image template bindings"))
        ids = bindings["declared_node_ids"]
        configured = bindings["binding"].get("references")
        if configured is None:
            # Compatibility with old bindings: discover links of DECLARED loaders
            # only, never derive IDs or invent slot names. Bundles need explicit slots.
            original = read_json(graph_path)
            configured = []
            for loader in ids["loaders"]:
                targets = [key for key, value in original[ids["image"]]["inputs"].items()
                           if value == [loader, 0]]
                if len(targets) != 1:
                    raise BatchError("Declared loader needs an explicit unambiguous reference binding")
                configured.append({"node_id": loader, "input_key": "image",
                                   "target_input": targets[0], "role": "reference"})
        return {"kind": "image", "graph_path": graph_path, "graph": read_json(graph_path),
                "paid": ids["image"], "output": ids["output"], "loaders": list(ids["loaders"]),
                "class_type": bindings["binding"]["class_type"],
                "input_map": dict(bindings["binding"]["input_map"]),
                "references": tuple(ReferenceInput(**r) for r in configured)}
    if roles == ["first_frame"]:
        key = "video_first"
    elif roles == ["first_frame", "last_frame"]:
        key = "video_first_last"
    else:
        raise BatchError(f"Unsupported video reference topology {roles}; scaffolds cover "
                         "[first_frame] or [first_frame, last_frame] only")
    spec = templates[key]
    if spec is None:
        raise BatchError(f"No validated {key} scaffold for {model} (live branch lacks this frame topology)")
    graph_path = rel_inside(project, spec["graph"], "video scaffold")
    evidence = read_json(rel_inside(project, spec["evidence"], "video route evidence"))
    ids = evidence["declared_node_ids"]
    return {"kind": key, "graph_path": graph_path, "graph": read_json(graph_path),
            "paid": ids["video"], "output": ids["output"],
            "frame_loaders": {"first_frame": ids["first_frame_loader"], "last_frame": ids["last_frame_loader"]},
            "class_type": evidence["class_type"],
            "input_map": dict(evidence["proposed_binding"]["input_map"])}


def literal(node, key, value, specs, where):
    """Set an existing STRING literal declared by the live descriptor, else block."""
    current = node.get("inputs", {}).get(key)
    if key not in node.get("inputs", {}) or isinstance(current, list):
        raise BatchError(f"{where}: {key} is not an existing literal input; refusing topology change")
    if specs.get(key, {}).get("type") != "STRING":
        raise BatchError(f"{where}: {key} is not a live STRING input")
    node["inputs"][key] = value


def check_branch(inputs, specs, model, where):
    """Template paid-node inputs must exactly fit the model's live branch (no stale keys)."""
    stale = sorted(k for k in inputs if k.startswith("model.") and k not in specs)
    missing = sorted(k for k, spec in specs.items() if k.startswith("model.") and spec.get("required")
                     and not spec.get("is_link") and not spec.get("autogrow") and k not in inputs)
    if stale or missing:
        raise BatchError(f"{where} does not match live branch of {model}: stale {stale}, missing {missing}; "
                         "supply a model-specific validated scaffold (templates in batch.yaml)")


def build_source(tpl, modality, refs, uploads, catalog, model, filename_prefix, negative, title,
                 negative_input=NEGATIVE_INPUT):
    """Separate source graph from a read-only validated template; never written back."""
    graph = copy.deepcopy(tpl["graph"])
    paid, out = tpl["paid"], tpl["output"]
    if graph.get(paid, {}).get("class_type") != tpl["class_type"] or tpl["class_type"] != CLASS_FOR[modality]:
        raise BatchError("Template paid node/class does not match declared bindings")
    if out not in graph or catalog.get(graph[out]["class_type"], {}).get("output_node") is not True:
        raise BatchError("Template output node is not a verified output node")
    paid_specs = _input_specs(catalog[tpl["class_type"]], model)
    out_specs = _input_specs(catalog[graph[out]["class_type"]], model)
    refs_bind = []
    if tpl["kind"] == "image":
        refs_bind = list(tpl["references"])
        if len(refs) != len(refs_bind):
            raise BatchError("Reference count must exactly match configured existing slots; topology preserved")
        construction = "image template copied with unchanged topology and explicit existing reference slots"
    else:
        for role, name in zip([r["role"] for r in refs], uploads):
            node_id = tpl["frame_loaders"][role]
            target = f"model.{role}"
            if graph.get(node_id, {}).get("class_type") != "LoadImage" or graph[paid]["inputs"].get(target) != [node_id, 0]:
                raise BatchError(f"Scaffold does not wire {role} as declared")
            refs_bind.append(ReferenceInput(node_id, "image", target, role))
        construction = f"video scaffold copied unchanged ({tpl['kind']})"
    check_branch(graph[paid]["inputs"], paid_specs, model, f"template {tpl['kind']}")
    if negative is not None:
        literal(graph[paid], negative_input, negative, paid_specs, "negative prompt")
    literal(graph[out], "filename_prefix", filename_prefix, out_specs, "output")
    binding = CloudBinding(paid, tpl["class_type"], tpl["input_map"], tuple(refs_bind))
    return graph, binding, construction


def mapping_report(graph, binding, params):
    inputs = graph[binding.node_id]["inputs"]
    report = {}
    for name in SEMANTICS:
        if name == "image_input":
            report[name] = [{"role": r.role, "loader": r.node_id, "target": r.target_input} for r in binding.references] or "none"
        elif name == "audio_input":
            report[name] = "none: route has no audio reference input"
        elif name in binding.input_map:
            report[name] = {"input": binding.input_map[name], "value_source": "plan"}
        else:
            literal_key = f"model.{name}"
            report[name] = ("unmapped" + (f"; scaffold literal {literal_key}={inputs[literal_key]!r} left unchanged"
                                          if literal_key in inputs else "; no such input on this route")
                            + ("; REQUESTED -> blocker" if name in params else ""))
    return report


# ----------------------------------------------------------------- prepare
def cmd_prepare(args):
    project = Path(args.project).resolve()
    batch_file = Path(args.batch).resolve()
    batch = yaml.safe_load(batch_file.read_text(encoding="utf-8"))
    if not isinstance(batch, dict) or batch.get("version") != 1 or not SLUG.match(str(batch.get("name", ""))):
        raise BatchError("batch.yaml requires version: 1 and a slug name")
    config = load_cloud_policy(Path(args.config))
    tier = batch.get("tier")
    if tier not in config["tiers"]:
        raise BatchError("batch tier must be an explicit configured tier")
    project_id = yaml.safe_load((project / "project.yaml").read_text())["project_id"]
    scope = ProjectScope(tuple(batch["scope"]["scene_ids"]), tuple(batch["scope"].get("entity_ids", [])))
    out = Path(args.out).resolve() if args.out else project / "workflows/cloud" / tier / "batches" / batch["name"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "uploads").mkdir(exist_ok=True)
    shutil.copyfile(batch_file, out / "batch.source.yaml")
    prefix = batch.get("upload_prefix", project.name)
    pricing_date = str(batch.get("pricing_checked_at", config["pricing_checked_at"]))
    manifest = {"version": 1, "batch": batch["name"], "project": str(project), "project_id": project_id,
                "tier": tier, "scope": asdict(scope), "scope_sha256": sha256_document(asdict(scope)),
                "batch_file_sha256": bytes_sha256(batch_file), "prepared_at": now_utc().isoformat(),
                "generation_tested": False, "jobs": []}
    seen = set()
    for item in batch.get("jobs", []):
        job_id = str(item.get("job_id", ""))
        record = {"job_id": job_id, "modality": item.get("modality")}
        manifest["jobs"].append(record)
        try:
            if not SLUG.match(job_id) or job_id in seen:
                raise BatchError("job_id must be a unique slug")
            seen.add(job_id)
            job_dir = out / job_id
            if (job_dir / "approval.json").exists():
                raise BatchError("job already approved; prepare a new batch for a new attempt")
            record.update(prepare_job(project, project_id, batch, item, config, tier, scope,
                                      out, job_dir, prefix, pricing_date))
        except (BatchError, CloudAdapterError, LedgerError, KeyError, ValueError, OSError) as exc:
            record.update(status="blocked", blocker=f"{type(exc).__name__}: {exc}")
    write_json(out / "manifest.json", manifest)
    print_prepare_summary(out, manifest)
    return 0 if all(j["status"] == "prepared" for j in manifest["jobs"]) else 2


def prepare_job(project, project_id, batch, item, config, tier, scope, out, job_dir, prefix, pricing_date):
    modality = item["modality"]
    if modality not in ("image", "video"):
        raise BatchError("modality must be image or video")
    profile = config["tiers"][tier][modality]
    model = profile["model"]
    if item.get("model", model) != model:
        raise BatchError(f"model {item['model']!r} differs from tier {tier} model {model!r}; no fallback")
    prompt_path = rel_inside(project, item["prompt_file"], "prompt_file")
    prompt_doc = yaml.safe_load(prompt_path.read_text(encoding="utf-8"))
    prompt = dotted(prompt_doc, item.get("prompt_key", "prompt"))
    if not isinstance(prompt, str) or not prompt.strip():
        raise BatchError("prompt text missing")
    if prompt_doc.get("model") not in (None, model):
        raise BatchError("prompt file model differs from selected tier model")
    negative = dotted(prompt_doc, item["negative_key"]).strip() if item.get("negative_key") else None
    catalog, catalog_info = load_catalog(project, batch, modality, out, model)
    paid_specs = _input_specs(catalog[CLASS_FOR[modality]], model)  # model absent -> blocker
    negative_input = next((k for k in NEGATIVE_INPUTS if paid_specs.get(k, {}).get("type") == "STRING"), None)
    negative_mode = None
    if negative and (modality == "image" or negative_input is None):
        if modality == "video" and item.get("negative_fold", batch.get("negative_fold")) is not True:
            raise BatchError(f"{model} has no live negative-prompt input; omit negative_key or set "
                             "negative_fold: true to fold it into the prompt explicitly")
        prompt = f"{prompt.rstrip()}\n\n{batch.get('negative_fold_header', FOLD_HEADER)}\n{' '.join(negative.split())}"
        negative, negative_mode = None, "folded_into_prompt"
    elif negative:
        negative_mode = negative_input
    params = dict(item.get("parameters") or {})
    # Ordered references -> deterministic, content-addressed upload names.
    refs, uploads, upload_rows = [], [], []
    for order, ref in enumerate(item.get("references") or [], start=1):
        asset = rel_inside(project, ref["asset"], "reference asset")
        digest = bytes_sha256(asset)
        if ref.get("sha256") and ref["sha256"] != digest:
            raise BatchError(f"reference {order} sha256 mismatch")
        role = ref.get("role", "reference" if modality == "image" else "first_frame")
        name = upload_name(prefix, ref.get("entity_id") or role, digest, asset.suffix)
        staged = out / "uploads" / name
        if not staged.exists() or bytes_sha256(staged) != digest:
            shutil.copyfile(asset, staged)
        refs.append({"role": role, "uploaded_path": name})
        uploads.append(name)
        upload_rows.append({"order": order, "role": role, "entity_id": ref.get("entity_id"),
                            "asset_path": ref["asset"], "sha256": digest, "uploaded_path": name,
                            "staged_file": str(staged)})
    job = {"version": 1, "tier": tier, "modality": modality, "model": model,
           "route": ROUTES[CLASS_FOR[modality]][1], "project_id": project_id,
           "prompt": prompt, "pricing_checked_at": pricing_date}
    if item.get("job_kind", "shot_render") == "reference_illustration":
        job.update(job_kind="reference_illustration", entity_type=item["entity_type"],
                   entity_id=item["entity_id"])
        if "reference_scope" in item:
            job["reference_scope"] = item["reference_scope"]
        if "scene_id" in item:
            job["scene_id"] = item["scene_id"]
        if "shot_id" in item:
            job["shot_id"] = item["shot_id"]
    else:
        job.update(job_kind="shot_render", shot_id=item.get("shot_id") or prompt_doc["shot_id"])
        if item.get("scene_id") or prompt_doc.get("scene_id"):
            job["scene_id"] = item.get("scene_id") or prompt_doc["scene_id"]
    if item.get("segment_id"):
        job["segment_id"] = item["segment_id"]
    if "reference_scope" in item and "reference_scope" not in job:
        job["reference_scope"] = item["reference_scope"]  # schema rejects scope on shot jobs
    base_prompt_id = item.get("prompt_id") or prompt_doc.get("prompt_id")
    if not base_prompt_id:
        raise BatchError("prompt_id missing (batch item or prompt file)")
    job["prompt_id"] = (base_prompt_id if item.get("prompt_id") or not item.get("segment_id")
                        else f"{base_prompt_id}_{item['segment_id']}")
    job["attempt_number"] = ledger_attempt(project, job)
    job["estimated_cost_usd"] = estimate(profile, modality, params, refs)
    if params:
        job["parameters"] = params
    if refs:
        job["references"] = refs
    if job.get("reference_scope") == "exploratory":
        for ref, asset in zip(refs, upload_rows):
            original = item["references"][asset["order"] - 1]
            ref.update(entity_id=original.get("entity_id"), entity_type=original.get("entity_type"),
                       asset_path=asset["asset_path"], sha256=asset["sha256"])
        _, job["target_evidence_sha256"] = exploratory_target_evidence(job, project, scope)
    tpl = template_for(project, batch, modality, [r["role"] for r in refs], model)
    target = job.get("shot_id") or job.get("entity_id")
    filename_prefix = (f"{project.name}/cloud/{tier}/batches/{batch['name']}/{item['job_id']}/"
                       f"attempt_{job['attempt_number']:02d}")
    graph, binding, construction = build_source(
        tpl, modality, refs, uploads, catalog, model, filename_prefix, negative,
        f"{batch['name']} / {item['job_id']} ({target})", negative_input or NEGATIVE_INPUT)
    loader = _input_specs(catalog["LoadImage"], model).get("image", {})
    choices = loader.get("choices") or []
    missing = [u for u in uploads if choices and u not in choices]
    job_dir.mkdir(parents=True, exist_ok=True)
    for stale in ("prepared.api.json", "validation.json"):
        (job_dir / stale).unlink(missing_ok=True)
    write_json(job_dir / "plan.json", job)
    write_json(job_dir / "source.api.json", graph)
    bindings = {"version": 1, "construction": construction,
                "template": str(tpl["graph_path"].relative_to(project)),
                "template_file_sha256": bytes_sha256(tpl["graph_path"]),
                "binding": {"node_id": binding.node_id, "class_type": binding.class_type,
                            "input_map": dict(binding.input_map),
                            "references": [asdict(r) for r in binding.references]},
                 "scope": asdict(scope), "ordered_reference_assets": upload_rows,
                "prompt_file": item["prompt_file"], "prompt_file_sha256": bytes_sha256(prompt_path),
                "negative_prompt_input": negative_mode,
                "parameter_mapping": mapping_report(graph, binding, params),
                "uploads_verified_in_live_choices": bool(choices) and not missing,
                **catalog_info, "paid_approval": None, "actual_cost_usd": None}
    write_json(job_dir / "bindings.json", bindings)
    row = {"job_dir": str(job_dir), "attempt_number": job["attempt_number"],
           "estimated_cost_usd": job["estimated_cost_usd"], "uploads": upload_rows,
           "plan_sha256": sha256_document(job)}
    if missing:
        return {**row, "status": "awaiting_upload",
                "blocker": f"uploads not in live LoadImage choices: {missing}"}
    prepared = prepare_cloud_workflow(graph, binding, job, config, node_catalog=catalog,
                                      project=project, scope=scope)
    write_json(job_dir / "prepared.api.json", prepared)
    return {**row, "status": "prepared", "prepared": str(job_dir / "prepared.api.json"),
            "prepared_file_sha256": bytes_sha256(job_dir / "prepared.api.json"),
            "workflow_sha256": sha256_document(prepared)}


def print_prepare_summary(out, manifest):
    print(f"Batch dir: {out}")
    staged = sorted({u["staged_file"] for j in manifest["jobs"] for u in j.get("uploads", [])})
    if staged:
        print("1) upload_file(paths=[...], overwrite=true) with:")
        for path in staged:
            print(f"   {path}")
        print(f"   then save fresh nodes(action='get', name='LoadImage') to {out}/live-descriptors/LoadImage.json"
              " and re-run prepare if any job is awaiting_upload.")
        print(f"   (or: cloud_batch.py uploads-refresh --batch-dir {out} --descriptor NODES_GET.json"
              " [--choices-from UPLOAD_RESULT.json])")
    total = Decimal(0)
    for job in manifest["jobs"]:
        print(f"- {job['job_id']}: {job['status']}" + (f" -> {job['blocker']}" if job.get("blocker") else
              f" attempt {job['attempt_number']} est ${job['estimated_cost_usd']}"))
        if job["status"] == "prepared":
            total += Decimal(str(job["estimated_cost_usd"]))
            print(f"   validate_workflow({job['prepared']}) -> save result as {job['job_dir']}/validation.json"
                  f" (or collect all and run: validations --batch-dir {out} --from RESULTS.json)")
    print(f"Estimated total (prepared jobs): ${total}  (no generation, nothing reserved)")


# ----------------------------------------------------------------- approve
def load_batch(batch_dir):
    batch_dir = Path(batch_dir).resolve()
    manifest = read_json(batch_dir / "manifest.json")
    return batch_dir, manifest, Path(manifest["project"])


# ------------------------------------------------- uploads-refresh / validations
def unwrap_envelope(data):
    """comfy-cli envelope/1 -> payload; a failed envelope is never treated as evidence."""
    if isinstance(data, dict) and data.get("schema") == "envelope/1":
        if data.get("ok") is not True:
            raise BatchError(f"Envelope reports failure ({data.get('command')}); not usable as live evidence")
        return data.get("data")
    return data


def loadimage_descriptor(data, source):
    data = unwrap_envelope(data)
    if isinstance(data, dict) and "LoadImage" in data and "inputs" not in data:
        data = data["LoadImage"]
    if not isinstance(data, dict) or data.get("name", data.get("id")) != "LoadImage":
        raise BatchError(f"{source} is not a nodes(action='get', name='LoadImage') descriptor")
    specs = [i for i in data.get("inputs", []) if isinstance(i, dict) and i.get("name") == "image"]
    if len(specs) != 1 or not isinstance(specs[0].get("choices"), list):
        raise BatchError(f"{source}: LoadImage descriptor has no image choices list")
    return data, specs[0]


def strings_in(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def batch_uploads(manifest):
    rows = {}
    for job in manifest["jobs"]:
        for upload in job.get("uploads", []):
            rows[upload["uploaded_path"]] = upload
    return rows


def cmd_uploads_refresh(args):
    """Write live-descriptors/LoadImage.json from a fresh nodes(get) and/or upload_file evidence.

    Only this batch's own content-addressed upload names are ever added, and only when the
    evidence file names them (a successful upload_file result or a live descriptor). The live
    validate_workflow run remains the authority that the server really has each file.
    """
    batch_dir, manifest, _ = load_batch(args.batch_dir)
    if not args.descriptor and not args.choices_from:
        raise BatchError("Provide --descriptor (nodes get LoadImage JSON) and/or --choices-from (upload result)")
    uploads = batch_uploads(manifest)
    if not uploads:
        raise BatchError("This batch stages no uploads; nothing to refresh")
    for name, row in uploads.items():
        staged = Path(row["staged_file"])
        if not staged.is_file() or bytes_sha256(staged) != row["sha256"]:
            raise BatchError(f"Staged upload {name} missing or changed since prepare")
    target = batch_dir / "live-descriptors" / "LoadImage.json"
    if args.descriptor:
        source = Path(args.descriptor).resolve()
        descriptor, spec = loadimage_descriptor(read_json(source), source)
    elif target.is_file():
        source = target
        descriptor, spec = loadimage_descriptor(read_json(target), target)
    else:
        raise BatchError(f"No live LoadImage descriptor: pass --descriptor (none saved at {target})")
    descriptor = copy.deepcopy(descriptor)
    spec = next(i for i in descriptor["inputs"] if i.get("name") == "image")
    live = set(spec["choices"])
    evidence, ignored = set(), []
    if args.choices_from:
        path = Path(args.choices_from).resolve()
        if path.suffix.lower() == ".json":
            values = list(strings_in(unwrap_envelope(read_json(path))))
        else:
            values = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        for value in values:
            name = Path(value).name if value else ""
            if name in uploads:
                evidence.add(name)
            elif name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                ignored.append(name)
    added = sorted(evidence - live)
    spec["choices"] = list(spec["choices"]) + added
    still_missing = sorted(set(uploads) - live - evidence)
    write_json(target, descriptor)
    report = {"refreshed_at": now_utc().isoformat(), "descriptor_source": str(source),
              "descriptor_source_sha256": bytes_sha256(source), "choices_from": args.choices_from,
              "batch_uploads": sorted(uploads), "already_in_live_choices": sorted(set(uploads) & live),
              "added_from_upload_evidence": added, "ignored_non_batch_names": sorted(set(ignored)),
              "still_missing": still_missing,
              "note": "Live validate_workflow on each prepared graph remains the authority."}
    write_json(batch_dir / "uploads-refresh.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if still_missing:
        print(f"Still missing from live choices: {still_missing} -> upload_file them, then refresh again.",
              file=sys.stderr)
        return 2
    print(f"Now re-run prepare for {batch_dir} (jobs awaiting_upload become prepared).")
    return 0


def validation_entries(data):
    data = unwrap_envelope(data)
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):
        data = data["jobs"]
    if isinstance(data, list):
        entries = []
        for item in data:
            if not isinstance(item, dict) or "job_id" not in item:
                raise BatchError("Each validation entry needs job_id")
            report = item.get("validation", item.get("result"))
            entries.append((str(item["job_id"]), unwrap_envelope(report), item.get("workflow_path")))
        return entries
    if isinstance(data, dict):
        return [(str(k), unwrap_envelope(v), None) for k, v in data.items()]
    raise BatchError("Unrecognized validation results file")


def cmd_validations(args):
    """Write <job>/validation.json from saved live validate_workflow results (verbatim report)."""
    batch_dir, manifest, _ = load_batch(args.batch_dir)
    rows = {j["job_id"]: j for j in manifest["jobs"]}
    entries = validation_entries(read_json(Path(args.source).resolve()))
    ids = [e[0] for e in entries]
    unknown = sorted(set(ids) - set(rows))
    if unknown or len(ids) != len(set(ids)):
        raise BatchError(f"Unknown or duplicate job ids in validation results: {unknown or ids}")
    checks = []
    for job_id, report, workflow_path in entries:  # full pre-check before any write
        row = rows[job_id]
        if row.get("status") != "prepared":
            raise BatchError(f"{job_id}: status {row.get('status')}, only prepared jobs can carry a validation")
        job_dir = Path(row["job_dir"])
        prepared = job_dir / "prepared.api.json"
        if (job_dir / "approval.json").exists():
            raise BatchError(f"{job_id}: already approved; validation is frozen")
        if not prepared.is_file() or bytes_sha256(prepared) != row["prepared_file_sha256"]:
            raise BatchError(f"{job_id}: prepared.api.json missing or changed since prepare")
        if workflow_path is not None and Path(workflow_path).resolve() != prepared.resolve():
            raise BatchError(f"{job_id}: validation was run on {workflow_path}, not {prepared}")
        if not isinstance(report, dict) or "valid" not in report:
            raise BatchError(f"{job_id}: not a validate_workflow report (no 'valid' key)")
        clean = (report.get("valid") is True and report.get("partner_nodes") == []
                 and report.get("spends_credits") is False)
        checks.append((job_dir, report, clean, job_id))
    for job_dir, report, clean, job_id in checks:
        write_json(job_dir / "validation.json", report)
        print(f"- {job_id}: {'clean' if clean else 'NOT CLEAN (approve will refuse)'} -> {job_dir / 'validation.json'}")
    missing = sorted(j for j, r in rows.items() if r.get("status") == "prepared" and j not in ids)
    if missing:
        print(f"Prepared jobs without a validation result: {missing}", file=sys.stderr)
    return 0 if all(c[2] for c in checks) and not missing else 2


def cmd_approve(args):
    batch_dir, manifest, project = load_batch(args.batch_dir)
    today = date.fromisoformat(args.today) if args.today else date.today()
    if not args.consent_verbatim.strip() or not args.question.strip():
        raise BatchError("Explicit user question and verbatim answer are required")
    ceiling = Decimal(str(args.ceiling_per_job))
    if ceiling <= 0:
        raise BatchError("ceiling-per-job must be positive")
    wanted = set(args.jobs.split(",")) if args.jobs else None
    jobs = [j for j in manifest["jobs"] if wanted is None or j["job_id"] in wanted]
    if wanted and wanted - {j["job_id"] for j in jobs}:
        raise BatchError(f"Unknown jobs: {sorted(wanted - {j['job_id'] for j in jobs})}")
    not_ready = [j["job_id"] for j in jobs if j.get("status") != "prepared"]
    if not jobs or not_ready:
        raise BatchError(f"Only prepared jobs can be approved; not ready: {not_ready}")
    decision_path = project / "budget/decision.yaml"
    decision = yaml.safe_load(decision_path.read_text())
    if decision.get("selected_tier") != manifest["tier"]:
        raise BatchError("Budget decision tier differs from batch tier; renewed review required")
    try:
        require_budget_review(project, selected_tier=manifest["tier"], config_path=Path(args.config), as_of=today)
    except Exception as exc:
        raise BatchError(f"Budget review/decision does not match: {exc}") from exc
    decision_sha, estimate_sha = file_sha256(decision_path), file_sha256(project / "budget/estimate.yaml")
    config = load_cloud_policy(Path(args.config))
    ledger = CloudLedger(project, config_path=Path(args.config))
    snap = ledger.snapshot()
    if snap["initialized"]:
        opening, opening_ref = snap["account"]["opening_hold_usd"], snap["account"]["opening_balance_reference"]
    elif args.opening_hold_usd is None or not args.opening_balance_reference:
        raise BatchError("New ledger: --opening-hold-usd and --opening-balance-reference are required")
    else:
        opening, opening_ref = args.opening_hold_usd, args.opening_balance_reference
    scope = ProjectScope(tuple(manifest["scope"]["scene_ids"]), tuple(manifest["scope"]["entity_ids"]))
    session = args.session or os.environ.get("OPENCODE_SESSION_ID", "session non précisée")
    staged = []
    for row in jobs:  # full offline pre-check before any reservation
        job_dir = Path(row["job_dir"])
        if bytes_sha256(job_dir / "prepared.api.json") != row["prepared_file_sha256"]:
            raise BatchError(f"{row['job_id']}: prepared.api.json changed since prepare")
        if (job_dir / "approval.json").exists():
            raise BatchError(f"{row['job_id']}: already approved; a new attempt needs a new batch")
        validation_path = job_dir / "validation.json"
        if not validation_path.exists():
            raise BatchError(f"{row['job_id']}: missing validation.json (live validate_workflow result)")
        validation = read_json(validation_path)
        if (validation.get("valid") is not True or validation.get("partner_nodes") != []
                or validation.get("spends_credits") is not False):
            raise BatchError(f"{row['job_id']}: live validation not clean for the confirm_spend=false route")
        graph, job = read_json(job_dir / "prepared.api.json"), read_json(job_dir / "plan.json")
        if sha256_document(job) != row["plan_sha256"] or job["tier"] != manifest["tier"]:
            raise BatchError(f"{row['job_id']}: plan changed or tier mismatch")
        if Decimal(str(job["estimated_cost_usd"])) > ceiling:
            raise BatchError(f"{row['job_id']}: estimate exceeds ceiling-per-job")
        plan_sha, wf_sha = sha256_document(job), sha256_document(graph)
        consent = (f"{session} ; {today.isoformat()} ; question: « {args.question.strip()} » ; "
                   f"réponse utilisateur verbatim « {args.consent_verbatim.strip()} » ; batch {manifest['batch']} ; "
                   f"job {row['job_id']} tentative {job['attempt_number']} ; plan {plan_sha[:12]}")
        approval = {"approved": True, "scope": "paid_generation_job", "approved_at": today.isoformat(),
                    "tier": job["tier"], "model": job["model"], "route": job["route"],
                    "project_id": manifest["project_id"], "scope_sha256": sha256_document(asdict(scope)),
                    "job_kind": job.get("job_kind"), "scene_id": job.get("scene_id"),
                    "shot_id": job.get("shot_id"), "entity_id": job.get("entity_id"),
                    "segment_id": job.get("segment_id"), "prompt_id": job["prompt_id"],
                    "parameters": job.get("parameters", {}), "ordered_references": job.get("references", []),
                    "count": 1, "attempt_number": job["attempt_number"],
                    "estimated_cost_usd": job["estimated_cost_usd"], "ceiling_usd": float(ceiling),
                    "workflow_sha256": wf_sha, "plan_sha256": plan_sha,
                    "estimate_sha256": estimate_sha, "decision_sha256": decision_sha,
                    "consent_reference": consent, "consent_user_verbatim": args.consent_verbatim.strip(),
                    "consent_question": args.question.strip(),
                    "consent_bundle_ceiling_usd": args.batch_ceiling}
        if job.get("reference_scope") == "exploratory":
            approval.update(reference_scope="exploratory", canonical_stage_completion=False,
                            target_evidence_sha256=job["target_evidence_sha256"])
        authorize_cloud_job(graph, job, config, approval, budget_estimate_sha256=estimate_sha,
                            workflow_validated=True, today=today, project=project, scope=scope)
        staged.append((row, job_dir, graph, job, approval))
    total = ceiling * len(staged)
    if args.batch_ceiling is not None and total > Decimal(str(args.batch_ceiling)):
        raise BatchError(f"Sum of per-job ceilings {total} exceeds approved batch ceiling {args.batch_ceiling}")
    remaining = snap.get("remaining_budget_usd")
    if remaining is not None and total > Decimal(remaining):
        raise BatchError(f"Holds {total} exceed remaining project budget {remaining}")
    claims_path = batch_dir / "claims.json"
    claims = read_json(claims_path) if claims_path.exists() else {
        "batch": manifest["batch"], "transport": "comfy-mcp run_workflow(wait=false, confirm_spend=false)", "jobs": []}
    claims.pop("error", None)
    new_entries = []
    for row, job_dir, graph, job, approval in staged:
        write_json(job_dir / "approval.json", approval)
        try:
            plan_sha = ledger.reserve(graph, job, approval, scope=scope, workflow_validated=True,
                                      opening_hold_usd=opening, opening_balance_reference=opening_ref, today=today)
        except LedgerError as exc:
            (job_dir / "approval.json").unlink()  # nothing reserved: approval not consumed
            claims["error"] = f"{row['job_id']}: reserve refused: {exc}"
            break
        try:
            ledger.claim(plan_sha, graph, job, today=today)
        except LedgerError as exc:  # reserved but unclaimed: hold kept, never submit
            claims["error"] = f"{row['job_id']}: reserved {plan_sha} but claim refused: {exc}"
            break
        else:
            entry = {"job_id": row["job_id"], "plan_sha256": plan_sha, "attempt_number": job["attempt_number"],
                     "reserved_usd": str(ceiling), "estimated_cost_usd": job["estimated_cost_usd"],
                     "workflow_path": str(job_dir / "prepared.api.json"),
                     "claimed_at": now_utc().isoformat(), "status": "claimed_before_transport"}
            write_json(job_dir / "claim.json", entry)
            claims["jobs"].append(entry)
            new_entries.append(entry)
    write_json(batch_dir / "claims.json", claims)
    print("Submit each, once, from the main session:")
    for entry in new_entries:
        print(f"  run_workflow(workflow_path={entry['workflow_path']!r}, wait=false, confirm_spend=false)")
    print(f"Then write {batch_dir}/results.json:")
    print(json.dumps({"jobs": [{"job_id": e["job_id"], "prompt_id": "<comfy prompt_id>",
                                "status": "completed|failed|ambiguous", "outputs": ["<fetched path>"]}
                               for e in new_entries]}, indent=2, ensure_ascii=False))
    if claims.get("error"):
        print(f"STOPPED: {claims['error']}", file=sys.stderr)
        return 3
    return 0


# ----------------------------------------------------------------- record
def studio_lookup(db_path, job, claimed_at, excluded):
    """Read-only match by prompt hash/model/media type/created_at; never guesses."""
    prompt_hash = hashlib.sha256(job["prompt"].encode("utf-8")).hexdigest()
    try:
        with closing(sqlite3.connect(Path(db_path).as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            rows = [dict(r) for r in db.execute(
                "SELECT local_job_id, provider_job_id, media_type, model_id, status, created_at, "
                "output_path, estimated_cost, actual_cost, error FROM jobs "
                "WHERE prompt_hash=? AND model_id=? AND media_type=?",
                (prompt_hash, job["model"], job["modality"]))]
    except sqlite3.Error as exc:
        return None, {"error": f"studio db unreadable: {exc}"}
    floor = datetime.fromisoformat(claimed_at) - timedelta(seconds=60)
    rows = [r for r in rows if datetime.fromisoformat(r["created_at"]) >= floor
            and r["local_job_id"] not in excluded and r["provider_job_id"] not in excluded]
    info = {"prompt_sha256": prompt_hash, "candidates": rows}
    return (rows[0] if len(rows) == 1 else None), info


def cmd_record(args):
    batch_dir, manifest, project = load_batch(args.batch_dir)
    claims = read_json(batch_dir / "claims.json")
    results = {r["job_id"]: r for r in read_json(args.results)["jobs"]}
    ledger = CloudLedger(project, config_path=Path(args.config))
    snap = ledger.snapshot()
    owned = {}  # provider/studio IDs already bound to a ledger plan
    for row in snap["jobs"]:
        record = json.loads(row["record"])
        for ident in filter(None, (record.get("provider_job_id"),)):
            owned[ident] = row["plan_hash"]
    code = 0
    for entry in claims["jobs"]:
        result = results.get(entry["job_id"])
        if result is None:
            print(f"- {entry['job_id']}: no result (still claimed/in flight)")
            continue
        status = result["status"]
        if status not in ("completed", "failed", "ambiguous"):
            raise BatchError(f"{entry['job_id']}: invalid status {status}")
        job_dir = Path(entry["workflow_path"]).parent
        job = read_json(job_dir / "plan.json")
        used_ids = {k for k, plan in owned.items() if plan != entry["plan_sha256"]}
        match, info = studio_lookup(args.studio_db, job, entry["claimed_at"], used_ids)
        actual = provider_id = cost_ref = None
        evidence = {"job_id": entry["job_id"], "plan_sha256": entry["plan_sha256"],
                    "comfy_prompt_id": result.get("prompt_id"), "reported_status": status,
                    "studio_db": str(args.studio_db), "read_at": now_utc().isoformat(),
                    "studio_match": match, "studio_lookup": info,
                    "tier": job["tier"], "model": job["model"], "attempt_number": job["attempt_number"],
                    "ordered_references": job.get("references", []),
                    "estimated_cost_usd": job["estimated_cost_usd"]}
        if match:
            provider_id = match["provider_job_id"] or None
            if provider_id:
                owned[provider_id] = entry["plan_sha256"]
            if match["actual_cost"] is not None and Decimal(str(match["actual_cost"])) > 0:
                actual = str(Decimal(str(match["actual_cost"])))
                where = job_dir / "outcome.json"
                where = where.relative_to(project) if where.is_relative_to(project) else where
                cost_ref = f"{where} ; OpenRouter Studio local_job_id={match['local_job_id']} (read-only)"
        evidence["actual_cost_usd"] = actual  # None = UNKNOWN, never zero
        write_json(job_dir / "outcome.json", evidence)
        try:
            ledger.record_outcome(entry["plan_sha256"], status=status, actual_cost_usd=actual,
                                  provider_job_id=provider_id, outputs=list(result.get("outputs") or []),
                                  cost_reference=cost_ref, comfy_prompt_id=result.get("prompt_id"))
            print(f"- {entry['job_id']}: {status}, actual={actual or 'UNKNOWN'}"
                  + ("" if match else f" (studio candidates: {len(info.get('candidates', []))})"))
        except LedgerError as exc:
            code = 3
            print(f"- {entry['job_id']}: NOT RECORDED: {exc}", file=sys.stderr)
    return code


# ----------------------------------------------------------------- status
def cmd_status(args):
    project = Path(args.project).resolve()
    snap = CloudLedger(project, config_path=Path(args.config)).snapshot()
    if not snap["initialized"]:
        print("Ledger not initialized: spent UNKNOWN/none recorded, nothing reserved.")
        return 0
    counts = {}
    for row in snap["jobs"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    in_flight = [(json.loads(r["record"])["plan"]["prompt_id"], r["attempt"], r["status"], r["reserved"])
                 for r in snap["jobs"] if r["status"] in ("reserved", "submitted")]
    unknown = [(json.loads(r["record"])["plan"]["prompt_id"], r["attempt"], r["status"], r["reserved"])
               for r in snap["jobs"] if r["actual"] is None and r["status"] not in ("reserved", "submitted")]
    summary = {"known_actual_spent_usd": snap["known_actual_cost_usd"],
               "unresolved_holds_usd": snap["unresolved_holds_usd"],
               "committed_usd": snap["committed_usd"],
               "external_committed_usd": snap["external_committed_usd"],
               "available_usd": snap["remaining_budget_usd"], "jobs_by_status": counts,
               "in_flight": in_flight, "terminal_unknown_cost_holds": unknown}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--project", required=True)
    p.add_argument("--batch", required=True)
    p.add_argument("--out")
    u = sub.add_parser("uploads-refresh")
    u.add_argument("--batch-dir", required=True)
    u.add_argument("--descriptor", help="saved nodes(action='get', name='LoadImage') JSON (envelope or bare)")
    u.add_argument("--choices-from", help="upload_file result JSON or a text list of uploaded names")
    v = sub.add_parser("validations")
    v.add_argument("--batch-dir", required=True)
    v.add_argument("--from", dest="source", required=True,
                   help="JSON: {job_id: report} or {jobs:[{job_id, validation|result, workflow_path?}]}")
    a = sub.add_parser("approve")
    a.add_argument("--batch-dir", required=True)
    a.add_argument("--consent-verbatim", required=True)
    a.add_argument("--question", required=True)
    a.add_argument("--ceiling-per-job", required=True, type=float)
    a.add_argument("--batch-ceiling", type=float)
    a.add_argument("--session")
    a.add_argument("--jobs", help="comma-separated subset of job_id")
    a.add_argument("--opening-hold-usd")
    a.add_argument("--opening-balance-reference")
    a.add_argument("--today", help=argparse.SUPPRESS)
    r = sub.add_parser("record")
    r.add_argument("--batch-dir", required=True)
    r.add_argument("--results", required=True)
    r.add_argument("--studio-db", default=str(DEFAULT_STUDIO_DB))
    s = sub.add_parser("status")
    s.add_argument("--project", required=True)
    args = parser.parse_args(argv)
    handler = {"prepare": cmd_prepare, "uploads-refresh": cmd_uploads_refresh, "validations": cmd_validations,
               "approve": cmd_approve, "record": cmd_record, "status": cmd_status}
    try:
        return handler[args.command](args)
    except (BatchError, CloudAdapterError, LedgerError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
