"""Offline synthetic approval fixtures: never real consent or network jobs."""
import copy
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import date
from pathlib import Path

import pytest
import yaml

from budget import save_budget
from cloud_policy import file_sha256
from comfyui.cloud_adapters import (
    CloudAdapterError, authorize_cloud_job, prepare_cloud_workflow,
    sha256_document, validate_cloud_job,
)
from comfyui.cloud_ledger import CloudLedger, LedgerError
from comfyui.cloud_targets import ProjectScope, validate_project_target
from validation import validate_data
from test_cloud_adapters import setup  # existing offline node/graph fixture

TODAY = date(2026, 10, 5)
SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value))


@pytest.fixture
def project(tmp_path):
    write(tmp_path / "project.yaml", {"project_id": "project_fixture", "duration_seconds": 50})
    write(tmp_path / "story/story.yaml", {"story_id": "story_fixture", "format": {"target_duration_seconds": 50}})
    write(tmp_path / "shots/shots.yaml", {"shots": [
        {"shot_id": "shot_one", "scene_id": "scene_one", "characters": ["char_one", "char_two"],
         "location_id": "loc_one", "prop_ids": ["prop_one"]},
        {"shot_id": "shot_two", "scene_id": "scene_two", "characters": ["char_other"]},
    ]})
    write(tmp_path / "characters/characters.yaml", {"characters": [
        {"character_id": "char_one"}, {"character_id": "char_two"}, {"character_id": "char_other"}]})
    write(tmp_path / "locations/locations.yaml", [{"location_id": "loc_one"}])
    write(tmp_path / "props/props.yaml", {"props": [{"prop_id": "prop_one"}]})
    save_budget(tmp_path, as_of=TODAY)
    write(tmp_path / "budget/decision.yaml", {
        "approved": True, "scope": "planning_only_not_spend_consent",
        "estimate_sha256": file_sha256(tmp_path / "budget/estimate.yaml"),
        "selected_tier": "preparation", "max_spend_usd": 10,
        "consent_reference": "OFFLINE fixture planning review, NOT user consent"})
    return tmp_path


@pytest.fixture
def parts(project, setup):
    graph, binding, job, _, catalog = setup
    from cloud_policy import load_cloud_policy
    config = load_cloud_policy()
    # Do not demand seed locking or alter the central capability config.
    job["parameters"] = {}
    del job["shot_id"]
    job.update(job_kind="reference_illustration", entity_type="character", entity_id="char_one",
               scene_id="scene_one", project_id="project_fixture")
    graph = prepare_cloud_workflow(graph, binding, job, config, node_catalog=catalog, project=project)
    scope = ProjectScope(("scene_one",), ("char_one", "char_two", "loc_one", "prop_one"))
    return graph, binding, job, config, catalog, scope


def approve(project, graph, job, scope, *, ceiling=1, consent="OFFLINE fixture paid approval 1"):
    return {"approved": True, "scope": "paid_generation_job", "tier": job["tier"],
            "model": job["model"], "route": job["route"],
            "workflow_sha256": sha256_document(graph), "plan_sha256": sha256_document(job),
            "estimate_sha256": file_sha256(project / "budget/estimate.yaml"),
            "decision_sha256": file_sha256(project / "budget/decision.yaml"),
            "project_id": "project_fixture", "scope_sha256": sha256_document(asdict(scope)),
            "ceiling_usd": ceiling, "consent_reference": consent}


def reserve(project, parts, *, approval=None, ledger=None, **kwargs):
    graph, _, job, _, _, scope = parts
    approval = approval or approve(project, graph, job, scope)
    return (ledger or CloudLedger(project)).reserve(
        graph, job, approval, scope=scope, workflow_validated=True,
        opening_hold_usd=kwargs.pop("opening_hold_usd", 0),
        opening_balance_reference="OFFLINE fixture reconciled opening liabilities", today=TODAY, **kwargs)


def test_reference_contract_and_backward_compatible_shot(project, parts):
    graph, binding, job, config, catalog, scope = parts
    validate_cloud_job(job)
    prompt = {key: job[key] for key in ("prompt_id", "model", "prompt", "job_kind", "entity_id",
                                      "entity_type", "scene_id", "project_id", "tier")}
    prompt["route"] = "openrouter_comfyui"
    validate_data(prompt, SCHEMAS / "image-prompt.schema.yaml")
    approval = approve(project, graph, job, scope)
    gated = authorize_cloud_job(graph, job, config, approval, project=project, scope=scope,
                               workflow_validated=True, budget_estimate_sha256=approval["estimate_sha256"], today=TODAY)
    assert gated.shot_id is None and gated.entity_id == "char_one"
    assert gated.job_kind == "reference_illustration" and gated.actual_cost_usd is None
    old = {key: value for key, value in job.items() if key not in ("job_kind", "entity_type", "entity_id", "scene_id", "project_id")}
    old["shot_id"] = "shot_one"
    validate_cloud_job(old)
    validate_project_target(old, project, scope)
    old["shot_id"] = "nonexistent"
    with pytest.raises(ValueError, match="Unknown canonical shot"):
        validate_project_target(old, project, scope)


@pytest.mark.parametrize("change", ["mixed", "absent_entity", "wrong_kind", "cross_scene", "cross_project", "no_project"])
def test_reference_target_fail_closed(project, parts, change):
    graph, binding, job, config, catalog, scope = parts
    if change == "mixed": job["shot_id"] = "shot_one"
    elif change == "absent_entity": job["entity_id"] = "not_canonical"
    elif change == "wrong_kind": job["entity_type"] = "prop"
    elif change == "cross_scene": job["scene_id"] = "scene_two"
    elif change == "cross_project": job["project_id"] = "other_project"
    with pytest.raises(CloudAdapterError):
        prepare_cloud_workflow(graph, binding, job, config, node_catalog=catalog,
                               project=None if change == "no_project" else project, scope=scope)


def test_cross_scope_shot_and_entity_rejected(project, parts):
    job, scope = parts[2], parts[5]
    with pytest.raises(ValueError, match="outside reviewed scope"):
        validate_project_target(job, project, ProjectScope(("scene_one",), ("char_two",)))
    job = {k: v for k, v in job.items() if k not in ("job_kind", "entity_id", "entity_type", "scene_id")}
    job["shot_id"] = "shot_two"
    with pytest.raises(ValueError, match="outside reviewed scope"):
        validate_project_target(job, project, scope)
    with pytest.raises(ValueError, match="Unknown canonical entity_id in scope"):
        validate_project_target(parts[2], project, ProjectScope(("scene_one",), ("nonexistent",)))


@pytest.mark.parametrize("kind,entity", [("location", "loc_one"), ("prop", "prop_one")])
def test_canonical_non_character_illustrations(project, parts, kind, entity):
    parts[2].update(entity_type=kind, entity_id=entity)
    validate_project_target(parts[2], project, parts[5])
    validate_cloud_job(parts[2])


def test_durable_claim_once_and_unknown_holds(project, parts):
    graph, job = parts[0], parts[2]
    key = reserve(project, parts)
    ledger = CloudLedger(project)  # new instance sees durable history
    assert ledger.snapshot()["committed_usd"] == "1"
    assert ledger.snapshot()["jobs"][0]["actual"] is None
    ledger.claim(key, graph, job, today=TODAY)
    with pytest.raises(LedgerError, match="already claimed"):
        ledger.claim(key, graph, job, today=TODAY)
    ledger.record_outcome(key, status="failed")
    assert ledger.snapshot()["committed_usd"] == "1"
    assert ledger.snapshot()["jobs"][0]["actual"] is None
    with pytest.raises(LedgerError):
        ledger.record_outcome(key, status="failed", actual_cost_usd=0)
    ledger.record_outcome(key, status="failed", actual_cost_usd=.018, cost_reference="fixture invoice")
    assert ledger.snapshot()["committed_usd"] == "0.018"
    with pytest.raises(LedgerError, match="cannot be rewritten"):
        ledger.record_outcome(key, status="failed", actual_cost_usd=0, cost_reference="fixture invoice")


@pytest.mark.parametrize("change", ["planning", "missing_consent", "workflow", "scope", "decision", "estimate", "unknown_price", "unknown_opening", "over_ceiling"])
def test_no_reservation_without_matching_paid_evidence(project, parts, change):
    approval = approve(project, parts[0], parts[2], parts[5])
    kwargs = {}
    if change == "planning": approval["scope"] = "planning_only_not_spend_consent"
    elif change == "missing_consent": approval["consent_reference"] = ""
    elif change == "workflow": approval["workflow_sha256"] = "0" * 64
    elif change == "scope": approval["scope_sha256"] = "0" * 64
    elif change == "decision": approval["decision_sha256"] = "0" * 64
    elif change == "estimate": approval["estimate_sha256"] = "0" * 64
    elif change == "unknown_price":
        parts[2]["estimated_cost_usd"] = None
        approval["plan_sha256"] = sha256_document(parts[2])
    elif change == "unknown_opening": kwargs["opening_hold_usd"] = None
    elif change == "over_ceiling": approval["ceiling_usd"] = 11
    with pytest.raises(LedgerError): reserve(project, parts, approval=approval, **kwargs)
    assert not CloudLedger(project).snapshot()["initialized"]


def test_duplicate_and_retry_consent_no_restarted_attempt(project, parts):
    graph, job = parts[0], parts[2]
    key = reserve(project, parts)
    with pytest.raises(LedgerError): reserve(project, parts)
    job["attempt_number"] = 2
    with pytest.raises(LedgerError, match="in flight"):
        reserve(project, parts, approval=approve(project, graph, job, parts[5], consent="fixture retry"))
    ledger = CloudLedger(project)
    first_job = copy.deepcopy(job); first_job.pop("attempt_number")
    ledger.claim(key, graph, first_job, today=TODAY)
    ledger.record_outcome(key, status="ambiguous")
    with pytest.raises(LedgerError, match="consent already consumed"):
        reserve(project, parts)
    retry = reserve(project, parts, approval=approve(project, graph, job, parts[5], consent="fixture distinct retry"))
    assert retry != key and ledger.snapshot()["committed_usd"] == "2"
    job["prompt_id"] = "different_prompt_same_entity"
    job["attempt_number"] = 1
    with pytest.raises(LedgerError): reserve(project, parts)


@pytest.mark.parametrize("artifact", ["budget/decision.yaml", "budget/estimate.yaml"])
def test_stale_review_between_reserve_and_claim(project, parts, artifact):
    key = reserve(project, parts)
    path = project / artifact
    path.write_text(path.read_text() + "\n# changed bytes\n")
    with pytest.raises(LedgerError): CloudLedger(project).claim(key, parts[0], parts[2], today=TODAY)
    assert CloudLedger(project).snapshot()["jobs"][0]["status"] == "reserved"


def test_changed_plan_or_graph_cannot_claim(project, parts):
    key = reserve(project, parts)
    graph = copy.deepcopy(parts[0]); graph["caller-image"]["inputs"]["prompt"] = "changed"
    with pytest.raises(LedgerError, match="differs"):
        CloudLedger(project).claim(key, graph, parts[2], today=TODAY)


def test_old_shot_plan_uses_same_ledger_without_entity_alias(project, parts):
    job = parts[2]
    for key in ("job_kind", "entity_id", "entity_type", "scene_id"):
        job.pop(key)
    job["shot_id"] = "shot_one"
    key = reserve(project, parts)
    record = CloudLedger(project).claim(key, parts[0], job, today=TODAY)
    assert record["audit"]["job_kind"] == "shot_render"
    assert record["audit"]["shot_id"] == "shot_one"
    assert record["audit"]["entity_id"] is None
    assert record["audit"]["scene_id"] == "scene_one"


def test_atomic_duplicate_reservation_concurrency(project, parts):
    def attempt():
        try: reserve(project, copy.deepcopy(parts)); return True
        except LedgerError: return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(lambda _: attempt(), range(2))) == 1
    assert len(CloudLedger(project).snapshot()["jobs"]) == 1


@pytest.mark.parametrize("modality", ["video", "audio", "text"])
def test_illustration_is_image_only(parts, modality):
    parts[2]["modality"] = modality
    with pytest.raises(CloudAdapterError): validate_cloud_job(parts[2])


def test_atomic_ceiling_and_double_claim_concurrency(project, parts):
    def attempt(entity, ceiling):
        p = copy.deepcopy(parts)
        p[2]["entity_id"] = entity
        approval = approve(project, p[0], p[2], p[5], ceiling=ceiling, consent="fixture " + entity)
        try: return reserve(project, p, approval=approval)
        except LedgerError: return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda entity: attempt(entity, 6), ("char_one", "char_two")))
    assert sum(key is not None for key in results) == 1
    assert CloudLedger(project).snapshot()["committed_usd"] == "6"
    key = next(key for key in results if key is not None)
    job = copy.deepcopy(parts[2]); job["entity_id"] = ("char_one" if results[0] else "char_two")
    def claim():
        try: CloudLedger(project).claim(key, parts[0], job, today=TODAY); return True
        except LedgerError: return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(lambda _: claim(), range(2))) == 1


def test_actual_above_ceiling_booked_and_blocks_new_spend(project, parts):
    key = reserve(project, parts)
    ledger = CloudLedger(project)
    ledger.claim(key, parts[0], parts[2], today=TODAY)
    ledger.record_outcome(key, status="completed", actual_cost_usd=12, cost_reference="fixture provider invoice")
    assert ledger.snapshot()["committed_usd"] == "12"
    parts[2]["entity_id"] = "char_two"
    with pytest.raises(LedgerError, match="ceiling exceeded"):
        reserve(project, parts, approval=approve(project, parts[0], parts[2], parts[5], consent="fixture other job"))


def test_secrets_rejected_without_persisting(project, parts):
    approval = approve(project, parts[0], parts[2], parts[5])
    approval["api_key"] = "sentinel"
    with pytest.raises(LedgerError, match="Credentials prohibited"):
        reserve(project, parts, approval=approval)
    assert not CloudLedger(project).path.exists()


def test_reported_zero_not_inferred_and_output_history_preserved(project, parts):
    key = reserve(project, parts)
    ledger = CloudLedger(project)
    ledger.claim(key, parts[0], parts[2], today=TODAY)
    ledger.record_outcome(key, status="completed", outputs=["fixture.png"], provider_job_id="fixture-id")
    assert ledger.snapshot()["jobs"][0]["actual"] is None
    ledger.record_outcome(key, status="completed", actual_cost_usd=0,
                          cost_reference="fixture explicitly reported zero charge",
                          outputs=["fixture.png"], provider_job_id="fixture-id")
    assert ledger.snapshot()["committed_usd"] == "0"
    with pytest.raises(LedgerError, match="outputs must be preserved"):
        ledger.record_outcome(key, status="completed", actual_cost_usd=0, cost_reference="fixture",
                              outputs=["replacement.png"], provider_job_id="fixture-id")


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True])
def test_actual_money_must_be_reported_finite_nonnegative(project, parts, value):
    key = reserve(project, parts)
    ledger = CloudLedger(project)
    ledger.claim(key, parts[0], parts[2], today=TODAY)
    with pytest.raises(LedgerError):
        ledger.record_outcome(key, status="failed", actual_cost_usd=value, cost_reference="fixture")


def test_segments_of_one_target_are_distinct_attempt_series(project, parts):
    graph, _, job, _, _, scope = parts
    seg_a = dict(job, segment_id="a")
    seg_b = dict(job, segment_id="b")
    for item in (seg_a, seg_b):
        validate_cloud_job(item)
    ledger = CloudLedger(project)
    ka = reserve(project, (graph, None, seg_a, None, None, scope),
                 approval=approve(project, graph, seg_a, scope, consent="OFFLINE fixture seg a"), ledger=ledger)
    kb = reserve(project, (graph, None, seg_b, None, None, scope),
                 approval=approve(project, graph, seg_b, scope, consent="OFFLINE fixture seg b"), ledger=ledger)
    assert ka != kb and len(ledger.snapshot()["jobs"]) == 2
    dup = dict(seg_a, prompt=seg_a["prompt"])  # same segment, same attempt 1, new consent
    with pytest.raises(LedgerError):
        reserve(project, (graph, None, dup, None, None, scope),
                approval=approve(project, graph, dup, scope, consent="OFFLINE fixture seg a dup"), ledger=ledger)
    with pytest.raises(Exception):
        validate_cloud_job(dict(job, segment_id="Bad Segment!"))
