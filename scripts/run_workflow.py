import argparse
from pathlib import Path

import yaml

from comfyui.client import ComfyUIClient
from comfyui.adapters import prepare_workflow
from config import (
    COMFYUI_URL,
    COMFYUI_TIMEOUT,
    POLL_INTERVAL,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("model")
    parser.add_argument("prompt")

    parser.add_argument("--negative", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--legacy-opt-in", action="store_true", help="Explicit local legacy execution; not permission for paid nodes")

    args = parser.parse_args()

    if not args.legacy_opt_in:
        parser.error("Local legacy execution requires --legacy-opt-in; cloud jobs use the gated project adapter + comfy-mcp")

    workflow = prepare_workflow(
        args.model,
        args.prompt,
        args.negative,
        args.seed,
    )

    client = ComfyUIClient(
        COMFYUI_URL,
        COMFYUI_TIMEOUT,
        POLL_INTERVAL,
        legacy_opt_in=True,
    )

    result = client.execute(workflow)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            yaml.safe_dump(result, sort_keys=False),
            encoding="utf-8",
        )

    print(result)


if __name__ == "__main__":
    main()
