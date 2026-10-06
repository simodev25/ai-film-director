"""Dashboard fixtures are deliberately unrelated to any checked-in film project."""

import datetime as dt
import contextlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.parse import quote

import yaml

from dashboard.catalog import Catalog
from dashboard.server import main, make_server, validate_host


class DashboardFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "films"
        self.root.mkdir()
        self.project_id = "atelier été"
        self.first = self.root / self.project_id
        self.first.mkdir()
        self.second = self.root / "unfinished"
        self.second.mkdir()
        self.write(self.first, "project.yaml", {
            "project_id": "project_atelier", "title": "Atelier d’été",
            "genre": "Drama", "aspect_ratio": "16:9", "fps": 24,
        })
        self.write(self.first, "story/story.yaml", {
            "story_id": "story_atelier", "title": "Atelier d’été", "logline": "Un retour.",
            "premise": "Retrouver un atelier.", "acts": [],
        })
        self.write(self.first, "screenplay/screenplay.yaml", {
            "screenplay_id": "screenplay_atelier", "scenes": [{
                "scene_id": "scene_atelier", "scene_number": 1,
                "heading": "INT. ATELIER", "location_id": "loc_room",
                "time": "DAY", "action": "Entrer.",
            }],
        })
        self.write(self.first, "shots/shots.yaml", {"shots": [
            {"shot_id": "shot_atelier_1", "scene_id": "scene_atelier", "sequence": 1,
             "shot_size": "wide", "subject": "La porte", "action": "Entrer.",
             "duration": 4, "characters": ["char_alice"], "prop_ids": ["prop_key"]},
            {"shot_id": "shot_atelier_2", "scene_id": "scene_missing", "sequence": 2,
             "shot_size": "close", "subject": "La clé", "action": "Tenir.",
             "duration": 2, "characters": ["char_missing"]},
        ]})
        self.write(self.first, "characters/characters.yaml", [{
            "character_id": "char_alice", "name": "Alice", "role": "protagonist",
            "identity": {"age": "30", "appearance": "Manteau bleu."},
        }])
        self.write(self.first, "locations/locations.yaml", [{
            "location_id": "loc_room", "name": "Atelier", "description": "Bois et lumière.",
            "visual_anchors": ["porte"],
        }])
        self.write(self.first, "props/props.yaml", {"key": {
            "prop_id": "prop_key", "name": "Clé", "description": "Cuivre.",
        }})
        self.write(self.first, "prompts/images/qwen-image/door.yaml", {
            "prompt_id": "prompt_door", "shot_id": "shot_atelier_1", "model": "qwen-image",
            "prompt": "Une porte.",
            "reference_assets": [{"entity_id": "char_alice", "path": "assets/alice.png"}],
        })
        self.write(self.first, "renders/tests/run.yaml", {
            "shot_id": "shot_atelier_1", "source_prompt_id": "prompt_door",
            "output_files": [f"films/{self.project_id}/renders/tests/result.png"],
            "production_final": False, "approved": False,
        })
        self.write(self.first, "renders/production-tests/run.yaml", {
            "shot_id": "shot_atelier_2", "output_files": ["renders/production-tests/detail.mp4"],
        })
        self.binary(self.first, "renders/tests/result.png", b"fake image")
        self.binary(self.first, "renders/tests/shot_atelier_1_variant.png", b"heuristic")
        self.binary(self.first, "renders/tests/shot_atelier_10.png", b"not a prefix match")
        self.binary(self.first, "renders/production-tests/detail.mp4", b"0123456789abcdef")
        self.binary(self.first, "assets/alice.png", b"reference")
        self.binary(self.first, "references/shot_atelier_1.png", b"not a shot render")
        self.binary(self.first, "audio/orphan.wav", b"orphan")
        self.write(self.first, "final/edit.yaml", {"render_id": "render_atelier", "shots": [
            {"shot_id": "shot_atelier_1", "video": "renders/missing.mp4"},
        ]})
        self.write(self.first, "budget/estimate.yaml", {"currency": "USD", "estimate": 12})
        self.binary(self.second, "renders/only.png", b"does not define shots")
        self.binary(self.second, "project.yaml", b"title: [broken")
        self.write(self.second, "prompts/images/orphan.yaml", {
            "prompt_id": "orphan_prompt", "shot_id": "shot_not_defined", "model": "qwen-image",
            "prompt": "No narrative declaration.",
        })
        self.catalog = Catalog(self.root, cache_seconds=0)

    @staticmethod
    def write(root, relative, data):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    @staticmethod
    def binary(root, relative, data):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class CatalogTests(DashboardFixture):
    def test_multi_project_contract_and_declared_narrative(self):
        result = self.catalog.list_projects()
        self.assertEqual({row["id"] for row in result["projects"]}, {self.project_id, "unfinished"})
        summary = next(row for row in result["projects"] if row["id"] == self.project_id)
        self.assertEqual(summary["title"], "Atelier d’été")
        self.assertEqual(summary["scene_count"], 1)
        self.assertEqual(summary["shot_count"], 2)
        self.assertEqual(summary["media_count"], 7)
        self.assertIsInstance(summary["cover"], dict)
        project = self.catalog.get_project(self.project_id)
        self.assertEqual(project["scenes"][0]["shot_ids"], ["shot_atelier_1"])
        shot = next(row for row in project["shots"] if row["id"] == "shot_atelier_1")
        self.assertEqual(shot["location_id"], "loc_room")
        self.assertEqual(shot["duration_seconds"], 4)
        self.assertEqual(shot["props"], ["prop_key"])
        self.assertEqual(shot["prompts"][0]["data"]["prompt_id"], "prompt_door")
        self.assertEqual(project["budget"]["estimate"]["currency"], "USD")
        self.assertTrue(any("scene_missing" in warning for warning in project["warnings"]))
        self.assertTrue(any("char_missing" in warning for warning in project["warnings"]))
        self.assertEqual(project["progress_basis"], "artifact_presence_not_production_approval")

    def test_pipeline_distinguishes_prompt_files_from_media_and_visual_sheets(self):
        stages = {row["id"]: row for row in self.catalog.get_project(self.project_id)["stages"]}
        self.assertIn("character_sheet", stages)
        self.assertIn("continuity", stages)
        self.assertEqual(stages["character_sheet"]["status"], "missing")
        self.assertEqual(stages["image_prompt"]["count"], 1)
        self.assertEqual(stages["image_media"]["count"], 2)
        self.assertEqual(stages["video_prompt"]["status"], "missing")
        self.assertEqual(stages["video_media"]["count"], 1)

    def test_explicit_filename_orphan_and_reference_links(self):
        project = self.catalog.get_project(self.project_id)
        media = {row["id"]: row for row in project["media"]}
        explicit = media["renders/tests/result.png"]
        self.assertEqual(explicit["relation"], "explicit")
        self.assertEqual(explicit["role"], "shot")
        self.assertEqual(explicit["shot_ids"], ["shot_atelier_1"])
        self.assertEqual(explicit["prompt_ids"], ["prompt_door"])
        self.assertEqual(media["renders/production-tests/detail.mp4"]["relation"], "explicit")
        self.assertEqual(media["renders/tests/shot_atelier_1_variant.png"]["relation"], "filename")
        self.assertEqual(media["renders/tests/shot_atelier_10.png"]["relation"], "unlinked")
        self.assertEqual(media["audio/orphan.wav"]["relation"], "unlinked")
        reference = media["assets/alice.png"]
        self.assertEqual(reference["role"], "reference")
        self.assertEqual(reference["relation"], "explicit")
        self.assertEqual(reference["entity_ids"], ["char_alice"])
        self.assertEqual(media["references/shot_atelier_1.png"]["role"], "reference")
        self.assertEqual(media["references/shot_atelier_1.png"]["shot_ids"], [])
        alice = next(row for row in project["entities"] if row["id"] == "char_alice")
        self.assertIn("assets/alice.png", alice["media_ids"])
        self.assertTrue(any("missing or unsafe media link" in warning for warning in project["warnings"]))

    def test_broken_yaml_does_not_create_narrative_or_production_readiness(self):
        project = self.catalog.get_project("unfinished")
        self.assertEqual(project["shots"], [])
        self.assertEqual(project["scenes"], [])
        self.assertEqual(project["title"], "unfinished")
        self.assertTrue(project["warnings"])
        self.assertTrue(any("unknown shot" in warning for warning in project["warnings"]))
        self.assertEqual(next(row for row in project["stages"] if row["id"] == "project")["status"], "invalid")
        self.assertEqual(next(row for row in project["stages"] if row["id"] == "shot")["status"], "missing")
        artifact = next(row for row in project["artifacts"] if row["path"] == "project.yaml")
        self.assertFalse(artifact["valid"])
        self.assertIsNone(artifact["data"])
        self.assertEqual(project["progress"], round(200 / len(project["stages"])))

    def test_local_schema_refs_and_validity_are_opportunistic(self):
        project = self.catalog.get_project(self.project_id)
        artifacts = {row["path"]: row for row in project["artifacts"]}
        self.assertTrue(artifacts["project.yaml"]["valid"])
        self.assertTrue(artifacts["prompts/images/qwen-image/door.yaml"]["valid"])
        self.assertIsNone(artifacts["renders/tests/run.yaml"]["valid"])
        self.assertFalse(artifacts["budget/estimate.yaml"]["valid"])
        self.assertFalse(artifacts["renders/tests/run.yaml"]["data"]["approved"])

    def test_hidden_secrets_workflows_and_symlinks_are_not_exposed(self):
        outside = self.base / "private.png"
        outside.write_bytes(b"private")
        (self.first / "leak.png").symlink_to(outside)
        (self.root / "linked-project").symlink_to(self.first, target_is_directory=True)
        (self.root / ".hidden-project").mkdir()
        self.binary(self.first, ".hidden/image.png", b"hidden")
        self.binary(self.first, "secrets/private.png", b"private")
        self.binary(self.first, ".env", b"OPENROUTER_API_KEY=private")
        self.write(self.first, "workflows/cloud/graph.json", {"api_key": "private-workflow-key"})
        self.write(self.first, "production/run.yaml", {
            "api_key": "private-key", "parameters": {"password": "private-password"},
            "note": "Bearer private-bearer", "when": dt.date(2026, 10, 5),
        })
        (self.first / "production" / "linked.yaml").symlink_to(self.first / "project.yaml")
        result = self.catalog.get_project(self.project_id)
        serialized = json.dumps(result)
        self.assertNotIn("private-key", serialized)
        self.assertNotIn("private-password", serialized)
        self.assertNotIn("private-bearer", serialized)
        self.assertNotIn("private-workflow-key", serialized)
        self.assertNotIn("leak.png", serialized)
        self.assertNotIn(".hidden/image.png", serialized)
        self.assertNotIn("linked.yaml", serialized)
        self.assertIn("2026-10-05", serialized)
        self.assertEqual(len(self.catalog.list_projects()["projects"]), 2)
        for path in ("../private.png", "%2e%2e/private.png", ".hidden/image.png", "leak.png", ".env", "workflows/cloud/graph.json"):
            with self.subTest(path=path), self.assertRaises((ValueError, FileNotFoundError)):
                self.catalog.media_file(self.project_id, path)

    def test_reference_illustration_output_is_not_a_shot(self):
        self.write(self.first, "renders/references/run.yaml", {
            "job_kind": "reference_illustration", "entity_id": "char_alice",
            "scene_id": "scene_atelier", "source_prompt_id": "ref_prompt",
            "output_files": ["renders/references/portrait.png"],
        })
        self.binary(self.first, "renders/references/portrait.png", b"portrait")
        project = self.catalog.get_project(self.project_id)
        portrait = next(row for row in project["media"] if row["path"].endswith("portrait.png"))
        self.assertEqual(portrait["role"], "reference")
        self.assertEqual(portrait["shot_ids"], [])
        self.assertEqual(portrait["entity_ids"], ["char_alice"])

    def test_cache_reload_discovers_changes_and_new_projects(self):
        cached = Catalog(self.root, cache_seconds=0.02)
        self.assertEqual(cached.get_project("unfinished")["title"], "unfinished")
        self.write(self.second, "project.yaml", {"title": "Changed"})
        (self.root / "new-film").mkdir()
        time.sleep(0.03)
        self.assertEqual(cached.get_project("unfinished")["title"], "Changed")
        self.assertEqual(len(cached.list_projects()["projects"]), 3)
        self.assertLessEqual(Catalog(self.root, cache_seconds=100).cache_seconds, 2)

    def test_yaml_recursive_alias_and_non_finite_json(self):
        self.binary(self.second, "production/odd.yaml", b"date: 2026-10-05\nnumber: .nan\ncycle: &x [*x]\n")
        result = self.catalog.get_project("unfinished")
        json.dumps(result, allow_nan=False)
        odd = next(row for row in result["artifacts"] if row["path"] == "production/odd.yaml")
        self.assertEqual(odd["data"]["date"], "2026-10-05")
        self.assertIsNone(odd["data"]["number"])
        self.assertEqual(odd["data"]["cycle"], ["[recursive alias]"])

    def test_real_sidecar_shapes_components_mapping_and_source_job_distinction(self):
        job_id = "12345678-1234-1234-1234-123456789abc"
        self.write(self.first, "prompts/production-tests/components.yaml", {
            "shot_id": "shot_atelier_1", "production_final": False,
            "components": [{"component_id": "portrait", "character_ids": ["char_alice"],
                            "shot_id": "shot_atelier_1"}],
            "generated_assets": [{"component_id": "portrait", "path": "assets/component.png", "approved": False}],
        })
        self.binary(self.first, "assets/component.png", b"component")
        self.write(self.first, "renders/tests/sidecar/run.yaml", {
            "shot_id": "shot_atelier_1", "source_prompt_id": "prompt_door", "prompt_id": job_id,
            "output_files": ["frame.png"], "status": "completed", "visual_review_status": "rejected_geometry",
            "approved": False, "production_final": False,
        })
        self.binary(self.first, "renders/tests/sidecar/frame.png", b"frame")
        self.binary(self.first, "renders/references/sidecar/reference.png", b"portrait")
        self.binary(self.first, "renders/references/sidecar/run.json", json.dumps({
            "job_kind": "reference_illustration", "entity_id": "char_alice", "source_prompt_id": "ref_alice",
            "output": {"file": "reference.png"}, "asset_status": "candidate_pending_review",
        }).encode())
        self.binary(self.first, "production/assembly-provenance.json", json.dumps({
            "asset_definitions": [{"path": "assets/component.png", "mapped_shot_ids": ["shot_atelier_1", "shot_atelier_2"],
                                   "source_prompt_id": "prompt_component", "job_prompt_id": job_id,
                                   "visual_review_status": "candidate", "production_final": False}],
        }).encode())
        project = self.catalog.get_project(self.project_id)
        media = {item["path"]: item for item in project["media"]}
        component = media["assets/component.png"]
        self.assertEqual(set(component["shot_ids"]), {"shot_atelier_1", "shot_atelier_2"})
        self.assertEqual(component["entity_ids"], ["char_alice"])
        self.assertFalse(component["approved"])
        self.assertFalse(component["production_final"])
        sidecar = media["renders/tests/sidecar/frame.png"]
        self.assertEqual(sidecar["prompt_ids"], ["prompt_door"])
        self.assertEqual(sidecar["job_ids"], [job_id])
        self.assertEqual(sidecar["review_status"], "rejected_geometry")
        self.assertEqual(sidecar["status"], "completed")
        reference = media["renders/references/sidecar/reference.png"]
        self.assertEqual(reference["entity_ids"], ["char_alice"])
        self.assertEqual(reference["role"], "reference")
        self.assertEqual(reference["review_status"], "candidate_pending_review")
        self.assertIsNone(reference["approved"])

    def test_superseded_archive_metadata_does_not_claim_current_render(self):
        self.write(self.first, "final/archive/old-proof.yaml", {
            "status": "archived_superseded", "video_path": "renders/production-tests/detail.mp4",
            "approved": False, "production_final": False, "reuse_as_current_opening": False,
        })
        project = self.catalog.get_project(self.project_id)
        video = next(item for item in project["media"] if item["path"].endswith("detail.mp4"))
        self.assertTrue(video["archived"])
        self.assertEqual(video["status"], "archived_superseded")
        self.assertFalse(video["approved"])
        self.assertEqual(next(item for item in project["stages"] if item["id"] == "render")["count"], 1)
        self.assertFalse(project["cover"]["archived"])
        self.assertEqual(next(item for item in project["stages"] if item["id"] == "video_media")["status"], "missing")

    def test_output_reused_as_input_keeps_source_provenance_and_separate_usage(self):
        source_path = "renders/tests/result.png"
        self.write(self.first, "renders/tests/run.yaml", {
            "shot_id": "shot_atelier_1", "entity_id": "char_alice",
            "source_prompt_id": "prompt_door", "output_files": [source_path],
            "approved": False, "production_final": False, "status": "source_candidate",
        })
        # These consumer documents are scanned before the source's run record.
        self.write(self.first, "prompts/videos/consumer.yaml", {
            "prompt_id": "consumer_video", "shot_id": "shot_atelier_2",
            "character_ids": ["char_alice", "prop_key"], "location_id": "loc_room",
            "references": [source_path], "image_input": source_path,
            "approved": True, "production_final": True,
        })
        self.write(self.first, "prompts/references/consumer.yaml", {
            "prompt_id": "consumer_reference", "job_kind": "reference_illustration",
            "entity_id": "prop_key", "source_image": source_path,
            "status": "archived_superseded_consumer", "approved": True,
        })
        # A later-scanned consumer also must not demote or contaminate the source.
        self.write(self.first, "renders/videos/consumer.yaml", {
            "shot_id": "shot_atelier_2", "entity_id": "loc_room", "prompt_id": "later_consumer",
            "ordered_references": [{"entity_id": "prop_key", "uploaded_path": source_path}],
            "approved": True,
        })
        project = self.catalog.get_project(self.project_id)
        source = next(item for item in project["media"] if item["path"] == source_path)
        self.assertEqual(source["role"], "shot")
        self.assertEqual(source["relation"], "explicit")
        self.assertEqual(source["shot_ids"], ["shot_atelier_1"])
        self.assertEqual(source["entity_ids"], ["char_alice"])
        self.assertEqual(source["prompt_ids"], ["prompt_door"])
        self.assertFalse(source["approved"])
        self.assertFalse(source["production_final"])
        self.assertFalse(source["archived"])
        self.assertEqual(source["status"], "source_candidate")
        self.assertEqual({item["path"] for item in source["review_records"]}, {"renders/tests/run.yaml"})
        usages = {item["path"]: item for item in source["usage_records"]}
        self.assertEqual(usages["prompts/videos/consumer.yaml"], {
            "path": "prompts/videos/consumer.yaml", "shot_ids": ["shot_atelier_2"],
            "entity_ids": [], "prompt_ids": ["consumer_video"], "relation": "explicit",
        })
        self.assertEqual(usages["renders/videos/consumer.yaml"]["entity_ids"], ["prop_key"])
        self.assertEqual(usages["prompts/references/consumer.yaml"]["entity_ids"], [])
        self.assertNotIn("_has_source", source)

    def test_input_aliases_cannot_inherit_consumer_approvals_entities_jobs_or_archive(self):
        keys = ("source_image", "end_image", "image_input", "source_image_path", "image_references",
                "first_frame", "last_frame", "reference_assets", "ordered_references", "uploaded_path")
        references = {}
        for index, key in enumerate(keys):
            path = f"assets/input-{index}.png"
            self.binary(self.first, path, b"reference")
            references[key] = path
        output_path = "renders/videos/approved-output.mp4"
        self.binary(self.first, output_path, b"consumer output")
        self.write(self.first, "prompts/videos/approved-consumer.yaml", {
            "prompt_id": "approved_consumer", "shot_id": "shot_atelier_2",
            "character_ids": ["char_alice"], "location_id": "loc_room",
            "job_prompt_id": "12345678-1234-1234-1234-123456789abc",
            "approved": True, "production_final": True, "film_final": True,
            "status": "archived_superseded_consumer", "output_files": [output_path], **references,
        })
        project = self.catalog.get_project(self.project_id)
        media = {item["path"]: item for item in project["media"]}
        self.assertTrue(media[output_path]["approved"])
        self.assertTrue(media[output_path]["production_final"])
        self.assertTrue(media[output_path]["archived"])
        for key, path in references.items():
            with self.subTest(key=key):
                source = media[path]
                self.assertEqual(source["role"], "reference")
                for field in ("approved", "production_final", "film_final", "status", "review_status"):
                    self.assertIsNone(source[field])
                for field in ("shot_ids", "entity_ids", "prompt_ids", "job_ids", "review_records"):
                    self.assertEqual(source[field], [])
                self.assertFalse(source["archived"])
                self.assertEqual(source["usage_records"], [{
                    "path": "prompts/videos/approved-consumer.yaml", "shot_ids": ["shot_atelier_2"],
                    "entity_ids": [], "prompt_ids": ["approved_consumer"], "relation": "explicit",
                }])

    def test_usage_only_reference_keeps_explicit_nested_entity_not_consumer_cast(self):
        self.binary(self.first, "assets/key-reference.png", b"reference")
        self.write(self.first, "prompts/videos/consumer.yaml", {
            "shot_id": "shot_atelier_2", "prompt_id": "consumer_video",
            "character_ids": ["char_alice"], "location_id": "loc_room",
            "reference_assets": {
                "prop_key": {"uploaded_path": "assets/key-reference.png", "approved": True},
            },
        })
        project = self.catalog.get_project(self.project_id)
        reference = next(item for item in project["media"] if item["path"] == "assets/key-reference.png")
        self.assertEqual(reference["role"], "reference")
        self.assertEqual(reference["entity_ids"], ["prop_key"])
        self.assertEqual(reference["shot_ids"], [])
        self.assertIsNone(reference["approved"])
        self.assertEqual(reference["usage_records"][0]["entity_ids"], ["prop_key"])
        self.assertEqual(reference["usage_records"][0]["shot_ids"], ["shot_atelier_2"])


class ReferenceStageTests(DashboardFixture):
    """Pre-screenplay projects: story registry IDs, model sheets, notes, ledger."""

    def setUp(self):
        super().setUp()
        self.film = self.root / "sheets-film"
        self.write(self.film, "story/story.yaml", {
            "story_id": "story_sheets", "title": "Planches", "logline": "Un test.", "premise": "Test.",
            "acts": [], "characters": ["char_001", "char_002"], "locations": ["loc_001"],
        })
        self.write(self.film, "budget/decision.yaml", {"selected_tier": "preparation", "max_spend_usd": 30})
        self.binary(self.film, "references/generated/char_001/attempt-01/aa11bb22_000.png", b"sheet")
        self.binary(self.film, "references/generated/char_001/attempt-01/crops/front.png", b"crop")
        self.binary(self.film, "references/generated/char_001/attempt-01/review.md", "# Revue\nApprouvé ?".encode())
        self.binary(self.film, "references/generated/char_002/attempt-01/cc33dd44_000.png", b"candidate")
        self.binary(self.film, "workflows/cloud/batch/uploads/char_001_upload.png", b"technical copy")
        self.write(self.film, "references/approved-references.yaml", {"references": [{
            "order": 1, "entity_id": "char_001", "entity_type": "character",
            "path": "references/generated/char_001/attempt-01/aa11bb22_000.png",
            "approved_at": "2026-10-05", "consent_verbatim": "oui",
            "views": [{"view": "front", "asset_path": "references/generated/char_001/attempt-01/crops/front.png"}],
        }]})

    def ledger(self, rows, opening="0"):
        import sqlite3
        path = self.film / "budget" / "cloud-ledger.sqlite3"
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, metadata TEXT NOT NULL)")
            db.execute("CREATE TABLE jobs (plan_hash TEXT PRIMARY KEY, consent TEXT, target TEXT, attempt INTEGER, reserved TEXT, actual TEXT, status TEXT, record TEXT)")
            db.execute("INSERT INTO account VALUES (1, ?)", (json.dumps({"opening_hold_usd": opening}),))
            for i, (reserved, actual, status) in enumerate(rows):
                db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?)", (f"h{i}", f"c{i}", "t", i, reserved, actual, status, "{}"))
            db.commit()
        return path

    def test_story_registry_entities_registry_approval_and_derived_views(self):
        project = self.catalog.get_project("sheets-film")
        entities = {row["id"]: row for row in project["entities"]}
        self.assertEqual(set(entities), {"char_001", "char_002", "loc_001"})
        self.assertEqual(entities["char_001"]["name"], "char_001")
        self.assertEqual(entities["char_001"]["description"], "")
        media = {row["path"]: row for row in project["media"]}
        sheet = media["references/generated/char_001/attempt-01/aa11bb22_000.png"]
        self.assertEqual(sheet["role"], "reference")
        self.assertEqual(sheet["reference_approvals"][0]["consent_verbatim"], "oui")
        crop = media["references/generated/char_001/attempt-01/crops/front.png"]
        self.assertEqual(crop["derived_from"], sheet["path"])
        self.assertEqual(crop["reference_approvals"], [])
        candidate = media["references/generated/char_002/attempt-01/cc33dd44_000.png"]
        self.assertEqual(candidate["reference_approvals"], [])
        self.assertIsNone(candidate["approved"])
        self.assertEqual(sheet["notes"], ["references/generated/char_001/attempt-01/review.md"])
        self.assertEqual(crop["notes"], ["references/generated/char_001/attempt-01/review.md"])
        note = next(row for row in project["artifacts"] if row["kind"] == "note")
        self.assertIn("Approuvé ?", note["data"])
        self.assertNotIn("approved", json.dumps(sheet["review_records"]))
        stages = {row["id"]: row for row in project["stages"]}
        self.assertEqual(stages["reference_sheets"]["count"], 2)
        self.assertEqual(stages["reference_sheets"]["documented_approvals"], 1)
        self.assertEqual(stages["screenplay"]["status"], "missing")
        self.assertTrue(all("phase" in row for row in project["stages"]))

    def test_workflow_upload_copies_are_not_film_media(self):
        project = self.catalog.get_project("sheets-film")
        self.assertFalse(any(row["path"].startswith("workflows/") for row in project["media"]))
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.catalog.media_file("sheets-film", "workflows/cloud/batch/uploads/char_001_upload.png")

    def test_ledger_is_read_only_and_unknown_costs_stay_unknown(self):
        path = self.ledger([("0.02", "0.018", "completed"), ("0.02", "0.018", "completed")])
        before = path.read_bytes()
        ledger = self.catalog.get_project("sheets-film")["budget"]["ledger"]
        self.assertEqual(ledger["jobs"], 2)
        self.assertAlmostEqual(ledger["committed_usd"], 0.036)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.film / "budget" / "cloud-ledger.sqlite3-journal").exists())
        path.unlink()
        self.ledger([("0.02", None, "submitted")], opening="not-a-number")
        ledger = Catalog(self.root, cache_seconds=0).get_project("sheets-film")["budget"]["ledger"]
        self.assertIsNone(ledger["committed_usd"])
        self.assertEqual(ledger["jobs_without_actual_cost"], 1)

    def test_shot_timing_fields_are_exposed_without_invention(self):
        shot = next(row for row in self.catalog.get_project(self.project_id)["shots"] if row["id"] == "shot_atelier_1")
        self.assertEqual(shot["sequence"], 1)
        self.assertIsNone(shot["start_seconds"])
        self.assertIsNone(shot["needs_motion"])


class StoryboardTests(DashboardFixture):
    def test_panels_scene_notes_and_storyboard_frames_are_not_shot_renders(self):
        self.write(self.first, "storyboard/storyboard.yaml", {"storyboard_id": "sb", "panels": [
            {"panel_id": "panel_a", "scene_id": "scene_atelier", "shot_id": "shot_atelier_1",
             "composition": "Plan large", "camera": {"movement": "travelling", "lens": "35mm"},
             "action": "Elle entre.", "image": "frames/panel_a.png",
             "references": ["assets/alice.png"]},
            {"panel_id": "panel_b", "scene_id": "scene_unknown", "shot_id": "shot_atelier_1", "composition": "Gros plan"},
        ]})
        self.binary(self.first, "storyboard/frames/panel_a.png", b"drawing")
        self.binary(self.first, "storyboard/panel_b_sketch.png", b"drawing b")
        self.binary(self.first, "screenplay/scene_atelier.md", "# Scène".encode())
        project = self.catalog.get_project(self.project_id)
        panels = {row["id"]: row for row in project["panels"]}
        self.assertEqual(panels["panel_a"]["camera"], "lens : 35mm · movement : travelling")
        self.assertEqual(panels["panel_a"]["media_ids"], ["storyboard/frames/panel_a.png"])
        self.assertEqual(panels["panel_b"]["media_ids"], ["storyboard/panel_b_sketch.png"])
        media = {row["path"]: row for row in project["media"]}
        frame = media["storyboard/frames/panel_a.png"]
        self.assertEqual((frame["role"], frame["relation"]), ("storyboard", "explicit"))
        self.assertEqual(media["storyboard/panel_b_sketch.png"]["relation"], "filename")
        self.assertEqual(media["assets/alice.png"]["role"], "reference")
        scene = project["scenes"][0]
        self.assertEqual(scene["panel_ids"], ["panel_a"])
        self.assertEqual(scene["notes"], ["screenplay/scene_atelier.md"])
        self.assertTrue(any("scene_unknown" in warning for warning in project["warnings"]))
        stages = {row["id"]: row for row in project["stages"]}
        self.assertEqual(stages["storyboard"]["count"], 2)
        self.assertEqual(stages["image_media"]["count"], 2)

    def test_scene_number_accepts_digit_strings_only(self):
        from dashboard.catalog import _number
        self.assertEqual((_number("3"), _number(4), _number(True), _number("III")), (3, 4, None, None))


class ServerTests(DashboardFixture):
    def setUp(self):
        super().setUp()
        self.static = self.base / "static"
        self.static.mkdir()
        self.binary(self.static, "index.html", "<h1>Été</h1>".encode())
        self.binary(self.static, "app.js", b"console.log('read-only');")
        self.server = make_server(self.root, port=0, static_root=self.static, cache_seconds=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.prefix = "/media/" + quote(self.project_id, safe="") + "/"

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, path, method="GET", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_http_api_static_utf8_head_and_no_cors(self):
        status, headers, body = self.request("/api/projects")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["projects"]), 2)
        self.assertIn("charset=utf-8", headers["Content-Type"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        endpoint = "/api/projects/" + quote(self.project_id, safe="")
        status, headers, body = self.request(endpoint)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["title"], "Atelier d’été")
        status, head_headers, head_body = self.request(endpoint, "HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(head_body, b"")
        self.assertEqual(head_headers["Content-Length"], headers["Content-Length"])
        self.assertEqual(self.request("/")[2], "<h1>Été</h1>".encode())
        self.assertIn("javascript", self.request("/static/app.js")[1]["Content-Type"])

    def test_video_full_head_and_single_byte_ranges(self):
        url = self.prefix + "renders/production-tests/detail.mp4"
        status, headers, body = self.request(url)
        self.assertEqual((status, body), (200, b"0123456789abcdef"))
        self.assertEqual(headers["Content-Type"], "video/mp4")
        self.assertEqual(headers["Accept-Ranges"], "bytes")
        for requested, expected, content_range in (
            ("bytes=2-5", b"2345", "bytes 2-5/16"),
            ("bytes=12-", b"cdef", "bytes 12-15/16"),
            ("bytes=-3", b"def", "bytes 13-15/16"),
            ("bytes=14-999", b"ef", "bytes 14-15/16"),
        ):
            with self.subTest(range=requested):
                status, headers, body = self.request(url, headers={"Range": requested})
                self.assertEqual((status, body), (206, expected))
                self.assertEqual(headers["Content-Range"], content_range)
                self.assertEqual(int(headers["Content-Length"]), len(expected))
        status, headers, body = self.request(url, "HEAD", {"Range": "bytes=2-5"})
        self.assertEqual(status, 206)
        self.assertEqual(headers["Content-Length"], "4")
        self.assertEqual(body, b"")
        for requested in ("bytes=99-", "bytes=5-2", "bytes=-0", "bytes=0-1,4-5", "invalid"):
            self.assertEqual(self.request(url, headers={"Range": requested})[0], 416)

    def test_requests_cannot_escape_media_or_read_secrets(self):
        outside = self.base / "private.png"
        outside.write_bytes(b"DO NOT EXPOSE")
        (self.first / "leak.png").symlink_to(outside)
        (self.static / "leak.png").symlink_to(outside)
        self.binary(self.first, ".env", b"DO NOT EXPOSE")
        for path in (
            self.prefix + "../private.png", self.prefix + "%2e%2e/private.png",
            self.prefix + "%252e%252e/private.png", self.prefix + "leak.png",
            self.prefix + ".env", self.prefix + "shots/shots.yaml", "/../private.png",
            "/%2e%2e/private.png", "/leak.png", "/.env", "/api/projects/%2e%2e",
        ):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertIn(status, (400, 404))
                self.assertNotIn(b"DO NOT EXPOSE", body)
                self.assertNotIn(str(self.base).encode(), body)
        self.assertEqual(self.request("/api/projects/missing")[0], 404)
        self.assertEqual(self.request("/api/projects", "POST")[0], 405)

    def test_non_loopback_hosts_are_rejected_without_binding(self):
        for host in ("0.0.0.0", "::", "192.168.1.2", "example.org"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                make_server(self.root, host=host, port=0)
        self.assertEqual(validate_host("localhost"), "127.0.0.1")
        self.assertEqual(validate_host("::1"), "::1")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as context:
            main(["--host", "0.0.0.0"])
        self.assertEqual(context.exception.code, 2)

    def test_dns_rebinding_hosts_are_forbidden_for_every_route_and_method(self):
        port = self.server.server_port
        routes = ("/api/projects", "/api/projects/" + quote(self.project_id, safe=""),
                  "/", "/static/app.js", self.prefix + "renders/tests/result.png")
        for route in routes:
            for host in (f"attacker.example:{port}", f"localhost.attacker.example:{port}",
                         f"192.168.1.2:{port}", f"127.0.0.1:{port + 1}", "localhost",
                         f"user@localhost:{port}", f"localhost:{port},attacker.example"):
                with self.subTest(route=route, host=host):
                    status, headers, body = self.request(route, headers={"Host": host})
                    self.assertEqual(status, 403)
                    self.assertEqual(json.loads(body), {"error": "Forbidden request origin"})
                    self.assertNotIn("Access-Control-Allow-Origin", headers)
        for method in ("HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"):
            with self.subTest(method=method):
                status, headers, body = self.request("/api/projects", method, {"Host": f"attacker.example:{port}"})
                self.assertEqual(status, 403)
                if method == "HEAD":
                    self.assertEqual(body, b"")
        for host in (f"localhost:{port}", f"127.0.0.1:{port}", f"[::1]:{port}"):
            self.assertEqual(self.request("/api/projects", headers={"Host": host})[0], 200)

    def test_external_origins_and_duplicate_hosts_are_forbidden(self):
        port = self.server.server_port
        for origin in ("http://attacker.example", f"http://attacker.example:{port}",
                       "null", f"http://localhost:{port + 1}", f"http://localhost:{port}/path"):
            for route in ("/api/projects", "/", self.prefix + "renders/tests/result.png"):
                with self.subTest(origin=origin, route=route):
                    self.assertEqual(self.request(route, headers={"Origin": origin})[0], 403)
        for origin in (f"http://localhost:{port}", f"http://127.0.0.1:{port}"):
            self.assertEqual(self.request("/api/projects", headers={"Origin": origin})[0], 200)
        self.assertEqual(self.request("http://attacker.example/api/projects")[0], 403)
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            connection.putrequest("GET", "/api/projects", skip_host=True)
            connection.putheader("Host", f"localhost:{port}")
            connection.putheader("Host", f"attacker.example:{port}")
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
