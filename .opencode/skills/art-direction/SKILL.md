---
name: art-direction
description: Define per-scene and per-shot emotional intent, user references, camera language, palette and sound.
compatibility: opencode
---

# Art direction

Read `docs/cloud-policy.md`, `config/cloud-tiers.yaml` and `docs/film-method.md`
from the repository root first. Art direction runs after characters/locations/
props and before model sheets and storyboard. It is planning only: no rendering,
no spend, no tier change.

Ask the user for visual references (films, anime, directors, stills) and the
feeling they want. **Never invent references**; if none are given, record
`none provided` and keep the brief descriptive.

Per scene define:

- emotional intent: what the viewer should feel, and how it evolves
- user-given references and what is borrowed from each (light, framing, pace)
- palette and lighting key (sources, contrast, color temperature)
- rhythm: shot count, average shot length, where to hold and where to cut
- sound intent from the start: ambience layers, silences, on-screen sources,
  J/L-cuts

Per shot define:

- intent (one sentence, viewer-side)
- camera language with justification: why tight/wide, why held or cut, why
  static or a slow move
- light/palette notes specific to the shot
- sound note (what is heard in and across the cut)

Store the brief in the existing storyboard/shot artifacts using only
schema-declared fields (e.g. visual/audio intent, notes); report unsupported
fields instead of inventing schema keys. Preserve stable scene/shot/entity IDs.
The storyboard and shot-design stages must cite this brief.
