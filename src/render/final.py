from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from config import FFMPEG_BIN


FFMPEG_MISSING_MESSAGE = (
    "FFmpeg not found ({bin}). The legacy route (concat renders/videos/*.mp4) needs it and does not "
    "read final/edit.yaml. On macOS, use the local Swift route instead: "
    "python scripts/render_final.py PROJECT --clips-file LIST.txt --out final/<name>.mp4 --audio <bed.wav> "
    "[--tool finish_anime|concat_cuts]. Nothing is installed automatically."
)


def ffmpeg_available(binary: str | None = None) -> bool:
    """True when the configured FFmpeg binary resolves on PATH (or is an existing path)."""
    binary = binary or FFMPEG_BIN
    return shutil.which(binary) is not None or Path(binary).is_file()


def create_concat_file(videos: list[Path], concat_file: Path) -> Path:
    concat_file.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for video in videos:
        path = video.resolve().as_posix()
        # FFmpeg concat: escape single quotes by closing, escaping, reopening
        path = path.replace("'", r"'\''")
        lines.append(f"file '{path}'")
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return concat_file


def _run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.strip()[:2000]}")


def render_final(project_root: Path, output_name: str = "film.mp4") -> Path:
    project_root = Path(project_root)
    video_dir = project_root / "renders" / "videos"
    final_dir = project_root / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    output = final_dir / output_name

    videos = sorted(video_dir.glob("*.mp4"))
    if not videos:
        raise FileNotFoundError(f"No video clips found in {video_dir}")
    if not ffmpeg_available():
        raise RuntimeError(FFMPEG_MISSING_MESSAGE.format(bin=FFMPEG_BIN))

    concat_file = final_dir / "concat.txt"
    create_concat_file(videos, concat_file)

    # Try fast concat (no re-encode). Fall back to re-encode if inputs have mismatched codecs.
    fast_cmd = [
        FFMPEG_BIN,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output),
    ]
    try:
        _run_ffmpeg(fast_cmd)
    except RuntimeError as exc:
        # Fallback: re-encode to h264/aac for compatibility (slower but robust)
        fallback_cmd = [
            FFMPEG_BIN,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
        _run_ffmpeg(fallback_cmd)
    return output
