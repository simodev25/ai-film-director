---
description: Plan selected-tier audio; generate only needed dialogue with explicit job consent.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use cloud-production or its repository SKILL.md for the one selected-tier audio
model (Seed Audio in the current profile). Qwen3-TTS remains explicit legacy
opt-in only. Preserve speaker/scene/shot/prompt IDs, dialogue text, voice identity,
and audio-event mappings. No dialogue/narration means no TTS job. Music is
optional and never presumed free; preparation can reuse existing local rain.

Audio prompts are separate from media. Require budget review plus additional
explicit paid-job consent through the actual project ComfyUI cloud adapter;
track attempts and costs, with unknown actual cost not zero. No automatic tier/
runtime LLM changes, fallback, API bypass, or unapproved retry. This command
alone does not authorize generation.

Sound design is layered (ambience, room tone, on-screen sources, discreet
foley, J/L-cuts): free procedural/local first, then Seed Audio for isolated
sounds via `scripts/cloud_batch.py` with one user agreement per batch.

Delegate to @audio-agent.

Project:

$ARGUMENTS
