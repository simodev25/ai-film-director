---
name: continuity
description: Audit visual, narrative, character, prop and camera continuity.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Audit stable IDs, scene/shot/prompt/media/event mappings, reference order,
actual selected-tier/model resolution, attempts, budget review and paid-job
consent. Flag silent fallbacks/upgrades, mislabeled cloud models, and unknown
costs; do not convert unknown to zero. Loaded/authenticated is not generated or
generation-tested. Do not fix errors by automatic rerender or canonical rewrites.
For cloud media operations, load cloud-production or read its SKILL.md directly.

Check every stage against all previous stages.

Flag:

missing IDs
orphan shots
missing characters
wardrobe changes
prop changes
location contradictions
time contradictions
camera continuity errors
screen-direction errors
