---
name: shot-design
description: Design cinematic shots from storyboard panels.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Keep canonical scene/shot IDs, timing, and prompt/media mappings. Resolve
one selected-tier model per media stage through cloud-production or its SKILL.md,
not all tiers or legacy models. Respect selected model caps; surface clip
segmentation/padding and changed costs for review rather than silently changing
shot duration. Shot planning is not paid consent; legacy routes are opt-in only.

Define:

shot size
angle
lens
camera height
camera movement
framing
composition
subject
action
duration
lighting
transition

Maintain screen direction and eyelines.

Cite the scene/shot art-direction brief (`art-direction` skill): every camera
choice states why (tight/wide, held/cut, static/moving).

Short-shot rules (`docs/film-method.md`):

- 4–8 s per shot, or the selected model's caps; one action, one simple camera
  move (static, slow push-in, or slow pan); hard cuts between shots.
- Never a long continuous or orbital move around a character; never chain
  last frame → first frame to fake a continuous camera. Cover with cuts.
- Few active subjects per shot; at most one active animal. Others stay still.
- Prefer a static or near-static camera for 8 s shots.
- Each shot declares `reference_entity_ids` and, per entity, the model-sheet
  view matching its angle (front, 3/4, profile, back, floor plan, prop state).
  Use only schema-declared fields; report unsupported ones.
