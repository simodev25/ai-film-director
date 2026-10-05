from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from comfyui.client import ComfyUIClient
from config import COMFYUI_TIMEOUT, COMFYUI_URL, POLL_INTERVAL
from render.images import render_image
from budget import require_budget_review
import yaml


def _render_one(prompt_file: Path, output_dir: Path, model_override: str | None) -> str:
    # Each thread gets its own client/Session to avoid Session thread-safety issues
    with ComfyUIClient(COMFYUI_URL, COMFYUI_TIMEOUT, POLL_INTERVAL, legacy_opt_in=True) as client:
        render_image(
            prompt_file=prompt_file,
            output_dir=output_dir,
            client=client,
            model_override=model_override,
        )
    return prompt_file.stem


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate images via ComfyUI")
    parser.add_argument("project", help="Path to project root (e.g. projects/my-film)")
    parser.add_argument(
        "--model",
        choices=["krea2", "flux2-klein", "qwen-image"],
        help="Override model for all prompts",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=3,
        help="Parallel ComfyUI jobs (default: 3). Use 1 for sequential.",
    )
    parser.add_argument("--force", action="store_true", help="Re-render even if output exists")
    parser.add_argument("--legacy-opt-in", action="store_true", help="Explicit local legacy route only; not paid-job consent")
    args = parser.parse_args()

    if not args.legacy_opt_in or not args.model:
        parser.error("Select one --model and --legacy-opt-in. Cloud uses the project cloud adapter through comfy-mcp, never this legacy batch renderer.")

    root = Path(args.project)
    require_budget_review(root)
    prompt_dir = root / "prompts" / "images"
    output_dir = root / "renders" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.model:
        model_dir = prompt_dir / args.model
        prompt_files = sorted(model_dir.glob("*.yaml")) if model_dir.exists() else []
    else:
        prompt_files = sorted(prompt_dir.glob("*.yaml"))
    if not prompt_files:
        print(f"No prompts found in {prompt_dir}", file=sys.stderr)
        return
    for prompt_file in prompt_files:
        data = yaml.safe_load(prompt_file.read_text(encoding="utf-8"))
        if data.get("model") != args.model:
            parser.error(f"Prompt model mismatch in {prompt_file}; do not silently replace its model")

    # Skip already-rendered unless --force
    if not args.force:
        todo = [p for p in prompt_files if not (output_dir / f"{yaml.safe_load(p.read_text(encoding='utf-8'))['shot_id']}.yaml").exists()]
        if not todo:
            print("All outputs already exist; no automatic retry.")
            return
    else:
        todo = prompt_files

    jobs = max(1, args.jobs)
    print(f"Rendering {len(todo)} image prompts with {jobs} job(s)...")

    if jobs == 1:
        failures = 0
        for pf in todo:
            try:
                _render_one(pf, output_dir, args.model)
                print(f"generated image: {pf.stem}")
            except Exception as exc:
                failures += 1
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)
        if failures:
            raise SystemExit(1)
        return

    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_file = {
            executor.submit(_render_one, pf, output_dir, args.model): pf for pf in todo
        }
        for future in as_completed(future_to_file):
            pf = future_to_file[future]
            try:
                stem = future.result()
                print(f"generated image: {stem}")
            except Exception as exc:
                failures.append((pf.stem, str(exc)))
                print(f"FAILED {pf.stem}: {exc}", file=sys.stderr)

    if failures:
        print(f"\n{len(failures)}/{len(todo)} failed", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
