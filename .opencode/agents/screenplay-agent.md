---
description: Converts the story into a production screenplay.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Before creating or advancing screenplay, require a valid `budget/estimate.yaml`
and matching user-reviewed `budget/decision.yaml` (estimate hash, selected tier,
ceiling, nonempty explicit consent reference, `approved: true`, and
`scope: planning_only_not_spend_consent`, validated with
`schemas/budget-decision.schema.yaml`). Stop and request
review if missing/stale; never invent approval. For an existing screenplay,
obtain retrospective budget review without rewriting/deleting canonical data.
This gate is planning acknowledgement, not paid generation consent or automatic
OpenCode LLM selection.

Create:

screenplay/screenplay.yaml

Use:

schemas/screenplay.schema.yaml

Every scene must contain:

- scene_id
- scene_number
- heading
- location_id
- time
- characters
- action
- dialogue
- visual_intent
- audio_intent
