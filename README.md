# AI Film Director

OpenCode-native pipeline that turns a story idea into a finished film:

```
Story → Budget estimate (3 gammes, low/mean/high) → Explicit user review → Screenplay → Characters + Sheets → Locations → Props → Storyboard → Shot List → Image Prompts → Image Generation → Video Prompts → Video Generation → Audio → Continuity → Final Edit
```

Continuity, IDs, and schemas are validated at every stage. ComfyUI workflows are executed through adapters that only touch configured prompt/input nodes.

## Cloud gammes and budget review

Read [`docs/cloud-policy.md`](docs/cloud-policy.md) before every stage. The versioned
[`config/cloud-tiers.yaml`](config/cloud-tiers.yaml) selects **one recommendation per
stage**, not simultaneous runs over all models. It does **not** change the running
OpenCode LLM. No API key belongs in this file or in a workflow.

| Gamme | Text recommendation | Images | Video | Non-verbal audio |
|---|---|---|---|---|
| Preparation | GPT-6 Luna | Seedream 5.0 Flash, 1K | Veo 3.1 Lite, 720p | Seed Audio 1.0; existing local maquette may be reused |
| Tests | Gemini 3.8 Flash | Nano Banana 2, 1K | Kling v3.0 Pro, 720p | Seed Audio 1.0 |
| Production | GPT-6.1 Sol | Nano Banana Pro, 2K | Veo 3.1, 1080p | Seed Audio 1.0 + Foley/mix |

Preparation is a **planning default**, not spending consent. Higher gammes need an
explicit user selection; there is no automatic upgrade, fallback, or model fan-out.
Skip TTS without dialogue/narration. Music is optional and not included by default.

After the story and **before screenplay**:

```bash
PYTHONPATH=src python -m cli budget projects/my-film
# Or supply explicit sizing using schemas/budget-assumptions.schema.yaml:
PYTHONPATH=src python -m cli budget projects/my-film --assumptions assumptions.yaml
```

This offline command writes `budget/estimate.yaml` and `budget/estimate.md`, comparing
**low / mean / high** in all three gammes with the same duration, image/reference
counts, video scope, audio sources, token counts and repeat assumptions. Defaults are
rough sizing, not invented shot IDs. Mean means the specified repeat hypothesis,
not measured success probability. Rates are bound to profile settings; the report
discloses rounding, margin, exclusions and price freshness. Unknown prices block
calculation rather than becoming zero.

Only after a real user review may a decision be recorded, matching
[`schemas/budget-decision.schema.yaml`](schemas/budget-decision.schema.yaml):
`approved: true`, `scope: planning_only_not_spend_consent`, `estimate_sha256`,
`selected_tier`, `max_spend_usd`, and a nonempty `consent_reference` identifying the
actual affirmative response. **No command automatically creates this approval.**
Changed estimates, story/project hashes, rates, or missing evidence block advancing.
Existing screenplays/media remain intact while a retrospective review is pending.

Planning approval is **not paid-job consent**. Every cloud job, including a retry,
needs separate explicit approval of its model, settings and cost within the ceiling.
Native OpenRouter media goes only through the project ComfyUI cloud adapter and
`comfy-mcp`; never directly to generation APIs. Loaded/authenticated plugins are not
generation-tested. OpenRouter nodes can be paid despite `is_api_node: false`.

The cloud adapter currently prepares a separate graph and verifies a job approval
offline; it **does not submit jobs**. The exact cloud graph, live input bindings,
workflow validation and budget ledger must be in place before an approved MCP
submission. See [`docs/cloud-adapter.md`](docs/cloud-adapter.md). Missing mappings
or accounting remain blockers; a planning decision is not a paid-job approval.

Existing user JSONs and local adapters are retained as **explicit legacy opt-in**,
not silent cloud fallbacks. The legacy Python submitter refuses OpenRouter/known
hosted graphs; cloud jobs require the gated MCP route. POST submissions are never
automatically retried. No paid-generation or installation test is part of this refactor.

## Tableau de bord web — Atelier

Suivre **tous les projets** sans ouvrir ComfyUI : vues scènes/plans, galerie de
versions, connexions entre références et rendus, documents et suivi. Site local
en lecture seule, découverte automatique des projets et actualisation toutes
les 5 secondes, sans génération ni modification des fichiers.

```bash
PYTHONPATH=src python3 -m dashboard.server --projects-root projects --port 8765
```

Ouvrir **http://127.0.0.1:8765**. Voir [le guide Atelier](docs/dashboard.md) pour
les commandes, les limites et la signification des indicateurs de progression.

## Requirements

- [OpenCode V2](https://opencode.ai/v2/docs/) with project agents and skills
- Python 3.11+
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (local or remote)
- FFmpeg (`ffmpeg` on PATH or via `FFMPEG_BIN`)
- ComfyUI workflow JSONs for the backends you use

## Directory Structure

```
ai-film-director/
├── README.md
├── opencode.json
├── pyproject.toml
├── .env.example
│
├── .opencode/
│   ├── agents/                  # 14 sub-agents delegated by @film-director
│   │   ├── film-director.md     # primary orchestrator
│   │   ├── story-agent.md
│   │   ├── screenplay-agent.md
│   │   ├── character-agent.md
│   │   ├── location-agent.md
│   │   ├── prop-agent.md
│   │   ├── storyboard-agent.md
│   │   ├── shot-agent.md
│   │   ├── image-prompt-agent.md
│   │   ├── video-prompt-agent.md
│   │   ├── audio-agent.md
│   │   ├── workflow-agent.md
│   │   ├── continuity-agent.md
│   │   └── final-editor-agent.md
│   ├── commands/                # 14 slash commands
│   │   ├── film.md              # full pipeline
│   │   ├── story.md
│   │   ├── screenplay.md
│   │   ├── characters.md
│   │   ├── locations.md
│   │   ├── props.md
│   │   ├── storyboard.md
│   │   ├── shots.md
│   │   ├── images.md
│   │   ├── videos.md
│   │   ├── audio.md
│   │   ├── render.md
│   │   ├── validate.md
│   │   └── status.md
│   └── skills/                  # 14 skills (see SKILL.md in each)
│       ├── story-development/
│       ├── screenplay/
│       ├── character-design/
│       ├── storyboard/
│       ├── shot-design/
│       ├── flux-2-klein/
│       ├── krea-2/
│       ├── qwen-image/
│       ├── ltx-2.5/             # references/: creative-examples.md, ltx-vocabulary.md, multishot-format.md, etc.
│       ├── minimax-h3/          # references/: base-en.txt, ref-en.txt
│       ├── qwen3-tts/
│       ├── continuity/
│       ├── comfyui/
│       └── final-edit/
│
├── schemas/                     # JSON Schema (YAML) for every artifact
│   ├── project.schema.yaml
│   ├── story.schema.yaml
│   ├── screenplay.schema.yaml
│   ├── character.schema.yaml
│   ├── character-sheet.schema.yaml
│   ├── location.schema.yaml
│   ├── prop.schema.yaml
│   ├── storyboard.schema.yaml
│   ├── shot.schema.yaml
│   ├── image-prompt.schema.yaml
│   ├── video-prompt.schema.yaml
│   ├── audio-prompt.schema.yaml
│   ├── workflow.schema.yaml
│   ├── render.schema.yaml
│   └── manifest.schema.yaml
│
├── workflows/                   # User-supplied ComfyUI graphs (gitignored content)
│   ├── image/
│   │   ├── krea2.json
│   │   ├── flux2-klein.json
│   │   └── qwen-image.json
│   ├── video/
│   │   ├── ltx-2.5.json
│   │   └── minimax-h3.json
│   └── audio/
│       └── qwen3-tts.json
│
├── projects/                    # Generated films (gitignored)
│   └── <film>/
│       ├── project.yaml
│       ├── story/story.yaml
│       ├── screenplay/screenplay.yaml
│       ├── characters/characters.yaml
│       ├── characters/sheets/*.yaml
│       ├── locations/locations.yaml
│       ├── props/props.yaml
│       ├── storyboard/storyboard.yaml
│       ├── shots/shots.yaml
│       ├── prompts/images/<model>/*.yaml  # krea2/, flux2-klein/, qwen-image/
│       ├── prompts/videos/<model>/*.yaml  # ltx-2.5/, minimax-h3/
│       ├── prompts/audio/*.yaml
│       ├── renders/images/
│       ├── renders/videos/
│       ├── audio/
│       ├── final/film.mp4
│       └── manifest.yaml
│
├── src/                         # Flat package (pip install -e ., PYTHONPATH=src)
│   ├── cli.py                   # film-director status|manifest
│   ├── config.py                # env: COMFYUI_URL, OUTPUT_ROOT, etc.
│   ├── paths.py                 # project_paths() / create_project_tree()
│   ├── validation.py            # validate_file() (cached schemas)
│   ├── manifest.py              # build_manifest() / save_manifest()
│   ├── comfyui/
│   │   ├── client.py            # ComfyUIClient (Session + retry + backoff + upload_image)
│   │   ├── workflow.py          # load_workflow() / set_node_input()
│   │   └── adapters.py          # prepare_workflow() (cached, LTX-2.5 I2V patch + dot/underscore fallback)
│   ├── pipeline/
│   │   └── director.py          # FilmDirector.status() / next_stage()
│   ├── render/
│   │   ├── images.py            # render_image() → renders/images/ (skips type=temp)
│   │   ├── videos.py            # render_video() I2V from renders/images/ via upload_image (skips temp)
│   │   ├── audio.py             # render_audio()
│   │   └── final.py             # render_final() → final/film.mp4
│   └── utils/
│       ├── files.py             # atomic load/save JSON/YAML
│       └── jsonx.py             # load_json / save_json
│
├── scripts/                     # Standalone entry points
│   ├── init_project.py
│   ├── validate_project.py
│   ├── generate_images.py
│   ├── generate_videos.py
│   ├── generate_audio.py
│   ├── render_final.py
│   ├── build_manifest.py
│   └── run_workflow.py
│
└── tests/
    ├── test_validation.py
    ├── test_workflow.py
    └── test_pipeline.py
```

## Install

```bash
git clone https://github.com/BitraAI/ai-film-director.git
cd ai-film-director

python3 -m venv film-env
source film-env/bin/activate
python -m pip install -U pip uv
uv pip install -e .
```

Verify:

```bash
film-director --help
python -m pytest -q
```

## Install PyTorch

```bash
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu132
```

## Install ComfyUI

```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
uv pip install -r ComfyUI/requirements.txt
cd ComfyUI/custom_nodes
git clone https://github.com/Comfy-Org/ComfyUI-Manager 
uv pip install -r ComfyUI-Manager/requirements.txt
```

## Configure

```bash
cp .env.example .env
```

`.env.example` (`src/config.py:1`):

```
COMFYUI_URL=http://127.0.0.1:8188
OUTPUT_ROOT=projects
COMFYUI_TIMEOUT=600
POLL_INTERVAL=1
FFMPEG_BIN=ffmpeg
PYTHONUNBUFFERED=1
```

| Var | Default | Description |
|-----|---------|-------------|
| `COMFYUI_URL` | `http://127.0.0.1:8188` | ComfyUI API endpoint |
| `OUTPUT_ROOT` | `projects` | Root for `init_project.py` |
| `COMFYUI_TIMEOUT` | `600` | Seconds to wait for a workflow |
| `POLL_INTERVAL` | `1` | Poll interval (seconds) |
| `FFMPEG_BIN` | `ffmpeg` | FFmpeg binary |

### FFmpeg

```bash
$ cd /tmp
$ wget https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz
$ tar xvf ffmpeg-master-latest-linuxarm64-gpl.tar.xz ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe
$ sudo mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg /usr/local/bin
$ sudo mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe /usr/local/bin
```

### ComfyUI Workflows

Right click Workflow tab and select Export (API). Place your exported ComfyUI API graphs here (adapters only mutate configured prompt/input nodes):

```
workflows/image/krea2.json
workflows/image/flux2-klein.json
workflows/image/qwen-image.json
workflows/video/ltx-2.5.json
workflows/video/minimax-h3.json
workflows/audio/qwen3-tts.json
```

Validate they load:

```bash
python -m pytest tests/test_workflow.py -v
```

## Create a Film

```bash
python scripts/init_project.py my-film
 → projects/my-film/
```

This creates `project.yaml` (`project_id`, `title`, `genre`, `subgenres`, `aspect_ratio`, `fps`, `duration_seconds` validated by `schemas/project.schema.yaml:1`) with genre enum: Action, Comedy, Drama, Horror, Sci-Fi, Documentary, Romance, Thriller, Family, Animation, Adventure, Fantasy, Historical, Musical and subgenres enum: Action Adventure, Action Comedy, Action Thriller, Comedy Drama, Sci-Fi Adventure, Sci-Fi Comedy, Sci-Fi Horror, Historical Drama, Historical Epic, Historical Fiction, Film Noir, Coming of Age, 3D Animation, Space Opera and the tree from `src/paths.py:4`:

```
story/  screenplay/  characters/sheets/  locations/  props/  storyboard/  shots/
prompts/images/<model>/  prompts/videos/<model>/  prompts/audio/  # images: krea2/flux2-klein/qwen-image, videos: ltx-2.5/minimax-h3
renders/images/  renders/videos/  audio/  final/
```

## Usage — OpenCode

Install OpenCode, then start it from the repo root:

```bash
curl -fsSL https://opencode.ai/install | bash
opencode
```

Primary orchestrator (`opencode.json:4`, `.opencode/agents/film-director.md:1`):

```
@film-director
```

Full pipeline (story → budget comparison → explicit review → screenplay → characters → locations → props → storyboard → shots → images → videos → audio → continuity → render):

```
/film my-film
```

Run stages independently:

```
/story my-film        # → story/story.yaml
/budget my-film       # → budget/estimate.yaml + estimate.md; stops for user review
/screenplay my-film   # → screenplay/screenplay.yaml
/characters my-film   # → characters/characters.yaml + characters/sheets/*.yaml
/locations my-film    # → locations/locations.yaml
/props my-film        # → props/props.yaml
/storyboard my-film   # → storyboard/storyboard.yaml
/shots my-film        # → shots/shots.yaml
/images my-film       # → one selected cloud image model's prompts; paid generation requires additional consent
/videos my-film       # → one selected cloud video model's prompts; paid generation requires additional consent
/audio my-film        # → prompts/audio/*.yaml + audio/
/render my-film       # → final/film.mp4
/validate my-film     # schema + continuity checks
/status my-film       # manifest status
```

Each command delegates to its agent (e.g. `/story` → `@story-agent`, `/images` → `@image-prompt-agent`). See `.opencode/commands/*.md` and `.opencode/agents/*.md`.

## Usage — Scripts & CLI

All scripts accept a project path (`projects/<name>` or absolute).

```bash
# Validate schemas (story, screenplay, characters, locations, props, storyboard, shots)
python scripts/validate_project.py projects/my-film
# src/validation.py:6 — jsonschema against schemas/*.schema.yaml

# Project status / manifest
python scripts/build_manifest.py projects/my-film  # preferred — writes manifest.yaml via src/manifest.py:29
film-director status projects/my-film   # src/cli.py:15 — prints READY/MISSING per stage + next_stage()
film-director manifest projects/my-film # same as build_manifest.py

# Images — iterate prompts/images/<model>/*.yaml (rglob) → renders/images/ (final outputs only)
# These scripts are LOCAL LEGACY only; cloud generation uses the gated MCP adapter.
# A reviewed budget is required, and opt-in is not paid-job consent.
python scripts/generate_images.py projects/my-film --model krea2 --legacy-opt-in
python scripts/generate_images.py projects/my-film --model flux2-klein --legacy-opt-in
python scripts/generate_images.py projects/my-film --model qwen-image --legacy-opt-in
# src/render/images.py:render_image() saves only type=output to renders/images/ (skips type=temp previews)
# src/comfyui/client.py:ComfyUIClient (Session + retry + backoff + rglob subfolders)
# Note: projects/<film>/images/ is removed – do not download from ComfyUI/temp

# Videos — iterate prompts/videos/<model>/*.yaml (rglob) → renders/videos/ (I2V via renders/images/)
python scripts/generate_videos.py projects/my-film --model ltx-2.5 --legacy-opt-in  # I2V; missing/upload-failed source is a blocker, not a T2V fallback
python scripts/generate_videos.py projects/my-film --model minimax-h3 --legacy-opt-in
# src/render/videos.py:render_video() + src/comfyui/adapters.py:prepare_workflow() (cached, dot/underscore workflow fallback) + rglob

# Audio — iterate prompts/audio/*.yaml → audio/
python scripts/generate_audio.py projects/my-film --legacy-opt-in  # speech only; skips non-dialogue plans
# src/render/audio.py:render_audio()

# Final edit — FFmpeg concat of renders → final/film.mp4 (does not read final/edit.yaml)
python scripts/render_final.py projects/my-film
# src/render/final.py:render_final()  — exits with a clear message when FFmpeg is absent
# No FFmpeg (macOS): local, free Swift route from an ordered clips file (tools/edit/*.swift)
python scripts/render_final.py projects/my-film --clips-file production/scene-01/cuts.txt \
  --out final/scene-01/finished.mp4 --audio audio/bed.wav [--tool finish_anime|concat_cuts] [--letterbox 2.39]
# src/render/swift_edit.py:run_swift_edit()

# Model sheets — crop an approved sheet into isolated views (local, free; Pillow)
python scripts/split_model_sheet.py SHEET.png --grid 1x4 --views front,three_quarter,profile,back \
  --out-dir projects/my-film/references/views/char_x \
  [--registry projects/my-film/references/approved-references.yaml --entity-id char_x --sheet-type turnaround]

# Ad-hoc ComfyUI execution
python scripts/run_workflow.py <legacy-model> "<prompt>" --legacy-opt-in [--negative "..."] [--seed 42] [--output out.yaml]
# src/comfyui/adapters.py:prepare_workflow() + src/comfyui/client.py:ComfyUIClient.execute()
```

## Pipeline Stages

| # | Stage | Command | Input | Output | Schema |
|---|-------|---------|-------|--------|--------|
| 1 | Story | `/story` | user idea | `story/story.yaml` | `story.schema.yaml` |
| Gate | Budget / review | `/budget` | story, duration, explicit assumptions | `budget/estimate.yaml`, `estimate.md`, user `decision.yaml` | `budget-estimate.schema.yaml`, `budget-decision.schema.yaml` |
| 2 | Screenplay | `/screenplay` | story | `screenplay/screenplay.yaml` | `screenplay.schema.yaml` |
| 3 | Characters | `/characters` | story + screenplay | `characters/characters.yaml`, `characters/sheets/*.yaml` | `character.schema.yaml`, `character-sheet.schema.yaml` |
| 4 | Locations | `/locations` | story + screenplay | `locations/locations.yaml` | `location.schema.yaml` |
| 5 | Props | `/props` | story + screenplay | `props/props.yaml` | `prop.schema.yaml` |
| 6 | Storyboard | `/storyboard` | screenplay + characters + locations | `storyboard/storyboard.yaml` | `storyboard.schema.yaml` |
| 7 | Shot List | `/shots` | storyboard | `shots/shots.yaml` | `shot.schema.yaml` |
| 8 | Image Prompts | `/images` (prompt phase) | shots + sheets + locations | `prompts/images/<model>/*.yaml` | `image-prompt.schema.yaml` |
| 9 | Image Generation | `/images` (render) / `generate_images.py` | image prompts + `workflows/image/*.json` | `renders/images/` | `workflow.schema.yaml` |
| 10 | Video Prompts | `/videos` (prompt phase) | shots + images | `prompts/videos/<model>/*.yaml` | `video-prompt.schema.yaml` |
| 11 | Video Generation | `/videos` (render) / `generate_videos.py` | video prompts + `workflows/video/*.json` | `renders/videos/` | `workflow.schema.yaml` |
| 12 | Audio | `/audio` / `generate_audio.py` | screenplay dialogue | `prompts/audio/*.yaml`, `audio/` | `audio-prompt.schema.yaml` |
| 13 | Final | `/render` / `render_final.py` | renders + audio | `final/film.mp4` | `render.schema.yaml` |

Continuity is enforced at every stage by `@continuity-agent` (`.opencode/skills/continuity/SKILL.md`). Director rules (`.opencode/agents/film-director.md:26`): stable IDs, every scene → shots, every shot → image prompt, every motion shot → video prompt, every dialogue → audio prompt, preserve appearance/state/chronology.

`FilmDirector.next_stage()` order: `story → budget → screenplay → characters → locations → props → storyboard → shots → images → videos → audio → final`. Budget is ready only with a valid estimate and matching explicit review. `require_stage()` checks the gate before advancing downstream planning.

## Schemas & Validation

All artifacts are YAML validated with `jsonschema` (`src/validation.py:6`):

```bash
python scripts/validate_project.py projects/my-film
python -m pytest tests/test_validation.py -v
```

Schemas live in `schemas/` and are referenced by each skill's `SKILL.md`.

## Development

```bash
# All tests
python -m pytest -v

# Specific
python -m pytest tests/test_pipeline.py -v  # FilmDirector.status/next_stage
python -m pytest tests/test_workflow.py -v  # workflows/*.json loadable
python -m pytest tests/test_validation.py -v
```

Project config: `pyproject.toml:1` (`setuptools`, `requires-python >=3.11`, deps `PyYAML`, `jsonschema`, `requests`).

## License

No `LICENSE` file is currently committed. All rights reserved unless a license is added.
