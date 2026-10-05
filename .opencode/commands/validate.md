---
description: Validate the complete film project.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Validate canonical schemas/IDs/continuity and report budget readiness separately:
valid estimate plus matching explicit tier/ceiling/consent decision is required
before screenplay/advancement. Inspect actual validation support; do not claim
unsupported checks passed. Existing artifacts lacking budget evidence remain
canonical and need retrospective review, not rewriting/deletion. Validate actual
model/route metadata and reference mappings, not by test generation. No paid
calls, consent fabrication, installations, or automatic runtime LLM/tier changes.

Run:

python scripts/validate_project.py projects/$ARGUMENTS
