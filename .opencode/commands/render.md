---
description: Assemble final film.
---

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root.
Assemble existing validated assets, preserving shot/audio mappings, timing,
continuity, and model/tier/attempt provenance. Report missing assets or budget
review before advancement; do not generate replacements automatically. Cloud
generation needs cloud-production (or its SKILL.md) and explicit paid-job
consent. No dialogue means no TTS; optional music is not presumed free. Preserve
existing legacy assets without automatic rerenders or runtime LLM changes.

Finish with the local Swift tools (`projects/<p>/production/scene-XX/finish_anime.swift`,
`concat_cuts.swift`; see the final-edit skill). Do not run
`scripts/render_final.py` (needs ffmpeg, ignores `final/edit.yaml`) until it
is replaced.

Delegate to @final-editor-agent.

Project:

$ARGUMENTS
