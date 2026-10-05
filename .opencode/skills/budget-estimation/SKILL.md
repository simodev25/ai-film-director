---
name: budget-estimation
description: Estimate all three film gammes and require user review before screenplay.
compatibility: opencode
---

# Budget estimation

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first; their consent, routing, continuity, and legacy guards apply to this skill.

Input: the canonical project/story, positive duration, and optional assumptions
file validated by `schemas/budget-assumptions.schema.yaml`. Estimate after story
development and before screenplay. Use the project
CLI `film-director budget PROJECT --assumptions FILE` (omit the option only when
the default duration/assumptions can be resolved). Inspect the available CLI
before execution; do not invent missing commands or pricing fields.

Output:

- `budget/estimate.yaml`, validated by `schemas/budget-estimate.schema.yaml`.
- `budget/estimate.md`, a user-readable comparison of preparation/tests/production.

Compare low / mean / high costs for all three gammes with identical assumptions.
Disclose film duration, shot/clip counts, references and separately generated
reference illustrations, resolution, token estimates, dialogue seconds, retries,
optional music, price date/source, and exclusions. Respect each model's clip and
reference caps; estimates of rounded clip duration must be visible. No dialogue
means no TTS; existing local rain can be reused without a charged generation.
Unknown costs are unknown, not zero. Never generate media to measure price.
Use supported inputs only; `images` includes shot images and reference
illustrations, whose breakdown must be explained in the report. Set
`audio_seconds: 0` when no new audio/dialogue is required, rather than retaining
a duration-based audio default. Optional music is outside the current estimate
and needs a separate quote. The standard-context input limit is below 272,000
tokens; do not extrapolate those prices for a larger context.

Present the comparison and ask for a selected tier and budget ceiling. Only
after an explicit affirmative user decision may `budget/decision.yaml` record
`estimate_sha256`, `selected_tier`, `max_spend_usd`, nonempty `consent_reference`,
and `approved: true`. Do not fabricate approval or mint it automatically.
Include `scope: planning_only_not_spend_consent` and validate against
`schemas/budget-decision.schema.yaml`. Hash the saved estimate YAML bytes, not
the parsed object or Markdown, for `estimate_sha256`.
Screenplay requires a valid estimate and matching decision; this acknowledgement
is planning approval, not paid-job consent. Refresh/review changed estimates.

For existing projects, label the estimate retrospective and report missing
review evidence without rewriting canonical artifacts. Use the actual CLI and
schema's supported fields; describe retrospective status in the report if a
machine-readable field is unavailable.
