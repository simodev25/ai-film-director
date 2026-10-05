---
name: minimax-h3
description: MiniMax H3 structured prompt adapter for T2VA/I2VA/FL2VA/L2VA/Ref2VA.
---
MiniMax H3 Prompt Adapter

Legacy-only guard

Read `docs/cloud-policy.md` and `config/cloud-tiers.yaml` from the repository root
first. This native dialect is for explicit legacy MiniMax H3 opt-in only, not a
three-tier default or fallback. Cloud video (Veo/WAN, per selected tier) uses cloud-production or its
repository SKILL.md, not H3's section/mode contract. Preserve canonical shot and
prompt IDs, reference order, source links, and separate prompt/media artifacts.
Native sound/music sections below express creative intent, not authorization for
audio generation; budget/consent guards still apply and music is not assumed
free. Use actual project adapters without editing user JSON. Loaded nodes are
not proof of generation-tested readiness; hosted legacy nodes may be paid.

MiniMax H3 uses structured prompt formats associated with its Context-IR workflow.
The official public prompt-writing skill defines five modes:
T2VA
I2VA
FL2VA
L2VA
Ref2VA
For base text/keyframe modes use: references/base-en.txt and follow its final prompt structure.
---
integrated_multimodal_description
overall_soundscape
non_diegetic_music
---
For Ref2VA use: references/ref-en.txt and follow its six-section rewrite format.
---
subject_definitions
summary
retention_analysis
detailed_description
overall_soundscape
non_diegetic_music
---
Do not claim to reproduce the private H3-Context-IR implementation.
Mode selection
Use:
T2VA when no visual reference is required.
I2VA when a first frame is supplied.
FL2VA when first and last frames define the path.
L2VA when a last frame is supplied.
Ref2VA when multiple reference images/video/audio assets must be preserved.
Base prompt
`integrated_multimodal_description` must contain the complete visual/audio timeline.
Then:
`overall_soundscape`
Then:
`non_diegetic_music`
Ref2VA
Keep reference labels stable.
Example labels:
<Subject 1>
<Image 1>
<Video 1>
<Audio 1>
Never create an unresolved reference label.
Dialogue
Preserve exact dialogue text and language.
Use explicit speaker identity.
Timing
Use monotonically increasing timestamps when describing multiple cuts.
Output
Create:
prompts/videos/minimax-h3/shot_{number}.yaml
Keep schemas/video-prompt.schema.yaml's canonical prompt_id, shot_id, model, and
prompt. Put the native required sections in the prompt body or supported schema
fields and validate them before saving; do not invent a competing artifact path
or claim an unavailable compiler was run.
