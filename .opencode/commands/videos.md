---
description: Prepare selected-model video prompts; render only with explicit job consent.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Load cloud-production or read its repository SKILL.md. Prepare one prompt per
moving shot for the one selected-tier video model, not all models/tiers. Preserve
IDs, source-image/reference order, canonical timing, and prompt/media separation.
Respect selected route caps and default no-audio video; disclose segmentation
costs. Do not apply LTX/H3 dialects to cloud models (use the selected model's
native contract; tests = WAN 3.0, first frame only) or switch the runtime LLM.
Do not start before the user approved the keyframe contact sheet.

Generation requires matching budget evidence and additional explicit paid-job
consent covering model/parameters/attempts/cost/ceiling. Use the actual project
ComfyUI cloud adapter only; no direct API bypass, installations, user JSON edits,
silent fallback, or unapproved retries. Legacy video is explicit opt-in with
native constraints and hardware guards. This command is not spending consent.

Generate through `scripts/cloud_batch.py` (`docs/cloud-batch.md`): one user
agreement per batch (job list + total cost), submitted from the main session.

Delegate to @video-prompt-agent.

Project:

$ARGUMENTS
