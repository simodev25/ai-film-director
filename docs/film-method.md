# Film method: prototype cheap, validate, then upgrade the same shots

Lessons from *La Pomme*, scene 01 (2026-10-05). This method orders the creative
work; it does **not** relax `docs/cloud-policy.md` or `config/cloud-tiers.yaml`.
Budget review before screenplay, one selected model per stage, no silent
fallback/upgrade, explicit consent before paid jobs, unknown cost ≠ 0, and
legacy-only-on-opt-in all still apply. It refines the policy's canonical
pipeline by inserting the stages in **bold**.

## Pipeline

story → budget estimate + user review → screenplay → characters / locations /
props → **art direction** → **reference model sheets** → storyboard →
**short shots** → image prompts → keyframes → **keyframe contact sheet approved
by the user** → video prompts → one video per shot → **finishing (look) +
sound design** → edit → optional **tier upgrade pass**.

## Philosophy

1. Prototype in `preparation` (cheap): validate découpage, rhythm, framing and
   sound on the whole scene before spending on quality.
2. Only once the user approves the cut, re-run the **same validated shots** in
   `tests`/`production`, passing each approved keyframe as the composition
   reference. The upgrade pass improves rendering; it never re-stages the scene.
3. Every tier change is an explicit user choice with its own estimate/consent.

## Stage notes

- **Art direction** (`art-direction` skill): per scene and per shot — the
  emotion the viewer should feel, visual references *given by the user* (films,
  anime; never invented), justified camera language (why tight/wide/held/cut),
  palette and light, rhythm, and sound intent from the start.
- **Reference model sheets** (`model-sheets` skill): turnarounds, expression
  sheets, per-outfit sheets; animals with lying/sitting poses; locations as
  3–4-angle sheets plus a top-down floor plan; props as multi-angle + state
  sheets. ≈ 1 image per sheet with the tier's image model, user-approved,
  recorded in `references/approved-references.yaml`. Keep the full sheet **and**
  crop each view to its own file; feed models the isolated view matching the
  shot angle (a whole grid makes models copy the grid).
- **Short shots** (`shot-design`): 4–8 s (or the model's caps), one action, one
  simple camera move (static, slow push-in, slow pan), hard cuts. Never a long
  continuous/orbital move around a character, never last-frame→first-frame
  chaining to fake a continuous camera. Few active subjects; at most one active
  animal. Each shot declares `reference_entity_ids` and the angle → sheet view.
- **Image prompts / keyframes**: rules in `image-prompt-agent`. Present a 3×3
  contact sheet of keyframes; the user approves before any video. One targeted
  correction per problematic shot, then re-review.
- **Video prompts**: rules in `video-prompt-agent`; start image only by default.
- **Generation**: `scripts/cloud_batch.py` (`docs/cloud-batch.md`): prepare →
  `upload_file` → save live `LoadImage` descriptor → `validate_workflow` →
  `approve` → `run_workflow(wait=false, confirm_spend=false)` from the **main
  session** → `job(action="wait")` → `fetch_outputs` → `record`. One user
  agreement per **batch** (job list + total cost) — each job still gets its own
  approval/ledger claim; anything outside the list needs new consent.
- **Finishing + sound** (`final-edit`): `projects/<p>/production/scene-XX/finish_anime.swift`
  (animation on twos, shared grade, bloom, grain, vignette, optional 2.39
  letterbox) and `concat_cuts.swift` for hard-cut assembly. `scripts/render_final.py`
  needs ffmpeg (absent here) and ignores `final/edit.yaml`: do not invoke it
  until replaced. Sound is layered (exterior/interior ambience, room tone,
  on-screen sources, discreet foley, J/L-cuts): free procedural/local first,
  Seed Audio for isolated sounds with consent.
- **Tier upgrade pass** (`cloud-production`): same shot IDs, approved keyframe
  as composition reference + the same sheet views; later ControlNet/targeted
  edits once those ComfyUI extensions are installed (not before; no automatic
  installation).

## Budget reporting

The ledger is always kept (`cloud_batch.py status`). If the user asks for less
noise, track budget internally and report only batch totals and ceiling
breaches instead of repeating full tables.
