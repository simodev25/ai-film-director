---
name: final-edit
description: Assemble generated shots and audio into the final film.
compatibility: opencode
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. Assemble existing validated assets and preserve canonical shot/audio
mappings, timing, voice identity, and tier/model/attempt provenance. Missing
assets require a report, not automatic generation; any cloud generation uses
cloud-production or its repository SKILL.md with explicit paid-job consent.
No dialogue means no TTS; music is optional and not presumed free. Preparation
can reuse existing local rain/ambience without a charged call. Do not upgrade
tiers, change runtime LLMs, or rerender legacy assets silently.

Order shots by shot.sequence.

Use:

duration
fps
transition
audio
dialogue
music
sound effects

Produce:

final/film.mp4 (or per-scene outputs under `final/scene-XX/`)

Real tools (local, free, AVFoundation/CoreImage, no ffmpeg; build with
`swiftc -O`; they refuse to overwrite outputs):

- `projects/<p>/production/scene-XX/finish_anime.swift` — finishing pass:
  animation on twos, shared grade, discreet bloom, grain, vignette, optional
  2.39 letterbox as a second output, report + contact sheet.
- `projects/<p>/production/scene-XX/concat_cuts.swift` — hard-cut assembly with
  an audio bed.

`scripts/render_final.py` needs ffmpeg (absent on this machine) and does not
read `final/edit.yaml`: do not invoke it until it has been replaced.

Sound design in layers: exterior/interior ambience, room tone, on-screen
sources (TV), discreet foley, J/L-cuts across shots. Procedural/local and free
first; Seed Audio only for isolated sounds, with batch consent.
