---
name: cloud-production
description: Resolve one selected cloud model per stage and guard ComfyUI jobs and costs.
compatibility: opencode
---

# Cloud production

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. This skill is a production procedure, not proof that a route is runnable.

1. Resolve the explicit selected tier (preparation is planning-only by default)
   and the exact stage model, pricing, and caps from the central config. Do not
   fan out across models/tiers or fall back silently. The text recommendation
   does not select the running OpenCode LLM; discover available runtime models
   only when requested and use the user's exact selected provider/model reference.
2. Read canonical scenes/shots and continuity anchors. Build one model-native
   prompt per needed shot/event for the selected stage. Keep prompts separate
   from media. Preserve IDs, entity references, reference order, voice identity,
   and image-to-video source links. Save canonical schema-valid YAML, including
   the exact model and only supported route metadata. Never label Nano Banana
   as Qwen/FLUX/Krea; do not load legacy dialects for cloud prompts.
3. Inspect the actual project ComfyUI cloud adapter and configured workflow
   inputs. Confirm server target, installed classes, model resolution, caps,
   reference support, and graph validity without generating. Work on a separate
   prepared graph, not user JSON; do not alter topology or guess node IDs. If the
   route is missing, report the blocker. No direct OpenRouter generation API
   bypass, installation, or model download.
   **Model options scan (mandatory, every time a model is used for a stage):**
   read the live `nodes(action="get")` descriptor of the node class and list the
   selected model's branch inputs (e.g. `model.special__*`, `enhancePrompt`,
   `negativePrompt`, `personGeneration`, `conditioningScale`, seed, resolution,
   size, aspect ratio, first/last frame, reference slots, provider options).
   Also check which local ComfyUI nodes/extensions could improve the result
   around the model (multi-reference **image editing** such as Nano Banana
   "same character, new angle / targeted fix", color match/LUT, upscaling,
   frame interpolation, masks). Write a short table per stage in the batch or
   scene notes: option → what it does → recommended value → cost impact →
   available now / needs install. Present the useful options to the user with
   the batch request; never enable a paid or quality-changing option silently,
   and never install extensions without the user's explicit agreement.
   Re-scan when the model, plugin version or tier changes.
4. Verify the current budget estimate and matching planning decision. Present
   job model/tier, parameters, duration/resolution, references, attempts, expected
   charge, and remaining ceiling; require additional explicit paid-job consent.
   OpenRouter plugin classes remain paid even with `is_api_node: false`.
5. The current `src/comfyui/cloud_adapters.py` is offline preparation plus an
   audit gate, not a submitter. Validate `schemas/cloud-job.schema.yaml`, prepare
   with live descriptors/existing bindings, and live-validate the exact graph.
   Additional generation approval binds tier/model/route, workflow/plan hashes,
   reviewed estimate hash, explicit consent reference, and per-job ceiling;
   planning-only budget review cannot substitute. An authorized GatedRun is not
   a submit token. Reserve/account for the cost in the caller's project ledger,
   then submit only the approved prepared graph via available comfy-mcp tools.
   For OpenRouter Studio graphs where `validate_workflow` returns
   `spends_credits: false`, submit with `confirm_spend=false`, because the
   elicitation popup never shows in OpenCode and times out. See the comfyui
   skill section "Submitting OpenRouter Studio graphs". Project consent and the
   ledger claim remain mandatory.
   Batch helper: `scripts/cloud_batch.py`; see `docs/cloud-batch.md`. Order:
   `prepare` → `upload_file(references, overwrite=true)` → save the live
   `nodes(action='get', name='LoadImage')` descriptor and re-`prepare` →
   `validate_workflow` per job → show the user ONE batch request (job list,
   model, parameters, references, attempts, total cost, ceiling) → `approve`
   with their verbatim answer (reserve + claim) → `run_workflow(wait=false,
   confirm_spend=false)` from the **main session** → `job(action="wait")` →
   `fetch_outputs` → `record` → `status`. One agreement covers only the listed
   jobs; retries or extra jobs need new consent. The helper never submits,
   generates, or invents consent.
   Missing transport, mappings, or ledger support is a blocker, not implemented
   execution. Require current route-specific pricing before spending. Keep
   attempt/job/output and consent records, estimated costs, and actual costs
   only if known. Unknown is never zero; failed attempts can cost money. Stop at
   the ceiling or on unresolved pricing; no unapproved retry/model/tier change.
6. Validate produced assets and continuity; map each output to its shot/event
   (or reference illustration's entity ID). Distinguish prepared, submitted,
   failed, completed, and generation-tested states. Loading/authentication is
   not a generation test. Keep credentials and headers out of files/logs.
7. Method (`docs/film-method.md`): prototype the whole scene in preparation;
   no video before the user approves the 3×3 keyframe contact sheet. If the
   user asks, track budget internally and report batch totals only.
8. Tier upgrade pass (only on explicit user tier selection, with a new
   estimate and batch consent): re-run the SAME approved shot IDs on the
   higher-tier model, passing the approved keyframe as composition reference
   (plus the same model-sheet views). Never re-stage, re-frame, or re-time
   shots at this step. Keep prior attempts. ControlNet/targeted editing comes
   later, only once those ComfyUI extensions are installed by the user.

No dialogue/narration: skip TTS. Music is optional and never presumed free.
Existing local rain/ambience may be reused in preparation without a charged call.
Legacy models require explicit opt-in and retain their own native dialects and
hardware limits, with the same budget/consent guards for any paid nodes.

If this skill is not registered in the live catalog, read this file directly;
do not call an unavailable skill name or claim automatic discovery/reloading.
