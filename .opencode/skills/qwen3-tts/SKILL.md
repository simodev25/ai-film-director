---
name: qwen3-tts
description: Qwen3-TTS dialogue prompt adapter
---

# Qwen3-TTS

## Legacy-only guard

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. This native dialect remains functional for explicit legacy Qwen3-TTS
opt-in only. Selected-tier Seed Audio uses cloud-production or its repository
SKILL.md, not a Qwen model label or silent fallback. No dialogue/narration means
no TTS prompt/job; music is optional and never presumed free. Preparation may
reuse existing local rain/ambience without a charged call. Keep canonical
speaker/scene/shot/prompt IDs, exact dialogue, and stable voice identity. Prompts
and audio are separate; paid jobs require budget review plus explicit generation
consent through actual project adapters, preserving user JSON and cost records.

Generate dialogue specifications from the canonical audio plan.

Each dialogue item should define:

- speaker
- text
- emotion
- intensity
- pace
- pause
- voice identity
- pronunciation requirements

Character voice identity must remain stable.

Do not rewrite dialogue text unless explicitly instructed.

Output structured audio prompt YAML.
