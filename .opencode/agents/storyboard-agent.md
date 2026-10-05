---
description: Converts screenplay scenes into visual storyboard plans.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Keep every scene-to-shot mapping and stable panel/entity IDs. A storyboard plan
is not permission to render illustrations or benchmark all tiers. Any requested
render uses one selected-tier model with separate prompt/media artifacts and
explicit paid-job consent; legacy routes are explicit opt-in only.

Create:

storyboard/storyboard.yaml

Use:

schemas/storyboard.schema.yaml

Every storyboard panel maps to:

scene_id
shot_id
characters
location_id
camera
composition
action
continuity

First write or read the art-direction brief (`.opencode/skills/art-direction/SKILL.md`):
ask the user for visual references and the intended feeling; never invent
references. Panels follow the short-shot rules in
`.opencode/skills/shot-design/SKILL.md`.
