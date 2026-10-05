---
name: story-development
description: Develop production-ready film stories with stable IDs and visual continuity.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Preparation is a planning default, not paid consent or an automatic
OpenCode LLM change. Preserve story IDs; establish a positive duration and hand
off to budget-estimation (or read its SKILL.md if unavailable) after the story.
The next stage is budget estimate and explicit user tier/budget review, then
screenplay. Never skip that gate or fabricate approval.

Create:

story/story.yaml

Required:

- premise
- logline
- genre
- tone
- theme
- characters
- conflict
- stakes
- acts
- beats
- ending

Rules:

1. Stable IDs.
2. Every beat belongs to an act.
3. Every character referenced by ID.
4. Every visual element must be concrete enough for later image generation.
5. Avoid continuity contradictions.

Validate with:

schemas/story.schema.yaml
