"""Synthetic offline receipts only; no generation or real paid approval."""
import copy
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from cloud_policy import file_sha256
from comfyui.cloud_ledger import CloudLedger, LedgerError
from test_cloud_ledger import project, parts, approve, reserve, TODAY
from test_cloud_adapters import setup

COMFY = "10000000-0000-4000-8000-000000000001"
STUDIO = "20000000-0000-4000-8000-000000000001"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, allow_nan=False))


def evidence(project, *, cost="0.018", hold=None, comfy=COMFY, studio=STUDIO):
    campaign_path = project / "budget/campaign.json"
    if not campaign_path.exists():
        write_json(campaign_path, {
            "project_id": "project_fixture", "campaign_id": "campaign_fixture", "scene_id": "scene_one",
            "tier": "preparation", "user_scope_clarification_confirmed": True, "max_spend_usd": 10,
            "opening_hold_usd_for_this_new_campaign": 0,
            "opening_balance_reference": "OFFLINE fixture reconciled opening liabilities",
            "decision_sha256": file_sha256(project / "budget/decision.yaml"),
            "estimate_sha256": file_sha256(project / "budget/estimate.yaml")})
    record = {
        "version": 1, "record_type": "user_initiated_external_submission", "external_id": "comfy:" + comfy,
        "project_id": "project_fixture", "campaign_id": "campaign_fixture", "scene_id": "scene_one",
        "campaign_file": "budget/campaign.json", "campaign_sha256": file_sha256(campaign_path),
        "decision_sha256": file_sha256(project / "budget/decision.yaml"), "tier": "preparation", "modality": "image",
        "model": "bytedance-seed/seedream-5-0-flash", "route": "/api/v1/images",
        "job_kind": "reference_illustration", "entity_type": "character", "entity_id": "char_one",
        "comfy_prompt_id": comfy, "studio_local_job_id": studio, "provider_job_id": None,
        "observed_status": "completed", "actual_cost_usd": cost, "unknown_hold_usd": hold,
        "evidence_file": "budget/external/" + comfy + ".json", "evidence_sha256": "0" * 64}
    sync_receipt(project, record)
    return record


def sync_receipt(project, record):
    # Test fixtures only: deliberately controllable receipt for negative tests.
    write_json(project / record["evidence_file"], {k: v for k, v in record.items() if k not in
               ("campaign_file", "campaign_sha256", "decision_sha256", "evidence_file", "evidence_sha256")})
    record["evidence_sha256"] = file_sha256(project / record["evidence_file"])


def initialize(project, parts, *, ambiguous=True):
    key = reserve(project, parts, approval=approve(project, parts[0], parts[2], parts[5], ceiling=.03))
    ledger = CloudLedger(project)
    if ambiguous:
        ledger.claim(key, parts[0], parts[2], today=TODAY)
        ledger.record_outcome(key, status="ambiguous")
    return ledger, key


def test_external_actual_is_independent_idempotent_and_preserves_managed(project, parts):
    ledger, key = initialize(project, parts)
    before = ledger.snapshot()
    r = evidence(project)
    result = ledger.import_external_cost(r, today=TODAY)
    assert result["imported"] and not result["idempotent"]
    after = ledger.snapshot()
    assert after["jobs"] == before["jobs"]
    assert after["events"][:len(before["events"])] == before["events"]
    assert len(after["external_jobs"]) == 1
    assert after["external_jobs"][0]["actual"] == "0.018"
    assert after["committed_usd"] == "0.048" and after["remaining_budget_usd"] == "9.952"
    assert after["known_actual_cost_usd"] == "0.018" and after["actual_cost_usd"] is None
    assert after["unresolved_holds_usd"] == "0.03"
    assert ledger.import_external_cost(r, today=TODAY)["idempotent"]
    assert ledger.snapshot() == after
    assert ledger.snapshot()["jobs"][0]["plan_hash"] == key


@pytest.mark.parametrize("change", ["project", "campaign", "scene", "entity", "model", "decision_hash", "campaign_hash", "receipt_hash", "reported_cost", "fake_approval", "stable_id"])
def test_scope_hash_identity_and_cost_fail_closed(project, parts, change):
    ledger, _ = initialize(project, parts)
    r = evidence(project)
    before = ledger.snapshot()
    if change == "project": r["project_id"] = "other_project"
    elif change == "campaign": r["campaign_id"] = "other_campaign"
    elif change == "scene": r["scene_id"] = "scene_two"
    elif change == "entity":
        r["entity_id"] = "not_canonical"; sync_receipt(project, r)
    elif change == "model": r["model"] = "other/model"
    elif change == "decision_hash": r["decision_sha256"] = "0" * 64
    elif change == "campaign_hash": r["campaign_sha256"] = "0" * 64
    elif change == "receipt_hash": r["evidence_sha256"] = "0" * 64
    elif change == "reported_cost": r["actual_cost_usd"] = "0.017"
    elif change == "fake_approval": r["approved"] = True
    elif change == "stable_id": r["external_id"] = "comfy:10000000-0000-4000-8000-000000000002"
    with pytest.raises(ValueError): ledger.import_external_cost(r, today=TODAY)
    assert ledger.snapshot() == before


def test_revision_and_duplicate_alias_are_rejected(project, parts):
    ledger, _ = initialize(project, parts)
    r = evidence(project)
    ledger.import_external_cost(r, today=TODAY)
    before = ledger.snapshot()
    revised = copy.deepcopy(r); revised["actual_cost_usd"] = "0.019"; sync_receipt(project, revised)
    with pytest.raises(LedgerError, match="Conflicting revision"):
        ledger.import_external_cost(revised, today=TODAY)
    another = evidence(project, comfy="10000000-0000-4000-8000-000000000002")
    with pytest.raises(LedgerError, match="Identity already belongs"):
        ledger.import_external_cost(another, today=TODAY)
    assert ledger.snapshot() == before


@pytest.mark.parametrize("cost,hold", [(None, None), (None, 0), ("0.018", ".03"), (-1, None), (float("nan"), None), (float("inf"), None), (True, None)])
def test_invalid_or_zero_unknown_money_never_books(project, parts, cost, hold):
    ledger, _ = initialize(project, parts)
    r = evidence(project)
    r.update(actual_cost_usd=cost, unknown_hold_usd=hold)
    before = ledger.snapshot()
    with pytest.raises(ValueError): ledger.import_external_cost(r, today=TODAY)
    assert ledger.snapshot() == before


def test_nullable_unknown_external_is_a_positive_accounting_hold_not_zero(project, parts):
    ledger, _ = initialize(project, parts)
    r = evidence(project, cost=None, hold="0.03")
    ledger.import_external_cost(r, today=TODAY)
    s = ledger.snapshot()
    assert s["external_jobs"][0]["actual"] is None
    assert s["committed_usd"] == "0.06" and s["unresolved_holds_usd"] == "0.06"
    assert s["actual_cost_usd"] is None and s["remaining_budget_usd"] == "9.94"


def test_identity_cannot_share_managed_and_external_in_either_order(project, parts):
    ledger, key = initialize(project, parts)
    r = evidence(project)
    ledger.record_outcome(key, status="ambiguous", comfy_prompt_id=COMFY)
    with pytest.raises(LedgerError, match="managed attempt"):
        ledger.import_external_cost(r, today=TODAY)
    other = evidence(project, comfy="10000000-0000-4000-8000-000000000002", studio="20000000-0000-4000-8000-000000000002")
    ledger.import_external_cost(other, today=TODAY)
    with pytest.raises(LedgerError, match="external job"):
        ledger.record_outcome(key, status="ambiguous", comfy_prompt_id=other["comfy_prompt_id"])
    assert ledger.snapshot()["jobs"][0]["status"] == "ambiguous"


def test_duplicate_concurrent_import_has_one_row_and_one_event(project, parts):
    ledger, _ = initialize(project, parts)
    r = evidence(project)
    def run(): return CloudLedger(project).import_external_cost(copy.deepcopy(r), today=TODAY)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sum(result["imported"] for result in results) == 1
    s = ledger.snapshot()
    assert len(s["external_jobs"]) == 1
    assert sum(json.loads(e["event"])["status"] == "external_imported" for e in s["events"]) == 1
    assert s["remaining_budget_usd"] == "9.952"


def test_import_counts_in_reserve_and_claim_ceiling_without_cost_truncation(project, parts):
    ledger, key = initialize(project, parts, ambiguous=False)
    # Booking truth is allowed even after an untracked expenditure broke the ceiling.
    ledger.import_external_cost(evidence(project, cost="10"), today=TODAY)
    assert ledger.snapshot()["remaining_budget_usd"] == "-0.03"
    with pytest.raises(LedgerError, match="over ceiling"):
        ledger.claim(key, parts[0], parts[2], today=TODAY)
    next_parts = copy.deepcopy(parts); next_parts[2]["entity_id"] = "char_two"
    with pytest.raises(LedgerError, match="ceiling exceeded"):
        reserve(project, next_parts, approval=approve(project, next_parts[0], next_parts[2], next_parts[5], ceiling=.03, consent="fixture next"))
    assert ledger.snapshot()["jobs"][0]["status"] == "reserved"


def test_no_account_no_import_and_consistent_backup_no_overwrite(project, parts, tmp_path):
    r = evidence(project)
    ledger = CloudLedger(project)
    with pytest.raises(LedgerError, match="initialized"):
        ledger.import_external_cost(r, today=TODAY)
    assert not ledger.path.exists()
    ledger, _ = initialize(project, parts)
    backup = ledger.backup(tmp_path / "before.sqlite3")
    assert ledger.snapshot()["external_jobs"] == []
    ledger.import_external_cost(r, today=TODAY)
    with sqlite3.connect(backup) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("SELECT COUNT(*) FROM external_jobs").fetchone()[0] == 0
        assert db.execute("SELECT actual,status FROM jobs").fetchone() == (None, "ambiguous")
    with pytest.raises(FileExistsError): ledger.backup(backup)


def test_changed_evidence_at_transaction_boundary_rolls_back(project, parts, monkeypatch):
    ledger, _ = initialize(project, parts)
    r = evidence(project)
    before = ledger.snapshot()
    original = ledger._evidence_file
    calls = 0
    def race(relative, digest):
        nonlocal calls
        calls += 1
        if calls == 3:
            campaign = project / "budget/campaign.json"
            campaign.write_text(campaign.read_text() + "\n")
        return original(relative, digest)
    monkeypatch.setattr(ledger, "_evidence_file", race)
    with pytest.raises(LedgerError, match="hash mismatch"):
        ledger.import_external_cost(r, today=TODAY)
    assert ledger.snapshot() == before
