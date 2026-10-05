"""Caller-owned durable budget holds; no transport, credentials or generation.

Reserve only after graph validation and real paid-job consent. A reservation is
not submission permission for unrelated code: the caller must atomically claim
it *before* calling comfy-mcp once. A crash/unknown/failed attempt retains its
full per-job ceiling until an evidenced actual cost is reconciled. SQLite uses
BEGIN IMMEDIATE and FULL synchronous durability, without floating money sums.
"""
from contextlib import closing, contextmanager
from dataclasses import asdict
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
from uuid import UUID

import yaml

from budget import require_budget_review
from cloud_policy import DEFAULT_CONFIG, file_sha256, load_cloud_policy
from validation import validate_data
from .cloud_adapters import CloudAdapterError, authorize_cloud_job, sha256_document
from .cloud_targets import ProjectScope, validate_project_target


class LedgerError(ValueError):
    pass


def _money(value, *, positive=False):
    if value is None or isinstance(value, bool):
        raise LedgerError("Unknown monetary value; unknown is never zero")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise LedgerError("Invalid monetary value") from exc
    if not amount.is_finite() or amount < 0 or (positive and amount == 0):
        raise LedgerError("Invalid monetary value")
    return amount


def _safe(data):
    """Do not persist credential-shaped fields or strings, even in audit extras."""
    if isinstance(data, dict):
        for key, value in data.items():
            if re.search(r"api.?key|password|secret|authorization|access.?token|private.?key", str(key), re.I):
                raise LedgerError("Credentials prohibited in ledger")
            _safe(value)
    elif isinstance(data, (list, tuple)):
        for value in data:
            _safe(value)
    elif isinstance(data, str) and re.search(r"sk-or-|Bearer\s+[A-Za-z0-9]", data):
        raise LedgerError("Credentials prohibited in ledger")


def _json(data):
    _safe(data)
    return json.dumps(data, sort_keys=True, allow_nan=False)


class CloudLedger:
    """One ledger per canonical project, shared across scopes and decisions.

    Merely constructing this object does not create a file. The first *valid*
    reserve initializes budget/cloud-ledger.sqlite3. opening_hold_usd and its
    evidence reconcile external/historical liabilities; unknown blocks reserve.
    Never initialize a zero opening hold merely because no invoice was found.
    """
    def __init__(self, project: Path, *, config_path: Path = DEFAULT_CONFIG):
        self.project = Path(project).resolve()
        self.config_path = Path(config_path)
        self.path = self.project / "budget/cloud-ledger.sqlite3"

    @contextmanager
    def _transaction(self):
        # budget exists after the reviewed-budget gate; do not invent artifacts.
        with closing(sqlite3.connect(self.path, timeout=30, isolation_level=None)) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY CHECK(id=1), metadata TEXT NOT NULL)")
                db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                    plan_hash TEXT PRIMARY KEY, consent TEXT NOT NULL UNIQUE,
                    target TEXT NOT NULL, attempt INTEGER NOT NULL,
                    reserved TEXT NOT NULL, actual TEXT, status TEXT NOT NULL,
                    record TEXT NOT NULL, UNIQUE(target, attempt))""")
                db.execute("""CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_hash TEXT NOT NULL, event TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))""")
                db.execute("""CREATE TABLE IF NOT EXISTS external_jobs (
                    external_id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL,
                    record_sha256 TEXT NOT NULL, actual TEXT, hold TEXT,
                    record TEXT NOT NULL)""")
                db.execute("""CREATE TABLE IF NOT EXISTS external_aliases (
                    identity TEXT PRIMARY KEY, raw_id TEXT NOT NULL,
                    external_id TEXT NOT NULL REFERENCES external_jobs(external_id))""")
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def _review(self, tier, today):
        try:
            require_budget_review(self.project, selected_tier=tier,
                                  config_path=self.config_path, as_of=today)
            decision_path = self.project / "budget/decision.yaml"
            decision = yaml.safe_load(decision_path.read_text())
            return decision, file_sha256(decision_path)
        except Exception as exc:
            raise LedgerError("Current matching planning review required") from exc

    @staticmethod
    def _committed(db, opening):
        managed = sum((_money(r["actual"] if r["actual"] is not None else r["reserved"])
                       for r in db.execute("SELECT reserved, actual FROM jobs")), Decimal(0))
        external = sum((_money(r["actual"] if r["actual"] is not None else r["hold"])
                        for r in db.execute("SELECT actual, hold FROM external_jobs")), Decimal(0))
        return opening + managed + external

    def _evidence_file(self, relative, digest):
        rel = PurePosixPath(relative)
        path = (self.project / relative).resolve()
        if (rel.is_absolute() or ".." in rel.parts or str(rel) != relative
                or not path.is_relative_to(self.project) or not path.is_file()):
            raise LedgerError("Evidence must be an existing project-relative file")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise LedgerError("Evidence hash mismatch")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise LedgerError("Evidence must be JSON") from exc
        if not isinstance(data, dict):
            raise LedgerError("Evidence must be a JSON object")
        _safe(data)
        return data

    @staticmethod
    def _reject_external_identity(db, identifiers):
        for identifier in identifiers:
            if identifier and db.execute("SELECT 1 FROM external_aliases WHERE raw_id=?", (identifier,)).fetchone():
                raise LedgerError("Identity already belongs to an external job; cannot share with managed attempt")

    def backup(self, out_path: Path):
        """Consistent SQLite backup of an existing ledger, never overwrite a file."""
        if not self.path.exists():
            raise LedgerError("No existing ledger to back up")
        out = Path(out_path).resolve()
        if out == self.path.resolve():
            raise LedgerError("Backup cannot replace the ledger")
        # Exclusive creation prevents accidental replacement of a prior backup.
        with out.open("xb"):
            pass
        out.chmod(0o600)
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as source:
            with closing(sqlite3.connect(out)) as destination:
                source.backup(destination)
                if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise LedgerError("Backup integrity check failed")
        return out

    def import_external_cost(self, evidence, *, today: date | None = None):
        """Import incurred external cost/hold, NOT approval, reservation or claim.

        Requires an initialized account, current reviewed campaign and a hashed
        JSON receipt matching identity, canonical target and reported cost.
        Identical imports are idempotent; changed/relabelled evidence is rejected.
        Incurring a cost over the ceiling is still booked, then blocks new spend.
        This method does not establish authenticity of third-party receipts: the
        caller must acquire and audit them read-only from the authoritative source.
        """
        if not self.path.exists():
            raise LedgerError("External import requires an initialized project account")
        _safe(evidence)
        try:
            validate_data(evidence, Path(__file__).resolve().parents[2] / "schemas/cloud-external-cost.schema.yaml")
        except Exception as exc:
            raise LedgerError("Invalid external cost schema") from exc
        record = dict(evidence)
        if record["external_id"] != "comfy:" + str(UUID(record["comfy_prompt_id"])):
            raise LedgerError("External ID must be the stable Comfy job identity")
        actual = None if record["actual_cost_usd"] is None else _money(record["actual_cost_usd"])
        hold = None if record["unknown_hold_usd"] is None else _money(record["unknown_hold_usd"], positive=True)
        if (actual is None and hold is None) or (actual is not None and hold is not None):
            raise LedgerError("Unknown actual requires positive hold; known actual must not also reserve")
        record["actual_cost_usd"] = None if actual is None else format(actual.normalize(), "f")
        record["unknown_hold_usd"] = None if hold is None else format(hold.normalize(), "f")
        decision, decision_hash = self._review(record["tier"], today or date.today())
        if record["decision_sha256"] != decision_hash:
            raise LedgerError("External evidence binds a stale decision")
        profile = load_cloud_policy(self.config_path)["tiers"][record["tier"]]["image"]
        if record["model"] != profile["model"]:
            raise LedgerError("External model differs from selected tier")
        campaign = self._evidence_file(record["campaign_file"], record["campaign_sha256"])
        receipt = self._evidence_file(record["evidence_file"], record["evidence_sha256"])
        for key in ("project_id", "campaign_id", "scene_id", "tier"):
            if campaign.get(key) != record[key]:
                raise LedgerError("External cost is outside reviewed campaign scope")
        if (campaign.get("user_scope_clarification_confirmed") is not True
                or campaign.get("decision_sha256") != decision_hash
                or campaign.get("estimate_sha256") != decision["estimate_sha256"]
                or _money(campaign.get("max_spend_usd")) != _money(decision["max_spend_usd"])):
            raise LedgerError("Campaign evidence does not match current review")
        for key in ("record_type", "external_id", "project_id", "campaign_id", "scene_id", "tier", "modality", "model", "route",
                    "job_kind", "entity_type", "entity_id", "comfy_prompt_id", "studio_local_job_id", "provider_job_id", "observed_status"):
            if receipt.get(key) != record[key]:
                raise LedgerError("Receipt identity/target/model differs from import")
        reported = receipt.get("actual_cost_usd")
        if (actual is None) != (reported is None) or (actual is not None and _money(reported) != actual):
            raise LedgerError("Actual cost differs from authoritative receipt")
        if hold is not None and _money(receipt.get("unknown_hold_usd"), positive=True) != hold:
            raise LedgerError("Unknown hold differs from accounting evidence")
        if hold is None and receipt.get("unknown_hold_usd") is not None:
            raise LedgerError("Known-cost receipt must not also carry an unknown hold")
        project_id, _ = validate_project_target(record, self.project,
                                               ProjectScope((campaign["scene_id"],), (record["entity_id"],)))
        encoded, digest = _json(record), sha256_document(record)
        identifiers = {k: record[k] for k in ("comfy_prompt_id", "studio_local_job_id", "provider_job_id") if record[k]}
        with self._transaction() as db:
            # Re-read evidence while holding the same serialization lock as reserve/claim.
            self._evidence_file(record["campaign_file"], record["campaign_sha256"])
            self._evidence_file(record["evidence_file"], record["evidence_sha256"])
            if (file_sha256(self.project / "budget/decision.yaml") != decision_hash
                    or file_sha256(self.project / "budget/estimate.yaml") != decision["estimate_sha256"]):
                raise LedgerError("Budget hashes changed during import")
            account = db.execute("SELECT metadata FROM account WHERE id=1").fetchone()
            if account is None:
                raise LedgerError("Missing initialized project account")
            meta = json.loads(account[0])
            if (meta["project_id"] != project_id or meta["project_path"] != str(self.project)
                    or meta["opening_balance_reference"] != campaign.get("opening_balance_reference")
                    or _money(meta["opening_hold_usd"]) != _money(campaign.get("opening_hold_usd_for_this_new_campaign"))):
                raise LedgerError("Campaign differs from durable account perimeter")
            for existing in db.execute("SELECT record FROM external_jobs"):
                old = json.loads(existing[0])
                if (old["campaign_id"], old["campaign_sha256"]) != (record["campaign_id"], record["campaign_sha256"]):
                    raise LedgerError("Cannot mix campaigns in one project account")
            for managed in db.execute("SELECT record FROM jobs"):
                old = json.loads(managed[0])
                if any(old.get(key) in identifiers.values() for key in ("comfy_prompt_id", "studio_local_job_id", "provider_job_id") if old.get(key)):
                    raise LedgerError("External identity already belongs to a managed attempt")
            old = db.execute("SELECT record_sha256 FROM external_jobs WHERE external_id=?", (record["external_id"],)).fetchone()
            if old is not None:
                if old[0] != digest:
                    raise LedgerError("Conflicting revision of imported external evidence")
                return {"external_id": record["external_id"], "imported": False, "idempotent": True}
            self._reject_external_identity(db, identifiers.values())
            db.execute("INSERT INTO external_jobs VALUES (?, ?, ?, ?, ?, ?)",
                       (record["external_id"], record["campaign_id"], digest, record["actual_cost_usd"], record["unknown_hold_usd"], encoded))
            for kind, identifier in identifiers.items():
                db.execute("INSERT INTO external_aliases VALUES (?, ?, ?)", (kind + ":" + identifier, identifier, record["external_id"]))
            db.execute("INSERT INTO events(plan_hash,event) VALUES (?,?)", ("external:" + record["external_id"],
                       _json({"status": "external_imported", "record_type": record["record_type"], "external_id": record["external_id"],
                              "actual_cost_usd": record["actual_cost_usd"], "unknown_hold_usd": record["unknown_hold_usd"],
                              "record_sha256": digest, "retroactive_paid_approval": False})))
        return {"external_id": record["external_id"], "imported": True, "idempotent": False}

    def reserve(self, graph, job, approval, *, scope: ProjectScope,
                workflow_validated: bool = False, opening_hold_usd=None,
                opening_balance_reference: str = "", today: date | None = None):
        """Validate paid approval, then atomically hold its ceiling and record it.

        approval additionally binds project_id, scope_sha256 and decision_sha256.
        Approval/consent_reference must be actual human evidence supplied by the
        caller; this library cannot infer consent from a technical 'go'.
        """
        today = today or date.today()
        decision, decision_hash = self._review(job["tier"], today)
        project_id, _ = validate_project_target(job, self.project, scope)
        if job.get("project_id") != project_id:
            raise LedgerError("Ledger plan requires canonical project_id")
        scope_hash = sha256_document(asdict(scope))
        if (approval.get("project_id") != project_id
                or approval.get("scope_sha256") != scope_hash
                or approval.get("decision_sha256") != decision_hash):
            raise LedgerError("Paid approval must bind project, scope and current decision hash")
        config = load_cloud_policy(self.config_path)
        try:
            gated = authorize_cloud_job(
                graph, job, config, approval, project=self.project, scope=scope,
                budget_estimate_sha256=decision["estimate_sha256"],
                workflow_validated=workflow_validated, today=today)
        except CloudAdapterError as exc:
            raise LedgerError(str(exc)) from exc
        opening = _money(opening_hold_usd)
        if not isinstance(opening_balance_reference, str) or not opening_balance_reference.strip():
            raise LedgerError("Opening balance evidence required, including historical liabilities")
        ceiling = _money(decision["max_spend_usd"], positive=True)
        hold = _money(gated.ceiling_usd, positive=True)
        record = {"audit": asdict(gated), "plan": job, "approval": approval,
                  "scope": asdict(scope), "decision_sha256": decision_hash,
                  "outputs": [], "provider_job_id": None}
        metadata = {"project_id": project_id, "project_path": str(self.project),
                    "opening_hold_usd": str(opening),
                    "opening_balance_reference": opening_balance_reference}
        # Exclude scene/scope from target key: cannot restart numbering by moving
        # the same canonical target to another scene or changing its prompt_id.
        target_parts = [job["modality"], job.get("job_kind", "shot_render"),
                        job.get("entity_type"), job.get("entity_id", job.get("shot_id"))]
        if job.get("segment_id") is not None:
            # Chained clips of one shot are distinct attempt series; absent
            # segment keeps the historical key so existing rows still match.
            target_parts.append({"segment_id": job["segment_id"]})
        target = _json(target_parts)
        encoded_record, encoded_meta = _json(record), _json(metadata)
        attempt = gated.attempt_number
        with self._transaction() as db:
            # Recheck reviewed bytes after acquiring the serialization lock.
            if (file_sha256(self.project / "budget/decision.yaml") != decision_hash
                    or file_sha256(self.project / "budget/estimate.yaml") != gated.estimate_sha256):
                raise LedgerError("Budget hash changed during reservation")
            account = db.execute("SELECT metadata FROM account WHERE id=1").fetchone()
            if account is not None and account["metadata"] != encoded_meta:
                raise LedgerError("Project/opening balance differs from durable ledger")
            previous = db.execute("SELECT MAX(attempt) FROM jobs WHERE target=?", (target,)).fetchone()[0]
            if attempt != (previous or 0) + 1:
                raise LedgerError("Attempt must follow durable history; no duplicate/restarted attempt")
            if previous is not None:
                prior = db.execute("SELECT status FROM jobs WHERE target=? AND attempt=?", (target, previous)).fetchone()[0]
                if prior not in ("completed", "failed", "ambiguous"):
                    raise LedgerError("Prior attempt still reserved/in flight; retry blocked")
            used = self._committed(db, opening)
            if used + hold > ceiling:
                raise LedgerError("Project ceiling exceeded by actual costs and unresolved holds")
            try:
                db.execute("INSERT OR IGNORE INTO account VALUES (1, ?)", (encoded_meta,))
                db.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, NULL, 'reserved', ?)",
                           (gated.plan_sha256, gated.consent_reference, target, attempt, str(hold), encoded_record))
            except sqlite3.IntegrityError as exc:
                raise LedgerError("Plan/consent already consumed; retry needs distinct explicit consent") from exc
            db.execute("INSERT INTO events(plan_hash,event) VALUES (?,?)",
                       (gated.plan_sha256, _json({"status": "reserved", "reserved_usd": str(hold)})))
        return gated.plan_sha256

    def claim(self, plan_sha256, graph, job, *, today: date | None = None):
        """Consume once *before* submission. Crash after claim retains the hold."""
        if not self.path.exists():
            raise LedgerError("No approved reservation")
        with self._transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE plan_hash=?", (plan_sha256,)).fetchone()
            if row is None or row["status"] != "reserved":
                raise LedgerError("Reservation missing or already claimed")
            record = json.loads(row["record"])
            today = today or date.today()
            decision, digest = self._review(record["plan"]["tier"], today)
            if (digest != record["decision_sha256"]
                    or decision["estimate_sha256"] != record["audit"]["estimate_sha256"]):
                raise LedgerError("Reservation budget review is stale")
            if (sha256_document(job) != plan_sha256
                    or sha256_document(graph) != record["audit"]["workflow_sha256"]):
                raise LedgerError("Claim graph/plan differs from approved reservation")
            try:
                authorize_cloud_job(graph, job, load_cloud_policy(self.config_path), record["approval"],
                                    project=self.project, scope=ProjectScope(**record["scope"]),
                                    budget_estimate_sha256=decision["estimate_sha256"],
                                    workflow_validated=True, today=today)
            except CloudAdapterError as exc:
                raise LedgerError(str(exc)) from exc
            used = _money(json.loads(db.execute("SELECT metadata FROM account WHERE id=1").fetchone()[0])["opening_hold_usd"])
            used = self._committed(db, used)
            if used > _money(decision["max_spend_usd"]):
                raise LedgerError("Project is over ceiling; submission blocked")
            db.execute("UPDATE jobs SET status='submitted' WHERE plan_hash=?", (plan_sha256,))
            db.execute("INSERT INTO events(plan_hash,event) VALUES (?,?)",
                       (plan_sha256, _json({"status": "submitted", "meaning": "claimed_before_transport"})))
            return record

    def record_outcome(self, plan_sha256, *, status, actual_cost_usd=None,
                       provider_job_id=None, outputs=(), cost_reference=None, comfy_prompt_id=None):
        """Record failed/ambiguous/completed attempts, preserving unknown holds.

        Only reported, evidenced actuals may be supplied. Known actuals cannot
        be rewritten or reset to unknown; an over-ceiling actual is still booked.
        No retry or cancellation/release is performed by this API.
        """
        if status not in ("completed", "failed", "ambiguous") or not self.path.exists():
            raise LedgerError("Invalid outcome or missing ledger")
        if (not isinstance(outputs, (list, tuple))
                or any(not isinstance(path, str) or not path for path in outputs)
                or (provider_job_id is not None and (not isinstance(provider_job_id, str) or not provider_job_id))
                or (comfy_prompt_id is not None and (not isinstance(comfy_prompt_id, str) or not comfy_prompt_id))):
            raise LedgerError("Invalid output/job metadata")
        actual = None if actual_cost_usd is None else str(_money(actual_cost_usd))
        if actual is not None and (not isinstance(cost_reference, str) or not cost_reference.strip()):
            raise LedgerError("Reported actual cost requires evidence reference")
        event = {"status": status, "actual_cost_usd": actual,
                 "provider_job_id": provider_job_id, "outputs": list(outputs),
                 "cost_reference": cost_reference, "comfy_prompt_id": comfy_prompt_id}
        encoded = _json(event)
        with self._transaction() as db:
            self._reject_external_identity(db, (provider_job_id, comfy_prompt_id))
            row = db.execute("SELECT * FROM jobs WHERE plan_hash=?", (plan_sha256,)).fetchone()
            if row is None or row["status"] == "reserved":
                raise LedgerError("Cannot settle an unclaimed reservation")
            if row["status"] in ("completed", "failed") and row["status"] != status:
                raise LedgerError("Terminal outcome cannot be replaced")
            if row["actual"] is not None and (actual is None or _money(actual) != _money(row["actual"])):
                raise LedgerError("Known actual cost cannot be rewritten")
            record = json.loads(row["record"])
            if record.get("outputs") and list(outputs) != record["outputs"]:
                raise LedgerError("Existing outputs must be preserved")
            if record.get("provider_job_id") and provider_job_id != record["provider_job_id"]:
                raise LedgerError("Existing provider job ID must be preserved")
            if record.get("comfy_prompt_id") and comfy_prompt_id != record["comfy_prompt_id"]:
                raise LedgerError("Existing Comfy job ID must be preserved")
            record["outputs"] = list(outputs)
            record["provider_job_id"] = provider_job_id
            record["comfy_prompt_id"] = comfy_prompt_id
            db.execute("UPDATE jobs SET status=?, actual=?, record=? WHERE plan_hash=?",
                       (status, actual, _json(record), plan_sha256))
            db.execute("INSERT INTO events(plan_hash,event) VALUES (?,?)", (plan_sha256, encoded))

    def snapshot(self):
        """Read-only existing DB; no schema creation or automatic zero baseline."""
        if not self.path.exists():
            return {"initialized": False, "actual_cost_usd": None, "jobs": []}
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not tables:
                return {"initialized": False, "actual_cost_usd": None, "jobs": []}
            if not {"jobs", "account", "events"} <= tables:
                raise LedgerError("Incomplete/corrupt durable ledger")
            rows = [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY rowid")]
            external = [dict(row) for row in db.execute("SELECT * FROM external_jobs ORDER BY rowid")] if "external_jobs" in tables else []
            metadata = json.loads(db.execute("SELECT metadata FROM account WHERE id=1").fetchone()[0])
            events = [dict(row) for row in db.execute("SELECT * FROM events ORDER BY sequence")]
        used = _money(metadata["opening_hold_usd"]) + sum(
            (_money(row["actual"] if row["actual"] is not None else row["reserved"]) for row in rows), Decimal(0))
        external_used = sum((_money(row["actual"] if row["actual"] is not None else row["hold"]) for row in external), Decimal(0))
        used += external_used
        known = sum((_money(row["actual"]) for row in [*rows, *external] if row["actual"] is not None), Decimal(0))
        holds = sum((_money(row.get("reserved", row.get("hold"))) for row in [*rows, *external] if row["actual"] is None), Decimal(0))
        holds += _money(metadata["opening_hold_usd"])
        remaining = None
        try:
            decision = yaml.safe_load((self.project / "budget/decision.yaml").read_text())
            validate_data(decision, Path(__file__).resolve().parents[2] / "schemas/budget-decision.schema.yaml")
            if file_sha256(self.project / "budget/estimate.yaml") == decision["estimate_sha256"]:
                remaining = str(_money(decision["max_spend_usd"]) - used)
        except Exception:
            pass
        return {"initialized": True, "account": metadata, "committed_usd": str(used),
                "known_actual_cost_usd": str(known), "unresolved_holds_usd": str(holds),
                "external_committed_usd": str(external_used), "remaining_budget_usd": remaining,
                "actual_cost_usd": None if holds > 0 else str(known),
                "jobs": rows, "external_jobs": external, "events": events}
