---
description: Creates characters and production-ready character sheets.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use the selected tier's single image model only if reference illustrations are
explicitly requested; character data/sheet planning is not image generation.
Preserve canonical character IDs and reusable identity/voice anchors. Account
for entity-linked reference illustrations separately from shot renders, keep
ordered references, and require budget review plus explicit paid-job consent.
Legacy models/dialects require explicit opt-in, never a silent fallback.

Create:

characters/characters.yaml
characters/sheets/*.yaml

Use:

schemas/character.schema.yaml
schemas/character-sheet.schema.yaml

Character identity must remain stable across all scenes.

Reference model sheets: follow `.opencode/skills/model-sheets/SKILL.md` —
turnaround + expression sheet + one sheet per outfit/era; animals add lying and
sitting poses. ≈ 1 image per sheet, batch consent, user approval, registered in
`references/approved-references.yaml` with per-view crops.
