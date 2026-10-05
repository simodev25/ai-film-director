"""Offline checks of the expressly NEW scaffold, never a generation test."""
import copy
import json
from pathlib import Path

import pytest

from cloud_policy import load_cloud_policy
from comfyui.cloud_adapters import discover_cloud_binding, prepare_cloud_workflow
from comfyui.cloud_targets import ProjectScope


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/la-pomme"
ARTIFACTS = PROJECT / "workflows/cloud/preparation"
pytestmark = pytest.mark.skipif(not (ARTIFACTS / "seedream-bindings.json").exists(),
                                reason="Optional local project scaffold is not packaged")


def read(name):
    return json.loads((ARTIFACTS / name).read_text())


def test_new_graph_ids_and_fixed_policy_controls():
    graph = read("seedream-scaffold-source.api.json")
    bindings = read("seedream-bindings.json")
    image, output = bindings["declared_node_ids"].values()
    assert set(graph) == {image, output}
    assert graph[image]["class_type"] == "OpenRouterStudioImage"
    assert graph[output]["class_type"] == "SaveImage"
    assert graph[output]["inputs"]["images"] == [image, 0]
    controls = graph[image]["inputs"]
    assert controls["model"] == load_cloud_policy()["tiers"]["preparation"]["image"]["model"]
    assert controls["model.prompt"] == ""  # no creative character prompt
    assert controls["model.size"] == ""  # do not suppress aspect/resolution
    assert controls["model.resolution"] == "1K" and controls["model.aspect_ratio"] == "16:9"
    assert controls["model.n"] == 1 and controls["model.seed"] == -1
    assert not any(key.startswith("model.reference_images.") for key in controls)
    provider = json.loads(controls["model.provider_options_json"])
    assert provider == {"only": ["seed"], "allow_fallbacks": False, "options": {"seed": {}}}
    assert bindings["binding"]["references"] == []
    assert bindings["paid_job_approval"] is None and not bindings["generation_tested"]


def test_actual_adapter_reproduces_technical_bound_copy_only():
    graph = read("seedream-scaffold-source.api.json")
    original = copy.deepcopy(graph)
    config = read("seedream-bindings.json")
    binding = discover_cloud_binding(graph, class_type=config["binding"]["class_type"],
                                     input_map=config["binding"]["input_map"])
    assert binding.node_id == config["binding"]["node_id"]
    probe = {"version": 1, "tier": "preparation", "modality": "image",
             "model": config["exact_model"], "route": config["route"],
             "prompt_id": "technical_adapter_probe_NOT_A_CHARACTER_JOB",
             "prompt": "__TECHNICAL_PLACEHOLDER_NO_GENERATION__",
             "pricing_checked_at": "2026-10-05", "estimated_cost_usd": .018,
             "parameters": {"resolution": "1K", "aspect_ratio": "16:9"},
             "references": [], **config["future_target"]}
    bound = prepare_cloud_workflow(graph, binding, probe, load_cloud_policy(),
                                   node_catalog=read("live-descriptors.selected.json"),
                                   project=PROJECT, scope=ProjectScope(("scene_la_pomme_01",), ("char_marc",)))
    assert graph == original
    assert bound == read("seedream-scaffold-bound.api.json")
    assert bound[config["declared_node_ids"]["output"]] == graph[config["declared_node_ids"]["output"]]
    assert "seed" not in probe["parameters"]


def test_ui_companion_has_same_ids_controls_and_link():
    ui = read("seedream-scaffold-source.ui.json")
    api = read("seedream-scaffold-source.api.json")
    assert ui["links"] == [[1, 1, 0, 2, 0, "IMAGE"]]
    for node in ui["nodes"]:
        source = api[str(node["id"])]
        assert node["type"] == source["class_type"]
        for key, value in node["widgets_values_named"].items():
            assert value == source["inputs"][key]
        assert node["widgets_values"]  # consumed by actual slot converter
