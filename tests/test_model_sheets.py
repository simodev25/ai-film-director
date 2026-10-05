"""Offline tests: model-sheet splitting, approved-references/shot/sheet_type schemas."""
import copy
import hashlib
import importlib.util
from pathlib import Path

import jsonschema
import pytest
import yaml

from validation import validate_data

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
spec = importlib.util.spec_from_file_location("split_model_sheet", ROOT / "scripts/split_model_sheet.py")
sms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sms)

Image = pytest.importorskip("PIL.Image")
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]


def make_sheet(path, cols=4, cell=(20, 30)):
    image = Image.new("RGB", (cell[0] * cols, cell[1]))
    for i in range(cols):
        image.paste(COLORS[i % 4], (i * cell[0], 0, (i + 1) * cell[0], cell[1]))
    image.save(path)
    return path


def test_grid_boxes_cover_exactly_and_respect_gutter():
    assert sms.grid_boxes(80, 30, 1, 4) == [(0, 0, 20, 30), (20, 0, 40, 30), (40, 0, 60, 30), (60, 0, 80, 30)]
    boxes = sms.grid_boxes(100, 50, 2, 2, margin=5, gutter=10)
    assert boxes[0] == (5, 5, 45, 20) and boxes[-1] == (55, 30, 95, 45)
    with pytest.raises(sms.SheetError):
        sms.grid_boxes(10, 10, 1, 4, margin=5)


def test_split_grid_writes_isolated_pngs_with_hashes(tmp_path):
    sheet = make_sheet(tmp_path / "sheet.png")
    views = ["front", "three_quarter", "profile", "back"]
    entries = sms.split_sheet(sheet, tmp_path / "out", sms.grid_boxes(80, 30, 1, 4), views, relative_to=tmp_path)
    assert [e["view"] for e in entries] == views
    for entry, color in zip(entries, COLORS):
        crop = tmp_path / entry["asset_path"]
        assert not Path(entry["asset_path"]).is_absolute()
        assert hashlib.sha256(crop.read_bytes()).hexdigest() == entry["sha256"]
        with Image.open(crop) as image:
            assert image.size == (20, 30) and image.getpixel((10, 15)) == color
    with pytest.raises(sms.SheetError, match="overwrite"):
        sms.split_sheet(sheet, tmp_path / "out", sms.grid_boxes(80, 30, 1, 4), views)


def test_explicit_boxes_and_invalid_inputs(tmp_path):
    sheet = make_sheet(tmp_path / "sheet.png")
    entries = sms.split_sheet(sheet, tmp_path / "o", sms.parse_boxes("0,0,20,30;60,0,80,30"), ["front", "back"])
    assert [e["box"] for e in entries] == [[0, 0, 20, 30], [60, 0, 80, 30]]
    with pytest.raises(sms.SheetError):
        sms.split_sheet(sheet, tmp_path / "p", [(0, 0, 200, 30)], ["front"])
    with pytest.raises(sms.SheetError):
        sms.parse_views("front,side", 2)
    with pytest.raises(sms.SheetError):
        sms.parse_views("front", 2)
    with pytest.raises(sms.SheetError):
        sms.parse_grid("4")


def test_cli_registry_binding_requires_approved_sheet_hash(tmp_path):
    project = tmp_path / "proj"
    (project / "references").mkdir(parents=True)
    (project / "renders").mkdir()
    sheet = make_sheet(project / "renders/sheet.png")
    registry = project / "references/approved-references.yaml"
    row = {"order": 1, "entity_id": "char_a", "entity_type": "character", "path": "renders/sheet.png",
           "sha256": hashlib.sha256(sheet.read_bytes()).hexdigest()}
    registry.write_text("# header kept\nregistry_version: 1\nproject_id: p\nreferences:\n"
                        + yaml.safe_dump([row], sort_keys=False))
    args = [str(sheet), "--grid", "1x4", "--views", "front,three_quarter,profile,back",
            "--out-dir", str(project / "references/views/char_a"), "--registry", str(registry),
            "--entity-id", "char_a", "--sheet-type", "turnaround"]
    assert sms.main(args) == 0
    text = registry.read_text()
    assert text.startswith("# header kept\n")
    data = yaml.safe_load(text)
    validate_data(data, SCHEMAS / "approved-references.schema.yaml")
    ref = data["references"][0]
    assert ref["sheet_type"] == "turnaround" and len(ref["views"]) == 4
    assert ref["views"][0]["asset_path"] == "references/views/char_a/sheet_01_front.png"
    # Existing views are never silently replaced; a wrong entity writes no crop.
    assert sms.main(args + ["--overwrite"]) == 2
    assert sms.main([str(sheet), "--grid", "1x4", "--views", "front,three_quarter,profile,back",
                     "--out-dir", str(project / "x"), "--registry", str(registry), "--entity-id", "char_b"]) == 2
    assert not (project / "x").exists()


def test_approved_references_schema_accepts_project_and_rejects_bad_views():
    schema = SCHEMAS / "approved-references.schema.yaml"
    path = ROOT / "projects/la-pomme/references/approved-references.yaml"
    if path.exists():
        validate_data(yaml.safe_load(path.read_text()), schema)
    doc = {"registry_version": 1, "project_id": "p", "references": [
        {"order": 1, "entity_id": "char_a", "entity_type": "character", "path": "a.png", "sha256": "a" * 64,
         "sheet_type": "turnaround", "views": [{"view": "profile", "asset_path": "v.png", "sha256": "b" * 64}]}]}
    validate_data(doc, schema)
    for bad in ({"view": "side", "asset_path": "v.png", "sha256": "b" * 64}, {"view": "front", "asset_path": "v.png"}):
        broken = copy.deepcopy(doc)
        broken["references"][0]["views"] = [bad]
        with pytest.raises(jsonschema.ValidationError):
            validate_data(broken, schema)


def test_sheet_type_only_on_reference_illustrations():
    base = {"prompt_id": "p1", "model": "bytedance-seed/seedream-5-0-flash", "prompt": "x",
            "tier": "preparation", "route": "openrouter_comfyui"}
    ref = {**base, "job_kind": "reference_illustration", "entity_id": "char_a", "entity_type": "character",
           "scene_id": "s", "project_id": "p", "sheet_type": "turnaround"}
    validate_data(ref, SCHEMAS / "image-prompt.schema.yaml")
    with pytest.raises(jsonschema.ValidationError):
        validate_data({**ref, "sheet_type": "poster"}, SCHEMAS / "image-prompt.schema.yaml")
    with pytest.raises(jsonschema.ValidationError):
        validate_data({**base, "shot_id": "shot_1", "sheet_type": "turnaround"}, SCHEMAS / "image-prompt.schema.yaml")
    job = {"version": 1, "tier": "preparation", "modality": "image", "model": "bytedance-seed/seedream-5-0-flash",
           "route": "/api/v1/images", "prompt_id": "p1", "prompt": "x", "pricing_checked_at": "2026-10-05",
           "estimated_cost_usd": 0.018, "job_kind": "reference_illustration", "entity_id": "char_a",
           "entity_type": "character", "scene_id": "s", "project_id": "p", "sheet_type": "expression"}
    validate_data(job, SCHEMAS / "cloud-job.schema.yaml")
    shot_job = {k: v for k, v in job.items() if k not in {"job_kind", "entity_id", "entity_type"}}
    with pytest.raises(jsonschema.ValidationError):
        validate_data({**shot_job, "shot_id": "shot_1"}, SCHEMAS / "cloud-job.schema.yaml")


def test_shot_schema_accepts_cloud_ids_reference_views_and_project_files():
    schema = SCHEMAS / "shot.schema.yaml"
    shot = {"shot_id": "s1", "scene_id": "sc", "sequence": 1, "shot_size": "MS", "subject": "x", "action": "y",
            "duration": 4}
    for image, video in (("krea2", "ltx-2.5"), ("bytedance-seed/seedream-5-0-flash", "google/veo-3.1-lite"),
                         ("google/gemini-3.1-flash-image", "alibaba/wan-3.0"), ("google/gemini-3-pro-image", "google/veo-3.1")):
        validate_data({"shots": [{**shot, "image_model": image, "video_model": video,
                                  "reference_views": [{"entity_id": "char_a", "view": "three_quarter", "asset_path": "a.png"}]}]}, schema)
    for bad in ({"image_model": "nano-banana"}, {"video_model": "kwaivgi/kling-v3.0-pro"},
                {"reference_views": [{"entity_id": "c", "view": "side", "asset_path": "a"}]},
                {"cloud_route": {"tier": "preparation", "route": "openrouter_comfyui", "image": {"model": "qwen-image"}}}):
        with pytest.raises(jsonschema.ValidationError):
            validate_data({**shot, **bad}, schema)
    for rel in ("shots/shots.yaml", "storyboard/planned-shots.yaml"):
        path = ROOT / "projects/la-pomme" / rel
        if path.exists():
            validate_data(yaml.safe_load(path.read_text()), schema)
