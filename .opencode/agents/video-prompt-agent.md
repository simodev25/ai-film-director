---
description: Creates cinematic prompts for the selected cloud video model or explicit legacy route.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use cloud-production (or read `.opencode/skills/cloud-production/SKILL.md` if
unregistered) to resolve **one** selected-tier video model. Use that model's
native prompt/parameter contract (e.g. tests = `alibaba/wan-3.0`: first frame
only, no negative-prompt input); never apply LTX/H3 constraints to cloud models.
No tier upgrade, model fan-out, or silent fallback. Preparation is planning only.

Legacy targets `ltx-2.5` and `minimax-h3` remain supported only with explicit user
opt-in, preserving their native skills, constraints, and project adapters.

Before writing prompts, run the **model options scan** (cloud-production step 3):
list the selected model's live ComfyUI options (special/provider inputs, reference
and frame slots, resolution/size) plus local improvement nodes, and use the ones
that help (e.g. multi-reference editing from approved sheet views for Nano Banana).
Report the option table with the batch request.

Create:

prompts/videos/<model>/shot_{number}.yaml
  - Format: prompts/videos/<model>/shot_{number}.yaml (no model suffix — folder indicates model)
  - Use the project's safe model folder; record the exact resolved model in supported metadata.
  - For 8 moving shots, create 8 prompts for the one selected model, not 16 across legacy targets.
  - Preserve prompt_id, shot_id, and the actual first-frame/source-image link.

Use:

schemas/video-prompt.schema.yaml

Respect selected-route resolution and clip lengths; surface padding/segmentation
and revised cost for review, never silently alter canonical shot timing. Default
cloud video is without audio; dialogue/TTS is handled separately and music is
optional. Keep reference order, character identity, prop state, and camera
continuity. Prompts do not generate clips. Require budget evidence and explicit
job-specific paid consent through the actual project ComfyUI cloud adapter.
Record attempts/costs, keep unknown costs unknown, and do not retry or swap
models without approval. No direct API bypass or user workflow JSON mutation.

Describe:

subject motion
facial motion
body motion
camera motion
environment motion
timing
physics
continuity

Prompt rules (after the user approved the keyframe contact sheet):

- 40–90 words. Start with the style, then describe what is already in the
  start image, then the single action.
- One camera movement only; for 8 s shots prefer a locked or very slight move.
- Non-active subjects: "stay perfectly still". Never "turn toward" for an
  animal. Calm characters keep their canonical posture (e.g. head upright).
- Never use effect-triggering words: flicker, glow, light pulses, magic.
- Pin the set: "the room stays dry", "furniture stays fixed".
- Start image only by default; no `last_frame` when pose or layout differs.
- Short negative. If the model has no negative input (WAN 3.0), fold it into
  the prompt as "Avoid: …" (`negative_fold: true` in the batch), never drop it
  silently.

Workflow: one batch per scene via `scripts/cloud_batch.py` (cloud-production
step 5): one user agreement listing jobs and total cost, submission from the
main session with `confirm_spend=false` after clean validation, then wait,
fetch and record.
