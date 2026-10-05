---
description: Plan the complete film pipeline with budget review and explicit generation gates.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use preparation for planning unless the user explicitly selects another tier.
Resolve one model per stage, never all-model fan-out, silent fallback, or runtime
LLM switching. Cloud tasks use cloud-production or its repository SKILL.md.

Run the film director pipeline (method: `docs/film-method.md`) for:

$ARGUMENTS

Execute:

story
budget estimate (low / mean / high across preparation, tests, production)
explicit user tier and budget review
screenplay
characters / locations / props
art direction (ask the user for references)
reference model sheets (user-approved)
storyboard
short shots
images (keyframes) → 3×3 contact sheet approved by the user
videos (one per shot)
finishing + sound design
continuity
edit / render
optional tier upgrade pass (explicit tier choice; same approved shots)

Validate every stage before continuing.

Stop before screenplay without a valid `budget/estimate.yaml` and matching
explicitly approved `budget/decision.yaml`; use budget-estimation or its SKILL.md.
Existing projects need retrospective review before advancement, not canonical
rewrites/deletions. Budget acknowledgement is planning only: pause again before
each paid job for explicit model/parameters/attempts/cost consent within the
ceiling. This command does not authorize generation. Use only actual project
ComfyUI adapters, preserve workflows/IDs/continuity, and report missing routes.
Skip TTS without dialogue/narration; optional music is not presumed free. Legacy
models require explicit opt-in; no generation tests, installations, or API bypass.
