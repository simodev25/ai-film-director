"""Synthetic offline evidence/consent only. No real project jobs or media calls."""
import copy
import json
from dataclasses import asdict

import pytest
import yaml

from budget import save_budget
from cloud_policy import file_sha256, load_cloud_policy
from comfyui.cloud_adapters import CloudAdapterError, authorize_cloud_job, sha256_document, validate_cloud_job
from comfyui.cloud_ledger import CloudLedger, LedgerError
from comfyui.cloud_targets import ProjectScope, exploratory_target_evidence, validate_project_target
from test_cloud_batch import project, dump, write_batch, cb, TODAY, validate_all, approve


@pytest.fixture
def exploratory(project, tmp_path):
    for relative in ("shots/shots.yaml", "characters/characters.yaml", "locations/locations.yaml"):
        (project / relative).unlink()
    dump(project / "story/story.yaml", {"story_id": "story_fx", "characters": ["char_x"],
                                      "locations": ["loc_y"], "format": {"target_duration_seconds": 50}})
    registry = {"registry_version": 1, "project_id": "project_fx", "references": [
        {"order": i, "entity_type": kind, "entity_id": entity, "path": path,
         "sha256": file_sha256(project / path), "approved_at": "2026-10-05",
         "consent_verbatim": "OFFLINE fixture source approval"}
        for i, kind, entity, path in [(1, "character", "char_x", "refs/char_x.png"),
                                     (2, "location", "loc_y", "refs/loc_y.png")]]}
    dump(project / "references/approved-references.yaml", registry)
    save_budget(project, as_of=TODAY)
    decision = yaml.safe_load((project / "budget/decision.yaml").read_text())
    decision["estimate_sha256"] = file_sha256(project / "budget/estimate.yaml")
    dump(project / "budget/decision.yaml", decision)
    dump(project / "prompts/exploratory/adult.yaml", {"prompt_id": "explore_adult", "prompt": "Reference portrait."})
    item = {"job_id": "portrait", "job_kind": "reference_illustration", "reference_scope": "exploratory",
            "modality": "image", "entity_type": "character", "entity_id": "char_x",
            "prompt_file": "prompts/exploratory/adult.yaml", "references": [
                {"entity_type": r["entity_type"], "entity_id": r["entity_id"], "asset": r["path"]}
                for r in registry["references"]]}
    batch_file = write_batch(project, tmp_path, jobs=[item])
    batch = yaml.safe_load(batch_file.read_text())
    batch["scope"]["scene_ids"] = []
    dump(batch_file, batch)
    return project, batch_file, tmp_path / "exploratory"


def run_prepare(fixture):
    project, batch_file, out = fixture
    code = cb.main(["prepare", "--project", str(project), "--batch", str(batch_file), "--out", str(out)])
    return code, json.loads((out / "manifest.json").read_text())


def prepared(fixture):
    code, manifest = run_prepare(fixture)
    assert code == 0, manifest
    project, _, out = fixture
    job = cb.read_json(out / "portrait/plan.json")
    graph = cb.read_json(out / "portrait/prepared.api.json")
    scope = ProjectScope((), ("char_x", "loc_y"))
    return project, out, manifest, job, graph, scope


def test_minimal_story_reference_scope_preserves_bytes_and_topology(exploratory):
    project, _, out = exploratory
    sources = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    _, _, manifest, job, graph, scope = prepared(exploratory)
    assert all(p.read_bytes() == raw for p, raw in sources.items())
    original = cb.read_json(project / "workflows/cloud/preparation/img/prepared.api.json")
    assert graph.keys() == original.keys()
    for ident in graph:
        assert graph[ident]["class_type"] == original[ident]["class_type"]
        for key, value in original[ident]["inputs"].items():
            if isinstance(value, list):
                assert graph[ident]["inputs"][key] == value
    assert validate_project_target(job, project, scope) == ("project_fx", None)
    assert job["estimated_cost_usd"] == 0.018
    assert not (project / "shots/shots.yaml").exists()
    assert not (project / "budget/cloud-ledger.sqlite3").exists()
    validate_all(out, manifest)
    assert approve(out) == 0  # synthetic fixture evidence, no transport
    audit = json.loads(CloudLedger(project).snapshot()["jobs"][0]["record"])["audit"]
    assert audit["reference_scope"] == "exploratory" and audit["canonical_stage_completion"] is False
    assert audit["scene_id"] is None and audit["actual_cost_usd"] is None


@pytest.mark.parametrize("change", ["unknown", "type", "project", "scene", "shot", "segment", "scope_scene", "scope_empty", "unknown_ref", "unapproved_asset", "too_few_slots"])
def test_invalid_exploratory_batch_blocks(exploratory, change):
    project, batch_file, out = exploratory
    batch = yaml.safe_load(batch_file.read_text())
    item = batch["jobs"][0]
    if change == "unknown": item["entity_id"] = "caller_invented"
    elif change == "type": item["entity_type"] = "prop"
    elif change in ("scene", "shot", "segment"): item[change + "_id"] = "forbidden"
    elif change == "scope_scene": batch["scope"]["scene_ids"] = ["invented"]
    elif change == "scope_empty": batch["scope"]["entity_ids"] = []
    elif change == "unknown_ref": item["references"][0]["entity_id"] = "invented"
    elif change == "unapproved_asset": item["references"][0]["asset"] = "renders/key_a.png"
    elif change == "too_few_slots": item["references"].append(copy.deepcopy(item["references"][0]))
    elif change == "project":
        registry = yaml.safe_load((project / "references/approved-references.yaml").read_text())
        registry["project_id"] = "other_project"
        dump(project / "references/approved-references.yaml", registry)
    dump(batch_file, batch)
    code, manifest = run_prepare(exploratory)
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked"
    assert not (out / "portrait/prepared.api.json").exists()


@pytest.mark.parametrize("change", ["hash", "escape", "duplicate_order", "wrong_type", "story_missing", "story_duplicate", "canonical_missing", "canonical_ambiguous"])
def test_invalid_source_evidence_blocks(exploratory, change, tmp_path):
    project, _, _ = exploratory
    path = project / "references/approved-references.yaml"
    registry = yaml.safe_load(path.read_text())
    if change == "hash": registry["references"][0]["sha256"] = "0" * 64
    elif change == "escape": registry["references"][0]["path"] = "../outside.png"
    elif change == "duplicate_order": registry["references"][1]["order"] = 1
    elif change == "wrong_type":
        row = copy.deepcopy(registry["references"][0]); row.update(order=3, entity_type="prop")
        registry["references"].append(row)
    elif change.startswith("story_"):
        story = yaml.safe_load((project / "story/story.yaml").read_text())
        story["characters"] = [] if change == "story_missing" else ["char_x", "char_x"]
        dump(project / "story/story.yaml", story)
    else:
        dump(project / "characters/characters.yaml", {"characters": [] if change == "canonical_missing" else [
            {"character_id": "char_x"}, {"character_id": "char_x"}]})
    dump(path, registry)
    code, manifest = run_prepare(exploratory)
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked"


def test_unambiguous_repeated_entity_appearances_allowed(exploratory):
    project, _, _ = exploratory
    path = project / "references/approved-references.yaml"
    registry = yaml.safe_load(path.read_text())
    row = copy.deepcopy(registry["references"][0]); row["order"] = 3
    registry["references"].append(row)
    dump(path, registry)
    assert run_prepare(exploratory)[0] == 0


@pytest.mark.parametrize("changed", ["references/approved-references.yaml", "refs/char_x.png", "canonical_created"])
def test_source_change_after_preparation_blocks_approval(exploratory, changed):
    project, out, manifest, _, _, _ = prepared(exploratory)
    validate_all(out, manifest)
    if changed == "canonical_created":
        dump(project / "characters/characters.yaml", {"characters": [{"character_id": "char_x"}]})
    else:
        path = project / changed
        path.write_bytes(path.read_bytes() + b"\n")
    assert approve(out) == 2
    assert not (project / "budget/cloud-ledger.sqlite3").exists()


def test_evidence_change_after_reservation_blocks_claim(exploratory):
    project, out, _, job, graph, scope = prepared(exploratory)
    approval = {"approved": True, "scope": "paid_generation_job", "tier": job["tier"], "model": job["model"],
                "route": job["route"], "workflow_sha256": sha256_document(graph), "plan_sha256": sha256_document(job),
                "project_id": job["project_id"], "scope_sha256": sha256_document(asdict(scope)),
                "estimate_sha256": file_sha256(project / "budget/estimate.yaml"),
                "decision_sha256": file_sha256(project / "budget/decision.yaml"), "ceiling_usd": 0.1,
                "target_evidence_sha256": job["target_evidence_sha256"], "consent_reference": "OFFLINE fixture paid consent"}
    ledger = CloudLedger(project)
    key = ledger.reserve(graph, job, approval, scope=scope, workflow_validated=True, today=TODAY,
                         opening_hold_usd=0, opening_balance_reference="OFFLINE fixture opening evidence")
    path = project / "references/approved-references.yaml"
    path.write_text(path.read_text() + "\n# changed source bytes\n")
    with pytest.raises(LedgerError, match="evidence changed"):
        ledger.claim(key, graph, job, today=TODAY)
    assert ledger.snapshot()["jobs"][0]["status"] == "reserved"


def test_exploratory_cannot_make_shot_or_scene_job_valid(exploratory):
    project, _, _, job, _, scope = prepared(exploratory)
    shot = {k: v for k, v in job.items() if k not in (
        "reference_scope", "target_evidence_sha256", "entity_id", "entity_type", "job_kind")}
    shot["shot_id"] = "caller_shot"
    validate_cloud_job(shot)
    with pytest.raises(OSError): validate_project_target(shot, project, scope)
    scene = {k: v for k, v in job.items() if k not in ("reference_scope", "target_evidence_sha256")}
    with pytest.raises(CloudAdapterError): validate_cloud_job(scene)
    shot["reference_scope"] = "exploratory"
    with pytest.raises(CloudAdapterError): validate_cloud_job(shot)


def test_symlink_asset_escape_blocked(exploratory, tmp_path):
    project, _, _ = exploratory
    outside = tmp_path / "outside.png"
    outside.write_bytes((project / "refs/char_x.png").read_bytes())
    (project / "refs/char_x.png").unlink()
    (project / "refs/char_x.png").symlink_to(outside)
    code, manifest = run_prepare(exploratory)
    assert code == 2 and manifest["jobs"][0]["status"] == "blocked"


def test_approved_reference_missing_and_canonical_registry_authority(exploratory):
    project, _, _ = exploratory
    # Even an approved story ID cannot fill an existing empty canonical category.
    dump(project / "characters/characters.yaml", {"characters": []})
    assert run_prepare(exploratory)[0] == 2
    (project / "characters/characters.yaml").unlink()
    (project / "references/approved-references.yaml").unlink()
    assert run_prepare(exploratory)[0] == 2


@pytest.mark.parametrize("field", ["reference_scope", "target_evidence_sha256"])
def test_exploratory_required_fields_never_inferred(exploratory, field):
    _, _, _, job, _, _ = prepared(exploratory)
    job.pop(field)
    with pytest.raises(CloudAdapterError): validate_cloud_job(job)


def test_exploratory_approval_must_explicitly_bind_entity_evidence(exploratory):
    project, _, _, job, graph, scope = prepared(exploratory)
    approval = {"approved": True, "scope": "paid_generation_job", "tier": job["tier"],
                "model": job["model"], "route": job["route"], "workflow_sha256": sha256_document(graph),
                "plan_sha256": sha256_document(job), "estimate_sha256": file_sha256(project / "budget/estimate.yaml"),
                "ceiling_usd": 0.1, "consent_reference": "OFFLINE fixture consent without evidence binding"}
    with pytest.raises(CloudAdapterError, match="Approval must bind"):
        authorize_cloud_job(graph, job, load_cloud_policy(), approval, project=project, scope=scope,
                            workflow_validated=True, today=TODAY,
                            budget_estimate_sha256=approval["estimate_sha256"])


def test_missing_comfy_credit_classification_is_not_clean_validation(exploratory):
    project, out, manifest, _, _, _ = prepared(exploratory)
    validate_all(out, manifest)
    path = out / "portrait/validation.json"
    report = cb.read_json(path); report.pop("partner_nodes")
    dump(path, report)
    assert approve(out) == 2
    assert not (project / "budget/cloud-ledger.sqlite3").exists()
