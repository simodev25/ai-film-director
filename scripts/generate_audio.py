from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from comfyui.client import ComfyUIClient
from config import COMFYUI_TIMEOUT, COMFYUI_URL, POLL_INTERVAL
from render.audio import render_audio
from budget import require_budget_review
import yaml


def _render_one(prompt_file: Path, output_dir: Path) -> str:
    with ComfyUIClient(COMFYUI_URL, COMFYUI_TIMEOUT, POLL_INTERVAL, legacy_opt_in=True) as client:
        render_audio(prompt_file=prompt_file, output_dir=output_dir, client=client)
    return prompt_file.stem


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate audio via ComfyUI")
    parser.add_argument("project", help="Path to project root")
    parser.add_argument("--legacy-opt-in", action="store_true", help="Explicit Qwen3-TTS route only; not paid-job consent")
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=3,
        help="Parallel jobs (default: 3)",
    )
    args = parser.parse_args()

    if not args.legacy_opt_in:
        parser.error("Qwen3-TTS requires --legacy-opt-in. Use the cloud adapter + comfy-mcp for hosted audio.")

    root = Path(args.project)
    require_budget_review(root)
    prompt_dir = root / "prompts" / "audio"
    output_dir = root / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt_files = sorted(prompt_dir.glob("*.yaml"))
    # Silence and Foley plans are not speech jobs. Never run TTS over them.
    prompt_files = [p for p in prompt_files if (lambda d: d.get("model", "qwen3-tts") == "qwen3-tts" and bool(d.get("text", "").strip()) and d.get("event_kind", "dialogue") in {"dialogue", "narration"})(yaml.safe_load(p.read_text(encoding="utf-8")))]
    if not prompt_files:
        print(f"No prompts found in {prompt_dir}", file=sys.stderr)
        return

    jobs = max(1, args.jobs)
    print(f"Rendering {len(prompt_files)} audio prompts with {jobs} job(s)...")

    if jobs == 1:
        failures = 0
        for pf in prompt_files:
            try:
                _render_one(pf, output_dir)
                print(f"generated audio: {pf.stem}")
            except Exception as exc:
                failures += 1
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)
        if failures:
            raise SystemExit(1)
        return

    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_file = {executor.submit(_render_one, pf, output_dir): pf for pf in prompt_files}
        for future in as_completed(future_to_file):
            pf = future_to_file[future]
            try:
                stem = future.result()
                print(f"generated audio: {stem}")
            except Exception as exc:
                failures.append((pf.stem, str(exc)))
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)}/{len(prompt_files)} failed", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
