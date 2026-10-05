"""Offline integrity tests of this local delegated prompt/plan/approval record; no run."""
import copy
import json
from pathlib import Path

import pytest
import yaml

from cloud_policy import file_sha256, load_cloud_policy
from comfyui.cloud_adapters import (CloudAdapterError, authorize_cloud_job, discover_cloud_binding,
                                    prepare_cloud_workflow, sha256_document, validate_cloud_job)
from comfyui.cloud_targets import ProjectScope
from validation import validate_data

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/la-pomme"
FILES = PROJECT / "workflows/cloud/preparation"
pytestmark = pytest.mark.skipif(not (FILES / "char_marc-attempt-01.review.json").exists(),
                                reason="Optional local project job is not packaged")


def read(name):
    return json.loads((FILES / name).read_text())


def test_real_plan_preserves_delegated_main_and_negative_strings():
    source = PROJECT / "prompts/references/seedream-5-0-flash/char_marc.yaml"
    p = yaml.safe_load(source.read_text())
    validate_data(p, ROOT / "schemas/image-prompt.schema.yaml")
    job = read("char_marc-attempt-01.plan.json")
    validate_cloud_job(job)
    review = read("char_marc-attempt-01.review.json")
    assert job["prompt"] == p["prompt"] + review["prompt_compilation"]["separator"] + p["negative_prompt"]
    assert job["prompt_id"] == p["prompt_id"]
    assert job["job_kind"] == "reference_illustration" and "shot_id" not in job
    assert job["parameters"] == {"resolution": "1K", "aspect_ratio": "16:9"}
    assert job["references"] == [] and job["attempt_number"] == 1
    assert file_sha256(source) == review["hashes"]["source_prompt_sha256"]


def test_real_prepared_graph_is_adapter_copy_and_hash_bound():
    source = read("seedream-scaffold-source.api.json")
    original = copy.deepcopy(source)
    binding_data = read("seedream-bindings.json")["binding"]
    binding = discover_cloud_binding(source, class_type=binding_data["class_type"], input_map=binding_data["input_map"])
    job = read("char_marc-attempt-01.plan.json")
    actual = prepare_cloud_workflow(source, binding, job, load_cloud_policy(),
                                   node_catalog=read("live-descriptors.selected.json"), project=PROJECT,
                                   scope=ProjectScope(("scene_la_pomme_01",), ("char_marc",)))
    saved = read("char_marc-attempt-01.workflow.api.json")
    assert source == original and actual == saved
    assert saved["2"] == source["2"] and set(saved) == set(source)
    assert [key for key in source["1"]["inputs"] if source["1"]["inputs"][key] != saved["1"]["inputs"][key]] == ["model.prompt"]
    review = read("char_marc-attempt-01.review.json")
    assert sha256_document(job) == review["hashes"]["plan_sha256"]
    assert sha256_document(saved) == review["hashes"]["workflow_sha256"]
    assert_estimate_bound_to_recorded_approval(review["hashes"], job, saved)


def archived_hashes(name):
    """SHA-256 of every saved budget artifact (current + archive) named ``name``."""
    paths = [PROJECT / "budget" / name, *(PROJECT / "budget/archive").rglob(name)]
    return {file_sha256(path) for path in paths if path.is_file()}


def assert_estimate_bound_to_recorded_approval(hashes, job, graph):
    """The paid approval binds the estimate/decision reviewed WHEN IT WAS GIVEN, not today's files.

    The project may re-estimate later (new scope); that must never silently re-bind or
    re-authorize an old approval. Invariant: review == approval hashes, the approved estimate
    and decision bytes are still preserved (current or archive), and if the current estimate
    differs the recorded approval no longer authorizes the job (fail closed).
    """
    approval_path = FILES / "char_marc-attempt-01.approval.json"
    if not approval_path.exists():
        # Before approval the review must match the live estimate/decision exactly.
        assert file_sha256(PROJECT / "budget/estimate.yaml") == hashes["estimate_sha256"]
        assert file_sha256(PROJECT / "budget/decision.yaml") == hashes["decision_sha256"]
        return
    approval = json.loads(approval_path.read_text())
    assert approval["approved"] is True and approval["scope"] == "paid_generation_job"
    assert approval["consent_reference"].strip()
    assert approval["estimate_sha256"] == hashes["estimate_sha256"]
    assert approval["decision_sha256"] == hashes["decision_sha256"]
    assert approval["plan_sha256"] == sha256_document(job) == hashes["plan_sha256"]
    assert approval["workflow_sha256"] == sha256_document(graph) == hashes["workflow_sha256"]
    assert (approval["tier"], approval["model"], approval["route"]) == (job["tier"], job["model"], job["route"])
    assert approval["retry_permitted"] is False and approval["future_paid_jobs_permitted"] is False
    assert approval["estimate_sha256"] in archived_hashes("estimate.yaml"), "Approved estimate bytes lost"
    assert approval["decision_sha256"] in archived_hashes("decision.yaml"), "Approved decision bytes lost"
    current = file_sha256(PROJECT / "budget/estimate.yaml")
    if current != approval["estimate_sha256"]:
        with pytest.raises(CloudAdapterError):
            authorize_cloud_job(graph, job, load_cloud_policy(), approval, budget_estimate_sha256=current,
                                workflow_validated=True, project=PROJECT,
                                scope=ProjectScope(("scene_la_pomme_01",), ("char_marc",)))


def test_prepared_does_not_manufacture_consent_or_unknown_costs():
    review = read("char_marc-attempt-01.review.json")
    assert review["paid_approval"] is None and review["consent_reference"] is None
    assert review["actual_cost_usd"] is None and review["opening_hold_usd"] is None
    assert review["remaining_budget_usd"] is None and review["reserved_usd"] is None
    assert review["estimated_cost_usd"] == .018
    assert review["suggested_per_job_ceiling_usd"] == .03
    assert review["submitted_attempts"] == 0 and not review["ledger_created"]
    assert not review["transport_called"] and not review["authorize_cloud_job_called"]
