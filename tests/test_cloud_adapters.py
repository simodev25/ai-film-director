"""Offline fixtures use input names observed by MCP nodes(get), not fake models."""
import copy
from dataclasses import asdict
from datetime import date

import pytest

from comfyui.cloud_adapters import (
    CloudAdapterError, CloudBinding, ReferenceInput, authorize_cloud_job,
    discover_cloud_binding, prepare_cloud_workflow, sha256_document,
    validate_cloud_job,
)


def spec(name, kind="STRING", **kwargs):
    return {"name": name, "type": kind, "is_link": False, **kwargs}


@pytest.fixture
def setup():
    model = "bytedance-seed/seedream-5-0-flash"
    graph = {
        "caller-image": {"class_type": "OpenRouterImageGenerate", "inputs": {
            "model": model, "prompt": "old", "seed": 42,
            "resolution": "1K", "aspect_ratio": "16:9", "count": 1,
        }},
        "caller-output": {"class_type": "SaveImage", "inputs": {
            "images": ["caller-image", 0], "filename_prefix": "existing-output"}},
    }
    config = {"version": 1, "currency": "USD", "pricing_checked_at": "2026-10-04",
              "tiers": {"preparation": {"image": {"model": model,
                  "pricing": {"output_per_image": .018},
                  "capabilities": {"resolutions": ["1K", "2K"],
                                   "aspect_ratios": ["16:9", "1:1"],
                                   "max_references": 14, "seed": True},
                  "defaults": {"resolution": "1K", "aspect_ratio": "16:9"}}}}}
    job = {"version": 1, "tier": "preparation", "modality": "image", "model": model,
           "route": "/api/v1/images", "prompt_id": "existing-prompt", "shot_id": "existing-shot",
           "prompt": "A rainy street.", "parameters": {"seed": 7}, "references": [],
           "estimated_cost_usd": .018, "pricing_checked_at": "2026-10-04"}
    catalog = {
        "OpenRouterImageGenerate": {"name": "OpenRouterImageGenerate", "is_api_node": False,
            "inputs": [spec("model"), spec("prompt"),
                       spec("seed", "INT", options={"min": 0, "max": 4294967295}),
                       spec("resolution", "COMBO", choices=["1K", "2K", "4K"]),
                       spec("aspect_ratio", "COMBO", choices=["16:9", "1:1"]),
                       spec("references", "IMAGE", is_link=True)]},
        "SaveImage": {"name": "SaveImage", "output_node": True, "inputs": []},
        "LoadImage": {"name": "LoadImage", "inputs": [spec("image")]},
    }
    binding = discover_cloud_binding(graph, class_type="OpenRouterImageGenerate", input_map={
        "model": "model", "prompt": "prompt", "seed": "seed",
        "resolution": "resolution", "aspect_ratio": "aspect_ratio"})
    return graph, binding, job, config, catalog


def prepare(parts):
    graph, binding, job, config, catalog = parts
    return prepare_cloud_workflow(graph, binding, job, config, node_catalog=catalog)


def approval_for(graph, job):
    return {"approved": True, "scope": "paid_generation_job", "tier": job["tier"], "model": job["model"], "route": job["route"],
            "workflow_sha256": sha256_document(graph), "plan_sha256": sha256_document(job),
            "estimate_sha256": "a" * 64, "ceiling_usd": .1,
            "consent_reference": "explicit-user-job-consent"}


def gate(graph, job, config, approval, **kwargs):
    return authorize_cloud_job(graph, job, config, approval, budget_estimate_sha256="a" * 64,
                               today=date(2026, 10, 4), **kwargs)


def test_deep_copy_literal_mapping_preserves_topology_and_ids(setup):
    original = copy.deepcopy(setup[0])
    result = prepare(setup)
    assert setup[0] == original
    assert result.keys() == original.keys()
    assert result["caller-image"]["inputs"]["prompt"] == setup[2]["prompt"]
    assert result["caller-image"]["inputs"]["seed"] == 7
    assert result["caller-output"] == original["caller-output"]
    result["caller-output"]["inputs"]["images"][0] = "mutated-copy"
    assert setup[0] == original


@pytest.mark.parametrize("field,value", [("model", "local-alias"), ("tier", "production"),
                                           ("route", "/api/v1/videos")])
def test_no_model_alias_tier_or_route_fallback(setup, field, value):
    setup[2][field] = value
    with pytest.raises(CloudAdapterError):
        prepare(setup)


@pytest.mark.parametrize("parameter,value", [("width", 1920), ("height", 1080),
                                               ("frames", 97), ("fps", 24)])
def test_unsupported_dimensions_frames_fps_never_silently_dropped(setup, parameter, value):
    setup[2]["parameters"][parameter] = value
    with pytest.raises(CloudAdapterError, match="does not support"):
        prepare(setup)


def test_supported_but_unmapped_parameter_is_blocker(setup):
    setup[3]["tiers"]["preparation"]["image"]["capabilities"]["width"] = True
    setup[2]["parameters"]["width"] = 1920
    with pytest.raises(CloudAdapterError, match="No verified configured input for width"):
        prepare(setup)


def test_linked_prompt_not_replaced(setup):
    setup[0]["caller-image"]["inputs"]["prompt"] = ["caller-output", 0]
    with pytest.raises(CloudAdapterError, match="topology"):
        prepare(setup)


def test_discovery_never_picks_first_ambiguous_class(setup):
    setup[0]["second"] = copy.deepcopy(setup[0]["caller-image"])
    with pytest.raises(CloudAdapterError, match="ambiguous"):
        discover_cloud_binding(setup[0], class_type=setup[1].class_type,
                               input_map=setup[1].input_map)


def with_reference(setup, path="uploads/entity.png"):
    graph, binding, job, config, catalog = setup
    graph["existing-loader"] = {"class_type": "LoadImage", "inputs": {"image": "original.png"}}
    graph[binding.node_id]["inputs"]["references"] = ["existing-loader", 0]
    job["references"] = [{"role": "reference", "uploaded_path": path}]
    new_binding = CloudBinding(binding.node_id, binding.class_type, binding.input_map,
                               (ReferenceInput("existing-loader", "image", "references"),))
    return graph, new_binding, job, config, catalog


def test_uploaded_image_reference_uses_existing_loader_no_rewire(setup):
    parts = with_reference(setup)
    original = copy.deepcopy(parts[0])
    result = prepare(parts)
    assert result["existing-loader"]["inputs"]["image"] == "uploads/entity.png"
    assert result["caller-image"]["inputs"]["references"] == ["existing-loader", 0]
    assert parts[0] == original


@pytest.mark.parametrize("path", ["https://site/image.png", "/Users/private.png", "../escape.png",
                                  "foo\nbar.png", "C:\\private.png", "./normal.png"])
def test_invalid_reference_paths_block(setup, path):
    with pytest.raises(CloudAdapterError, match="input-relative"):
        prepare(with_reference(setup, path))


def test_reference_topology_and_inherited_references_require_exact_plan(setup):
    parts = with_reference(setup)
    parts[0]["caller-image"]["inputs"]["references"] = ["caller-output", 0]
    with pytest.raises(CloudAdapterError, match="reference bundle topology"):
        prepare(parts)
    parts[0]["caller-image"]["inputs"]["references"] = ["existing-loader", 0]
    setup[2]["references"] = []
    with pytest.raises(CloudAdapterError, match="Inherited media link"):
        prepare(setup)


def test_model_reference_cap_never_truncates(setup):
    setup[2]["references"] = [{"role": "reference", "uploaded_path": f"r{i}.png"} for i in range(15)]
    with pytest.raises(CloudAdapterError, match="count exceeds"):
        prepare(setup)


def test_unloaded_class_missing_output_and_unreviewed_paid_node_block(setup):
    del setup[4]["SaveImage"]
    with pytest.raises(CloudAdapterError, match="live catalog"):
        prepare(setup)
    setup[4]["SaveImage"] = {"name": "SaveImage", "is_api_node": True, "output_node": True}
    with pytest.raises(CloudAdapterError, match="Additional paid"):
        prepare(setup)
    setup[4]["SaveImage"]["is_api_node"] = False
    setup[4]["SaveImage"]["output_node"] = False
    with pytest.raises(CloudAdapterError, match="output node"):
        prepare(setup)


def test_workflow_credentials_prohibited_without_echoing_secret(setup):
    setup[0]["caller-image"]["inputs"]["api_key"] = "sentinel-secret"
    with pytest.raises(CloudAdapterError) as error:
        prepare(setup)
    assert "sentinel-secret" not in str(error.value)


def test_paid_false_api_node_is_still_gated_and_unknown_actual_cost(setup):
    graph = prepare(setup)
    with pytest.raises(CloudAdapterError, match="Explicit spend"):
        gate(graph, setup[2], setup[3], approval_for(graph, setup[2]))
    record = gate(graph, setup[2], setup[3], approval_for(graph, setup[2]), workflow_validated=True)
    assert record.paid is True
    assert record.actual_cost_usd is None
    assert record.attempts == ()
    assert record.transport == "comfy-mcp"
    assert asdict(record)["prompt_id"] == "existing-prompt"


def test_planning_approval_cannot_be_used_as_spending_consent(setup):
    graph = prepare(setup)
    approval = approval_for(graph, setup[2])
    approval["scope"] = "planning_only_not_spend_consent"
    with pytest.raises(CloudAdapterError, match="not planning only"):
        gate(graph, setup[2], setup[3], approval, workflow_validated=True)


def test_price_age_uses_configured_limit(setup):
    graph = prepare(setup)
    setup[3]["pricing_max_age_days"] = 1
    setup[3]["pricing_checked_at"] = "2026-10-02"
    with pytest.raises(CloudAdapterError, match="configured age limit"):
        gate(graph, setup[2], setup[3], approval_for(graph, setup[2]), workflow_validated=True)


@pytest.mark.parametrize("change", ["declined", "wrong_model", "changed_graph", "changed_estimate",
                                     "ceiling", "missing_consent", "stale", "future", "unknown", "zero"])
def test_gate_fails_closed(setup, change):
    graph = prepare(setup)
    job, config = setup[2], setup[3]
    approval = approval_for(graph, job)
    if change == "declined":
        approval["approved"] = False
    elif change == "wrong_model":
        approval["model"] = "other/exact-id"
    elif change == "changed_graph":
        graph["caller-image"]["inputs"]["prompt"] = "new unapproved prompt"
    elif change == "changed_estimate":
        approval["estimate_sha256"] = "b" * 64
    elif change == "ceiling":
        approval["ceiling_usd"] = .001
    elif change == "missing_consent":
        del approval["consent_reference"]
    elif change == "stale":
        config["pricing_checked_at"] = "2026-08-01"
    elif change == "future":
        config["pricing_checked_at"] = "2026-10-05"
    elif change in ("unknown", "zero"):
        job["estimated_cost_usd"] = None if change == "unknown" else 0
        approval = approval_for(graph, job)
    with pytest.raises(CloudAdapterError):
        gate(graph, job, config, approval, workflow_validated=True)


def test_schema_rejects_extra_keys_and_invalid_seed(setup):
    setup[2]["parameters"]["seed"] = -1
    with pytest.raises(CloudAdapterError, match="Invalid cloud job"):
        validate_cloud_job(setup[2])


def test_studio_dynamic_inputs_verified_for_exact_model(setup):
    graph, binding, job, config, catalog = setup
    inputs = graph["caller-image"]["inputs"]
    graph["caller-image"]["inputs"] = {("model" if key == "model" else f"model.{key}"): value
                                         for key, value in inputs.items()}
    graph["caller-image"]["class_type"] = "OpenRouterStudioImage"
    flat = catalog["OpenRouterImageGenerate"]["inputs"]
    catalog["OpenRouterStudioImage"] = {"name": "OpenRouterStudioImage", "inputs": [
        spec("model", "COMFY_DYNAMICCOMBO_V3", selection_keys=[job["model"]], dynamic_options=[
            {"key": job["model"], "inputs": [{**item, "name": f"model.{item['name']}"}
                                             for item in flat if item["name"] != "model"]}])]}
    studio = CloudBinding("caller-image", "OpenRouterStudioImage", {
        key: ("model" if key == "model" else f"model.{key}") for key in binding.input_map})
    assert prepare((graph, studio, job, config, catalog))["caller-image"]["inputs"]["model.prompt"] == job["prompt"]
    catalog["OpenRouterStudioImage"]["inputs"][0]["dynamic_options"] = []
    with pytest.raises(CloudAdapterError, match="absent from live"):
        prepare((graph, studio, job, config, catalog))


def test_nonverbal_audio_empty_voice_mapping_is_required(setup):
    graph, _, job, config, catalog = setup
    model = "bytedance-seed/seed-audio-1-0"
    job.update(modality="audio", model=model, route="/api/v1/audio/speech", parameters={})
    config["tiers"]["preparation"]["audio"] = {"model": model, "capabilities": {"non_speech": True}}
    graph["caller-image"] = {"class_type": "OpenRouterAudioSpeak", "inputs": {
        "model": model, "text": "old", "voice": "Kore"}}
    catalog["OpenRouterAudioSpeak"] = {"name": "OpenRouterAudioSpeak", "inputs": [
        spec("model"), spec("text"), spec("voice")]}
    binding = CloudBinding("caller-image", "OpenRouterAudioSpeak", {
        "model": "model", "prompt": "text", "voice": "voice"})
    result = prepare((graph, binding, job, config, catalog))
    assert result["caller-image"]["inputs"]["voice"] == ""
    assert graph["caller-image"]["inputs"]["voice"] == "Kore"


def test_reference_bundle_order_and_count_not_just_reachability(setup):
    graph, binding, job, config, catalog = with_reference(setup)
    graph["second-loader"] = {"class_type": "LoadImage", "inputs": {"image": "old2.png"}}
    graph["existing-batch"] = {"class_type": "ImageBatch", "inputs": {
        "image1": ["existing-loader", 0], "image2": ["second-loader", 0]}}
    graph["caller-image"]["inputs"]["references"] = ["existing-batch", 0]
    catalog["ImageBatch"] = {"name": "ImageBatch", "inputs": [
        spec("image1", "IMAGE", is_link=True), spec("image2", "IMAGE", is_link=True)]}
    job["references"].append({"role": "reference", "uploaded_path": "second.png"})
    slots = (*binding.references, ReferenceInput("second-loader", "image", "references"))
    bundle = CloudBinding(binding.node_id, binding.class_type, binding.input_map, slots)
    result = prepare((graph, bundle, job, config, catalog))
    assert result["second-loader"]["inputs"]["image"] == "second.png"
    reversed_bundle = CloudBinding(binding.node_id, binding.class_type, binding.input_map, tuple(reversed(slots)))
    with pytest.raises(CloudAdapterError, match="order/count"):
        prepare((graph, reversed_bundle, job, config, catalog))


def test_video_duration_first_last_and_audio_use_verified_existing_inputs(setup):
    graph, _, job, config, catalog = setup
    model = "google/veo-3.1-lite"
    job.update(modality="video", model=model, route="/api/v1/videos", parameters={"duration": 6})
    config["tiers"]["preparation"]["video"] = {
        "model": model, "capabilities": {"durations": [4, 6, 8], "resolutions": ["720p", "1080p"],
                                            "first_last_frame": True, "audio": True},
        "defaults": {"resolution": "720p", "audio": False}}
    graph["caller-image"] = {"class_type": "OpenRouterVideoGenerate", "inputs": {
        "model": model, "prompt": "old", "duration": 4, "resolution": "720p", "generate_audio": "on",
        "first_frame": ["first-loader", 0], "last_frame": ["last-loader", 0],
        "reference_audio": ["audio-loader", 0]}}
    graph["first-loader"] = {"class_type": "LoadImage", "inputs": {"image": "old-first.png"}}
    graph["last-loader"] = {"class_type": "LoadImage", "inputs": {"image": "old-last.png"}}
    graph["audio-loader"] = {"class_type": "LoadAudio", "inputs": {"audio": "old.wav"}}
    catalog["LoadAudio"] = {"name": "LoadAudio", "inputs": [spec("audio")]}
    catalog["OpenRouterVideoGenerate"] = {"name": "OpenRouterVideoGenerate", "inputs": [
        spec("model"), spec("prompt"), spec("duration", "INT"),
        spec("resolution", "COMBO", choices=["720p", "1080p"]),
        spec("generate_audio", "COMBO", choices=["model default", "on", "off"]),
        spec("first_frame", "IMAGE", is_link=True), spec("last_frame", "IMAGE", is_link=True),
        spec("reference_audio", "AUDIO", is_link=True)]}
    binding = CloudBinding("caller-image", "OpenRouterVideoGenerate", {
        "model": "model", "prompt": "prompt", "duration": "duration", "resolution": "resolution",
        "generate_audio": "generate_audio"}, (
            ReferenceInput("first-loader", "image", "first_frame", "first_frame"),
            ReferenceInput("last-loader", "image", "last_frame", "last_frame"),
            ReferenceInput("audio-loader", "audio", "reference_audio", "audio")))
    job["references"] = [{"role": "first_frame", "uploaded_path": "first.png"},
                         {"role": "last_frame", "uploaded_path": "last.png"},
                         {"role": "audio", "uploaded_path": "reference.wav"}]
    result = prepare((graph, binding, job, config, catalog))
    assert result["caller-image"]["inputs"]["duration"] == 6
    assert result["caller-image"]["inputs"]["generate_audio"] == "off"
    assert result["audio-loader"]["inputs"]["audio"] == "reference.wav"
    assert result["first-loader"]["inputs"]["image"] == "first.png"
    assert result["last-loader"]["inputs"]["image"] == "last.png"
    assert result["caller-image"]["inputs"]["reference_audio"] == ["audio-loader", 0]
    job["parameters"]["duration"] = 5
    with pytest.raises(CloudAdapterError, match="does not support duration"):
        prepare((graph, binding, job, config, catalog))
