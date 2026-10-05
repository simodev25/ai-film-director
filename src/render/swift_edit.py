"""Local, free hard-cut finishing via the repository Swift tools (macOS, no ffmpeg).

Supported route when FFmpeg is absent: an ordered clips file (one project-relative
clip per line, ``#`` comments allowed) rendered by ``tools/edit/finish_anime.swift``
(animation on twos, shared grade, bloom, grain, vignette, optional letterbox) or
assembled by ``tools/edit/concat_cuts.swift`` (plain hard cuts + audio bed).

Nothing here generates media with a model, calls the network, or spends credits.
The Swift tools refuse to overwrite outputs; this wrapper also checks inputs first.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

REPO = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO / "tools" / "edit"
SWIFT_TOOLS = ("finish_anime", "concat_cuts")


class EditRouteError(RuntimeError):
    """The local Swift edit route is unavailable or its inputs are invalid."""


@dataclass(frozen=True)
class SwiftEditResult:
    tool: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def read_clips_file(clips_file: Path) -> list[str]:
    """Same parsing as finish_anime.swift: trimmed lines, skip empty and ``#`` comments."""
    clips_file = Path(clips_file)
    if not clips_file.is_file():
        raise EditRouteError(f"Clips file not found: {clips_file}")
    clips = [line.strip() for line in clips_file.read_text(encoding="utf-8").splitlines()]
    clips = [c for c in clips if c and not c.startswith("#")]
    if not clips:
        raise EditRouteError(f"Clips file lists no clips: {clips_file}")
    return clips


def swift_available() -> bool:
    return sys.platform == "darwin" and shutil.which("swiftc") is not None


def build_tool(name: str, build_dir: Path | None = None) -> Path:
    """Compile tools/edit/<name>.swift once per source hash; reuse the cached binary."""
    if name not in SWIFT_TOOLS:
        raise EditRouteError(f"Unknown Swift edit tool: {name}")
    if not swift_available():
        raise EditRouteError("Swift edit tools need macOS with swiftc (Xcode command line tools); "
                             "not available here. Install FFmpeg for the legacy route instead.")
    source = TOOLS_DIR / f"{name}.swift"
    if not source.is_file():
        raise EditRouteError(f"Missing repository tool {source}")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    root = Path(build_dir) if build_dir else Path(tempfile.gettempdir()) / "ai-film-director-edit-tools"
    binary = root / digest / name
    if binary.is_file():
        return binary
    binary.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["swiftc", "-O", "-o", str(binary), str(source)], capture_output=True, text=True)
    if result.returncode != 0 or not binary.is_file():
        raise EditRouteError(f"swiftc failed for {source.name}: {result.stderr.strip()[-2000:]}")
    return binary


def run_swift_edit(project_root: Path, clips_file: Path, out: str, *, tool: str = "finish_anime",
                   audio: str | None = None, letterbox: float | None = None, seed: int | None = None,
                   tier: str | None = None, video_model: str | None = None, model_folder: str | None = None,
                   build_dir: Path | None = None) -> SwiftEditResult:
    """Validate inputs, build the tool if needed, then run it with project-relative paths."""
    project_root = Path(project_root).resolve()
    if not project_root.is_dir():
        raise EditRouteError(f"Project root not found: {project_root}")
    clips_file = Path(clips_file).resolve()
    clips = read_clips_file(clips_file)
    missing = [c for c in clips if not (project_root / c).is_file()]
    if missing:
        raise EditRouteError(f"Missing clip(s) relative to {project_root}: {missing}")
    out_path = project_root / out
    if out_path.exists():
        raise EditRouteError(f"Refusing to overwrite existing output {out_path}")
    if tool not in SWIFT_TOOLS:
        raise EditRouteError(f"Unknown Swift edit tool: {tool}")
    if not audio:
        # Both tools lay one audio bed under the picture; never rely on a project-specific default.
        raise EditRouteError("--audio is required (project-relative audio bed laid at 0 s under the cuts)")
    if tool == "concat_cuts":
        if any(v is not None for v in (letterbox, seed, tier, video_model, model_folder)):
            raise EditRouteError("--letterbox/--seed/provenance options apply to finish_anime only")
    if not (project_root / audio).is_file():
        raise EditRouteError(f"Missing audio bed {project_root / audio}")
    binary = build_tool(tool, build_dir)
    if tool == "finish_anime":
        command = [str(binary), "--project-root", str(project_root), "--out", out, "--clips-file", str(clips_file)]
        for flag, value in (("--audio", audio), ("--letterbox", letterbox), ("--seed", seed), ("--tier", tier),
                            ("--video-model", video_model), ("--model-folder", model_folder)):
            if value is not None:
                command += [flag, str(value)]
    else:
        command = [str(binary), str(project_root), out, audio, *clips]
    result = subprocess.run(command, capture_output=True, text=True, cwd=project_root)
    return SwiftEditResult(tool, tuple(command), result.returncode, result.stdout, result.stderr)
