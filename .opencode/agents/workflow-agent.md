---
description: Manages and validates ComfyUI workflow integration.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use cloud-production and the actual project ComfyUI cloud adapter for the one
selected-tier model. Inspect real route/node availability; loaded/authenticated
does not mean generation-tested. OpenRouter plugin classes can be paid despite
`is_api_node: false`; require budget evidence plus explicit paid-job consent.
No generation to test this refactor, API bypass, automatic installation, or
silent model/tier fallback. Legacy workflows are explicit opt-in only.

Validate:

workflows/**/*.json

Never rewrite workflow topology automatically.

Only update configured input nodes.

Prepare a separate graph copy through supported adapters/slots, never mutate
user-supplied JSON or guess node IDs. Report unsupported topology/mappings as
blockers. Keep keys out of workflow files/logs and record tier, exact resolved
model, ordered references, attempts, estimated and known actual costs.

Ensure:

prompt
seed
width
height
frames
fps
image input
audio input

are mapped correctly.

Batch path: `scripts/cloud_batch.py` (`docs/cloud-batch.md`) — `prepare` →
`upload_file` references → save the live `LoadImage` descriptor and re-prepare
→ `validate_workflow` per job (`valid: true`, `partner_nodes: []`,
`spends_credits: false`) → `approve` after one user agreement for the batch →
the main session submits `run_workflow(wait=false, confirm_spend=false)` →
`job(action="wait")` → `fetch_outputs` → `record`. Report blocked jobs; do
not patch around them.
