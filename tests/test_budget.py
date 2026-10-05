from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
import yaml

from budget import budget_state, default_assumptions, estimate_budget, require_budget_review, save_budget
from cloud_policy import DEFAULT_CONFIG, file_sha256, load_cloud_policy
from pipeline.director import FilmDirector
from validation import validate_data

AS_OF = date(2026, 10, 5)


@pytest.fixture
def project(tmp_path):
    (tmp_path / "story").mkdir()
    (tmp_path / "story" / "story.yaml").write_text("story_id: existing_story\nformat:\n  target_duration_seconds: 50\n")
    (tmp_path / "project.yaml").write_text("project_id: existing_project\nduration_seconds: 50\n")
    return tmp_path


def decide(project, **overrides):
    decision = {"approved": True, "scope": "planning_only_not_spend_consent", "estimate_sha256": file_sha256(project / "budget" / "estimate.yaml"), "selected_tier": "tests", "max_spend_usd": 15, "consent_reference": "test-fixture-explicit-review-not-real-consent", **overrides}
    (project / "budget" / "decision.yaml").write_text(yaml.safe_dump(decision))


def test_default_models_and_single_model_per_stage():
    config = load_cloud_policy()
    assert config["default_tier"] == "preparation"
    assert config["policy"]["automatic_spending"] is False
    assert config["tiers"]["tests"]["video"]["model"] == "alibaba/wan-3.0"


def test_three_tiers_low_mean_high_and_known_arithmetic(project):
    assumptions = default_assumptions(project)
    assumptions.update(images=100, references_per_image=4, audio_seconds=0, text_input_tokens=0, text_output_tokens=0, contingency_fraction=0)
    report = estimate_budget(project, assumptions, as_of=AS_OF)
    assert report["tiers"]["tests"]["low"]["total_usd"] == pytest.approx(11.944)  # 100 NB2 images 6.944 + Wan 3.0 50 s x 0.10
    # Veo's aggregate max-length clipping rounds 50s to 52s, explicitly visible.
    assert report["tiers"]["production"]["video_billable_seconds_per_pass"] == 52
    assert report["tiers"]["production"]["low"]["total_usd"] == pytest.approx(24.288)
    for tier in report["tiers"].values():
        assert tier["low"]["total_usd"] <= tier["mean"]["total_usd"] <= tier["high"]["total_usd"]
        assert tier["mean"]["total_usd"] == pytest.approx(2 * tier["low"]["total_usd"])


def test_story_then_budget_gate_preserves_existing_screenplay(project):
    (project / "screenplay").mkdir()
    screenplay = project / "screenplay" / "screenplay.yaml"
    screenplay.write_text("untouched existing screenplay")
    director = FilmDirector(project)
    assert director.status()["screenplay"]
    assert director.next_stage() == "budget"
    with pytest.raises(ValueError, match="Budget review required"):
        director.require_stage("screenplay")
    save_budget(project, as_of=AS_OF)
    assert not (project / "budget" / "decision.yaml").exists()
    assert budget_state(project, as_of=AS_OF)["reason"] == "awaiting_user_review"
    assert screenplay.read_text() == "untouched existing screenplay"


def test_review_requires_matching_explicit_decision(project):
    save_budget(project, as_of=AS_OF)
    decide(project)
    require_budget_review(project, as_of=AS_OF)
    require_budget_review(project, selected_tier="tests", as_of=AS_OF)
    with pytest.raises(ValueError, match="Requested tier differs"):
        require_budget_review(project, selected_tier="production", as_of=AS_OF)
    assert budget_state(project, as_of=AS_OF)["reviewed"]
    for bad in ({"approved": False}, {"consent_reference": " "}, {"estimate_sha256": "0" * 64}, {"selected_tier": "premium"}, {"max_spend_usd": -1}, {"scope": "spend_consent"}):
        decide(project, **bad)
        assert not budget_state(project, as_of=AS_OF)["reviewed"]


def test_changed_estimate_invalidates_old_review(project):
    save_budget(project, as_of=AS_OF)
    decide(project)
    assumptions = default_assumptions(project)
    assumptions["images"] += 1
    save_budget(project, assumptions, as_of=AS_OF)
    assert budget_state(project, as_of=AS_OF)["reason"] == "estimate_changed"


def test_tampered_totals_or_model_fail_closed(project):
    save_budget(project, as_of=AS_OF)
    path = project / "budget" / "estimate.yaml"
    report = yaml.safe_load(path.read_text())
    report["tiers"]["tests"]["mean"]["total_usd"] = 0
    path.write_text(yaml.safe_dump(report))
    decide(project)
    assert not budget_state(project, as_of=AS_OF)["reviewed"]


def test_changed_story_invalidates_review(project):
    save_budget(project, as_of=AS_OF)
    decide(project)
    story = project / "story" / "story.yaml"
    story.write_text(story.read_text() + "new_revision: true\n")
    assert not budget_state(project, as_of=AS_OF)["reviewed"]


def test_config_edit_and_stale_rates_invalidate_review(project, tmp_path):
    save_budget(project, as_of=AS_OF)
    decide(project)
    assert budget_state(project, as_of=date(2026, 12, 5))["reason"] == "pricing_refresh_required"
    changed = tmp_path / "config.yaml"
    config = load_cloud_policy()
    config["tiers"]["tests"]["video"]["pricing"]["output_per_second"] = .5
    changed.write_text(yaml.safe_dump(config))
    assert not budget_state(project, config_path=changed, as_of=AS_OF)["reviewed"]


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_invalid_duration_is_rejected(project, value):
    inputs = default_assumptions(project)
    inputs["duration_seconds"] = value
    with pytest.raises(Exception):
        estimate_budget(project, inputs, as_of=AS_OF)


def test_missing_prices_are_not_zero(project):
    config = load_cloud_policy()
    del config["tiers"]["tests"]["audio"]["pricing"]["output_per_second"]
    config_file = project / "bad-config.yaml"
    config_file.write_text(yaml.safe_dump(config))
    with pytest.raises(Exception):
        estimate_budget(project, config_path=config_file, as_of=AS_OF)


def test_sizing_cannot_upgrade_or_zero_retries(project):
    assumptions = default_assumptions(project)
    assumptions["attempts"] = {"low": 2, "mean": 1, "high": 3}
    with pytest.raises(ValueError):
        estimate_budget(project, assumptions, as_of=AS_OF)
    assumptions = default_assumptions(project)
    assumptions.update(video_fraction=0, audio_seconds=0, images=0)
    for tier in estimate_budget(project, assumptions, as_of=AS_OF)["tiers"].values():
        assert tier["video_clips_per_pass"] == 0
        assert tier["low"]["audio_usd"] == 0  # absent event, not unknown pricing


def test_cloud_and_legacy_prompt_schemas():
    schemas = Path(__file__).resolve().parents[1] / "schemas"
    legacy = {"prompt_id": "existing_prompt", "shot_id": "existing_shot", "model": "qwen-image", "prompt": "text"}
    validate_data(legacy, schemas / "image-prompt.schema.yaml")
    cloud = {**legacy, "model": "google/gemini-3-pro-image", "tier": "production", "route": "openrouter_comfyui", "references": [{"asset_path": "characters/existing.png", "entity_id": "existing_character"}]}
    validate_data(cloud, schemas / "image-prompt.schema.yaml")
    del cloud["tier"]
    with pytest.raises(Exception):
        validate_data(cloud, schemas / "image-prompt.schema.yaml")
    sound = {"prompt_id": "existing_sound", "scene_id": "existing_scene", "model": "bytedance-seed/seed-audio-1-0", "event_kind": "ambience", "prompt": "quiet rain", "tier": "tests", "route": "openrouter_comfyui"}
    validate_data(sound, schemas / "audio-prompt.schema.yaml")
    sound["event_kind"] = "dialogue"
    with pytest.raises(Exception):
        validate_data(sound, schemas / "audio-prompt.schema.yaml")
