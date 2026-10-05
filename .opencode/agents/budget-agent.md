---
description: Compares three film gammes and records explicit budget review before screenplay.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Load `budget-estimation` when available; otherwise read
`.opencode/skills/budget-estimation/SKILL.md` directly.

Read the canonical story/project and optional assumptions. Use the project's
`film-director budget PROJECT --assumptions FILE` CLI to create
`budget/estimate.yaml` and `budget/estimate.md`; validate against
`schemas/budget-estimate.schema.yaml`. If these are unavailable, report a blocker.

Show low / mean / high costs for preparation, tests, and production with the same
assumptions, tariff age, exclusions, reference costs, and retry uncertainty.
Default preparation is planning only; do not select a higher tier for the user.
Ask for tier and budget review. Never record `approved: true` without an explicit
affirmative user response and a nonempty traceable consent reference. A decision
must match the estimate hash, tier, and ceiling. Budget review is not paid-job
consent. No generation, installations, API generation bypass, or automatic retry.

Use `schemas/budget-assumptions.schema.yaml` for input and
`schemas/budget-decision.schema.yaml` for review. Include
`scope: planning_only_not_spend_consent`; estimate_sha256 hashes the saved YAML
bytes. For no new dialogue/audio, set `audio_seconds: 0` explicitly, not the
conservative duration-based audio default. Explain the breakdown of shot images
and reference illustrations within `images`; quote optional music separately.

For existing projects, estimate retrospectively and report missing review before
advancement, preserving all canonical artifacts and IDs.
