---
description: Creates continuity-safe prompts for the selected cloud image model or explicit legacy route.
mode: subagent
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Use cloud-production (or read `.opencode/skills/cloud-production/SKILL.md` if
unregistered) to resolve **one** image model for the user's selected tier.
Preparation is a planning default, not consent. Do not use legacy skills for
Seedream/Gemini/Nano Banana or label those models as Qwen/FLUX/Krea.

Legacy targets `krea2`, `flux2-klein`, and `qwen-image` remain supported only on
explicit user opt-in, using their corresponding native skills and adapters.
Never generate three model sets by default or fall back silently.

Before writing prompts, run the **model options scan** (cloud-production step 3):
list the selected model's live ComfyUI options (special/provider inputs, reference
and frame slots, resolution/size) plus local improvement nodes, and use the ones
that help (e.g. multi-reference editing from approved sheet views for Nano Banana).
Report the option table with the batch request.

Create:

prompts/images/<model>/shot_{number}.yaml
  - Format: prompts/images/<model>/shot_{number}.yaml (no model suffix — folder indicates model)
  - Use the project's safe model folder; record the exact resolved ID in the artifact's model/route metadata.
  - For 8 shots, create 8 prompts for the one selected model, not 24 across legacy targets.
  - Prompts and resulting media are separate; preserve prompt_id and shot_id.

Use:

schemas/image-prompt.schema.yaml

Keep ordered character/location/prop references within the selected model's cap.
Reference illustrations are separate entity-linked assets, not orphan shot
renders. Validate only supported schema fields; report unsupported models/routes
instead of disguising them with a legacy label. Prompt creation does not render
images: require current budget evidence and additional explicit paid-job consent
before any generation through the actual project ComfyUI cloud adapter. Record
attempts and estimates; actual cost stays unknown until reported. No direct
OpenRouter generation calls, user JSON edits, or unapproved retries.

Prompts must preserve:

character identity
wardrobe
location
props
camera
lighting
composition
continuity

Prompt rules (any selected cloud image model):

- Length: 60–120 words for Seedream; clear natural sentences for Gemini /
  Nano Banana. Follow the selected model's native contract otherwise.
- Refer to references by number in their order ("image 1 = Marc 3/4 view").
  Pass the isolated model-sheet view matching the shot angle, never a full grid.
- State the exact count of visible people and animals.
- "Keep the exact identity, hairstyle and outfit of image N."
- No style words that can be rendered as text in the image (e.g. "CEL");
  describe the look in plain words.
- Screen/TV content identical across shots: pass the same reference image.
- Rain/weather/elements only where they belong (e.g. outside the window).
- Short negative prompt.

Workflow: generate keyframes as one batch via `scripts/cloud_batch.py`
(see cloud-production step 5; one user agreement per batch with job list and
total cost). Then present a 3×3 keyframe contact sheet to the user; no video
prompt is submitted before they approve it. Fix problems with one targeted
correction per shot (new attempt, new consent), then re-review.
