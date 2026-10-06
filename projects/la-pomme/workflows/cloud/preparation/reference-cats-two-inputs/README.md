# Two cats — separate two-reference scaffold, preparation only

User request relayed verbatim: **« go fait les 2 en meme temps »**. This authorizes
preparation of one batch with two exploratory cat illustrations, not upload,
priced paid-job approval, reservation, claim or submission. No media generated.

## Files and exact design

This is a **new project-owned design**, not a rewritten copy of the existing
one-reference graph. Declared IDs: `110` = own cat identity loader; `120` = adult
portrait graphic-style-only loader; `200` = `OpenRouterStudioImage`; `300` =
`SaveImage`, linked to image output 0. Two explicit direct links go to
`model.reference_images.reference_1` then `.reference_2`. Bindings are explicit;
batch preparation copies this graph and changes only configured existing
literal inputs/output prefix. No reference autogrow or loader insertion occurs.

`../reference-exploration/` was read only. Its scaffold SHA-256 is
`af274c52b12843f2b9ee8588a9d3e750f8830dc69128c7569445defe58a32642`.
Original sources, drafts, approved registry, story, budget and legacy workflows
were not edited. No invented scenes, shots, character IDs or canonical-stage completion.

## Actual live evidence and honest readiness

- First MCP `server_info`: running `http://127.0.0.1:8188`, ComfyUI `v0.38.2`,
  comfy-cli `1.22.0`, OpenRouter Studio `0.3.0`; core/Studio not outdated.
- MCP `nodes(get)` inspected **OpenRouterStudioImage, LoadImage and SaveImage**.
  The oversized image response was preserved by the tool, then parsed from its
  actual output. `OpenRouterStudioImage.selected.live.json` retains the complete
  selected branch, shared inputs and outputs; only the other models' dynamic
  branches/selection keys were removed. No selected fields were reconstructed.
  LoadImage/SaveImage were saved from subsequent fresh, read-only
  `comfy --json nodes show … --host 127.0.0.1 --port 8188` descriptor reads.
  `node-catalog.selected.live.json` combines these three actual descriptors.
- Timestamp of saved evidence: **2026-10-05 UTC**, as reported by the live tools;
  provenance/source digest and check time are in `offline-checks.json`.
- Both job plans pass `schemas/cloud-job.schema.yaml`. Exact model branch,
  literals, types, links, count, provider pin and reference order pass offline
  checks against this live catalog. The real `prepare_cloud_workflow` resolver
  corroborates typed approved references and then **correctly refuses missing
  live uploaded filename choices**. Descriptors were not relaxed/faked.
- Helper result: both jobs **`awaiting_upload`**, exit 2; no
  `prepared.api.json` yet. This is not live workflow validation or a generation
  test. Main session must live-validate every exact graph after upload/re-prepare.
- The unused `comfyui-openrouter` pack is outdated. If that different pack is
  needed later, update it first (`comfy node update comfyui-openrouter`) with
  appropriate authorization; no update/install was done or needed for this
  selected Studio branch.

## Model options scan — selected image stage only

One model: `bytedance-seed/seedream-5-0-flash`, tier `preparation`, route
`/api/v1/images`. No fallback, alternate-model call or runtime LLM rerouting.

| Live option / surrounding node | Effect | Recommended current value | Cost impact | Availability |
| --- | --- | --- | --- | --- |
| `model.prompt` | Six views on one sheet, identity ref 1/style ref 2 | Existing respective draft `prompt` | Included in image estimate; unrelated planning costs excluded | Selected live branch |
| `model.size` | Optional provider size string | Empty, no explicit width/height | No size upgrade planned | Live STRING; central profile does not approve arbitrary dimensions |
| `model.resolution` | Resolution | **1K**, not 2K | $0.018 per output per current Seed endpoint | Live 1K/2K |
| `model.aspect_ratio` | Landscape sheet | **16:9** | No extra published SKU here | Live; other ratios not enabled |
| `model.n` | Number of model outputs | **1** (six views within it) | One output charge per job | Live min=max=1 |
| `model.seed` | Optional determinism control | Preserve live default **-1**, no explicit job seed | No extra published SKU | Live INT -1..2147483647; central config has no seed capability, so explicit requests block |
| `model.reference_images` | Ordered image conditioning/editing | Exactly **2** direct slots | $0 per reference, **output remains paid** | Live autogrow maximum 14; scaffold fixes 2 existing slots |
| `model.provider_options_json` | Provider/fallback policy | `only:["seed"]`, `allow_fallbacks:false`, empty `options.seed` | Seed tariff only; failures may bill | Actual selected branch; no separate provider-route/sort controls |
| Shared `strict_validation` | Reject invalid requests | **true**, unchanged live default | Not a quality upgrade or paid approval | Available now |
| Shared raw artifacts / ref size / timeout / manifest / nonce | Audit and transport defaults | `true` / 16 MP / 600 s / empty / 0 | No extra generation requested; local storage/compute excluded | Available now, unchanged defaults |
| Enhancement/negative-prompt/mask/audio controls | Extra generation conditioning | **Absent on selected branch; do not add** | No additional call | Not mapped/supported here |
| `SaveImage` | Save one sheet PNG | One output node only | No additional hosted call | Actual live core descriptor |
| `MaskComposite`, `GrowMask`, `ImageCompositeMasked` | Local mask/compositing support | **Off**, no added nodes | Local compute not quoted; no hosted call planned | Found by live MCP mask search; not enabled/tested |
| `ColorTransfer`, `ImageColorSpace` | Local color matching/conversion | **Off**, avoid altering approved coat colours | No hosted call planned; local work excluded | Found by live MCP color search; not enabled/tested |
| `ImageUpscaleWithModel`, `UpscaleModelLoader`, `ImageScale` | Local enlargement | **Off**, retain native 1K | Model weights/compute unverified; no hosted call planned | Classes found live; weights not checked, no installation/download |
| `FrameInterpolate`, `FrameInterpolationModelLoader` | Video interpolation | **Off / N/A for still sheets** | No video/paid enhancement call | Classes found live; weights unverified |

Multi-reference editing is already supported by **this selected model**; no
Nano Banana/other model call is added. No masks, color transfer, enhancement,
upscale or interpolation were silently enabled. Class availability is not proof
that a processing path or weights have been generation-tested.

### Mapping audit

Prompt → `200.model.prompt`; resolution/aspect → `200.model.resolution` and
`200.model.aspect_ratio`. Seed is **preserved scaffold literal -1**, not an
injected parameter: the helper correctly reports `unmapped; scaffold literal
model.seed=-1 left unchanged`. Width, height, frames and fps are absent and not
requested, never derived from 1K or silently dropped. Audio input is absent,
audio is not generated. Images → `110.image`/reference_1 and
`120.image`/reference_2, always ordered. Unsupported requested parameters or a
different reference count block; they do not trigger topology edits.

## Batch quote — NOT APPROVED

`references/drafts/cats-reference-exploration.batch.yaml` has scope
`scene_ids: []`, `entity_ids: [char_002, char_003, char_001]`. Both jobs are
typed character `reference_illustration`, `reference_scope: exploratory`.

| Job / prompt | Ref 1: identity | Ref 2: style only | Planned attempts | Estimate | Proposed ceiling |
| --- | --- | --- | --- | --- | --- |
| `char-002-turnaround` / `ref_char_002_turnaround_01` | `references/source-crops/cats/char_002-source-conditioning.png` | `art-direction/Homme fatigué dans un appartement nocturne.png` | 1 | $0.018 | $0.02, unapproved |
| `char-003-turnaround` / `ref_char_003_turnaround_01` | `references/source-crops/cats/char_003-source-crop.png` | Same approved adult portrait, never depict the human | 1 | $0.018 | $0.02, unapproved |

**Total: $0.036 estimated; proposed batch ceiling $0.04, not approved.** Two
outputs, not twelve calls. Both plans use attempt 1 from the real ledger series.
References are corroborated against approved registry entries/views and their
hashes. Tariff evidence: root `config/cloud-tiers.yaml` and project
`references/technical-pricing.json`, checked 2026-10-05, 30-day maximum age.
Use its published Seed endpoint pricing records, not the historical single-image
quote's counts/accounting snapshot. Reference input charge is $0; output is
$0.018 each. Actual costs **null/unknown**, no reserve/claim/paid consent. Taxes,
external source costs, runtime LLM, local work/compute and optional music are
excluded. No automatic retries; failures can bill and extra attempts need consent.
The helper's `$0 prepared jobs` summary means no job cleared the upload gate,
**not** zero expected or actual media cost for this pending batch.

## Main-session continuation (not executed here)

From repository root, exact offline preparation command, also used here:

```sh
PYTHONPATH=src python3 scripts/cloud_batch.py prepare --project projects/la-pomme --batch projects/la-pomme/references/drafts/cats-reference-exploration.batch.yaml
```

Batch directory:
`projects/la-pomme/workflows/cloud/preparation/batches/cats-reference-exploration`.
Only after explicit upload authorization, main may upload these **staged,
content-addressed** paths (`overwrite=true`); identical style bytes are shared:

```text
/Users/mbensass/projetPreso/ai-film-director/projects/la-pomme/workflows/cloud/preparation/batches/cats-reference-exploration/uploads/la_pomme_cats_refexplore_char_002_5245c6f54dcd1bc2.png
/Users/mbensass/projetPreso/ai-film-director/projects/la-pomme/workflows/cloud/preparation/batches/cats-reference-exploration/uploads/la_pomme_cats_refexplore_char_003_9bf67e5fb35316a5.png
/Users/mbensass/projetPreso/ai-film-director/projects/la-pomme/workflows/cloud/preparation/batches/cats-reference-exploration/uploads/la_pomme_cats_refexplore_char_001_7e85faaddab814f5.png
```

Then save actual fresh MCP `nodes(get, LoadImage)` descriptor to
`<batch>/live-descriptors/LoadImage.json`, and run the **same prepare command**.
Live-validate the resulting `<batch>/char-002-turnaround/prepared.api.json` and
`<batch>/char-003-turnaround/prepared.api.json`; save reports per job. Require
`valid: true`, `partner_nodes: []`, `spends_credits: false` for each exact graph.
Those flags address Comfy credits only; Studio still spends OpenRouter money.
Anything blocked stays blocked, no patch-around or descriptor relaxation.

After current budget review/accounting and one **new priced batch agreement**
covering both exact jobs/attempts/parameters/references and ceilings, main may
use helper `approve` to bind hashes and reserve/claim. Only main then submits
`run_workflow(wait=false, confirm_spend=false)` → `job(action="wait")` →
`fetch_outputs` → helper `record` → `status`. Not authorized by the earlier
creative request. Review outputs before approving appearance/views or registering
new sheets. Generation-tested remains false until actual evidenced execution.

## Root `workflows/**/*.json` read-only live validation

All six matching root workflow JSON files were validated with MCP, no changes:
`qwen3-tts`, `qwen-image`, `krea2`, `minimax-h3` are placeholder/non-node graphs
with `prompt_no_outputs` (all invalid). `Flux2_Klein.json`: five errors — sampler
`res_2s`, missing requested VAE/CLIP/LoRA choices, and unknown
`DiffusionModelLoaderKJ`; unreachable LoRA warning. `ltx-2.5.json`: seventeen
errors — missing requested models, sampler, KJ/Director/helper classes and
`VHS_VideoCombine`. All report no Comfy partner nodes/credit spending, which
does not make them runnable. These legacy routes are unused, explicit opt-in
only, and were not repaired, substituted, installed or generated.
