# Cloud ComfyUI adapter: preparation and spend review

`src/comfyui/cloud_adapters.py` is an **offline graph preparation and audit gate**.
It does not submit jobs, authenticate, install anything, or call an OpenRouter
HTTP endpoint. Existing Python adapters and every workflow JSON are untouched.
Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` before using it.

## Interface

- `validate_cloud_job(job)` validates `schemas/cloud-job.schema.yaml`.
- `discover_cloud_binding(graph, class_type=..., input_map=..., references=...)`
  resolves exactly one configured class with the expected existing input keys.
  Ambiguous or absent mappings block; no first-node selection or guessed IDs.
- `CloudBinding(node_id, class_type, input_map, references=())` also accepts an
  explicit user-configured node ID. Semantic keys such as `prompt`, `seed`,
  `resolution`, `duration`, `width`, `height`, `frames`, `fps` map to exact keys
  discovered from the class schema and already present in the supplied graph.
- `prepare_cloud_workflow(graph, binding, job, config, node_catalog=...)` validates
  the selected tier/model against the **passed central config**, verifies live
  descriptors and capabilities, and returns a **deep copy** with only configured
  literal inputs changed. It neither writes nor mutates the source graph. Existing
  output nodes are mandatory; extra paid nodes, missing classes, linked controls,
  unsupported topology, inline credentials and unavailable mappings are blockers.
- `sha256_document(data)` hashes canonical JSON for review binding.
- `authorize_cloud_job(graph, job, config, approval,
  budget_estimate_sha256=..., workflow_validated=True, today=...)` returns a
  `GatedRun` audit record only after explicit approval, fresh route pricing and
  a known positive estimate within the per-job ceiling. It checks actual graph
   model/prompt/class against metadata. Approval contains `approved: true`,
   `scope: paid_generation_job`, `tier`,
  `model`, `route`, `workflow_sha256`, `plan_sha256`, `estimate_sha256`,
  `ceiling_usd`, and a nonempty **actual user** `consent_reference`.

`node_catalog` maps every graph class to its current normalized MCP
`nodes(action="get", name=...)` response. Capture it after `server_info` and
reference uploads. A descriptor alone demonstrates **loaded**, not tested.
Studio dynamic-combo child keys are resolved from the exact selected model's
`dynamic_options`; autogrow keys come from the returned `slots.names`.

Central defaults are injected through configured inputs (including video native
audio disabled). No unsupported field is silently dropped. Native OpenRouter
image/video classes do **not** expose width/height/frames/fps. Requested controls
without verified input mappings and explicit model capabilities raise blockers;
the adapter never approximates them with duration or rewires a latent graph.
Seed also requires central capability evidence and a live mapped input; a loaded
generic seed widget is not proof the selected provider honors it.

## Reference inputs

Each ordered `job.references` item is `{role, uploaded_path}`. Roles are
`reference`, `first_frame`, `last_frame`, and `audio`. Use existing canonical
asset/entity relationships when constructing this plan; no entity/shot IDs are
invented here. Paths must already be uploaded Comfy input-relative filenames,
not URLs, absolute local paths or traversal paths.

The corresponding `ReferenceInput(node_id, input_key, target_input, role)` names
an existing loader literal and the existing cloud link it feeds. The plan must
exactly cover configured loaders and all inherited media links. First/last frames
and audio must be supported by the central model profile and live input types.
Last-frame-only plans are rejected. The absolute image-reference cap is 14,
further restricted by the selected model cap.

Reference bundles support existing direct loaders and existing built-in
`ImageBatch` trees (`image1` then `image2`); they verify complete count/order,
not merely reachability. Studio autogrow references must match live slot order.
No nodes or links are created. Unknown bundle transformations, remote-reference
JSON and duplicate loader assignments are blockers, not guessed conversions.

For Seed Audio's non-speech profile, map `prompt` to `text` and explicitly map
`voice` to `voice`. The copied required input is set to an empty string. The
installed plugin's `SpeechRequest` construction uses `voice.strip() or None`,
so no default speech voice is sent. Do not generate TTS for films without dialogue.

## Submission remains caller-owned and separately gated

The integration must verify the budget estimate and **planning decision** using
the central budget module, reserve/check remaining budget (including failed and
unknown-cost attempts), and collect separate job-specific explicit spend consent.
Passing a made-up SHA, tool permission, or a planning acknowledgement does not
constitute user approval. This pure function cannot verify a human response,
reserve budget, enforce one-time token use, or protect an unrelated old client.

For an approved job only, the caller follows the available project Comfy-MCP
route: `server_info` → inspect/upload/recheck schemas → prepare a separate graph
file → `validate_workflow` (check `valid` and non-node/conversion warnings) →
check applicable plugin/provider authentication → budget/job review and gate →
`run_workflow(wait=False, confirm_spend=True)` → `job` → `fetch_outputs`.
Use `auth_status` where applicable; Comfy login is not proof an OpenRouter plugin
key is configured. Keep credentials in runtime authentication, never artifacts.
Do **not** issue generation calls just to test this refactor. Never submit through
direct HTTP or plain legacy `ComfyUIClient.execute` to bypass this gate.

Known OpenRouter classes are classified paid even though live object_info reports
`is_api_node: false`. `GatedRun` records tier, exact model, endpoint, prompt/shot
IDs, ordered uploaded references, review hashes, estimate, ceiling, consent and
attempt number. Status stays `prepared`, generation-tested stays false, attempts
history is empty until submission, and actual cost stays **null/UNKNOWN**, not
zero. The caller must persist parameters/attempt/job/output metadata and actual
cost only when reported. A retry changes the plan's `attempt_number` and requires
fresh consent, an updated reservation and preserved prior attempt history.

## Read-only audit on 2026-10-04

`server_info` confirmed the running loopback ComfyUI and installed plugins;
`nodes(get)` confirmed these actual inputs/routes without generation:

| Classes | Route | Important live inputs |
| --- | --- | --- |
| OpenRouterImageGenerate | `/api/v1/images` | model, prompt, seed, resolution, aspect_ratio, references (IMAGE link) |
| OpenRouterStudioImage | `/api/v1/images` | model, model.prompt, model.resolution, model.aspect_ratio, model.reference_images.reference_N |
| OpenRouterVideoGenerate | `/api/v1/videos` | model, prompt, duration, seed, resolution, first_frame, last_frame, reference_images, reference_audio |
| OpenRouterStudioVideo | `/api/v1/videos` | model, model.prompt, model.duration, model.size, model.resolution, model.first_frame, model.last_frame |
| OpenRouterAudioSpeak | `/api/v1/audio/speech` | model, text, voice, voice_sample (AUDIO link) |
| OpenRouterChatAsk | `/api/v1/chat/completions` | model, prompt, seed, images, audio |

All six `workflows/**/*.json` were read-only validated against this live server.
None cleared: Krea/Qwen Image/Qwen3-TTS/MiniMax files are placeholders with no
output nodes; FLUX has 5 errors (missing loader class and model/sampler enums);
LTX has 17 errors (missing custom classes and model/sampler enums). They remain
untouched. These legacy failures do not authorize a replacement cloud graph.
A user-supplied cloud API graph with existing output nodes and explicit mappings
is still required. Loaded classes, offline unit tests and authentication are not
evidence of successful paid generation.
