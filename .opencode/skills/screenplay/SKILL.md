---
name: screenplay
description: Convert story structure into a production-ready screenplay.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Require a valid `budget/estimate.yaml` and matching explicitly reviewed
`budget/decision.yaml` before creating/advancing screenplay: current estimate
hash, selected tier, ceiling, nonempty consent reference, `approved: true`, and
`scope: planning_only_not_spend_consent`, validated with
`schemas/budget-decision.schema.yaml`.
Missing/stale evidence requires user review, not automatic approval. For existing
screenplays, add retrospective review without rewriting/deleting canonical
artifacts. This gate acknowledges planning, not paid generation or runtime LLM
routing. Cloud media tasks use cloud-production or its repository SKILL.md.

Create scene-level screenplay data.

Each scene requires:

scene_id
scene_number
heading
location_id
time
characters
action
dialogue
visual_intent
audio_intent

Every scene must be visually producible.
