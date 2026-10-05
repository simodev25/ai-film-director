from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from comfyui.client import ComfyUIClient
from config import COMFYUI_TIMEOUT, COMFYUI_URL, POLL_INTERVAL
from render.videos import render_video
from budget import require_budget_review
import yaml


def _render_one(prompt_file: Path, output_dir: Path, model_override: str | None) -> str:
    with ComfyUIClient(COMFYUI_URL, COMFYUI_TIMEOUT, POLL_INTERVAL, legacy_opt_in=True) as client:
        render_video(
            prompt_file=prompt_file,
            output_dir=output_dir,
            client=client,
            model_override=model_override,
        )
    return prompt_file.stem


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate videos via ComfyUI")
    parser.add_argument("project", help="Path to project root")
    parser.add_argument(
        "--model",
        choices=["ltx-2.5", "minimax-h3"],
        help="Override model for all prompts",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=2,
        help="Parallel ComfyUI jobs (default: 2, videos are heavier)",
    )
    parser.add_argument("--force", action="store_true", help="Re-render even if output exists")
    parser.add_argument("--legacy-opt-in", action="store_true", help="Explicit local legacy route only; not paid-job consent")
    args = parser.parse_args()

    if not args.legacy_opt_in or not args.model:
        parser.error("Select one --model and --legacy-opt-in. Cloud uses the project cloud adapter through comfy-mcp.")

    root = Path(args.project)
    require_budget_review(root)
    prompt_dir = root / "prompts" / "videos"
    output_dir = root / "renders" / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Support both flat layout (prompts/videos/*.yaml) and new model subfolders (prompts/videos/<model>/*.yaml)
    prompt_files = sorted(prompt_dir.rglob("*.yaml"))
    # filter by model if specified (match either folder name or filename suffix .<model>.yaml)
    if args.model:
        prompt_files = [p for p in prompt_files if p.parent.name == args.model or f".{args.model}." in p.name]
    for prompt_file in prompt_files:
        data = yaml.safe_load(prompt_file.read_text(encoding="utf-8"))
        if data.get("model") != args.model:
            parser.error(f"Prompt model mismatch in {prompt_file}; do not silently replace its model")
    if not args.force:
        prompt_files = [p for p in prompt_files if not (output_dir / f"{yaml.safe_load(p.read_text(encoding='utf-8'))['shot_id']}.yaml").exists()]
    if not prompt_files:
        print(f"No prompts found in {prompt_dir}", file=sys.stderr)
        return

    jobs = max(1, args.jobs)
    print(f"Rendering {len(prompt_files)} video prompts with {jobs} job(s)...")

    if jobs == 1:
        failures = 0
        for pf in prompt_files:
            try:
                _render_one(pf, output_dir, args.model)
                print(f"generated video: {pf.stem}")
            except Exception as exc:
                failures += 1
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)
        if failures:
            raise SystemExit(1)
        return

    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_file = {
            executor.submit(_render_one, pf, output_dir, args.model): pf for pf in prompt_files
        }
        for future in as_completed(future_to_file):
            pf = future_to_file[future]
            try:
                stem = future.result()
                print(f"generated video: {stem}")
            except Exception as exc:
                failures.append((pf.stem, str(exc)))
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)}/{len(prompt_files)} failed", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
