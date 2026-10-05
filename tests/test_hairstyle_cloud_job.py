"""Offline preparation checks only: no upload, HTTP, reserve, approval or run."""
import copy
import json
from pathlib import Path

import pytest
import yaml

from cloud_policy import file_sha256, load_cloud_policy
from comfyui.cloud_adapters import CloudAdapterError, CloudBinding, ReferenceInput, prepare_cloud_workflow, validate_cloud_job
from comfyui.cloud_targets import ProjectScope
from validation import validate_data

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/la-pomme"
FILES = PROJECT / "workflows/cloud/preparation/char_marc-hairstyle-edit-attempt-02"
pytestmark = pytest.mark.skipif(not (FILES / "plan.json").exists(), reason="Optional local hairstyle preparation not packaged")


def read(name):
    return json.loads((FILES / name).read_text())


def parts():
    config = read("bindings.json")["binding"]
    binding = CloudBinding(config["node_id"], config["class_type"], config["input_map"],
                           tuple(ReferenceInput(**r) for r in config["references"]))
    catalog = json.loads((PROJECT / "workflows/cloud/preparation/live-descriptors.selected.json").read_text())
    catalog["LoadImage"] = read("loader-descriptor.live.json")
    return read("source.api.json"), binding, read("plan.json"), catalog


def prepare(graph, binding, job, catalog):
    return prepare_cloud_workflow(graph, binding, job, load_cloud_policy(), node_catalog=catalog,
                                  project=PROJECT, scope=ProjectScope(("scene_la_pomme_01",), ("char_marc",)))


def test_hair_only_source_compilation_and_canonical_asset():
    source = PROJECT / "prompts/references/seedream-5-0-flash/char_marc-hairstyle-edit.yaml"
    prompt = yaml.safe_load(source.read_text())
    validate_data(prompt, ROOT / "schemas/image-prompt.schema.yaml")
    job = read("plan.json")
    validate_cloud_job(job)
    assert job["prompt"] == prompt["prompt"] + "\n\nContraintes d’exclusion (negative_prompt canonique):\n" + prompt["negative_prompt"]
    assert "cheveux courts" not in job["prompt"].lower()
    assert "Ne pas corriger les rides" in job["prompt"] and "un peu plus longs" in job["prompt"]
    assert job["attempt_number"] == 2 and "shot_id" not in job
    assert len(job["references"]) == 1
    refs = read("bindings.json")["ordered_reference_assets"]
    assert len(refs) == 1 and refs[0]["order"] == 1 and not refs[0]["identity_approved"]
    assert file_sha256(PROJECT / refs[0]["asset_path"]) == refs[0]["source_sha256"]
    assert job["references"][0]["uploaded_path"] == refs[0]["uploaded_path"]


def test_real_reference_adapter_preserves_new_source_and_topology():
    graph, binding, job, catalog = parts()
    original = copy.deepcopy(graph)
    result = prepare(graph, binding, job, catalog)
    assert graph == original and result == read("prepared.api.json")
    assert set(result) == {"21", "22", "23"}
    assert result["21"] == graph["21"] and result["23"] == graph["23"]
    assert result["22"]["inputs"]["model.reference_images.reference_1"] == ["21", 0]
    assert result["23"]["inputs"]["images"] == ["22", 0]
    assert [k for k in graph["22"]["inputs"] if graph["22"]["inputs"][k] != result["22"]["inputs"][k]] == ["model.prompt"]
    assert json.loads(result["22"]["inputs"]["model.provider_options_json"])["allow_fallbacks"] is False
    assert result["22"]["inputs"]["model.n"] == 1 and result["22"]["inputs"]["model.seed"] == -1


def test_unresolved_upload_or_missing_reference_plan_fails_closed():
    graph, binding, job, catalog = parts()
    job["references"][0]["uploaded_path"] = "not_a_loaded_input_choice.png"
    with pytest.raises(CloudAdapterError, match="live input choices"):
        prepare(graph, binding, job, catalog)
    job["references"] = []
    with pytest.raises(CloudAdapterError, match="exactly cover configured loaders"):
        prepare(graph, binding, job, catalog)


def test_ui_has_correct_dynamic_prompt_and_visible_reference_wire():
    ui, api = read("preview.ui.json"), read("prepared.api.json")
    nodes = {str(n["id"]): n for n in ui["nodes"]}
    assert set(nodes) == set(api)
    assert ui["links"] == [[1, 21, 0, 22, 0, "IMAGE"], [2, 22, 0, 23, 0, "IMAGE"]]
    assert nodes["21"]["widgets_values"][0] == api["21"]["inputs"]["image"]
    assert nodes["22"]["widgets_values"][0] == api["22"]["inputs"]["model"]
    assert nodes["22"]["widgets_values"][1] == api["22"]["inputs"]["model.prompt"]
    assert nodes["22"]["inputs"] == [{"name": "model.reference_images.reference_1", "type": "IMAGE", "link": 1}]
    assert not list(FILES.glob("*approval*"))
