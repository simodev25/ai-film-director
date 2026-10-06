"""Offline OpenRouter/ComfyUI planning. No HTTP client or submission capability.

Only literal inputs already present in a caller's API graph may be changed.
Live ``nodes(action='get')`` descriptors must be supplied by the caller; neither
node IDs nor dynamic-combo layouts are guessed. Legacy adapters are untouched.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import jsonschema
import yaml

from .cloud_targets import ProjectScope, validate_project_target


class CloudAdapterError(ValueError):
    """A cloud plan cannot safely be prepared or authorized."""


# Class/endpoint pairs verified against the loaded plugins on 2026-10-04.
# is_api_node is FALSE for these paid nodes: never use it as a spend detector.
ROUTES = {
    "OpenRouterImageGenerate": ("image", "/api/v1/images"),
    "OpenRouterStudioImage": ("image", "/api/v1/images"),
    "OpenRouterVideoGenerate": ("video", "/api/v1/videos"),
    "OpenRouterStudioVideo": ("video", "/api/v1/videos"),
    "OpenRouterAudioSpeak": ("audio", "/api/v1/audio/speech"),
    "OpenRouterChatAsk": ("text", "/api/v1/chat/completions"),
}
PARAMETERS = {"seed", "aspect_ratio", "resolution", "duration", "width",
              "height", "frames", "fps", "generate_audio"}


@dataclass(frozen=True)
class ReferenceInput:
    """An existing uploaded-file loader feeding an existing cloud input.

    role is 'reference', 'first_frame', 'last_frame', or 'audio'. The target
    link MUST already reach node_id; this adapter never wires or creates nodes.
    """
    node_id: str
    input_key: str
    target_input: str
    role: str = "reference"


@dataclass(frozen=True)
class CloudBinding:
    node_id: str
    class_type: str
    # Semantic name -> exact API-graph input, e.g. prompt -> model.prompt.
    input_map: Mapping[str, str]
    references: tuple[ReferenceInput, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GatedRun:
    """Audit record, NOT a submit token and NOT an executable workflow."""
    tier: str
    model: str
    route: str
    prompt_id: str
    shot_id: str | None
    workflow_sha256: str
    plan_sha256: str
    estimate_sha256: str
    estimated_cost_usd: str
    ceiling_usd: str
    consent_reference: str
    ordered_references: tuple[tuple[str, str], ...] = ()
    attempts: tuple = ()
    paid: bool = True
    actual_cost_usd: None = None  # UNKNOWN, not zero
    transport: str = "comfy-mcp"
    status: str = "prepared"
    generation_tested: bool = False
    attempt_number: int = 1
    job_kind: str = "shot_render"
    entity_id: str | None = None
    entity_type: str | None = None
    project_id: str | None = None
    scene_id: str | None = None
    reference_scope: str | None = None
    target_evidence_sha256: str | None = None
    canonical_stage_completion: bool = False


def sha256_document(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def validate_cloud_job(job: Mapping[str, Any]) -> None:
    schema_path = Path(__file__).resolve().parents[2] / "schemas/cloud-job.schema.yaml"
    with schema_path.open(encoding="utf-8") as handle:
        schema = yaml.safe_load(handle)
    try:
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(job)
    except jsonschema.ValidationError as exc:
        raise CloudAdapterError(f"Invalid cloud job: {exc.message}") from exc


def _validate_target(job, project, scope):
    if project is None:
        if job.get("job_kind") == "reference_illustration" or scope is not None:
            raise CloudAdapterError("Canonical project required for reference illustration/scope")
        return
    try:
        return validate_project_target(job, project, scope)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        raise CloudAdapterError(f"Invalid canonical cloud target: {exc}") from exc


def _profile(config: Mapping[str, Any], job: Mapping[str, Any]) -> Mapping[str, Any]:
    if config.get("version") != 1 or config.get("currency") != "USD":
        raise CloudAdapterError("Cloud config requires version 1 and USD")
    try:
        profile = config["tiers"][job["tier"]][job["modality"]]
    except (KeyError, TypeError) as exc:
        raise CloudAdapterError("Missing selected tier/modality in central config") from exc
    if profile.get("model") != job["model"]:
        raise CloudAdapterError("Model must exactly match the selected central tier; no aliases")
    if not isinstance(profile.get("capabilities"), Mapping):
        raise CloudAdapterError("Missing central model capabilities")
    return profile


def _linked(value: Any) -> bool:
    return (isinstance(value, list) and len(value) == 2
            and isinstance(value[0], str) and type(value[1]) is int)


def _input_specs(descriptor: Mapping[str, Any], model: str) -> dict[str, Any]:
    """Accept normalized MCP nodes(get) descriptors, including Studio slots."""
    result = {}
    for spec in descriptor.get("inputs", []):
        result[spec["name"]] = spec
        if spec["name"] == "model" and spec.get("dynamic_options") is not None:
            selected = [item for item in spec["dynamic_options"] if item["key"] == model]
            if len(selected) != 1:
                raise CloudAdapterError("Model absent from live dynamic-combo schema")
            for child in selected[0]["inputs"]:
                if child.get("autogrow"):
                    for slot in child.get("slots", {}).get("names", []):
                        result[f"{child['name']}.{slot}"] = {
                            **child, "type": child["element_type"]}
                else:
                    result[child["name"]] = child
    return result


def _check_value(spec: Mapping[str, Any], value: Any, name: str) -> None:
    if _linked(value):
        raise CloudAdapterError(f"Cannot replace a link at {name}")
    kind = spec.get("type")
    if kind == "INT" and type(value) is not int:
        raise CloudAdapterError(f"{name} must be an integer")
    if kind == "STRING" and not isinstance(value, str):
        raise CloudAdapterError(f"{name} must be text")
    choices = spec.get("choices") or spec.get("selection_keys")
    if choices and value not in choices:
        raise CloudAdapterError(f"{name} is not in live input choices")
    options = spec.get("options", {})
    for key, cmp in (("min", lambda a, b: a < b), ("max", lambda a, b: a > b)):
        if options.get(key) is not None:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or cmp(value, options[key]):
                raise CloudAdapterError(f"{name} violates live {key}")


def _reachable(graph: Mapping[str, Any], target: Any, wanted: str) -> bool:
    seen = set()
    todo = [target[0]] if _linked(target) else []
    while todo:
        current = todo.pop()
        if current == wanted:
            return True
        if current in seen or current not in graph:
            continue
        seen.add(current)
        todo.extend(v[0] for v in graph[current].get("inputs", {}).values() if _linked(v))
    return False


def _reference_leaves(graph: Mapping[str, Any], target: Any,
                      loader_ids: set[str], seen: frozenset[str] = frozenset()) -> list[str]:
    """Only a direct loader or verified built-in ImageBatch concatenation.

    Arbitrary reference transformations may reorder, drop or duplicate images;
    reachability alone is not sufficient evidence of ordered references.
    """
    if not _linked(target) or target[0] in seen or target[1] != 0:
        raise CloudAdapterError("Unsupported/cyclic reference bundle mapping")
    node_id = target[0]
    if node_id in loader_ids:
        return [node_id]
    node = graph.get(node_id, {})
    if node.get("class_type") != "ImageBatch":
        raise CloudAdapterError("Unsupported reference bundle topology; cannot establish order")
    inputs = node.get("inputs", {})
    return (_reference_leaves(graph, inputs.get("image1"), loader_ids, seen | {node_id})
            + _reference_leaves(graph, inputs.get("image2"), loader_ids, seen | {node_id}))


def _uploaded_path(value: str) -> None:
    # Comfy upload input-relative filenames only, never URLs, local absolute
    # paths, traversal, line injection, or authentication-bearing locations.
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or ".." in path.parts or ":" in value
            or "\\" in value or any(ord(c) < 32 for c in value)
            or value != str(path) or value in (".", "..")):
        raise CloudAdapterError("Reference must be an uploaded Comfy input-relative path")


def _check_graph(graph: Mapping[str, Any], catalog: Mapping[str, Any], paid_id: str) -> None:
    output_found = False
    for node_id, node in graph.items():
        if not isinstance(node_id, str) or not isinstance(node, Mapping):
            raise CloudAdapterError("Malformed API graph")
        descriptor = catalog.get(node.get("class_type"))
        if not descriptor:
            raise CloudAdapterError("Every graph class must be present in the live catalog")
        if descriptor.get("is_api_node") is True and node_id != paid_id:
            raise CloudAdapterError("Additional paid API nodes require separate budget/consent")
        output_found |= descriptor.get("output_node") is True
        for key, value in node.get("inputs", {}).items():
            if re.search(r"api.?key|password|secret|authorization|access.?token|private.?key", key, re.I):
                raise CloudAdapterError("Credentials belong in runtime authentication, not workflow inputs")
            if isinstance(value, str) and re.search(r"(?:sk-or-|Bearer\s+[A-Za-z0-9])", value):
                raise CloudAdapterError("Credential-like workflow value prohibited")
            if _linked(value) and (value[0] not in graph or value[1] < 0):
                raise CloudAdapterError("Dangling or invalid workflow link")
    if not output_found:
        raise CloudAdapterError("An existing verified output node is required; adapter cannot create one")


def _check_capabilities(job: Mapping[str, Any], caps: Mapping[str, Any]) -> None:
    for name, value in job.get("parameters", {}).items():
        if name not in PARAMETERS:
            raise CloudAdapterError(f"Unsupported parameter: {name}")
        if name == "duration":
            if "durations" in caps:
                good = value in caps["durations"]
            elif "duration_range" in caps:
                bounds = caps["duration_range"]
                good = bounds[0] <= value <= bounds[1] and type(value) is int
            elif "min_duration_seconds" in caps and "max_duration_seconds" in caps:
                good = caps["min_duration_seconds"] <= value <= caps["max_duration_seconds"]
            else:
                good = False
        elif name in ("resolution", "aspect_ratio"):
            key = "resolutions" if name == "resolution" else "aspect_ratios"
            good = value in caps.get(key, [])
        else:
            good = caps.get(name) is True
        if not good:
            raise CloudAdapterError(f"Selected model does not support {name}={value!r}")
    refs = job.get("references", [])
    count = sum(ref["role"] == "reference" for ref in refs)
    if count > min(14, caps.get("max_reference_images", caps.get("max_references", 0))):
        raise CloudAdapterError("Reference-image count exceeds model cap (absolute maximum 14)")
    for role in ("first_frame", "last_frame", "audio"):
        matches = [ref for ref in refs if ref["role"] == role]
        supported = caps.get(role) is True or (role in ("first_frame", "last_frame")
                                              and caps.get("first_last_frame") is True)
        if len(matches) > 1 or (matches and not supported):
            raise CloudAdapterError(f"Selected model does not support requested {role}")
    if any(ref["role"] == "last_frame" for ref in refs) and not any(
            ref["role"] == "first_frame" for ref in refs):
        raise CloudAdapterError("A last frame requires a first frame")
    if count and any(ref["role"] in ("first_frame", "last_frame") for ref in refs):
        raise CloudAdapterError("Frame images can override input references; use one explicitly reviewed conditioning mode")


def discover_cloud_binding(graph: Mapping[str, Any], *, class_type: str,
                           input_map: Mapping[str, str],
                           references: tuple[ReferenceInput, ...] = ()) -> CloudBinding:
    """Discover only an unambiguous configured class with expected input keys."""
    if class_type not in ROUTES:
        raise CloudAdapterError("Unsupported cloud class")
    matches = [node_id for node_id, node in graph.items()
               if isinstance(node, Mapping) and node.get("class_type") == class_type
               and set(input_map.values()) <= set(node.get("inputs", {}))]
    if len(matches) != 1:
        raise CloudAdapterError("Configured cloud node missing or ambiguous; supply explicit binding")
    return CloudBinding(matches[0], class_type, dict(input_map), references)


def prepare_cloud_workflow(graph: Mapping[str, Any], binding: CloudBinding,
                           job: Mapping[str, Any], config: Mapping[str, Any], *,
                            node_catalog: Mapping[str, Mapping[str, Any]],
                            project: Path | None = None,
                            scope: ProjectScope | None = None) -> dict:
    """Validate plan and inject configured literals into a deep copy, never run.

    node_catalog maps class names to current normalized nodes(get) responses.
    Every touched input must already exist in the provided API-format graph.
    References require prewired existing loaders; uploads happen externally.
    """
    validate_cloud_job(job)
    _validate_target(job, project, scope)
    profile = _profile(config, job)
    if binding.class_type not in ROUTES or ROUTES[binding.class_type] != (job["modality"], job["route"]):
        raise CloudAdapterError("Class, modality and endpoint do not match")
    if "nodes" in graph or binding.node_id not in graph:
        raise CloudAdapterError("Requires an existing API-format cloud graph, not a legacy/UI replacement")
    _check_graph(graph, node_catalog, binding.node_id)
    paid_nodes = {node_id for node_id, node in graph.items() if isinstance(node, Mapping)
                  and str(node.get("class_type", "")).startswith("OpenRouter")}
    if paid_nodes != {binding.node_id}:
        raise CloudAdapterError("One paid node per plan; unreviewed OpenRouter nodes prohibited")
    node = graph[binding.node_id]
    if node.get("class_type") != binding.class_type or binding.class_type not in node_catalog:
        raise CloudAdapterError("Configured class missing or not verified in live catalog")
    descriptor = node_catalog[binding.class_type]
    if descriptor.get("name", descriptor.get("id")) != binding.class_type:
        raise CloudAdapterError("Catalog class mismatch")
    specs = _input_specs(descriptor, job["model"])
    if node.get("inputs", {}).get("count", node.get("inputs", {}).get("model.n", 1)) != 1:
        raise CloudAdapterError("One output per cloud job plan; batch output counts need a separate reviewed mapping")
    for key in ("model.remote_references_json", "remote_references_json"):
        if node.get("inputs", {}).get(key, "") not in ("", "[]", "{}"):
            raise CloudAdapterError("Remote references require a separate supported mapping; uploaded loaders only")
    params = {key: value for key, value in profile.get("defaults", {}).items() if key in PARAMETERS}
    params.update(job.get("parameters", {}))
    _check_capabilities({**job, "parameters": params}, profile["capabilities"])
    values = {"model": job["model"], "prompt": job["prompt"], **params}
    if "audio" in profile.get("defaults", {}) and "generate_audio" not in params:
        key = binding.input_map.get("generate_audio")
        choices = specs.get(key, {}).get("choices", [])
        enabled = profile["defaults"]["audio"]
        if type(enabled) is not bool:
            raise CloudAdapterError("Default native audio must be boolean")
        encoded = ("true" if enabled else "false") if "false" in choices else ("on" if enabled else "off")
        values["generate_audio"] = encoded
    # Nonverbal Seed Audio must not inherit the speech node's default voice.
    # Keep the required workflow input, but empty it (plugin omits empty voice).
    if job["modality"] == "audio" and (profile["capabilities"].get("nonverbal") is True
                                     or profile["capabilities"].get("non_speech") is True):
        values["voice"] = ""
    result = copy.deepcopy(dict(graph))
    for semantic, value in values.items():
        key = binding.input_map.get(semantic)
        if not key or key not in node.get("inputs", {}) or key not in specs:
            raise CloudAdapterError(f"No verified configured input for {semantic}; refusing guesses")
        if specs[key].get("is_link") or _linked(node["inputs"][key]):
            raise CloudAdapterError(f"Input {key} is linked; topology cannot be rewritten")
        _check_value(specs[key], value, key)
        result[binding.node_id]["inputs"][key] = copy.deepcopy(value)
    refs = job.get("references", [])
    if len(refs) != len(binding.references):
        raise CloudAdapterError("Reference plan must exactly cover configured loaders")
    covered = {slot.target_input for slot in binding.references}
    for key, value in node.get("inputs", {}).items():
        if specs.get(key, {}).get("type") in ("IMAGE", "AUDIO", "VIDEO") and _linked(value) and key not in covered:
            raise CloudAdapterError("Inherited media link is absent from the explicit reference plan")
    loader_keys = [(slot.node_id, slot.input_key) for slot in binding.references]
    if len(set(loader_keys)) != len(loader_keys):
        raise CloudAdapterError("Reference loaders must be distinct; duplicate assignments prohibited")
    for target_key in covered:
        slots = [slot for slot in binding.references if slot.target_input == target_key]
        leaf_ids = _reference_leaves(graph, node["inputs"].get(target_key),
                                     {slot.node_id for slot in binding.references})
        if leaf_ids != [slot.node_id for slot in slots]:
            raise CloudAdapterError("Reference bundle order/count does not match explicit ordered plan")
    # Autogrow slots are consumed in descriptor order, not the caller's dict order.
    reference_targets = list(dict.fromkeys(slot.target_input for slot in binding.references
                                          if slot.role == "reference"))
    if reference_targets != [key for key in specs if key in reference_targets]:
        raise CloudAdapterError("Autogrow reference order differs from live slot order")
    for ref, slot in zip(refs, binding.references):
        if ref["role"] != slot.role:
            raise CloudAdapterError("Reference role/order mismatch")
        _uploaded_path(ref["uploaded_path"])
        loader = graph.get(slot.node_id, {})
        loader_type = loader.get("class_type")
        if loader_type not in node_catalog:
            raise CloudAdapterError("Reference loader not verified in live catalog")
        loader_specs = _input_specs(node_catalog[loader_type], job["model"])
        if slot.input_key not in loader.get("inputs", {}) or slot.input_key not in loader_specs:
            raise CloudAdapterError("Configured loader input is missing")
        target = specs.get(slot.target_input, {})
        expected_type = "AUDIO" if slot.role == "audio" else "IMAGE"
        if (target.get("type") != expected_type or not target.get("is_link")
                or not _reachable(graph, node.get("inputs", {}).get(slot.target_input), slot.node_id)):
            raise CloudAdapterError("Reference requires an existing correctly typed link to its loader")
        if _linked(loader["inputs"][slot.input_key]) or loader_specs[slot.input_key].get("is_link"):
            raise CloudAdapterError("Cannot replace linked loader input")
        _check_value(loader_specs[slot.input_key], ref["uploaded_path"], slot.input_key)
        result[slot.node_id]["inputs"][slot.input_key] = ref["uploaded_path"]
    return result


def _money(value: Any, name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CloudAdapterError(f"Unknown {name}") from exc
    if not result.is_finite() or result <= 0:
        raise CloudAdapterError(f"{name} must be known, finite and positive; UNKNOWN is never zero")
    return result


def authorize_cloud_job(graph: Mapping[str, Any], job: Mapping[str, Any],
                        config: Mapping[str, Any], approval: Mapping[str, Any], *,
                        budget_estimate_sha256: str, workflow_validated: bool = False,
                         today: date | None = None, project: Path | None = None,
                         scope: ProjectScope | None = None) -> GatedRun:
    """Fail-closed audit gate before caller-owned MCP submission.

    Approval must come from explicit user review, never blanket tool permission.
    This pure function cannot authenticate, submit, or bypass old client APIs.
    Caller must prepare and live-validate the exact graph first and enforce its
    own central budget reservation/ledger. Each changed graph needs new review.
    """
    validate_cloud_job(job)
    resolved_target = _validate_target(job, project, scope)
    _profile(config, job)
    paid_nodes = [node for node in graph.values() if isinstance(node, Mapping)
                  and str(node.get("class_type", "")).startswith("OpenRouter")]
    if len(paid_nodes) != 1:
        raise CloudAdapterError("Authorization requires exactly one reviewed cloud node")
    paid_node = paid_nodes[0]
    class_type = paid_node.get("class_type")
    actual_inputs = paid_node.get("inputs", {})
    prompt_key = ("model.prompt" if str(class_type).startswith("OpenRouterStudio")
                  else "text" if class_type == "OpenRouterAudioSpeak" else "prompt")
    if (ROUTES.get(class_type) != (job["modality"], job["route"])
            or actual_inputs.get("model") != job["model"]
            or actual_inputs.get(prompt_key) != job["prompt"]):
        raise CloudAdapterError("Actual graph class/model/prompt differs from reviewed job metadata")
    today = today or date.today()
    for checked in (config.get("pricing_checked_at"), job["pricing_checked_at"]):
        try:
            checked_date = checked if type(checked) is date else date.fromisoformat(str(checked))
        except ValueError as exc:
            raise CloudAdapterError("Pricing check date is missing/invalid") from exc
        max_age = config.get("pricing_max_age_days", 30)
        if type(max_age) is not int or max_age < 1:
            raise CloudAdapterError("Invalid configured pricing freshness limit")
        if not 0 <= (today - checked_date).days <= max_age:
            raise CloudAdapterError("Pricing must be route-specific and refreshed within the configured age limit")
    if workflow_validated is not True or approval.get("approved") is not True:
        raise CloudAdapterError("Explicit spend approval and live workflow validation required")
    if approval.get("scope") != "paid_generation_job":
        raise CloudAdapterError("Approval must explicitly cover this paid generation job, not planning only")
    workflow_hash, plan_hash = sha256_document(graph), sha256_document(job)
    checks = {"tier": job["tier"], "model": job["model"], "route": job["route"],
              "workflow_sha256": workflow_hash, "plan_sha256": plan_hash,
              "estimate_sha256": budget_estimate_sha256}
    if job.get("reference_scope") == "exploratory":
        checks["target_evidence_sha256"] = job["target_evidence_sha256"]
    if (len(budget_estimate_sha256) != 64
            or any(c not in "0123456789abcdef" for c in budget_estimate_sha256)
            or any(approval.get(key) != value for key, value in checks.items())):
        raise CloudAdapterError("Approval must bind selected tier/model/route, graph, plan and reviewed estimate SHA")
    consent = approval.get("consent_reference")
    if not isinstance(consent, str) or not consent.strip():
        raise CloudAdapterError("Missing explicit user consent reference")
    estimate = _money(job.get("estimated_cost_usd"), "route-specific estimate")
    ceiling = _money(approval.get("ceiling_usd"), "per-job ceiling")
    if estimate > ceiling:
        raise CloudAdapterError("Estimated paid cost exceeds explicitly approved per-job ceiling")
    return GatedRun(job["tier"], job["model"], job["route"], job["prompt_id"], job.get("shot_id"),
                    workflow_hash, plan_hash, budget_estimate_sha256, str(estimate), str(ceiling), consent,
                    tuple((ref["role"], ref["uploaded_path"]) for ref in job.get("references", [])),
                    attempt_number=job.get("attempt_number", 1),
                    job_kind=job.get("job_kind", "shot_render"),
                    entity_id=job.get("entity_id"), entity_type=job.get("entity_type"),
                    project_id=resolved_target[0] if resolved_target else job.get("project_id"),
                    scene_id=resolved_target[1] if resolved_target else job.get("scene_id"),
                    reference_scope=job.get("reference_scope"),
                    target_evidence_sha256=job.get("target_evidence_sha256"))
