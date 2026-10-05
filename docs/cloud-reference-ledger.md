# Canonical cloud illustrations and caller-owned budget ledger

Read `cloud-policy.md` and `../config/cloud-tiers.yaml` first. This implementation
does not generate, authenticate or install anything. Technical approval to edit
code is **not** approval to reserve or submit a paid job.

## Target contract (version 1, backward compatible)

`schemas/cloud-job.schema.yaml` now supports exactly one target kind:

- **shot_render**: `shot_id` required. Omitting `job_kind` keeps the old contract.
  `entity_id` and `entity_type` are prohibited.
- **reference_illustration**: explicit `job_kind`, `project_id`, `scene_id`,
  `entity_id`, `entity_type` (`character`, `location`, `prop`), `modality: image`;
  `shot_id` prohibited. No invented shot ID for an illustration.

`schemas/image-prompt.schema.yaml` supports the same target distinction for
cloud image prompts. Existing legacy and cloud shot prompts remain valid. A
reference illustration prompt stays a prompt, not an approved media asset.
Canonical entity metadata belongs to the **output**; `references` continues to
mean ordered input conditioning. Neither a canonical entity ID nor a text
description creates an input reference image.

`comfyui.cloud_targets.validate_project_target(job, project, scope=None)` resolves
targets from `project.yaml`, `shots/shots.yaml`, and the existing character,
location or prop collections. Illustrations must reference an entity actually
used by shots in their declared scene. Unknown/ambiguous IDs, incorrect entity
categories, mismatched scene/shot and cross-project jobs fail closed.
`ProjectScope(scene_ids=(...), entity_ids=(...))` restricts canonical content;
it cannot supply missing IDs. Its hash is additionally bound by paid approval.

`prepare_cloud_workflow(..., project=project, scope=scope)` and
`authorize_cloud_job(..., project=project, scope=scope)` require canonical
project context for illustrations. Old shot-only calls without `project`
remain compatible but do **not** claim canonical validation; the ledger always
uses canonical validation. `GatedRun.shot_id` is null for illustrations and
records `job_kind`, `entity_id`, `entity_type`, `project_id`, `scene_id`.

No graph creation or topology repair has been added. Every graph must be an
existing caller-supplied API graph with live-verified bindings and output nodes.
Only configured inputs on a deep copy are updated. Seed remains optional and
requires configured capabilities; no central pricing/capability config changed.
Width, height, frames, fps and image/audio conditioning still fail closed when
not supported/mapped; no pixel-size inference from 1K.

## Durable accounting API

`comfyui.cloud_ledger.CloudLedger(project, config_path=...)` is a small SQLite
accounting library, **not a transport**. It uses a single fixed per-project
`budget/cloud-ledger.sqlite3`; merely constructing it creates nothing.
Do not create an alternative DB per scene/tier/retry: all prior attempts across
scopes/reviews contribute to the project ceiling.

### reserve

`ledger.reserve(graph, job, approval, scope=scope, workflow_validated=True,
opening_hold_usd=..., opening_balance_reference=...)`:

1. Requires the real current planning decision and recomputed estimate through
   `require_budget_review`, exact tier/config, current estimate bytes/hash.
2. Validates canonical target/scope and the existing adapter's paid approval
   gate: exact model/route, positive estimate, per-job ceiling, pricing freshness,
   graph/plan/estimate hashes, explicit `scope: paid_generation_job`, affirmative
   approval, nonempty actual user `consent_reference`.
3. Additionally requires approval `project_id`, `scope_sha256`
   (`sha256_document(asdict(scope))`) and `decision_sha256` (saved YAML bytes).
4. Requires an explicitly reconciled opening hold and evidence reference for
   external/historical liabilities. **None/unknown blocks**; the library never
   treats absent invoices as zero. The initialized baseline is immutable in this
   minimal API; later evidence corrections require a separately reviewed
   extension, not deleting/restarting the ledger.
5. Atomically holds the **per-job ceiling**, not merely the expected image cost.
   `BEGIN IMMEDIATE`, unique plan/consent and target-attempt constraints,
   Decimal sums and `synchronous=FULL` prevent concurrent overspend/reuse.

The job includes `project_id`, also for old shot plans using this API. Attempt
numbering is sequential per modality/kind/canonical target, independent of
prompt IDs, scene or scope. A retry requires a prior completed/failed/ambiguous
attempt, a new plan/hash/attempt and a distinct explicit consent reference.
No concurrent or automatic retries are offered.

### claim once, then caller-owned submission

`ledger.claim(plan_sha256, graph, job)` atomically consumes a reserved attempt
**before** the caller submits once through comfy-mcp. It rechecks the current
planning decision, canonical scope, fresh pricing and graph/plan hashes. A
changed/stale review or an over-ceiling account blocks submission. A second
claim fails. A crash after claim conservatively keeps the hold; investigate
provider activity, do not replay the transport.

Claim returns the persisted audit/plan/approval record, **not** an executable
token. The caller remains responsible for exact live graph validation, correct
server/provider authentication without leaking secrets, routing only that graph
via comfy-mcp, and honoring the real human consent. The library cannot prove a
human response is genuine or intercept arbitrary tools/scripts outside it.
No CLI automatically submits or reserves on a planning/technical `go`.

### outcomes and unknown charges

`ledger.record_outcome(plan_sha256, status='completed'|'failed'|'ambiguous',
actual_cost_usd=None, provider_job_id=None, outputs=(), cost_reference=None)`:

- Unknown actual stays **null** and retains the whole hold, including failed
  and ambiguous calls. No automatic release/cancellation/refund.
- Known actual requires explicit evidence; finite nonnegative values only.
  A genuine reported zero can be booked with evidence, never inferred.
  Studio's unknown FLOAT sentinel **-1** must be mapped to None by the caller,
  not zero (negative monetary input is rejected).
- Known costs cannot be decreased or reset to unknown, terminal outcomes and
  existing output/provider-job identities cannot be overwritten. Reconciliation
  appends events; history is preserved.
- An actual exceeding the approved ceiling is still booked honestly and blocks
  further overspending, rather than being truncated to the estimate/ceiling.

`snapshot()` is read-only. It returns account baseline, committed dollars,
jobs (complete plan/parameters/ordered input references, target metadata,
approval/consent/hashes, reserved/actual/status) and append-only outcome events.
Uninitialized snapshots report unknown actual, never fictional zero spend.
Credential-shaped fields and values are rejected before persistence. No runtime
key/config is read by the ledger.

### External incurred costs — accounting only

`ledger.import_external_cost(evidence, today=...)` imports an **already performed**
`user_initiated_external_submission`; it is not a retroactive approval, managed
reservation/claim, transport permission or change to the target attempt history.
The minimal contract currently covers canonical image reference illustrations.
Validate `schemas/cloud-external-cost.schema.yaml`. It requires a stable
`external_id = comfy:<comfy_prompt_id>`, project/campaign/decision hashes, exact
tier/model/route and entity/scene, Comfy/Studio/provider identifiers, and a
project-relative JSON receipt bound by its **file-byte hash**.

The receipt must match the identity, scope, model and reported actual amount.
The caller must acquire it read-only from authoritative provider/plugin evidence;
matching hashes are integrity checks, not proof that arbitrary third-party
claims are authentic. No keys, credentials, approval or consent fields belong
in the external import contract. The campaign declaration must match the
initialized account's opening perimeter and current reviewed budget.

- New `external_jobs`/`external_aliases` tables are separate from managed jobs.
  Exact repeated imports are idempotent; revised cost/evidence or reuse of any
  Comfy/Studio/provider identity is rejected, including sharing with a managed
  attempt. `record_outcome` optionally records a managed `comfy_prompt_id` and
  rejects external ID reuse in the reverse direction too.
- Known actuals are finite nonnegative Decimal amounts. A genuinely reported
  zero is permitted with matching evidence. Unknown actual remains null and
  requires a positive accounting provision `unknown_hold_usd`, not a fictional
  actual zero. Known actual and unknown hold cannot both be booked.
- Imports append an `external_imported` accounting event under a distinct
  external namespace; no false consent or reserved-before-run history.
  Existing managed rows and prior events are not rewritten or released.
- `BEGIN IMMEDIATE` serializes import with reserve/claim. All three use the
  aggregate of opening liabilities, managed actuals/holds and external
  actuals/holds. An already incurred over-ceiling cost is booked honestly;
  subsequent reservation or claim is blocked, not the recorded cost truncated.
- `snapshot()` also exposes `external_jobs`, `external_committed_usd`,
  `known_actual_cost_usd`, `unresolved_holds_usd` and `remaining_budget_usd`.
  Grand `actual_cost_usd` stays null while any hold remains unresolved.
  Invalid/missing current budget hashes leave remaining unknown. Older ledgers
  without the additive tables are readable without mutating their schema.
- Immutable external imports do not silently support refunds/revisions or
  unknown-to-known settlement yet: conflicting revisions fail closed and need
  a separately reviewed reconciliation extension.

Before changing a real ledger, `ledger.backup(new_path)` uses SQLite's consistent
backup API from a read-only source and verifies destination integrity. It never
overwrites an existing backup. This is a backup operation, not raw SQL mutation
or a way around budget/job gates. Compare managed rows and old events before/
after import and preserve the backup and receipt hashes in the audit report.

## Limits and remaining production gates

- SQLite assumes a local trustworthy durable filesystem and one shared project
  ledger. Manual DB deletion/editing, alternate transport or invented consent
  evidence is not a supported way to bypass the gate.
- The library does not intercept unrelated historical jobs. Reconcile those via
  the opening hold; unknown historical exposure blocks first reservation.
- Budget/scene scope review is caller-owned: scope is additionally bound by the
  paid-job approval, not extracted by interpreting prose in the planning decision.
- Live graph validation remains caller attestation and must inspect dynamic
  controls as well as comfy-cli's known blind spots. Loaded/authenticated is not
  generation-tested; unit-test fixtures are not production graph templates.
- Ordered reference assets must still be verified/approved by the caller using
  canonical prompt asset/entity associations and actual uploads. The ledger
  records the ordered plan; it does not manufacture or approve media assets.
- Missing graph/bindings, route-specific pricing or authentication remain blockers.
  No direct OpenRouter generation endpoint or legacy fallback is introduced.
