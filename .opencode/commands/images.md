---
description: Prepare selected-model image prompts; render only with explicit job consent.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Load cloud-production or read its repository SKILL.md. Prepare one image prompt
per shot for the one selected-tier model, not all tiers/legacy targets. Preserve
canonical IDs, ordered references, and separate prompt/media artifacts. Default
preparation is planning only; do not switch the runtime LLM automatically.

Before rendering, verify budget estimate/review and ask for additional explicit
job-specific paid consent (model, parameters, references, attempts, cost and
ceiling). Use the actual project ComfyUI cloud adapter, not direct API calls;
loaded/authenticated is not generation-tested. No user JSON edits, installations,
silent model swap, or unapproved retry. Legacy models require explicit opt-in;
never label Nano Banana/Gemini/Seedream as Qwen/FLUX/Krea. This command alone is
not paid generation consent.

Generate through `scripts/cloud_batch.py` (`docs/cloud-batch.md`): one user
agreement per batch (job list + total cost), submitted from the main session.
Then present a 3×3 keyframe contact sheet for user approval before any video;
one targeted correction per problematic shot.

Delegate to @image-prompt-agent.

Project:

$ARGUMENTS
