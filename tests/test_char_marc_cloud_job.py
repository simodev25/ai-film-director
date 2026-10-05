"""Offline integrity tests of this local delegated prompt/plan; no approval/run."""
import copy
import json
from pathlib import Path

import pytest
import yaml

from cloud_policy import file_sha256, load_cloud_policy
from comfyui.cloud_adapters import discover_cloud_binding, prepare_cloud_workflow, sha256_document, validate_cloud_job
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
    assert file_sha256(PROJECT / "budget/estimate.yaml") == review["hashes"]["estimate_sha256"]
    assert file_sha256(PROJECT / "budget/decision.yaml") == review["hashes"]["decision_sha256"]


def test_prepared_does_not_manufacture_consent_or_unknown_costs():
    review = read("char_marc-attempt-01.review.json")
    assert review["paid_approval"] is None and review["consent_reference"] is None
    assert review["actual_cost_usd"] is None and review["opening_hold_usd"] is None
    assert review["remaining_budget_usd"] is None and review["reserved_usd"] is None
    assert review["estimated_cost_usd"] == .018
    assert review["suggested_per_job_ceiling_usd"] == .03
    assert review["submitted_attempts"] == 0 and not review["ledger_created"]
    assert not review["transport_called"] and not review["authorize_cloud_job_called"]
