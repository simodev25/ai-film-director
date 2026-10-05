"""Final render entry point.

Legacy route (unchanged): ``python scripts/render_final.py PROJECT`` concatenates
``renders/videos/*.mp4`` with FFmpeg into ``final/film.mp4``. It does not read
``final/edit.yaml``.

Local Swift route (macOS, no FFmpeg, free, no generation)::

    python scripts/render_final.py PROJECT --clips-file production/scene-01/scene01-v3.clips.txt \
        --out final/scene-01/scene01-finished-v4.mp4 --audio audio/opening-rain/rain-preview.wav \
        [--tool finish_anime|concat_cuts] [--letterbox 2.39] [--seed N] \
        [--tier T --video-model ID --model-folder F]

Paths in the clips file, ``--out`` and ``--audio`` are relative to PROJECT; the
clips file itself may be relative to PROJECT or to the current directory.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from render.final import FFMPEG_MISSING_MESSAGE, ffmpeg_available, render_final
from render.swift_edit import EditRouteError, run_swift_edit, swift_available
from config import FFMPEG_BIN


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Render/assemble the final film (local only, no generation).")
    parser.add_argument("project", type=Path)
    parser.add_argument("--clips-file", type=Path, help="ordered clip list for the local Swift route")
    parser.add_argument("--out", help="project-relative output .mp4 (Swift route)")
    parser.add_argument("--audio", help="project-relative audio bed .wav (Swift route)")
    parser.add_argument("--tool", choices=["finish_anime", "concat_cuts"], default="finish_anime")
    parser.add_argument("--letterbox", type=float)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--tier")
    parser.add_argument("--video-model")
    parser.add_argument("--model-folder")
    parser.add_argument("--build-dir", type=Path, help="where compiled Swift tools are cached")
    return parser.parse_args(argv)


def resolve_clips_file(project: Path, clips_file: Path) -> Path:
    if clips_file.is_absolute() or clips_file.is_file():
        return clips_file
    return project / clips_file


def main(argv=None) -> int:
    args = parse_args(argv)
    project = args.project
    if args.clips_file is None:
        if not ffmpeg_available():
            print(FFMPEG_MISSING_MESSAGE.format(bin=FFMPEG_BIN), file=sys.stderr)
            return 2
        output = render_final(project)
        print(f"final film: {output}")
        return 0
    if not swift_available():
        print("The --clips-file route uses the repository Swift tools (tools/edit/*.swift) and needs macOS "
              "with swiftc. " + ("FFmpeg is present but its legacy route does not take a clips file."
                                 if ffmpeg_available() else "FFmpeg is also absent; nothing can render here."),
              file=sys.stderr)
        return 2
    if not args.out:
        print("--out is required with --clips-file (project-relative .mp4; existing files are never overwritten)",
              file=sys.stderr)
        return 2
    try:
        result = run_swift_edit(project, resolve_clips_file(project, args.clips_file), args.out, tool=args.tool,
                                audio=args.audio, letterbox=args.letterbox, seed=args.seed, tier=args.tier,
                                video_model=args.video_model, model_folder=args.model_folder,
                                build_dir=args.build_dir)
    except EditRouteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"{result.tool} failed (exit {result.returncode}): {result.stderr.strip()[-2000:]}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
