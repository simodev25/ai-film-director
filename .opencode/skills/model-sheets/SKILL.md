---
name: model-sheets
description: Plan, generate (with consent) and register reference model sheets for characters, animals, locations and props.
compatibility: opencode
---

# Reference model sheets

Read `docs/cloud-policy.md`, `config/cloud-tiers.yaml` and `docs/film-method.md`
from the repository root first; load `cloud-production` (or read its SKILL.md)
before any generation. Sheets come after art direction and before storyboard.

## Sheet types (one image each)

- **Character**: turnaround — front, 3/4, profile, back, full body, neutral
  pose, plain background; an expression sheet; one sheet per outfit/era.
- **Animal**: turnaround plus lying and sitting poses.
- **Location**: 3–4-angle sheet, plus a top-down **floor plan** showing
  windows, TV/screens, doors and furniture positions.
- **Prop**: multi-angle sheet plus each story state.

## Generation

- Use the selected tier's single image model; ≈ 1 image per sheet. Sheets are
  entity-linked reference illustrations, accounted separately from shot renders.
- Batch them through `scripts/cloud_batch.py` (`job_kind: reference_illustration`)
  with one user agreement for the batch (job list + total), never automatically.
- Prompt for neutral, evenly lit, plain-background views; no text labels
  inside the image; exact view count and layout.

## Approval and registration

1. Show each sheet to the user; regenerate only with consent, one targeted
   correction at a time.
2. Record approved sheets in `references/approved-references.yaml` (entity_id,
   entity_type, path, sha256, approval verbatim/date, notes).
3. Keep the full sheet **and** crop each view into its own file locally (free,
   no model), recording parent sheet, view name and sha256. Use only fields the
   registry/schema supports; report gaps rather than inventing keys.

## Use in shots

Give models the **isolated view** matching the shot angle (3/4 view for a 3/4
shot, floor plan to place furniture/window/TV), never the whole grid — a grid
reference makes models reproduce the grid. Shots declare `reference_entity_ids`
and the view used per entity.
