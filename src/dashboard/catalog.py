"""Filesystem-backed, read-only catalogue of film development artefacts.

Presence, schema validity and production approval are deliberately independent.
Only IDs declared in narrative/entity documents become narrative/entity records.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
from itertools import islice
from pathlib import Path, PurePosixPath
import re
import threading
import time
from urllib.parse import quote, unquote

import yaml
from jsonschema import validators
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


MEDIA_TYPES = {
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image",
    ".gif": "image", ".mp4": "video", ".webm": "video", ".mov": "video",
    ".wav": "audio", ".mp3": "audio", ".ogg": "audio", ".m4a": "audio",
    ".flac": "audio",
}
DOCUMENT_SUFFIXES = {".yaml", ".yml", ".json"}
DOCUMENT_DIRS = {
    "story", "screenplay", "characters", "locations", "props", "storyboard",
    "shots", "prompts", "renders", "production", "production-tests", "audio",
    "final", "continuity", "references", "reference_assets",
}
STAGES = (
    ("project", "Projet"), ("story", "Histoire"), ("budget", "Budget"),
    ("screenplay", "Scénario"), ("character", "Personnages"),
    ("character_sheet", "Fiches visuelles"),
    ("location", "Décors"), ("prop", "Accessoires"),
    ("storyboard", "Storyboard"), ("shot", "Plans"),
    ("image_prompt", "Prompts image"), ("image_media", "Images sur disque"),
    ("video_prompt", "Prompts vidéo"), ("video_media", "Vidéos sur disque"),
    ("audio_prompt", "Prompts audio"), ("audio_media", "Audio sur disque"),
    ("continuity", "Continuité"), ("render", "Montage"),
)
MAX_DOCUMENT_BYTES = 4 * 1024 * 1024
INPUT_MEDIA_KEYS = {
    "references", "reference_assets", "style_reading_references", "ordered_references",
    "ordered_reference_assets", "image_references", "image_input", "audio_input",
    "reference_image", "reference_images", "reference_image_path", "source_images",
    "start_image", "start_image_path", "input_image", "input_images",
    "source_image", "source_image_path", "end_image", "end_image_path",
    "first_frame", "first_frame_path", "last_frame", "last_frame_path", "uploaded_path",
}
_SECRET_KEY = re.compile(
    r"(?:api[_-]?key|password|passwd|secret|credential|authorization|"
    r"(?:access|refresh|auth|registration)[_-]?token|^token$|cookie|private[_-]?key)", re.I
)
_SECRET_TEXT = re.compile(r"(?i)\b(?:bearer\s+\S+|sk-[a-z0-9_-]{8,})")


def safe_parts(value: str) -> tuple[str, ...]:
    """Validate an already URL-decoded relative path, including double encoding."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("Invalid relative path")
    # Reject residual encoded traversal too, without treating encoded '/' as a path.
    probe = value
    for _ in range(4):
        if probe.startswith("/") or "\\" in probe or "\x00" in probe:
            raise ValueError("Invalid relative path")
        parts = probe.split("/")
        if any(not part or part in {".", ".."} or part.startswith(".") for part in parts):
            raise ValueError("Invalid relative path")
        if any(_SECRET_KEY.search(part) or part.lower() in {"env", "secrets"} for part in parts):
            raise ValueError("Private path")
        decoded = unquote(probe)
        if decoded == probe:
            break
        probe = decoded
    return tuple(value.split("/"))


def contained_file(root: Path, relative: str) -> Path:
    parts = safe_parts(relative)
    target = root.joinpath(*parts)
    # Disallow all symlinks, including ones swapped after catalogue construction.
    current = root
    if current.is_symlink():
        raise ValueError("Symlink not served")
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink not served")
    resolved = target.resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise FileNotFoundError(relative)
    return resolved


def json_safe(value, seen=None, depth=0, _budget=None):
    """Convert YAML dates, non-finite numbers and aliases; redact credential fields."""
    seen = set() if seen is None else seen
    _budget = [100_000] if _budget is None else _budget
    _budget[0] -= 1
    if _budget[0] < 0:
        raise ValueError("Document expansion exceeds limit")
    if depth > 40:
        return "[depth limit]"
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, str):
        return _SECRET_TEXT.sub("[redacted]", value)
    if isinstance(value, (dict, list, tuple, set)):
        if id(value) in seen:
            return "[recursive alias]"
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                return {
                    str(key): "[redacted]" if _SECRET_KEY.search(str(key)) else
                    json_safe(item, seen, depth + 1, _budget)
                    for key, item in value.items()
                }
            return [json_safe(item, seen, depth + 1, _budget) for item in value]
        finally:
            seen.remove(id(value))
    return str(value)


def _text(*values):
    return next((value for value in values if isinstance(value, str) and value), "")


def _ids(value):
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return list(dict.fromkeys(item for item in value if isinstance(item, str) and item))
    return []


def _records(data, plural, id_key):
    if isinstance(data, dict):
        if id_key in data:
            data = [data]
        elif plural in data:
            data = data[plural]
        else:
            data = list(data.values())
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and
            isinstance(row.get(id_key), str) and row[id_key]]


def _iso(timestamp):
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat()


def _kind(path: str, data=None):
    parts = PurePosixPath(path).parts
    area = parts[0]
    if "archive" in parts:
        return "record"
    if len(parts) == 1:
        return "project" if PurePosixPath(path).stem == "project" else "manifest"
    if area == "budget":
        return "budget"
    if area == "prompts":
        if "audio" in parts:
            return "audio_prompt"
        if "videos" in parts:
            return "video_prompt"
        if isinstance(data, dict) and "prompt_id" in data and "prompt" in data:
            if data.get("modality") == "video":
                return "video_prompt"
            if data.get("modality") == "audio":
                return "audio_prompt"
            return "image_prompt"
        if any(part in {"images", "references", "tests"} for part in parts):
            return "image_prompt"
        return "record"
    if area == "characters" and "sheets" in parts:
        return "character_sheet"
    return {"characters": "character", "locations": "location", "props": "prop",
            "shots": "shot", "final": "render"}.get(area, area if area in
             {"story", "screenplay", "storyboard", "continuity"} else "record")


class Catalog:
    """Small TTL cache. Refreshes never mutate project files or import director code."""

    def __init__(self, projects_root, *, cache_seconds=1.0, schemas_root=None):
        self.root = Path(projects_root).expanduser().resolve()
        self.cache_seconds = max(0.0, min(float(cache_seconds), 2.0))
        self.schemas_root = Path(schemas_root) if schemas_root else Path(__file__).resolve().parents[2] / "schemas"
        self._lock = threading.RLock()
        self._expires = 0.0
        self._projects = {}
        self._validators = {}
        self._load_schemas()

    def _load_schemas(self):
        resources = []
        schemas = {}
        for path in sorted(self.schemas_root.glob("*.schema.yaml")):
            try:
                schema = yaml.safe_load(path.read_text(encoding="utf-8"))
                if isinstance(schema, dict):
                    uri = path.resolve().as_uri()
                    resources.append((uri, Resource.from_contents(schema, default_specification=DRAFT202012)))
                    schemas[path.name.removesuffix(".schema.yaml")] = (uri, schema)
            except (OSError, ValueError, yaml.YAMLError):
                continue
        registry = Registry().with_resources(resources)
        for name, (uri, schema) in schemas.items():
            # Set a local base URI so sibling YAML $refs work without network I/O.
            schema = dict(schema, **{"$id": uri})
            try:
                cls = validators.validator_for(schema)
                cls.check_schema(schema)
                self._validators[name] = cls(schema, registry=registry)
            except Exception:
                continue

    def _refresh(self):
        with self._lock:
            if time.monotonic() < self._expires:
                return
            projects = {}
            try:
                children = sorted(self.root.iterdir(), key=lambda item: item.name.casefold())
            except OSError:
                children = []
            for child in children:
                try:
                    safe_parts(child.name)
                    if child.is_dir() and not child.is_symlink():
                        projects[child.name] = self._build(child)
                except (ValueError, OSError):
                    continue
            self._projects = projects
            self._expires = time.monotonic() + self.cache_seconds

    def list_projects(self):
        self._refresh()
        with self._lock:
            return {"projects": [
                {key: project[key] for key in (
                    "id", "title", "description", "scene_count", "shot_count",
                    "media_count", "progress", "updated_at", "cover",
                )} for project in self._projects.values()
            ]}

    def get_project(self, project_id):
        if len(safe_parts(project_id)) != 1:
            raise ValueError("Invalid project ID")
        self._refresh()
        with self._lock:
            if project_id not in self._projects:
                raise FileNotFoundError(project_id)
            return self._projects[project_id]

    def media_file(self, project_id, relative):
        if len(safe_parts(project_id)) != 1 or Path(relative).suffix.lower() not in MEDIA_TYPES:
            raise ValueError("Not media")
        project = self.get_project(project_id)
        if relative not in {item["id"] for item in project["media"]}:
            raise FileNotFoundError(relative)
        return contained_file(self.root / project_id, relative)

    def _files(self, root):
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(name for name in dirs if self._visible(root, Path(directory) / name))
            for name in sorted(files):
                path = Path(directory) / name
                if self._visible(root, path):
                    yield path

    @staticmethod
    def _visible(root, path):
        try:
            safe_parts(path.relative_to(root).as_posix())
            return not path.is_symlink() and (path.is_dir() or path.is_file())
        except (ValueError, OSError):
            return False

    def _artifact(self, path, relative):
        artifact = {"path": relative, "kind": _kind(relative), "data": None,
                    "valid": None, "errors": []}
        try:
            if path.stat().st_size > MAX_DOCUMENT_BYTES:
                raise ValueError("Document exceeds size limit")
            text = path.read_text(encoding="utf-8")
            data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
            artifact["data"] = json_safe(data)
            artifact["kind"] = _kind(relative, artifact["data"])
            schema_name = artifact["kind"].replace("_", "-")
            if artifact["kind"] == "budget":
                schema_name = "budget-" + path.stem
            validator = self._validators.get(schema_name)
            if validator:
                try:
                    errors = list(islice(validator.iter_errors(artifact["data"]), 20))
                    artifact["valid"] = not errors
                    artifact["errors"] = [
                        "Schema constraint {} at {}".format(error.validator, "/".join(
                            str(part) for part in error.absolute_path) or "$")
                        for error in errors[:20]
                    ]
                except Exception:
                    artifact["errors"] = ["Schema validation unavailable (unresolved or unsupported schema)"]
        except (OSError, UnicodeError, ValueError, yaml.YAMLError, RecursionError):
            artifact["valid"] = False
            artifact["errors"] = ["Unreadable, oversized or malformed document"]
        return artifact

    def _build(self, root):
        warnings = []
        artifacts = []
        media = {}
        modified = []
        for path in self._files(root):
            relative = path.relative_to(root).as_posix()
            parts = PurePosixPath(relative).parts
            suffix = path.suffix.lower()
            try:
                modified.append(path.stat().st_mtime)
                if suffix in MEDIA_TYPES:
                    media[relative] = {
                        "id": relative, "path": relative,
                        "url": "/media/" + quote(root.name, safe="") + "/" + quote(relative, safe="/"),
                        "kind": MEDIA_TYPES[suffix], "role": "unlinked",
                        "shot_ids": [], "entity_ids": [], "prompt_ids": [],
                        "job_ids": [], "relation": "unlinked", "modified_at": path.stat().st_mtime,
                        "status": None, "review_status": None, "approved": None,
                        "production_final": None, "film_final": None,
                        "archived": "archive" in parts, "review_records": [],
                        "usage_records": [], "_has_source": False,
                    }
                elif suffix in DOCUMENT_SUFFIXES:
                    eligible = parts[0] in DOCUMENT_DIRS or (len(parts) == 1 and
                                path.stem in {"project", "manifest"}) or (
                                len(parts) == 2 and parts[0] == "budget" and
                                path.stem in {"estimate", "decision", "assumptions"})
                    if eligible:
                        artifacts.append(self._artifact(path, relative))
            except OSError:
                warnings.append(f"{relative}: file unavailable")
        components = {}
        prompt_sources = {}
        for artifact in artifacts:
            data = artifact["data"]
            if artifact["kind"].endswith("_prompt") and isinstance(data, dict):
                if isinstance(data.get("prompt_id"), str):
                    prompt_sources[data["prompt_id"]] = data
            if isinstance(data, dict) and isinstance(data.get("components"), (list, dict)):
                definitions = data["components"]
                definitions = list(definitions.values()) if isinstance(definitions, dict) else definitions
                for row in definitions:
                    if isinstance(row, dict) and isinstance(row.get("component_id"), str):
                        existing = components.setdefault(row["component_id"], {"shots": [], "entities": []})
                        existing["shots"] += _ids(row.get("shot_id")) + _ids(row.get("main_shot_id")) + _ids(row.get("mapped_shot_ids"))
                        for kind in ("entity", "character", "location", "prop"):
                            existing["entities"] += _ids(row.get(kind + "_id")) + _ids(row.get(kind + "_ids"))
        for artifact in artifacts:
            if artifact["errors"]:
                warnings.append(f"{artifact['path']}: " + "; ".join(artifact["errors"]))

        scenes, shots, entities = {}, {}, {}
        metadata, story, budget = {}, {}, {}
        for artifact in artifacts:
            kind, data = artifact["kind"], artifact["data"]
            if kind == "project" and isinstance(data, dict):
                metadata.update(data)
            elif kind == "story" and isinstance(data, dict):
                story.update(data)
            elif kind == "budget":
                budget[PurePosixPath(artifact["path"]).stem] = data
            elif kind == "screenplay":
                for row in _records(data, "scenes", "scene_id"):
                    sid = row["scene_id"]
                    if sid in scenes:
                        warnings.append(f"{artifact['path']}: duplicate scene ID {sid}")
                        continue
                    scenes[sid] = {
                        "id": sid, "title": _text(row.get("title"), row.get("heading"), sid),
                        "description": _text(row.get("description"), row.get("action")),
                        "location_id": _text(row.get("location_id")) or None, "shot_ids": [],
                    }
            elif kind == "shot":
                for row in _records(data, "shots", "shot_id"):
                    sid = row["shot_id"]
                    if sid in shots:
                        warnings.append(f"{artifact['path']}: duplicate shot ID {sid}")
                        continue
                    duration = row.get("duration_seconds", row.get("duration"))
                    shots[sid] = {
                        "id": sid, "scene_id": _text(row.get("scene_id")) or None,
                        "title": _text(row.get("title"), row.get("subject"), sid),
                        "description": _text(row.get("description"), row.get("action")),
                        "duration_seconds": duration if isinstance(duration, (int, float)) and not isinstance(duration, bool) else None,
                        "characters": _ids(row.get("characters", row.get("character_ids"))),
                        "location_id": _text(row.get("location_id")) or None,
                        "props": _ids(row.get("prop_ids", row.get("props"))),
                        "prompts": [], "media_ids": [],
                    }
            elif kind in {"character", "location", "prop"}:
                for row in _records(data, kind + "s", kind + "_id"):
                    eid = row[kind + "_id"]
                    if eid in entities:
                        warnings.append(f"{artifact['path']}: duplicate entity ID {eid}")
                        continue
                    identity = row.get("identity") if isinstance(row.get("identity"), dict) else {}
                    entities[eid] = {
                        "id": eid, "kind": kind, "name": _text(row.get("name"), eid),
                        "description": _text(row.get("description"), identity.get("appearance"), row.get("role")),
                        "media_ids": [],
                    }
        for shot in shots.values():
            scene = scenes.get(shot["scene_id"])
            if scene:
                scene["shot_ids"].append(shot["id"])
                if not shot["location_id"]:
                    shot["location_id"] = scene["location_id"]
            else:
                warnings.append(f"{shot['id']}: scene link missing or unknown ({shot['scene_id']})")
            for eid in shot["characters"] + shot["props"] + _ids(shot["location_id"]):
                if eid not in entities:
                    warnings.append(f"{shot['id']}: unknown entity {eid}")
        for scene in scenes.values():
            if scene["location_id"] and scene["location_id"] not in entities:
                warnings.append(f"{scene['id']}: unknown location {scene['location_id']}")

        for artifact in artifacts:
            if artifact["kind"].endswith("_prompt") and isinstance(artifact["data"], dict):
                sid = artifact["data"].get("shot_id")
                if isinstance(sid, str):
                    if sid in shots:
                        shots[sid]["prompts"].append(artifact)
                    else:
                        warnings.append(f"{artifact['path']}: unknown shot {sid}")
            self._link_document(root, artifact, media, shots, entities, warnings, components, prompt_sources)

        for item in media.values():
            reference_dir = any(part in {"references", "reference_assets"} for part in PurePosixPath(item["path"]).parts)
            if item["relation"] == "unlinked":
                item["shot_ids"] = self._filename_ids(item["path"], shots) if not reference_dir else []
                item["entity_ids"] = self._filename_ids(item["path"], entities)
                if item["shot_ids"] or item["entity_ids"]:
                    item["relation"] = "filename"
                    item["role"] = "reference" if reference_dir or item["entity_ids"] and not item["shot_ids"] else "shot"
            if reference_dir:
                item["role"] = "reference"
            if item["usage_records"] and not item["_has_source"]:
                # Usage-only assets are references, not outputs of the consumer.
                item["role"] = "reference"
                if item["relation"] == "unlinked":
                    item["relation"] = "explicit"
                for usage in item["usage_records"]:
                    item["entity_ids"] = list(dict.fromkeys(item["entity_ids"] + usage["entity_ids"]))
                    if usage["entity_ids"]:
                        item["relation"] = "explicit"
            del item["_has_source"]
            for sid in item["shot_ids"]:
                if sid in shots:
                    shots[sid]["media_ids"].append(item["id"])
            for eid in item["entity_ids"]:
                if eid in entities:
                    entities[eid]["media_ids"].append(item["id"])
            if item["relation"] == "unlinked":
                warnings.append(f"{item['path']}: unlinked media (no declared association)")

        stages = []
        for stage_id, label in STAGES:
            matching = [a for a in artifacts if a["kind"] == stage_id]
            if stage_id.endswith("_media"):
                media_kind = stage_id.removesuffix("_media")
                present = [item for item in media.values() if item["kind"] == media_kind
                           and not item["archived"] and
                           (media_kind == "audio" or item["role"] == "shot")]
                stages.append({"id": stage_id, "label": label,
                               "status": "present" if present else "missing", "count": len(present)})
                continue
            stages.append({"id": stage_id, "label": label,
                           "status": "invalid" if any(a["valid"] is False for a in matching) else
                           "present" if matching else "missing", "count": len(matching)})
        media_list = list(media.values())
        return {
            "id": root.name, "title": _text(metadata.get("title"), story.get("title"), root.name),
            "project_id": _text(metadata.get("project_id")) or None,
            "genre": _text(metadata.get("genre"), story.get("genre")) or None,
            "aspect_ratio": _text(metadata.get("aspect_ratio")) or None,
            "duration_seconds": metadata.get("duration_seconds") if isinstance(metadata.get("duration_seconds"), (int, float)) and not isinstance(metadata.get("duration_seconds"), bool) else None,
            "description": _text(metadata.get("description"), story.get("logline"), story.get("premise"), metadata.get("production_scope")),
            "scenes": list(scenes.values()), "shots": list(shots.values()),
            "entities": list(entities.values()), "media": media_list, "artifacts": artifacts,
            "stages": stages, "warnings": list(dict.fromkeys(warnings)), "budget": budget or None,
            "progress": round(100 * sum(stage["count"] > 0 for stage in stages) / len(stages)),
            "progress_basis": "artifact_presence_not_production_approval",
            "updated_at": _iso(max(modified)) if modified else None,
            "scene_count": len(scenes), "shot_count": len(shots), "media_count": len(media),
            "cover": next((item for item in media_list if item["kind"] == "image" and not item["archived"] and item["role"] == "shot"),
                          next((item for item in media_list if item["kind"] == "image" and not item["archived"]), None)),
        }

    @staticmethod
    def _filename_ids(path, records):
        # Exact ID tokens in filename/parent directories, not prefix collisions.
        return [identifier for identifier in records if re.search(
            r"(?<![A-Za-z0-9])" + re.escape(identifier) + r"(?![A-Za-z0-9])", path)]

    def _link_document(self, root, artifact, media, shots, entities, warnings, components, prompt_sources):
        def resolve(value):
            if not isinstance(value, str) or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value) or value.startswith("//") or Path(value).suffix.lower() not in MEDIA_TYPES:
                return None
            if value.startswith("/"):
                try:
                    value = Path(value).relative_to(root).as_posix()
                except ValueError:
                    return None
            prefixes = (self.root.name + "/" + root.name + "/", root.name + "/")
            for prefix in prefixes:
                if value.startswith(prefix):
                    value = value[len(prefix):]
                    break
            try:
                safe_parts(value)
            except ValueError:
                return None
            candidates = [value, (PurePosixPath(artifact["path"]).parent / value).as_posix()]
            return next((candidate for candidate in candidates if candidate in media), None)

        def walk(value, context, key="", depth=0):
            if depth > 40:
                return
            context = {name: list(values) if isinstance(values, list) else values for name, values in context.items()}
            if isinstance(value, dict):
                component = components.get(value.get("component_id")) if isinstance(value.get("component_id"), str) else None
                if component and not context["input"]:
                    context["shots"] = component["shots"] or context["shots"]
                    context["entities"] = component["entities"] or context["entities"]
                declared_shots = _ids(value.get("shot_id")) + _ids(value.get("shot_ids")) + _ids(value.get("mapped_shot_ids"))
                if declared_shots and not context["input"]:
                    context["shots"] = list(dict.fromkeys(declared_shots))
                declared_entities = _ids(value.get("entity_id")) + _ids(value.get("entity_ids"))
                for kind in ("character", "location", "prop"):
                    declared_entities += _ids(value.get(kind + "_id")) + _ids(value.get(kind + "_ids"))
                if declared_entities:
                    context["entities"] = list(dict.fromkeys(declared_entities))
                # ComfyUI's prompt_id is a job UUID, not the source prompt ID.
                declared_prompts = _ids(value.get("source_prompt_id"))
                candidate = value.get("prompt_id")
                declared_jobs = _ids(value.get("job_prompt_id")) + _ids(value.get("comfy_prompt_id"))
                if isinstance(candidate, str):
                    if re.fullmatch(r"[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}", candidate):
                        declared_jobs.append(candidate)
                    elif not declared_prompts:
                        declared_prompts.append(candidate)
                if declared_prompts and not context["input"]:
                    context["prompts"] = list(dict.fromkeys(declared_prompts))
                    source = prompt_sources.get(declared_prompts[0], {})
                    if not context["shots"]:
                        context["shots"] = _ids(source.get("shot_id"))
                    if not context["entities"]:
                        context["entities"] = _ids(source.get("entity_id"))
                    if source.get("job_kind") == "reference_illustration":
                        context["reference"] = True
                if declared_jobs and not context["input"]:
                    context["jobs"] = list(dict.fromkeys(declared_jobs))
                if value.get("job_kind") == "reference_illustration" and not context["input"]:
                    context["reference"] = True
                    context["shots"] = []
                review = dict(context["review"])
                for field in ("status", "review_status", "visual_review_status", "asset_status", "approved", "production_final", "film_final", "identity_approved", "canonical_identity_approved", "component_approved"):
                    if not context["input"] and isinstance(value.get(field), (str, bool)):
                        review[field] = value[field]
                context["review"] = review
                if not context["input"] and (any(isinstance(value.get(field), str) and re.search(r"archiv|superseded", value[field], re.I)
                       for field in ("status", "scope", "review_status")) or value.get("reuse_as_current_opening") is False):
                    context["archived"] = True
                for child_key, child in value.items():
                    next_context = dict(context)
                    if child_key in entities:
                        next_context["entities"] = [child_key]
                    if child_key in INPUT_MEDIA_KEYS and not context["input"]:
                        # Crossing into an input subtree starts a separate usage.
                        # IDs declared *inside* that subtree may identify the source,
                        # but the consumer's cast, jobs and review never do.
                        next_context.update(input=True, entities=[], review={}, jobs=[],
                                            archived=False, reference=False)
                    walk(child, next_context, child_key, depth + 1)
            elif isinstance(value, list):
                for child in value:
                    walk(child, context, key, depth + 1)
            elif isinstance(value, str) and Path(value).suffix.lower() in MEDIA_TYPES and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
                relative = resolve(value)
                if relative is None:
                    if key.endswith(("path", "file", "files")) or key in {"video", "audio", "reference_assets", "references"}:
                        warnings.append(f"{artifact['path']}: missing or unsafe media link")
                    return
                item = media[relative]
                shot_ids = [sid for sid in context["shots"] if sid in shots]
                entity_ids = [eid for eid in context["entities"] if eid in entities]
                for sid in context["shots"]:
                    if sid not in shots:
                        warnings.append(f"{artifact['path']}: unknown shot {sid}")
                for eid in context["entities"]:
                    if eid not in entities:
                        warnings.append(f"{artifact['path']}: unknown entity {eid}")
                if context["input"]:
                    usage = {"path": artifact["path"], "shot_ids": shot_ids,
                             "entity_ids": entity_ids, "prompt_ids": context["prompts"],
                             "relation": "explicit"}
                    if usage not in item["usage_records"]:
                        item["usage_records"].append(usage)
                    return
                item["_has_source"] = True
                for field, ids in (("shot_ids", shot_ids), ("entity_ids", entity_ids), ("prompt_ids", context["prompts"]), ("job_ids", context["jobs"])):
                    item[field] = list(dict.fromkeys(item[field] + ids))
                review = context["review"]
                if review:
                    record = {"path": artifact["path"], **review}
                    if record not in item["review_records"]:
                        item["review_records"].append(record)
                    for field in ("approved", "production_final", "film_final"):
                        declared = review.get(field)
                        if isinstance(declared, bool) and item[field] is not False:
                            item[field] = declared
                    if isinstance(review.get("status"), str) and not item["archived"]:
                        item["status"] = review["status"]
                    review_status = _text(review.get("review_status"), review.get("visual_review_status"), review.get("asset_status"))
                    if review_status and not item["archived"]:
                        item["review_status"] = review_status
                if context["archived"]:
                    item["archived"] = True
                    item["status"] = _text(review.get("status"), "archived_or_superseded")
                if shot_ids or entity_ids or context["prompts"]:
                    item["relation"] = "explicit"
                    if context["reference"] or entity_ids and not shot_ids:
                        item["role"] = "reference"
                    elif shot_ids and item["role"] != "reference":
                        item["role"] = "shot"

        walk(artifact["data"], {"shots": [], "entities": [], "prompts": [], "jobs": [],
                                "reference": False, "input": False, "review": {},
                                "archived": "archive" in PurePosixPath(artifact["path"]).parts})
