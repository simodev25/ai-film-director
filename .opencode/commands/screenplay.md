---
description: Generate screenplay.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Require a schema-valid `budget/estimate.yaml` and matching user-reviewed
`budget/decision.yaml` (estimate hash, selected tier, ceiling, nonempty consent
reference, `approved: true`, `scope: planning_only_not_spend_consent`, validated
with `schemas/budget-decision.schema.yaml`) before creating/advancing screenplay. Stop for
review if missing/stale; never fabricate approval. Existing screenplay needs
retrospective review, not rewriting/deletion. This gate approves planning only,
not paid generation or an automatic OpenCode LLM switch.

Delegate to @screenplay-agent.

Project:

$ARGUMENTS
