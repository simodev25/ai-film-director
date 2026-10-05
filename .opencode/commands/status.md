---
description: Show AI film pipeline status.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Report pipeline and budget readiness separately: estimate/review missing or
stale, selected tier, planned versus known actual costs, and prepared versus
generated/tested assets. Inspect supported artifacts if the manifest lacks these
fields; do not claim it validates them automatically. Unknown cost is not zero.
Status is read-only: no consent creation, generation, runtime LLM changes, or
canonical artifact rewriting. Existing projects lacking budget evidence need
retrospective review before advancement, not deletion.

Run:

film-director status PROJECT

Resolve PROJECT from `$ARGUMENTS` (a project path, or a name under `projects/`)
and quote the actual path when invoking the CLI. If the entry point is not
available, inspect the supported CLI invocation or report the blocker; do not
install it. Do not run `scripts/build_manifest.py` as a read-only status check,
because that script writes `manifest.yaml`.
