---
description: Creates selected-tier audio plans and stable voice assignments, with optional explicit legacy TTS.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Resolve one selected-tier audio model through cloud-production; the current
profile uses Seed Audio, not automatic Qwen3-TTS. Qwen3-TTS and its native skill
remain supported only with explicit legacy opt-in, never a silent fallback.
No dialogue/narration means no TTS prompt/job. Music is optional and never
presumed free; preparation may reuse existing local rain without a charged call.
Keep canonical text, speaker/scene/shot IDs, voice identity, and audio-event
mappings. Planning prompts are separate from generated audio. Require budget
evidence and additional explicit paid-job consent before submitting through the
actual project ComfyUI cloud adapter; track attempts/estimates and unknown actual
costs honestly. Do not change the runtime LLM or bypass the adapter via API calls.

Create:

prompts/audio/*.yaml

Use:

schemas/audio-prompt.schema.yaml

Handle:

dialogue
narration
voice
emotion
pace
pitch
sound intent

Sound design (from the art-direction brief): build in layers — exterior and
interior ambience, room tone, on-screen sources (e.g. TV), discreet foley,
J/L-cuts across shot boundaries. Use free procedural/local sources first;
use Seed Audio only for isolated sounds, batched via `scripts/cloud_batch.py`
with one user agreement per batch. Deliver a bed usable by the local
finishing tools (`finish_anime.swift --audio`, `concat_cuts.swift`).
