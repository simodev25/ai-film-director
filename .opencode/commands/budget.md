---
description: Compare three film gammes and request budget review before screenplay.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.

Project and optional assumptions:

$ARGUMENTS

Use budget-agent only if it is available in the live agent catalog; otherwise
read `.opencode/agents/budget-agent.md` and
`.opencode/skills/budget-estimation/SKILL.md` directly and perform the task, or
delegate to an available general agent when authorized. Do not invoke an
undiscovered skill/agent or change the runtime LLM automatically.

Use `film-director budget PROJECT --assumptions FILE` (assumptions optional when
duration resolves from project/story) to create `budget/estimate.yaml` and
`budget/estimate.md`; validate with `schemas/budget-estimate.schema.yaml`.
Show low / mean / high costs for all three tiers using the same assumptions.
Validate assumptions with `schemas/budget-assumptions.schema.yaml`; set
`audio_seconds: 0` when no new dialogue/audio is needed rather than inheriting a
duration-based default. Explain reference illustrations separately within the
total `images` count; optional music needs a separate quote.
Stop for explicit user review of tier and budget ceiling. Never fabricate an
approved `budget/decision.yaml`. This command does not authorize paid generation.
Decisions must validate against `schemas/budget-decision.schema.yaml`, include
`scope: planning_only_not_spend_consent`, and hash the saved estimate YAML bytes.
