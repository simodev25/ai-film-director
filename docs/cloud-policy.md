# Film cloud policy: three gammes

This is the common guard for every film agent, skill, and command. Read it from
the **repository root**, together with `config/cloud-tiers.yaml`, before planning,
writing prompts, choosing a model, preparing workflows, or submitting jobs.
The config is the source of truth for `version`, `pricing_checked_at`, `currency`,
`default_tier`, and each tier's `text`, `image`, `video`, and `audio` entries
(`model`, `pricing`, capability caps in `capabilities`, and applicable `defaults`).
If the file is absent or invalid, stop tier resolution
and report the blocker; never substitute a remembered default.

## Selection, not permission

The three gammes are `preparation`, `tests`, and `production`. `preparation` is
the default **planning** tier, not permission to spend. Only an explicit user
selection can promote work to `tests` or `production`. Use **one selected model
per stage/tier**, not every tier or all legacy models. A comparison estimate is
not a request to generate three sets of assets. Do not silently fall back,
swap providers/models, upgrade resolution, or change tier after an error.

Reference profile below is a readable summary; resolve actual IDs, prices, and
capabilities from the current config, not from this table:

| Gamme | Text recommendation | Image | Video (without audio) | Audio |
| --- | --- | --- | --- | --- |
| preparation | `openai/gpt-6-luna` | `bytedance-seed/seedream-5-0-flash` | `google/veo-3.1-lite` | `bytedance-seed/seed-audio-1-0` |
| tests | `google/gemini-3.8-flash` | `google/gemini-3.1-flash-image` | `alibaba/wan-3.0` | `bytedance-seed/seed-audio-1-0` |
| production | `openai/gpt-6.1-sol` | `google/gemini-3-pro-image` | `google/veo-3.1` | `bytedance-seed/seed-audio-1-0` |

Reference USD prices/caps (not a freshness guarantee):

- Text input/output per million tokens: preparation $0.10/$0.50; tests
  $0.75/$3.75; production $2/$10. GPT Luna/Sol use standard-context rates;
  expose long-context/at-or-above-272k-token pricing uncertainty rather than applying
  the standard rate blindly. Disclose excluded/unknown reasoning-token costs.
  The current budget-assumptions schema supports input counts below 272,000;
  larger contexts require a separately reviewed quote, not a fabricated estimate.
- Preparation images: $0.018 per 1K/2K image, up to 14 reference images, no
  additional reference-image charge in this profile. The **output is not free**.
- Tests images: 1K, estimated $0.0672 output + $0.00056 per reference image,
  up to 14 references. Production: 2K, estimated $0.1344 output + $0.00112 per
  reference image, up to 14 references. Token-derived image estimates are not
  guaranteed flat tariffs.
- Preparation video: 720p, $0.03/second, 4/6/8-second clips. Tests: Wan 3.0
  720p, $0.10/second, integer 2–30-second clips, first frame only (no last
  frame, no negative-prompt input). Production: 1080p, $0.20/second,
  4/6/8-second clips. All three estimates assume **no generated video audio**.
  Until 2026-10-05 the tests video model was `kwaivgi/kling-v3.0-pro`
  ($0.112/second, 3–15 s); it was replaced by an explicit user choice
  (« WAN 3.0 en 720p »), not by an automatic fallback.
- Seed Audio: $0.0025/second in all three tiers. No dialogue/narration means no
  TTS job. Music is optional; never assume Lyria or any hosted music is free.
  Preparation may reuse an existing local rain/ambience recording without a
  charged generation call; disclose its provenance and any other local costs.

The OpenRouter text IDs above are recommendations, **not automatic OpenCode
runtime routing**. A raw OpenRouter media/model ID is not an OpenCode
`provider/model` reference. Do not insert these raw IDs into agent/command
`model` frontmatter. Agents without an override inherit their actual runtime
model; do not claim that selecting a gamme changed it. If the user requests a
specific runtime LLM, discover available models with the OpenCode models tool,
resolve the exact available provider/model reference, and obtain/retain the
user's exact selection before passing a subagent model parameter. Report a
missing model; do not quietly replace it. Do not edit `opencode.json` to make
the planning recommendation appear active.

## Story → budget estimate → screenplay gate

The canonical pipeline remains:

`story → budget estimate → user review/decision → screenplay → characters →
character sheets → locations → props → storyboard → shots → image prompts →
image generation → video prompts → video generation → audio prompts →
audio generation → continuity → final edit`.

1. Establish `story/story.yaml` and a positive film duration. Run the project
   CLI's `film-director budget PROJECT --assumptions FILE` to create
   `budget/estimate.yaml` and `budget/estimate.md`; the assumptions argument is
   optional if duration can be resolved from `project.yaml`'s `duration_seconds`
   or `story.format.target_duration_seconds`.
   Validate with `schemas/budget-estimate.schema.yaml`. If the CLI/schema is not
   available, report that fact instead of inventing a successful estimate.
2. Show preliminary **low / mean / high** costs for **all three tiers**, using
   the **same assumptions**: duration, provisional shot count/clip lengths,
   illustration/reference-image counts, text tokens, dialogue seconds, optional
   music, and retry assumptions. Before shots exist these are planning counts,
   not new shot IDs. Explain uncertainty, excluded costs, reference charges,
   reasoning-token assumptions, and the age/source of the tariffs. Read-only
   tariff refreshes are allowed; generation calls are not price checks. Use
   `schemas/budget-assumptions.schema.yaml` for the CLI input. Its `images`
   count includes shot images and separately explained reference illustrations;
   keep their breakdown in the user report rather than adding unsupported input
   fields. For a silent/no-new-audio film, explicitly set `audio_seconds: 0`
   instead of accepting a conservative duration-based audio default. Optional
   music is excluded from the current estimator; quote it separately if requested.
3. Ask the user to review the estimate and select a tier and budget ceiling.
   `budget/decision.yaml` must contain `estimate_sha256`, `selected_tier`,
   `max_spend_usd`, nonempty `consent_reference`, `approved: true`, and
   `scope: planning_only_not_spend_consent`, matching
   the current estimate and requested tier. Record an affirmative decision
   **only from an actual explicit user response**. Never generate approved
   consent from a default, tool permission, or inferred preference. Validate the
   decision against `schemas/budget-decision.schema.yaml`; use the SHA-256 of the
   saved `budget/estimate.yaml` bytes, not a hash of the Markdown or parsed object.
4. Before creating or advancing the screenplay stage, require a valid estimate
   and a matching explicit user-review decision. Editing the assumptions,
   estimate, selected tier, or ceiling invalidates the old acknowledgement;
   request renewed review. Budget acknowledgement authorizes the **planning
   scope**, not paid generation. Each paid job needs additional explicit
   generation consent covering its model, parameters, attempts, estimated cost,
   and budget ceiling. A `/film`, `/images`, or other command alone is not that
   consent.
5. For an existing screenplay/project, add a retrospective estimate/review and
   mark missing budget evidence before advancing. Do not delete, rewrite, or
   invalidate existing canonical story/screenplay/media solely because the
   budget artifacts did not exist. Re-estimate as downstream detail improves;
   do not regenerate assets automatically.

The `budget-estimation` and `cloud-production` skills and `budget-agent` define
these tasks. If newly added definitions are not in the live session's catalog,
read their repository files directly; use an available general agent only when
delegation is authorized. Never invoke an undiscovered skill/agent or claim a
reload has happened.

## Canonical artifacts and continuity

- Keep the existing YAML artifacts, schemas, stable IDs, and pipeline mappings.
  Every scene maps to shots; every shot maps to its image prompt; every shot
  requiring motion maps to a video prompt; every dialogue/audio event maps to
  its audio plan/prompt. A prompt and the resulting media are separate artifacts.
- Keep `prompts/images/<model-folder>/shot_{number}.yaml` and
  `prompts/videos/<model-folder>/shot_{number}.yaml`. Use the project's safe
  model-folder convention (raw IDs can contain `/`); store the **actual resolved
  model ID** in schema-declared model/route metadata, not a misleading legacy
  label. Preserve `prompt_id`, `shot_id`, and source links across attempts.
- Preserve identity, appearance, wardrobe, voice, location spatial anchors,
  lighting, chronology, prop ownership/state, screen direction, and eyelines.
  Ordered image references must resolve to existing canonical assets and stable
  character/location/prop IDs. Never invent reference labels or claim an asset
  was generated when only a prompt or workflow was prepared.
- Character/location/prop reference illustrations are separate approved assets,
  not extra shot renders. Link them to their canonical entity IDs and account
  for their cost/count separately; final shot images still map to shot IDs.
- Validate using the current schemas. Use only schema-declared cloud fields;
  if a required cloud model/metadata is unsupported, report that incompatibility
  rather than disguising Nano Banana/Gemini/Seedream as Qwen, FLUX, or Krea.

## ComfyUI-only generation and honest readiness

Native OpenRouter media calls must run through the **project's ComfyUI cloud
adapter** and configured workflow mappings. No direct Python `requests`, curl,
SDK, or other bypass to an OpenRouter generation endpoint. Inspect the actual
adapter/CLI capabilities before naming an execution entry point; a policy or
loaded plugin alone does not implement a missing route.

Current implementation boundary: `src/comfyui/cloud_adapters.py` prepares a
separate graph and provides `authorize_cloud_job` as an offline audit gate; it
has **no network/submission capability**. Use its actual binding API and
`schemas/cloud-job.schema.yaml` with the live node descriptors, then validate
the exact prepared graph on the intended ComfyUI. An authorized `GatedRun` is an
audit record, not a submit token or executable workflow. Actual submission,
when separately requested/approved, is caller-owned via `comfy-mcp`; reserve and
account for the approved spend in the project ledger before that call. Missing
bindings, transport, or budget accounting must be surfaced, not assumed implemented.
The generation approval must bind tier/model/route, the prepared workflow and
plan hashes, the reviewed estimate hash, a positive per-job ceiling, and an
explicit consent reference, with `scope: paid_generation_job`. A planning-only `budget/decision.yaml` is not this
approval. Require route-specific current pricing (within the configured age
limit, currently 30 days); unknown pricing blocks spending.

Before any job, confirm the running target, available node classes, exact model
resolution, parameters, reference order, workflow validation, budget ceiling,
and job-specific consent. User authentication/provider/plugin checks demonstrate
readiness only: **loaded/authenticated is not generation-tested**. OpenRouter
plugin nodes can be paid even when `is_api_node: false`; classify known
OpenRouter/partner classes by their real provider behavior, not that flag alone.
Treat all hosted media in this profile as paid. No test generation, installation,
download, or paid call merely to validate the refactor or inspect pricing.

Preserve user-supplied workflow JSON and topology. Prepare a separate copy
through project adapters/slots; change only supported configured inputs and
never guess node IDs. Do not silently rewire a workflow, mutate the user's JSON,
or insert credentials into a workflow, prompt, config artifact, or log. An
unavailable adapter, missing node, or unresolved mapping is a blocker, not
permission to install software or use a direct endpoint.

For each prepared/submitted attempt, keep an auditable record in the project's
supported metadata/manifest: tier, exact model resolution, stage, prompt/shot or
entity ID, ordered reference assets, parameters, attempt number, estimated cost,
consent reference, job/output status, and actual cost when reported. Unknown
actual cost remains **unknown/null**, never zero. Failed attempts may still be
billable; include them in budget accounting and ask before extra attempts.
Keep keys, headers, and secrets out of logs. Preserve prior assets and attempt
history; never overwrite a successful render to hide a retry or model swap.

## Legacy explicit opt-in

Existing Krea 2, FLUX.2 Klein, Qwen Image, LTX-2.5, MiniMax H3, and Qwen3-TTS
dialects/workflows remain supported **only when the user explicitly chooses the
legacy route/model**. They are not the default three-tier route, benchmarks to
run automatically, or silent cloud fallbacks. Preserve their native prompt
rules, constraints, and adapters after opt-in; do not relabel a cloud model with
a legacy name. Legacy does not mean free: inspect hosted nodes and retain
consent/cost guards. Local hardware limits and any applicable ComfyUI safety
instructions still apply; choosing a legacy prompt dialect is not permission
to run diffusion or video on unsuitable hardware.
