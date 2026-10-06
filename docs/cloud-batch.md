# Cloud batch helper (`scripts/cloud_batch.py`)

Offline tool for Seedream images (`OpenRouterStudioImage`) and Veo videos (`OpenRouterStudioVideo`); it never submits, generates, or calls the network. Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` first. Run with `PYTHONPATH=src python3 scripts/cloud_batch.py …`.

1. `prepare --project P --batch BATCH.yaml [--out DIR]` — per job (`job_id`, `modality`, `shot_id` or `job_kind: reference_illustration` + `entity_type/entity_id/scene_id`, optional `segment_id`, `prompt_file`, `prompt_key` (dotted, e.g. `clips.0.prompt`), `negative_key`, `parameters`, ordered `references` [`asset`, `role`, `entity_id`]) writes `plan.json` (attempt = next in ledger), `source.api.json`, `bindings.json` (prompt/seed/width/height/frames/fps/image/audio mapping report) and `prepared.api.json` via `prepare_cloud_workflow`. Batch keys: `version: 1`, `name`, `tier`, `scope` {scene_ids, entity_ids}, optional `templates`, `node_catalogs`, `upload_prefix`. Default output: `P/workflows/cloud/<tier>/batches/<name>/`.
2. Templates are the validated scaffolds (image `scene-01-shots/shot_la_pomme_01_03` + its `bindings.json`; video `scene-01-video/scaffold[-first-only].api.json` + `route-evidence.json`); user JSON is only read. Unsupported topology/parameters (seed, width, frames, fps, audio, model/tier mismatch) are reported as `blocked`. Model-specific scaffolds (`MODEL_DEFAULTS`): `google/gemini-3.1-flash-image` → `workflows/cloud/tests/scene-01-shots/scaffold-gemini-3.1-flash-image.*` + full live image catalog (1..14 ordered references); `alibaba/wan-3.0` → `workflows/cloud/tests/scene-01-video/scaffold-first-only.wan-3.0.api.json` (first frame only; first+last is blocked). Every template's paid-node `model.*` inputs must exactly match the model's live branch (`check_branch`), otherwise the job is blocked. Video negatives go to the model's live negative input (`special__negativePrompt` / `special__negative_prompt`); a model without one (Wan 3.0) is blocked unless the batch/job sets `negative_fold: true` (folded into the prompt, recorded as `folded_into_prompt`). Native video audio without a configured `audio_per_second` price is blocked.
3. References are staged in `uploads/` under deterministic sha256 names: `upload_file(paths, overwrite=true)`, then save `nodes(action='get', name='LoadImage')` to `<batch>/live-descriptors/LoadImage.json` and rerun `prepare` (jobs show `awaiting_upload` until the names appear in live choices). Shortcut: `uploads-refresh --batch-dir D --descriptor NODES_GET.json [--choices-from UPLOAD_RESULT.json]` writes `live-descriptors/LoadImage.json` (envelope or bare descriptor accepted; without `--descriptor` the saved one is reused) and adds **only this batch's own content-addressed upload names** that the upload evidence names; it refuses changed staged files, writes `uploads-refresh.json` (added / already live / still missing) and exits 2 while any batch upload is still missing. Live `validate_workflow` stays the authority. The video catalog must be saved from `nodes(get)` to `node_catalogs.video` (default `scene-01-video/node-catalog.selected.live.json`).
4. For each prepared job, run `validate_workflow(prepared.api.json)` and save the result as `<job>/validation.json` (must be `valid: true`, `partner_nodes: []`, `spends_credits: false`). Shortcut: save all reports in one JSON (`{job_id: report}` or `{"jobs":[{"job_id","validation","workflow_path"?}]}`) and run `validations --batch-dir D --from RESULTS.json`: it writes each report verbatim, only for `prepared` jobs whose `prepared.api.json` is unchanged and not yet approved (a `workflow_path` must be that file), and exits 2 if any report is not clean or a prepared job has no result.
5. `approve --batch-dir D --consent-verbatim "<user answer>" --question "<question asked>" --ceiling-per-job X [--batch-ceiling Y] [--session ses_…] [--jobs a,b]` — only after a real user answer. Writes `approval.json` per job (unique consent reference, plan/workflow/estimate/decision/scope hashes), then `CloudLedger.reserve` + `claim`, writes `claims.json`, and prints the `run_workflow(…, wait=false, confirm_spend=false)` calls plus the `results.json` template. Refuses on tier/decision mismatch, stale files, unclean validation, or exceeded ceilings.
6. `record --batch-dir D --results results.json` — `{"jobs":[{"job_id","prompt_id","status":"completed|failed|ambiguous","outputs":[…]}]}`; reads actual cost read-only from the OpenRouter Studio `jobs.sqlite3` (prompt sha256 + model + media type + created after claim, `--studio-db` to override); an unmatched or zero cost stays UNKNOWN (null), and `<job>/outcome.json` keeps the evidence.
7. `status --project P` — known actual spend, unresolved holds, committed, available budget, in-flight and unknown-cost jobs.
# Standalone exploratory reference illustrations (technical adaptation)

Before scene planning, a batch may explicitly prepare **noncanonical exploratory
reference art**. This is not a screenplay, scene, shot, character sheet, or
production-stage completion. The canonical pipeline and budget-review gate are
unchanged. Technical adaptation consent never authorizes `approve`, ledger
reservation/claim, uploads, or generation.

Use `job_kind: reference_illustration`, `modality: image`, and
`reference_scope: exploratory` on each exploratory job. Its batch scope must
have `scene_ids: []` and unique, nonempty `entity_ids`. No `scene_id`, `shot_id`,
or `segment_id` is allowed. An omitted scope (or `reference_scope: scene`)
retains the existing strict scene-linked reference contract, requiring a
canonical entity present in that scene's shots. Shot renders stay strict.

Example **configuration only**, not spend consent:

```yaml
scope: {scene_ids: [], entity_ids: [char_001]}
templates:
  image:
    graph: workflows/cloud/exploratory/scaffold.api.json
    bindings: workflows/cloud/exploratory/bindings.json
node_catalogs: {image: workflows/cloud/exploratory/node-catalog.selected.live.json}
jobs:
  - job_id: adult-reference
    modality: image
    job_kind: reference_illustration
    reference_scope: exploratory
    entity_type: character
    entity_id: char_001
    prompt_file: prompts/exploratory/adult.yaml
    references:
      - entity_id: char_001
        entity_type: character
        asset: art-direction/existing-approved-source.png
```

The typed target comes from an existing canonical category registry, if present.
Only an **absent** category may resolve via
`references/approved-references.yaml`, corroborated by the corresponding typed
story declaration (`characters`, optional `locations`, optional `props`).
Caller scope/IDs never create entities. Existing empty or malformed canonical
registries cannot be bypassed. Approved entries must belong to this project,
carry approval evidence, and resolve to existing contained paths with matching
SHA-256 (including views). Repeated appearances of one entity are allowed when
typed identity and ordered assets remain unambiguous; cross-type collisions,
duplicate order numbers, stale files, traversal and symlink escapes block.
Every exploratory conditioning reference specifies its approved typed entity
and asset; arbitrary caller assets are not accepted.

`exploratory_target_evidence(job, project, scope)` is the adapter's read-only
resolver. Batch preparation stores its `target_evidence_sha256` in the plan;
direct adapter callers must also obtain and bind this evidence. The digest
covers source bytes, canonical-registry presence/absence, approved assets,
scope and ordered references. Preparation and authorization re-resolve it;
paid approval binds it, and ledger reservation/claim rechecks it. Changes
require re-preparation and renewed paid consent, never automatic approval.
Exploratory attempts use the same reference-art accounting/attempt series as
entity illustrations (no reset by scope); audit records explicitly carry
`reference_scope: exploratory`, `scene_id: null`, and
`canonical_stage_completion: false`. Unknown actual cost remains null.

## Configured topology, not loader expansion

All batch image templates now require the exact number of **existing wired
reference slots**. The helper never deletes/adds loaders, derives node IDs,
invents autogrow links or rewrites topology. Configure `binding.references` as
ordered `{node_id, input_key, target_input, role}` objects alongside the existing
`declared_node_ids` and `binding.input_map`. Old direct-loader declarations are
accepted only when each declared loader has one unambiguous existing direct
link. Bundles require explicit bindings and the adapter's supported `ImageBatch`
ordering. Too few/many slots or unsupported mappings block; supply a separately
created, evidenced scaffold rather than patching around the blocker. No
helper-managed topology-rewrite mode is provided.

Source JSON/PNG bytes remain untouched. Prepared copies change only configured
literal model/prompt/parameter/loader inputs, and the verified output prefix
(plus a configured negative-prompt literal when present). Prompt, seed, width,
height, frames, fps, image/audio conditioning are audited; unsupported requested
parameters are blockers, not silently dropped. Save live descriptors before
preparation, upload only after separate authorization, re-prepare with the live
`LoadImage` descriptor and live-validate **each** exact graph. The required
`valid: true`, `partner_nodes: []`, `spends_credits: false` is Comfy-credit
validation only: OpenRouter images remain paid. `approve` still requires the
current estimate/decision, explicit paid-batch agreement, positive per-job
ceiling and evidenced opening liabilities. Main-session submission remains the
only caller-owned transport. Loaded/authenticated is not generation-tested.
