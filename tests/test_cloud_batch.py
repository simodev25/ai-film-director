"""Offline cloud_batch.py tests: synthetic project, catalogs and Studio DB.

No network, no ComfyUI, no MCP, no generation. Consent strings are fixtures,
never real user consent.
"""
import hashlib
import importlib.util
import json
import sqlite3
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from budget import save_budget
from cloud_policy import file_sha256
from comfyui.cloud_ledger import CloudLedger

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cloud_batch", ROOT / "scripts/cloud_batch.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

TODAY = date(2026, 10, 5)
IMG_MODEL = "bytedance-seed/seedream-5-0-flash"
VID_MODEL = "google/veo-3.1-lite"


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(data, indent=2))
    else:
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def s(name, kind="STRING", **kw):
    return {"name": name, "type": kind, "is_link": False, **kw}


def image_catalog(choices):
    return {
        "OpenRouterStudioImage": {"name": "OpenRouterStudioImage", "is_api_node": False, "output_node": False,
            "inputs": [{"name": "model", "type": "COMFY_DYNAMICCOMBO_V3", "is_link": False,
                        "selection_keys": [IMG_MODEL], "dynamic_options": [{"key": IMG_MODEL, "inputs": [
                            s("model.prompt"), s("model.resolution", "COMBO", choices=["1K", "2K"]),
                            s("model.aspect_ratio", "COMBO", choices=["16:9", "1:1"]), s("model.n", "INT"),
                            s("model.seed", "INT"),
                            {"name": "model.reference_images", "type": "COMFY_AUTOGROW_V3", "autogrow": True,
                             "element_type": "IMAGE", "is_link": True,
                             "slots": {"names": [f"reference_{i}" for i in range(1, 15)]}}]}]}]},
        "SaveImage": {"name": "SaveImage", "output_node": True,
                      "inputs": [s("images", "IMAGE", is_link=True), s("filename_prefix")]},
        "LoadImage": {"name": "LoadImage", "inputs": [s("image", "COMBO", choices=choices)]},
    }


def video_catalog(choices):
    return {
        "OpenRouterStudioVideo": {"name": "OpenRouterStudioVideo", "is_api_node": False, "output_node": False,
            "inputs": [{"name": "model", "type": "COMFY_DYNAMICCOMBO_V3", "is_link": False,
                        "selection_keys": [VID_MODEL], "dynamic_options": [{"key": VID_MODEL, "inputs": [
                            s("model.prompt"), s("model.duration", "INT"),
                            s("model.resolution", "COMBO", choices=["720p", "1080p"]),
                            s("model.generate_audio", "COMBO", choices=["false", "true"]),
                            s("model.seed", "INT"), s("model.remote_references_json"),
                            s("model.special__negativePrompt"),
                            s("model.first_frame", "IMAGE", is_link=True),
                            s("model.last_frame", "IMAGE", is_link=True)]}]}]},
        "SaveVideo": {"name": "SaveVideo", "output_node": True,
                      "inputs": [s("video", "VIDEO", is_link=True), s("filename_prefix")]},
        "LoadImage": {"name": "LoadImage", "inputs": [s("image", "COMBO", choices=choices)]},
    }


def video_graph(last):
    graph = {"1": {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}},
             "3": {"class_type": "OpenRouterStudioVideo", "inputs": {
                 "model": VID_MODEL, "model.prompt": "__PLACEHOLDER__", "model.duration": 4,
                 "model.resolution": "720p", "model.generate_audio": "false", "model.seed": -1,
                 "model.special__negativePrompt": "", "model.remote_references_json": "",
                 "model.first_frame": ["1", 0]}},
             "4": {"class_type": "SaveVideo", "inputs": {"video": ["3", 0], "filename_prefix": "scaffold"}}}
    if last:
        graph["2"] = {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}}
        graph["3"]["inputs"]["model.last_frame"] = ["2", 0]
    return graph


@pytest.fixture
def project(tmp_path):
    p = tmp_path / "proj"
    dump(p / "project.yaml", {"project_id": "project_fx", "duration_seconds": 50})
    dump(p / "story/story.yaml", {"story_id": "story_fx", "format": {"target_duration_seconds": 50}})
    dump(p / "shots/shots.yaml", {"shots": [
        {"shot_id": "shot_a", "scene_id": "scene_1", "characters": ["char_x"], "location_id": "loc_y"},
        {"shot_id": "shot_b", "scene_id": "scene_1", "characters": ["char_x"], "location_id": "loc_y"}]})
    dump(p / "characters/characters.yaml", {"characters": [{"character_id": "char_x"}]})
    dump(p / "locations/locations.yaml", {"locations": [{"location_id": "loc_y"}]})
    save_budget(p, as_of=TODAY)
    dump(p / "budget/decision.yaml", {
        "approved": True, "scope": "planning_only_not_spend_consent",
        "estimate_sha256": file_sha256(p / "budget/estimate.yaml"), "selected_tier": "preparation",
        "max_spend_usd": 10, "consent_reference": "OFFLINE fixture planning review, NOT user consent"})
    for name, data in (("refs/char_x.png", b"char"), ("refs/loc_y.png", b"loc"),
                       ("renders/key_a.png", b"keyA"), ("renders/key_b.png", b"keyB")):
        (p / name).parent.mkdir(parents=True, exist_ok=True)
        (p / name).write_bytes(data)
    dump(p / "prompts/images/m/shot_a.yaml", {"prompt_id": "img_shot_a", "shot_id": "shot_a", "scene_id": "scene_1",
                                              "model": IMG_MODEL, "prompt": "Wide rainy room.",
                                              "negative_prompt": "text,\n logo"})
    dump(p / "prompts/videos/m/shot_a.yaml", {"prompt_id": "vid_shot_a", "shot_id": "shot_a", "scene_id": "scene_1",
                                              "model": VID_MODEL, "clips": [{"prompt": "Slow dolly-in."}],
                                              "negative": "cut, morphing"})
    wf = p / "workflows/cloud/preparation"
    dump(wf / "img/prepared.api.json", {
        "11": {"class_type": "LoadImage", "inputs": {"image": "old.png"}},
        "12": {"class_type": "LoadImage", "inputs": {"image": "old2.png"}},
        "50": {"class_type": "OpenRouterStudioImage", "inputs": {
            "model": IMG_MODEL, "model.prompt": "old", "model.resolution": "1K", "model.aspect_ratio": "16:9",
            "model.n": 1, "model.seed": -1, "model.reference_images.reference_1": ["11", 0],
            "model.reference_images.reference_2": ["12", 0]}},
        "51": {"class_type": "SaveImage", "inputs": {"images": ["50", 0], "filename_prefix": "old"}}})
    dump(wf / "img/bindings.json", {"declared_node_ids": {"loaders": ["11", "12"], "image": "50", "output": "51"},
                                    "binding": {"class_type": "OpenRouterStudioImage", "input_map": {
                                        "model": "model", "prompt": "model.prompt",
                                        "resolution": "model.resolution", "aspect_ratio": "model.aspect_ratio"}}})
    dump(wf / "vid/first.api.json", video_graph(False))
    dump(wf / "vid/first_last.api.json", video_graph(True))
    dump(wf / "vid/route-evidence.json", {
        "class_type": "OpenRouterStudioVideo",
        "declared_node_ids": {"first_frame_loader": "1", "last_frame_loader": "2", "video": "3", "output": "4"},
        "proposed_binding": {"input_map": {"model": "model", "prompt": "model.prompt", "duration": "model.duration",
                                           "resolution": "model.resolution", "generate_audio": "model.generate_audio"}}})
    return p


def names(p):
    sha = lambda f: hashlib.sha256((p / f).read_bytes()).hexdigest()[:16]
    return {"char": f"fx_char_x_{sha('refs/char_x.png')}.png", "loc": f"fx_loc_y_{sha('refs/loc_y.png')}.png",
            "ka": f"fx_first_frame_{sha('renders/key_a.png')}.png", "kb": f"fx_last_frame_{sha('renders/key_b.png')}.png"}


def write_batch(p, tmp, *, jobs=None, choices=True):
    n = names(p)
    allowed = list(n.values()) if choices else ["unrelated.png"]
    dump(p / "cat/image.json", image_catalog(allowed))
    dump(p / "cat/video.json", video_catalog(allowed))
    batch = {"version": 1, "name": "wave-1", "tier": "preparation", "upload_prefix": "fx",
             "scope": {"scene_ids": ["scene_1"], "entity_ids": ["char_x", "loc_y"]},
             "templates": {"image": {"graph": "workflows/cloud/preparation/img/prepared.api.json",
                                     "bindings": "workflows/cloud/preparation/img/bindings.json"},
                           "video_first": {"graph": "workflows/cloud/preparation/vid/first.api.json",
                                           "evidence": "workflows/cloud/preparation/vid/route-evidence.json"},
                           "video_first_last": {"graph": "workflows/cloud/preparation/vid/first_last.api.json",
                                                "evidence": "workflows/cloud/preparation/vid/route-evidence.json"}},
             "node_catalogs": {"image": "cat/image.json", "video": "cat/video.json"},
             "jobs": jobs if jobs is not None else [
                 {"job_id": "img_a", "modality": "image", "prompt_file": "prompts/images/m/shot_a.yaml",
                  "negative_key": "negative_prompt", "parameters": {"resolution": "1K", "aspect_ratio": "16:9"},
                  "references": [{"asset": "refs/char_x.png", "entity_id": "char_x"},
                                 {"asset": "refs/loc_y.png", "entity_id": "loc_y"}]},
                 {"job_id": "vid_a", "modality": "video", "prompt_file": "prompts/videos/m/shot_a.yaml",
                  "prompt_key": "clips.0.prompt", "negative_key": "negative", "segment_id": "a",
                  "parameters": {"duration": 8},
                  "references": [{"role": "first_frame", "asset": "renders/key_a.png"},
                                 {"role": "last_frame", "asset": "renders/key_b.png"}]}]}
    path = tmp / "batch.yaml"
    dump(path, batch)
    return path


def prepare(p, tmp, sub="out", **kw):
    out = tmp / sub
    code = cb.main(["prepare", "--project", str(p), "--batch", str(write_batch(p, tmp, **kw)), "--out", str(out)])
    return code, out, json.loads((out / "manifest.json").read_text())


def validate_all(out, manifest, **extra):
    for job in manifest["jobs"]:
        dump(Path(job["job_dir"]) / "validation.json",
             {"valid": True, "errors": [], "partner_nodes": [], "spends_credits": False, **extra})


def approve(out, *extra):
    return cb.main(["approve", "--batch-dir", str(out), "--consent-verbatim", "ok fixture",
                    "--question", "Fixture question?", "--ceiling-per-job", "0.30", "--session", "ses_fixture",
                    "--opening-hold-usd", "0", "--opening-balance-reference", "OFFLINE fixture opening",
                    "--today", TODAY.isoformat(), *extra])


def test_prepare_maps_inputs_without_touching_sources(project, tmp_path):
    templates = {f: f.read_bytes() for f in (project / "workflows").rglob("*.json")}
    prompts = {f: f.read_bytes() for f in (project / "prompts").rglob("*.yaml")}
    code, out, manifest = prepare(project, tmp_path)
    assert code == 0, manifest
    assert {f: f.read_bytes() for f in (project / "workflows").rglob("*.json")} == templates
    assert {f: f.read_bytes() for f in (project / "prompts").rglob("*.yaml")} == prompts
    n = names(project)
    img = json.loads((out / "img_a/prepared.api.json").read_text())
    assert img["11"]["inputs"]["image"] == n["char"] and img["12"]["inputs"]["image"] == n["loc"]
    assert img["50"]["inputs"]["model.reference_images.reference_2"] == ["12", 0]
    assert img["50"]["inputs"]["model.prompt"].startswith("Wide rainy room.")
    assert img["50"]["inputs"]["model.prompt"].endswith("text, logo")  # folded negative
    assert img["51"]["inputs"]["filename_prefix"].endswith("wave-1/img_a/attempt_01")
    vid = json.loads((out / "vid_a/prepared.api.json").read_text())
    assert vid["3"]["inputs"]["model.prompt"] == "Slow dolly-in."
    assert vid["3"]["inputs"]["model.duration"] == 8 and vid["3"]["inputs"]["model.generate_audio"] == "false"
    assert vid["3"]["inputs"]["model.special__negativePrompt"] == "cut, morphing"
    assert (vid["1"]["inputs"]["image"], vid["2"]["inputs"]["image"]) == (n["ka"], n["kb"])
    plan = json.loads((out / "vid_a/plan.json").read_text())
    assert plan["prompt_id"] == "vid_shot_a_a" and plan["segment_id"] == "a" and plan["attempt_number"] == 1
    assert plan["estimated_cost_usd"] == 0.24
    assert json.loads((out / "img_a/plan.json").read_text())["estimated_cost_usd"] == 0.018
    mapping = json.loads((out / "vid_a/bindings.json").read_text())["parameter_mapping"]
    assert mapping["prompt"]["input"] == "model.prompt" and mapping["seed"].startswith("unmapped")
    assert [r["role"] for r in mapping["image_input"]] == ["first_frame", "last_frame"]
    assert mapping["audio_input"].startswith("none") and "frames" in mapping and "fps" in mapping
    assert sorted(p.name for p in (out / "uploads").iterdir()) == sorted(n.values())


def test_awaiting_upload_then_live_override(project, tmp_path):
    code, out, manifest = prepare(project, tmp_path, choices=False)
    assert code == 2 and {j["status"] for j in manifest["jobs"]} == {"awaiting_upload"}
    assert not (out / "img_a/prepared.api.json").exists()
    dump(out / "live-descriptors/LoadImage.json", image_catalog(list(names(project).values()))["LoadImage"])
    code = cb.main(["prepare", "--project", str(project), "--batch", str(tmp_path / "batch.yaml"), "--out", str(out)])
    assert code == 0 and (out / "vid_a/prepared.api.json").exists()


@pytest.mark.parametrize("job,needle", [
    ({"parameters": {"duration": 8, "seed": 3}}, "seed"),
    ({"parameters": {"duration": 8, "fps": 24}}, "fps"),
    ({"parameters": {"duration": 8, "width": 1280}}, "width"),
    ({"parameters": {}}, "duration"),
    ({"model": "google/veo-3.1"}, "no fallback"),
    ({"references": [{"role": "last_frame", "asset": "renders/key_b.png"}]}, "Unsupported video reference"),
    ({"references": [{"role": "audio", "asset": "renders/key_b.png"}]}, "Unsupported video reference"),
])
def test_unsupported_mappings_are_blockers(project, tmp_path, job, needle):
    base = {"job_id": "vid_a", "modality": "video", "prompt_file": "prompts/videos/m/shot_a.yaml",
            "prompt_key": "clips.0.prompt", "parameters": {"duration": 8},
            "references": [{"role": "first_frame", "asset": "renders/key_a.png"}]}
    code, out, manifest = prepare(project, tmp_path, jobs=[{**base, **job}])
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked"
    assert needle in manifest["jobs"][0]["blocker"]
    assert not (out / "vid_a/prepared.api.json").exists()


def test_approve_claim_record_status(project, tmp_path, capsys):
    code, out, manifest = prepare(project, tmp_path)
    assert approve(out) == 2  # no live validation yet -> refused, nothing reserved
    assert not (project / "budget/cloud-ledger.sqlite3").exists()
    validate_all(out, manifest)
    assert approve(out) == 0
    printed = capsys.readouterr().out
    assert "confirm_spend=false" in printed and '"prompt_id": "<comfy prompt_id>"' in printed
    approvals = [json.loads((out / j / "approval.json").read_text()) for j in ("img_a", "vid_a")]
    assert approvals[0]["consent_reference"] != approvals[1]["consent_reference"]
    assert all(a["scope"] == "paid_generation_job" and a["consent_user_verbatim"] == "ok fixture" for a in approvals)
    assert approvals[0]["decision_sha256"] == file_sha256(project / "budget/decision.yaml")
    snap = CloudLedger(project).snapshot()
    assert [r["status"] for r in snap["jobs"]] == ["submitted", "submitted"]
    assert approve(out) == 2  # already approved: never re-reserve the same attempt
    # In-flight prior attempt blocks a new preparation of the same target.
    code, _, again = prepare(project, tmp_path, sub="again")
    assert {j["status"] for j in again["jobs"]} == {"blocked"} and "still submitted" in again["jobs"][0]["blocker"]

    claims = json.loads((out / "claims.json").read_text())
    img_plan = json.loads((out / "img_a/plan.json").read_text())
    vid_plan = json.loads((out / "vid_a/plan.json").read_text())
    db_path = tmp_path / "jobs.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE jobs (local_job_id TEXT PRIMARY KEY, media_type TEXT, provider_job_id TEXT,"
                   " model_id TEXT, request_hash TEXT, prompt_hash TEXT, request_summary TEXT, status TEXT,"
                   " created_at TEXT, updated_at TEXT, output_path TEXT, estimated_cost REAL, actual_cost REAL, error TEXT)")
        stamp = datetime.now(timezone.utc).isoformat()
        h = lambda t: hashlib.sha256(t.encode()).hexdigest()
        db.execute("INSERT INTO jobs VALUES ('L1','image','gen-img-1',?, 'r', ?, '{}', 'completed', ?, ?, '/o/a.png', 0.018, 0.018, NULL)",
                   (IMG_MODEL, h(img_plan["prompt"]), stamp, stamp))
        db.execute("INSERT INTO jobs VALUES ('L0','image','gen-img-0',?, 'r', ?, '{}', 'completed', '2020-01-01T00:00:00+00:00', ?, '/o/old.png', 0.018, 0.018, NULL)",
                   (IMG_MODEL, h(img_plan["prompt"]), stamp))  # older, must not match
        db.execute("INSERT INTO jobs VALUES ('L2','video','gen-vid-2',?, 'r', ?, '{}', 'completed', ?, ?, '/o/v.mp4', 0.24, NULL, NULL)",
                   (VID_MODEL, h(vid_plan["prompt"]), stamp, stamp))
    results = tmp_path / "results.json"
    dump(results, {"jobs": [
        {"job_id": "img_a", "prompt_id": "11111111-1111-1111-1111-111111111111", "status": "completed", "outputs": ["renders/a.png"]},
        {"job_id": "vid_a", "prompt_id": "22222222-2222-2222-2222-222222222222", "status": "failed", "outputs": []}]})
    assert cb.main(["record", "--batch-dir", str(out), "--results", str(results), "--studio-db", str(db_path)]) == 0
    rows = {r["plan_hash"]: r for r in CloudLedger(project).snapshot()["jobs"]}
    img_row, vid_row = rows[claims["jobs"][0]["plan_sha256"]], rows[claims["jobs"][1]["plan_sha256"]]
    assert (img_row["status"], img_row["actual"]) == ("completed", "0.018")
    assert json.loads(img_row["record"])["provider_job_id"] == "gen-img-1"
    assert (vid_row["status"], vid_row["actual"]) == ("failed", None)  # unknown stays unknown, never 0
    outcome = json.loads((out / "vid_a/outcome.json").read_text())
    assert outcome["actual_cost_usd"] is None and outcome["estimated_cost_usd"] == 0.24
    capsys.readouterr()
    assert cb.main(["status", "--project", str(project)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert Decimal(status["known_actual_spent_usd"]) == Decimal("0.018")
    assert Decimal(status["unresolved_holds_usd"]) == Decimal("0.3")
    assert Decimal(status["available_usd"]) == Decimal("9.682")
    # Next preparation of the same targets gets the next ledger attempt.
    _, _, nxt = prepare(project, tmp_path, sub="next")
    assert [j["attempt_number"] for j in nxt["jobs"]] == [2, 2]


@pytest.mark.parametrize("case", ["tier", "ceiling", "batch_ceiling", "partner", "changed"])
def test_approve_refusals_reserve_nothing(project, tmp_path, case):
    code, out, manifest = prepare(project, tmp_path)
    validate_all(out, manifest, **({"partner_nodes": ["X"]} if case == "partner" else {}))
    extra = []
    if case == "tier":
        decision = yaml.safe_load((project / "budget/decision.yaml").read_text())
        decision["selected_tier"] = "production"
        dump(project / "budget/decision.yaml", decision)
    if case == "changed":
        graph = json.loads((out / "img_a/prepared.api.json").read_text())
        graph["50"]["inputs"]["model.prompt"] = "tampered"
        dump(out / "img_a/prepared.api.json", graph)
    if case == "batch_ceiling":
        extra = ["--batch-ceiling", "0.4"]
    if case == "ceiling":
        assert cb.main(["approve", "--batch-dir", str(out), "--consent-verbatim", "ok", "--question", "q?",
                        "--ceiling-per-job", "0.1", "--opening-hold-usd", "0",
                        "--opening-balance-reference", "fx", "--today", TODAY.isoformat()]) == 2
    else:
        assert approve(out, *extra) == 2
    assert not (project / "budget/cloud-ledger.sqlite3").exists()
    assert not list(out.glob("*/approval.json"))


# ------------------------------------------------- tests tier: Nano Banana 2 + Wan 3.0
WAN = "alibaba/wan-3.0"
NB2 = "google/gemini-3.1-flash-image"


def wan_catalog(choices):
    return {
        "OpenRouterStudioVideo": {"name": "OpenRouterStudioVideo", "is_api_node": False, "output_node": False,
            "inputs": [{"name": "model", "type": "COMFY_DYNAMICCOMBO_V3", "is_link": False,
                        "selection_keys": [VID_MODEL, WAN], "dynamic_options": [
                            {"key": VID_MODEL, "inputs": []},
                            {"key": WAN, "inputs": [
                                s("model.prompt", required=True),
                                s("model.duration", "COMBO", choices=list(range(2, 31)), required=True),
                                s("model.resolution", "COMBO", choices=["480p", "720p", "1080p"], required=True),
                                s("model.aspect_ratio", "COMBO", choices=["16:9", "4:3", "1:1", "3:4", "9:16"], required=True),
                                s("model.generate_audio", "COMBO", choices=["false", "true", "provider default"], required=True),
                                s("model.seed", "INT", required=True),
                                s("model.remote_references_json", required=True),
                                s("model.provider_options_json", required=True),
                                s("model.first_frame", "IMAGE", is_link=True, required=False)]}]}]},
        "SaveVideo": {"name": "SaveVideo", "output_node": True,
                      "inputs": [s("video", "VIDEO", is_link=True), s("filename_prefix")]},
        "LoadImage": {"name": "LoadImage", "inputs": [s("image", "COMBO", choices=choices)]},
    }


def nb2_catalog(choices):
    return {
        "OpenRouterStudioImage": {"name": "OpenRouterStudioImage", "is_api_node": False, "output_node": False,
            "inputs": [{"name": "model", "type": "COMFY_DYNAMICCOMBO_V3", "is_link": False,
                        "selection_keys": [NB2], "dynamic_options": [{"key": NB2, "inputs": [
                            s("model.prompt", required=True), s("model.size", required=True),
                            s("model.resolution", "COMBO", choices=["provider default", "512", "1K", "2K", "4K"], required=True),
                            s("model.aspect_ratio", "COMBO", choices=["provider default", "1:1", "16:9", "9:16"], required=True),
                            s("model.n", "INT", required=True, options={"min": 1, "max": 1}),
                            {"name": "model.reference_images", "type": "COMFY_AUTOGROW_V3", "autogrow": True,
                             "element_type": "IMAGE", "is_link": True, "required": True,
                             "slots": {"names": [f"reference_{i}" for i in range(1, 15)], "min": 0, "max": 14}},
                            s("model.provider_route", "COMBO", choices=["automatic routing"], required=True),
                            s("model.allow_fallbacks", "COMBO", choices=["provider default", "true", "false"], required=True),
                            s("model.provider_sort", "COMBO", choices=["provider default"], required=True),
                            s("model.special__cachedContent", required=True),
                            s("model.provider_options_json", required=True)]}]}]},
        "SaveImage": {"name": "SaveImage", "output_node": True,
                      "inputs": [s("images", "IMAGE", is_link=True), s("filename_prefix")]},
        "LoadImage": {"name": "LoadImage", "inputs": [s("image", "COMBO", choices=choices)]},
    }


def make_tests_tier_files(p):
    wf = p / "workflows/cloud/tests"
    dump(wf / "wan/first.api.json", {
        "1": {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}},
        "3": {"class_type": "OpenRouterStudioVideo", "inputs": {
            "model": WAN, "model.prompt": "__PLACEHOLDER__", "model.duration": 5, "model.resolution": "720p",
            "model.aspect_ratio": "16:9", "model.generate_audio": "false", "model.seed": -1,
            "model.remote_references_json": "", "model.provider_options_json": "", "model.first_frame": ["1", 0]}},
        "4": {"class_type": "SaveVideo", "inputs": {"video": ["3", 0], "filename_prefix": "scaffold"}}})
    dump(wf / "wan/route-evidence.json", {
        "class_type": "OpenRouterStudioVideo",
        "declared_node_ids": {"first_frame_loader": "1", "last_frame_loader": None, "video": "3", "output": "4"},
        "proposed_binding": {"input_map": {"model": "model", "prompt": "model.prompt", "duration": "model.duration",
                                           "resolution": "model.resolution", "generate_audio": "model.generate_audio"}}})
    dump(wf / "nb2/scaffold.api.json", {
        "3001": {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}},
        "3050": {"class_type": "OpenRouterStudioImage", "inputs": {
            "model": NB2, "model.prompt": "__PLACEHOLDER__", "model.size": "", "model.resolution": "1K",
            "model.aspect_ratio": "16:9", "model.n": 1, "model.reference_images.reference_1": ["3001", 0],
            "model.provider_route": "automatic routing", "model.allow_fallbacks": "provider default",
            "model.provider_sort": "provider default", "model.special__cachedContent": "",
            "model.provider_options_json": ""}},
        "3051": {"class_type": "SaveImage", "inputs": {"images": ["3050", 0], "filename_prefix": "scaffold"}}})
    dump(wf / "nb2/bindings.json", {"declared_node_ids": {"loaders": ["3001"], "image": "3050", "output": "3051"},
                                    "binding": {"class_type": "OpenRouterStudioImage", "input_map": {
                                        "model": "model", "prompt": "model.prompt",
                                        "resolution": "model.resolution", "aspect_ratio": "model.aspect_ratio"}}})
    for i in range(1, 16):
        (p / f"refs/r{i:02d}.png").write_bytes(f"ref{i}".encode())
    dump(p / "prompts/videos/wan/shot_a.yaml", {"prompt_id": "vid_wan_shot_a", "shot_id": "shot_a", "scene_id": "scene_1",
                                                "model": WAN, "prompt": "Slow push-in, rain on glass.",
                                                "negative": "morphing, text"})
    dump(p / "prompts/images/nb2/shot_a.yaml", {"prompt_id": "img_nb2_shot_a", "shot_id": "shot_a", "scene_id": "scene_1",
                                                "model": NB2, "prompt": "Wide rainy room.", "negative_prompt": "logo"})


def prepare_tests_tier(p, tmp, jobs, *, wan_template=True):
    make_tests_tier_files(p)
    # Explicit fixture topology; the helper must never expand a supplied graph.
    count = next((len(j.get("references", [])) for j in jobs if j["modality"] == "image"), 1)
    graph_path = p / "workflows/cloud/tests/nb2/scaffold.api.json"
    graph = json.loads(graph_path.read_text())
    binding_path = p / "workflows/cloud/tests/nb2/bindings.json"
    binding = json.loads(binding_path.read_text())
    for i in range(2, min(count, 14) + 1):
        loader = str(3000 + i)
        graph[loader] = {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}}
        graph["3050"]["inputs"][f"model.reference_images.reference_{i}"] = [loader, 0]
        binding["declared_node_ids"]["loaders"].append(loader)
    dump(graph_path, graph)
    dump(binding_path, binding)
    choices = [cb.upload_name("fx", "first_frame", hashlib.sha256((p / "renders/key_a.png").read_bytes()).hexdigest(), ".png")]
    choices += [cb.upload_name("fx", f"r{i:02d}", hashlib.sha256((p / f"refs/r{i:02d}.png").read_bytes()).hexdigest(), ".png")
                for i in range(1, 16)]
    dump(p / "cat/wan.json", wan_catalog(choices))
    dump(p / "cat/nb2.json", nb2_catalog(choices))
    video_first = ({"graph": "workflows/cloud/tests/wan/first.api.json", "evidence": "workflows/cloud/tests/wan/route-evidence.json"}
                   if wan_template else
                   {"graph": "workflows/cloud/preparation/vid/first.api.json", "evidence": "workflows/cloud/preparation/vid/route-evidence.json"})
    batch = {"version": 1, "name": "tests-1", "tier": "tests", "upload_prefix": "fx",
             "scope": {"scene_ids": ["scene_1"], "entity_ids": ["char_x", "loc_y"]},
             "templates": {"image": {"graph": "workflows/cloud/tests/nb2/scaffold.api.json",
                                     "bindings": "workflows/cloud/tests/nb2/bindings.json"},
                           "video_first": video_first},
             "node_catalogs": {"image": "cat/nb2.json", "video": "cat/wan.json"}, "jobs": jobs}
    path = tmp / "batch-tests.yaml"
    dump(path, batch)
    out = tmp / "out-tests"
    code = cb.main(["prepare", "--project", str(p), "--batch", str(path), "--out", str(out)])
    return code, out, json.loads((out / "manifest.json").read_text())


WAN_JOB = {"job_id": "vid_wan", "modality": "video", "prompt_file": "prompts/videos/wan/shot_a.yaml",
           "parameters": {"duration": 12}, "references": [{"role": "first_frame", "asset": "renders/key_a.png"}]}


def test_wan_first_frame_job_maps_exact_live_inputs(project, tmp_path):
    code, out, manifest = prepare_tests_tier(project, tmp_path, [WAN_JOB])
    assert code == 0, manifest
    graph = json.loads((out / "vid_wan/prepared.api.json").read_text())
    inputs = graph["3"]["inputs"]
    assert inputs["model"] == WAN and inputs["model.prompt"] == "Slow push-in, rain on glass."
    assert (inputs["model.duration"], inputs["model.resolution"], inputs["model.generate_audio"]) == (12, "720p", "false")
    assert inputs["model.first_frame"] == ["1", 0] and "model.last_frame" not in inputs
    assert not any(k.startswith("model.special__") or k == "model.size" for k in inputs)
    plan = json.loads((out / "vid_wan/plan.json").read_text())
    assert plan["tier"] == "tests" and plan["model"] == WAN and plan["estimated_cost_usd"] == pytest.approx(1.2)
    bindings = json.loads((out / "vid_wan/bindings.json").read_text())
    assert bindings["negative_prompt_input"] is None
    mapping = bindings["parameter_mapping"]
    assert mapping["seed"].startswith("unmapped; scaffold literal model.seed=-1")
    assert mapping["width"].endswith("no such input on this route") and mapping["fps"].endswith("no such input on this route")
    assert [r["role"] for r in mapping["image_input"]] == ["first_frame"] and mapping["audio_input"].startswith("none")


@pytest.mark.parametrize("job,needle", [
    ({"negative_key": "negative"}, "no live negative-prompt input"),
    ({"parameters": {"duration": 31}}, "duration"),
    ({"parameters": {"duration": 1}}, "duration"),
    ({"parameters": {"duration": 8, "generate_audio": "true"}}, "unknown pricing"),
    ({"parameters": {"duration": 8, "seed": 7}}, "seed"),
    ({"parameters": {"duration": 8, "resolution": "4K"}}, "resolution"),
    ({"references": [{"role": "first_frame", "asset": "renders/key_a.png"},
                     {"role": "last_frame", "asset": "renders/key_b.png"}]}, "video_first_last scaffold"),
    ({"model": "kwaivgi/kling-v3.0-pro"}, "no fallback"),
])
def test_wan_unsupported_requests_are_blockers(project, tmp_path, job, needle):
    code, out, manifest = prepare_tests_tier(project, tmp_path, [{**WAN_JOB, **job}])
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked", manifest
    assert needle in manifest["jobs"][0]["blocker"]
    assert not (out / "vid_wan/prepared.api.json").exists()


def test_wan_negative_fold_is_explicit_opt_in(project, tmp_path):
    code, out, manifest = prepare_tests_tier(project, tmp_path, [{**WAN_JOB, "negative_key": "negative", "negative_fold": True}])
    assert code == 0, manifest
    prompt = json.loads((out / "vid_wan/prepared.api.json").read_text())["3"]["inputs"]["model.prompt"]
    assert prompt.startswith("Slow push-in") and prompt.endswith("morphing, text")
    assert json.loads((out / "vid_wan/bindings.json").read_text())["negative_prompt_input"] == "folded_into_prompt"


def test_veo_scaffold_with_wan_model_is_a_blocker(project, tmp_path):
    code, _, manifest = prepare_tests_tier(project, tmp_path, [WAN_JOB], wan_template=False)
    assert code == 2 and "does not match live branch of alibaba/wan-3.0" in manifest["jobs"][0]["blocker"]


def nb2_job(count):
    return {"job_id": "img_nb2", "modality": "image", "prompt_file": "prompts/images/nb2/shot_a.yaml",
            "negative_key": "negative_prompt", "parameters": {"resolution": "1K", "aspect_ratio": "16:9"},
            "references": [{"asset": f"refs/r{i:02d}.png", "entity_id": f"r{i:02d}"} for i in range(1, count + 1)]}


def test_nano_banana_2_1k_16x9_fourteen_ordered_references(project, tmp_path):
    code, out, manifest = prepare_tests_tier(project, tmp_path, [nb2_job(14)])
    assert code == 0, manifest
    graph = json.loads((out / "img_nb2/prepared.api.json").read_text())
    inputs = graph["3050"]["inputs"]
    assert (inputs["model"], inputs["model.resolution"], inputs["model.aspect_ratio"]) == (NB2, "1K", "16:9")
    assert inputs["model.prompt"].startswith("Wide rainy room.") and inputs["model.prompt"].endswith("logo")
    for i in range(1, 15):
        loader = inputs[f"model.reference_images.reference_{i}"][0]
        assert graph[loader]["inputs"]["image"].startswith(f"fx_r{i:02d}_")
    plan = json.loads((out / "img_nb2/plan.json").read_text())
    assert plan["estimated_cost_usd"] == pytest.approx(0.0672 + 14 * 0.00056)
    assert "model.seed" not in inputs


def test_nano_banana_2_fifteen_references_blocked(project, tmp_path):
    code, _, manifest = prepare_tests_tier(project, tmp_path, [nb2_job(15)])
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked"


LIVE = ROOT / "projects/la-pomme/workflows/cloud"


@pytest.mark.skipif(not (LIVE / "tests/scene-01-video/scaffold-first-only.wan-3.0.api.json").exists(),
                    reason="la-pomme live scaffolds absent")
@pytest.mark.parametrize("model,catalog,graph,node", [
    (WAN, "preparation/scene-01-video/node-catalog.selected.live.json",
     "tests/scene-01-video/scaffold-first-only.wan-3.0.api.json", "3"),
    (NB2, "tests/scene-01-shots/node-catalog.selected.live.json",
     "tests/scene-01-shots/scaffold-gemini-3.1-flash-image.api.json", "3050"),
])
def test_real_live_scaffolds_fit_live_branches(model, catalog, graph, node):
    cat = json.loads((LIVE / catalog).read_text())
    g = json.loads((LIVE / graph).read_text())
    specs = cb._input_specs(cat[g[node]["class_type"]], model)
    cb.check_branch(g[node]["inputs"], specs, model, graph)  # raises on stale/missing keys
    if model == NB2:
        assert specs["model.reference_images.reference_14"]["type"] == "IMAGE"
        assert "model.reference_images.reference_15" not in specs
        assert {"1K"} <= set(specs["model.resolution"]["choices"]) and "16:9" in specs["model.aspect_ratio"]["choices"]
    else:
        assert specs["model.duration"]["choices"] == list(range(2, 31))
        assert "model.last_frame" not in specs and not any("negative" in k for k in specs)


# ------------------------------------------------- uploads-refresh / validations
def test_uploads_refresh_from_envelope_descriptor_then_prepare(project, tmp_path, capsys):
    code, out, manifest = prepare(project, tmp_path, choices=False)
    assert code == 2 and {j["status"] for j in manifest["jobs"]} == {"awaiting_upload"}
    n = names(project)
    live = image_catalog(["clipspace.png", *n.values()])["LoadImage"]
    dump(tmp_path / "nodes_get.json", {"schema": "envelope/1", "ok": True, "command": "nodes show", "data": live})
    assert cb.main(["uploads-refresh", "--batch-dir", str(out), "--descriptor", str(tmp_path / "nodes_get.json")]) == 0
    saved = json.loads((out / "live-descriptors/LoadImage.json").read_text())
    assert saved == live  # verbatim live descriptor, nothing added
    report = json.loads((out / "uploads-refresh.json").read_text())
    assert report["added_from_upload_evidence"] == [] and report["still_missing"] == []
    code = cb.main(["prepare", "--project", str(project), "--batch", str(tmp_path / "batch.yaml"), "--out", str(out)])
    assert code == 0


def test_uploads_refresh_adds_only_batch_names_named_by_upload_evidence(project, tmp_path):
    code, out, manifest = prepare(project, tmp_path, choices=False)
    n = names(project)
    dump(tmp_path / "nodes_get.json", image_catalog(["unrelated.png"])["LoadImage"])
    # partial evidence: two uploads + a foreign name -> foreign ignored, others still missing
    dump(tmp_path / "upload.json", {"uploaded": [{"name": n["char"]}, {"name": f"sub/{n['loc']}"}, "evil.png"]})
    args = ["uploads-refresh", "--batch-dir", str(out), "--descriptor", str(tmp_path / "nodes_get.json"),
            "--choices-from", str(tmp_path / "upload.json")]
    assert cb.main(args) == 2
    report = json.loads((out / "uploads-refresh.json").read_text())
    assert report["added_from_upload_evidence"] == sorted([n["char"], n["loc"]])
    assert report["ignored_non_batch_names"] == ["evil.png"]
    assert report["still_missing"] == sorted([n["ka"], n["kb"]])
    choices = json.loads((out / "live-descriptors/LoadImage.json").read_text())["inputs"][0]["choices"]
    assert choices == ["unrelated.png", *sorted([n["char"], n["loc"]])] and "evil.png" not in choices
    # text evidence for the rest; saved descriptor reused without --descriptor
    (tmp_path / "rest.txt").write_text(f"{n['ka']}\n{n['kb']}\n")
    assert cb.main(["uploads-refresh", "--batch-dir", str(out), "--choices-from", str(tmp_path / "rest.txt")]) == 0
    code = cb.main(["prepare", "--project", str(project), "--batch", str(tmp_path / "batch.yaml"), "--out", str(out)])
    assert code == 0


@pytest.mark.parametrize("bad", [
    {"schema": "envelope/1", "ok": False, "command": "nodes show", "data": None},
    {"name": "SaveImage", "inputs": []},
    {"name": "LoadImage", "inputs": [{"name": "image", "type": "COMBO"}]},
])
def test_uploads_refresh_rejects_non_live_descriptors(project, tmp_path, bad):
    code, out, manifest = prepare(project, tmp_path, choices=False)
    dump(tmp_path / "bad.json", bad)
    assert cb.main(["uploads-refresh", "--batch-dir", str(out), "--descriptor", str(tmp_path / "bad.json")]) == 2
    assert not (out / "live-descriptors/LoadImage.json").exists()


def test_uploads_refresh_refuses_changed_staged_upload(project, tmp_path):
    code, out, manifest = prepare(project, tmp_path, choices=False)
    staged = Path(manifest["jobs"][0]["uploads"][0]["staged_file"])
    staged.write_bytes(b"tampered")
    dump(tmp_path / "nodes_get.json", image_catalog(list(names(project).values()))["LoadImage"])
    assert cb.main(["uploads-refresh", "--batch-dir", str(out), "--descriptor", str(tmp_path / "nodes_get.json")]) == 2
    assert not (out / "live-descriptors/LoadImage.json").exists()


def test_validations_writes_verbatim_reports_then_approve(project, tmp_path):
    code, out, manifest = prepare(project, tmp_path)
    clean = {"valid": True, "error_count": 0, "errors": [], "warnings": [], "partner_nodes": [], "spends_credits": False}
    rows = {j["job_id"]: j for j in manifest["jobs"]}
    dump(tmp_path / "vr.json", {"jobs": [
        {"job_id": "img_a", "validation": {"schema": "envelope/1", "ok": True, "data": clean},
         "workflow_path": rows["img_a"]["prepared"]},
        {"job_id": "vid_a", "result": clean}]})
    assert cb.main(["validations", "--batch-dir", str(out), "--from", str(tmp_path / "vr.json")]) == 0
    assert json.loads((out / "img_a/validation.json").read_text()) == clean
    assert approve(out) == 0


def test_validations_unclean_or_missing_is_reported_and_blocks_approve(project, tmp_path):
    code, out, manifest = prepare(project, tmp_path)
    dump(tmp_path / "vr.json", {"img_a": {"valid": True, "partner_nodes": ["OpenRouterStudioImage"],
                                          "spends_credits": True}})
    assert cb.main(["validations", "--batch-dir", str(out), "--from", str(tmp_path / "vr.json")]) == 2
    assert (out / "img_a/validation.json").exists() and not (out / "vid_a/validation.json").exists()
    assert approve(out) == 2
    assert not (project / "budget/cloud-ledger.sqlite3").exists()


@pytest.mark.parametrize("case", ["unknown_job", "wrong_path", "not_report", "changed_graph", "awaiting"])
def test_validations_refusals_write_nothing(project, tmp_path, case):
    code, out, manifest = prepare(project, tmp_path, choices=(case != "awaiting"))
    clean = {"valid": True, "partner_nodes": [], "spends_credits": False}
    data = {"jobs": [{"job_id": "img_a", "validation": clean}, {"job_id": "vid_a", "validation": clean}]}
    if case == "unknown_job":
        data["jobs"].append({"job_id": "ghost", "validation": clean})
    elif case == "wrong_path":
        data["jobs"][1]["workflow_path"] = str(out / "img_a/prepared.api.json")
    elif case == "not_report":
        data["jobs"][1]["validation"] = {"ok": True}
    elif case == "changed_graph":
        (out / "vid_a/prepared.api.json").write_text("{}")
    dump(tmp_path / "vr.json", data)
    assert cb.main(["validations", "--batch-dir", str(out), "--from", str(tmp_path / "vr.json")]) == 2
    assert not list(out.glob("*/validation.json"))
