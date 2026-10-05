---
name: character-design
description: Create consistent characters and production-ready character sheets.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Preserve stable canonical character IDs and appearance/voice anchors.
Planning a sheet is not generating an image. If reference illustrations are
requested, load cloud-production or read its repository SKILL.md; use the one
selected-tier model with ordered entity-linked references, separate illustration
costs, and explicit paid-job consent. Legacy rendering requires explicit opt-in.

Define:

identity
physical appearance
face
hair
eyes
body
age
wardrobe
accessories
personality
expression
movement
voice
visual anchors

Character sheets must contain reusable identity anchors for image and video prompts.

Visual reference model sheets (after art direction) follow the `model-sheets`
skill: turnaround (front, 3/4, profile, back, full body, neutral pose, plain
background), expression sheet, one sheet per outfit/era; animals add lying and
sitting poses. User-approved sheets go in `references/approved-references.yaml`;
keep the full sheet and per-view crops, and feed models the view matching the
shot angle.
