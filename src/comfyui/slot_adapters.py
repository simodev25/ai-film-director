"""Explicit frontend slot plans; application is delegated to comfy-mcp.

Unlike the legacy API-dictionary adapter this never edits graph topology or
subgraph definitions. Call list_workflow_slots first, build this plan, then pass
its structured overrides to set_workflow_slot on a dedicated workflow copy.
"""
from __future__ import annotations

from typing import Any


SLOT_ADAPTERS = {
    "anima-base-v1": {
        "template": "image_anima_base_v1",
        "slots": {
            "prompt": "90.text",
            "negative_prompt": "90.text_1",
            "seed": "90.seed",
            "aspect_ratio": "91.aspect_ratio",
            "megapixels": "91.megapixels",
            "multiple": "91.multiple",
            "filename_prefix": "46.filename_prefix",
            "turbo": "90.value",
        },
        "models": {
            "90.unet_name": "anima-base-v1.0.safetensors",
            "90.clip_name": "qwen_3_06b_base.safetensors",
            "90.vae_name": "qwen_image_vae.safetensors",
            "90.lora_name": "anima-turbo-lora-v0.2.safetensors",
        },
    },
}


def prepare_slot_plan(
    source: dict[str, Any],
    observed_slots: list[dict[str, Any]],
    *,
    test_model: str,
    seed: int,
    width: int = 1024,
    height: int = 576,
    filename_prefix: str,
    turbo: bool | None = None,
    aspect_ratio: str = "16:9",
) -> dict[str, Any]:
    """Validate discovered addresses, then return a typed MCP injection plan.

    This intentionally requires an explicit test_model; source.model remains
    provenance, not a silently overwritten canonical model choice. This small
    adapter supports one approved exploratory T2I route, not general rendering.
    Dimension inputs are upstream ResolutionSelector slots, never linked latent
    widgets. Frames/fps and media inputs are not applicable to this still route.
    """
    if test_model not in SLOT_ADAPTERS:
        raise ValueError(f"Unknown slot adapter: {test_model}")
    if not isinstance(source.get("prompt"), str) or not source["prompt"].strip():
        raise ValueError("A nonempty canonical prompt is required")
    if not isinstance(source.get("shot_id"), str) or not source["shot_id"]:
        raise ValueError("A canonical shot_id is required")
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("seed must be an unsigned 64-bit integer")
    ratios = {"16:9": (16, 9, "16:9 (Widescreen)"),
              "9:16": (9, 16, "9:16 (Portrait Widescreen)")}
    if aspect_ratio not in ratios:
        raise ValueError("Only explicitly requested 16:9 or 9:16 is supported")
    ratio_width, ratio_height, ratio_slot_value = ratios[aspect_ratio]
    if source.get("aspect_ratio", aspect_ratio) != aspect_ratio:
        raise ValueError("Requested aspect_ratio conflicts with source prompt")
    if (type(width) is not int or type(height) is not int or
            width <= 0 or height <= 0 or width * ratio_height != height * ratio_width or
            width % 16 or height % 16):
        raise ValueError("Dimensions must match the explicit aspect_ratio and be divisible by 16")
    if width * height > 1024 * 576:
        raise ValueError("Exploratory local test is limited to 1024x576")
    source_adapter = source.get("source_adapter", {})
    if not isinstance(source_adapter, dict):
        raise ValueError("source_adapter must be a mapping")
    if ("turbo" in source and "turbo" in source_adapter and
            source["turbo"] != source_adapter["turbo"]):
        raise ValueError("Source turbo fields disagree")
    source_turbo = source.get("turbo", source_adapter.get("turbo", True))
    if turbo is None:
        turbo = source_turbo
    if type(turbo) is not bool or type(source_turbo) is not bool:
        raise ValueError("turbo must be boolean")
    if ("turbo" in source or "turbo" in source_adapter) and turbo != source_turbo:
        raise ValueError("Requested turbo conflicts with source prompt")
    if not isinstance(filename_prefix, str) or not filename_prefix:
        raise ValueError("An explicit output prefix is required")
    negative = source.get("negative_prompt", "")
    if not isinstance(negative, str):
        raise ValueError("negative_prompt must be a string")

    config = SLOT_ADAPTERS[test_model]
    slots = config["slots"]
    observed = {s["address"]: s for s in observed_slots}
    required = set(slots.values()) | set(config["models"])
    missing = required - set(observed)
    if missing:
        raise ValueError(f"Discovered workflow is missing configured slots: {sorted(missing)}")
    for address, expected in config["models"].items():
        if observed[address].get("current_value") != expected:
            raise ValueError(f"Unexpected model at {address}; expected {expected}")
    values = {
        "prompt": source["prompt"], "negative_prompt": negative, "seed": seed,
        "aspect_ratio": ratio_slot_value,
        "megapixels": width * height / 1_000_000,
        "multiple": 16, "filename_prefix": filename_prefix, "turbo": turbo,
    }
    for name, value in values.items():
        slot = observed[slots[name]]
        if slot.get("linked_from") is not None:
            raise ValueError(f"Cannot override linked configured slot {slots[name]}")
        if slot.get("enum") and value not in slot["enum"]:
            raise ValueError(f"Value is not supported by {slots[name]}")
    return {
        "adapter": test_model,
        "template": config["template"],
        "shot_id": source["shot_id"],
        "source_prompt_id": source.get("prompt_id"),
        "source_model": source.get("model"),
        "source_status": source.get("status"),
        "test_model": test_model,
        "exploratory_only": True,
        "seed": seed, "requested_width": width, "requested_height": height,
        "requested_aspect_ratio": aspect_ratio, "turbo": turbo,
        "frames": None, "fps": None, "image_input": None, "audio_input": None,
        "overrides": [{"address": slots[name], "value": value}
                      for name, value in values.items()],
    }
