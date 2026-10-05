---
name: comfyui
description: Execute and validate ComfyUI workflow JSON pipelines.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Load cloud-production or read `.opencode/skills/cloud-production/SKILL.md`
directly if unavailable. Use the actual project ComfyUI cloud adapter for the
one selected-tier model; inspect implemented routes/mappings before claiming
readiness. Preparation defaults to planning, not permission to generate.

Preserve user JSON/topology and prepare a separate graph through configured
adapters/slots. Validate the target, available nodes, exact model, parameters,
and ordered references without test generation or installations. OpenRouter
plugin classes are paid even when `is_api_node: false`. Require matching budget
review and additional explicit paid-job consent. No direct OpenRouter generation
API bypass, automatic retries, or silent model/tier fallback. Track attempts,
estimates, known actual costs, and outputs; unknown cost is not zero. Keys never
belong in workflows/logs. Loaded/authenticated is not generation-tested.

## Submitting OpenRouter Studio graphs via comfy-mcp (known pitfall)

Lesson from 2026-10-05: `run_workflow(confirm_spend=true)` fails with
`TimeoutError` before any job is queued. That flag triggers an MCP elicitation
popup that the OpenCode client does not display. `comfy generate consent always`
does not apply to `run_workflow`, and `codemode: false` does not fix it.

1. Run `validate_workflow` on the exact prepared graph first.
2. If it reports `partner_nodes: []` and `spends_credits: false` (the case for
   `OpenRouterStudioImage` / `OpenRouterImageGenerate`), submit with
   `run_workflow(workflow_path, wait=false, confirm_spend=false)`. The MCP gate
   only covers Comfy partner credits, so `--allow-spend` is irrelevant here.
3. The graph still spends OpenRouter money. The real gate stays the project
   one: explicit user consent in chat for the job or batch, an approval file,
   and a ledger `reserve` plus a single `claim` *before* submission. Then use
   `job(action="wait")`, then `fetch_outputs`, then `record_outcome`.
4. Never use `confirm_spend=false` to get past a user's *decline* or to run a
   graph whose validation lists real `partner_nodes` (Comfy credits). For
   those, `confirm_spend=true` and the elicitation remain mandatory.
5. Submit from the main session. A timeout with no job created still keeps its
   ledger hold until reconciled (mark it `ambiguous`). A new attempt needs a new
   attempt number and explicit consent.

## Model options scan (every stage, every model)

Before preparing any batch, read the live descriptor of the node class
(`nodes(action="get", name=...)`) and list the selected model's branch inputs
and the local nodes/extensions that could improve the output (multi-reference
editing, color match, upscaling, interpolation, masks). Record a short table
(option → effect → recommended value → cost impact → available/needs install)
and show the useful options to the user with the batch request. Details:
cloud-production step 3. Never enable paid/quality options or install
extensions silently.

Legacy workflows below remain supported only by explicit user opt-in; they are
not the default tier routes. Resolve their actual paths through project adapters:

image/krea2.json
image/flux2-klein.json
image/qwen-image.json
video/ltx-2.5.json
video/minimax-h3.json
audio/qwen3-tts.json

Never assume node IDs.

Legacy node mappings are configured in:

src/comfyui/adapters.py

Read the actual cloud adapter and configured mappings for cloud routes instead
of assuming the legacy map implements them. A missing route is a blocker.
