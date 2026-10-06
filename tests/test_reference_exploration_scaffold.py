"""Offline integrity checks of the expressly authorized new project graph.

These tests do not execute a model, upload assets, initialize a ledger or claim
that exploratory references complete any canonical film production stage.
"""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from cloud_policy import load_cloud_policy
from comfyui.cloud_adapters import ReferenceInput, discover_cloud_binding, _input_specs


PROJECT = Path(__file__).resolve().parents[1] / "projects/la-pomme"
ROOT = PROJECT / "workflows/cloud/preparation/reference-exploration"
pytestmark = pytest.mark.skipif(
    not (ROOT / "scaffold.api.json").exists(),
    reason="Optional project-owned reference scaffold not packaged",
)


def read(name):
    return json.loads((ROOT / name).read_text())


def test_explicit_new_graph_binding_and_links():
    graph, cfg = read("scaffold.api.json"), read("bindings.json")
    ids = cfg["declared_node_ids"]
    assert set(graph) == {ids["image"], ids["output"], *ids["loaders"]}
    refs = tuple(ReferenceInput(**r) for r in cfg["binding"]["references"])
    binding = discover_cloud_binding(
        graph, class_type=cfg["binding"]["class_type"],
        input_map=cfg["binding"]["input_map"], references=refs,
    )
    assert binding.node_id == ids["image"]
    assert graph[ids["output"]]["inputs"]["images"] == [ids["image"], 0]
    assert len(refs) == 1
    assert graph[ids["image"]]["inputs"][refs[0].target_input] == [refs[0].node_id, 0]
    assert graph[refs[0].node_id]["class_type"] == "LoadImage"
    assert cfg["paid_job_approval"] is None
    assert cfg["generation_tested"] is False


def test_exact_live_branch_and_single_model_policy():
    graph, cfg = read("scaffold.api.json"), read("bindings.json")
    controls = graph[cfg["declared_node_ids"]["image"]]["inputs"]
    profile = load_cloud_policy()["tiers"]["preparation"]["image"]
    assert controls["model"] == cfg["exact_model"] == profile["model"]
    catalog = read("node-catalog.selected.live.json")
    specs = _input_specs(catalog["OpenRouterStudioImage"], profile["model"])
    assert not {k for k in controls if k.startswith("model.")} - set(specs)
    for key, spec in specs.items():
        if spec.get("required") and not spec.get("is_link"):
            assert key in controls
    assert controls["model.resolution"] == profile["defaults"]["resolution"] == "1K"
    assert controls["model.aspect_ratio"] == "16:9"
    assert controls["model.n"] == 1
    assert controls["model.size"] == ""
    assert controls["model.seed"] == -1  # unchanged provider default, no seed override
    provider = json.loads(controls["model.provider_options_json"])
    assert provider == {"only": ["seed"], "allow_fallbacks": False, "options": {"seed": {}}}
    assert catalog["SaveImage"]["output_node"] is True
    assert controls["model.prompt"] == "__TECHNICAL_SCAFFOLD_ONLY_DO_NOT_GENERATE__"


def test_source_identity_is_real_not_other_server_inputs():
    registry = yaml.safe_load((PROJECT / "references/approved-references.yaml").read_text())
    source = next(r for r in registry["references"] if r["entity_id"] == "char_001")
    asset = PROJECT / source["path"]
    assert hashlib.sha256(asset.read_bytes()).hexdigest() == source["sha256"]
    story = yaml.safe_load((PROJECT / "story/story.yaml").read_text())
    assert "char_001" in story["characters"]
    graph, cfg = read("scaffold.api.json"), read("bindings.json")
    name = graph[cfg["declared_node_ids"]["loaders"][0]]["inputs"]["image"]
    assert source["sha256"][:16] in name
    assert "char_001" in name
    assert "char_marc" not in name
