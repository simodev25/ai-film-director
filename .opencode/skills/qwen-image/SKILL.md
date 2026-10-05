---
name: qwen-image
description: Qwen Image prompt adapter
---

# Qwen Image

## Legacy-only guard

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Use this native dialect only after explicit user opt-in to legacy Qwen Image.
It is not a tier default/fallback. For selected-tier cloud images, load
cloud-production or read its repository SKILL.md; never label Seedream/Gemini/
Nano Banana as Qwen or apply this dialect as their API contract. Preserve
canonical prompt_id/shot_id and ordered entity references in schema-valid YAML.
Prompts do not render images; require budget evidence and explicit paid-job
consent through the actual project adapter, without changing user workflow JSON.

Transform the canonical shot into a detailed visual generation prompt.

Preserve:

- exact character identity
- action
- environment
- composition
- lighting
- text requirements when explicitly required

Never introduce story changes.

Return:

prompt
negative_prompt
references
parameters
