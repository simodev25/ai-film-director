"""Canonical target checks, without creating IDs or changing project artifacts."""
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml


@dataclass(frozen=True)
class ProjectScope:
    """Caller-reviewed content scope, additionally bound by paid-job approval."""
    scene_ids: tuple[str, ...]
    entity_ids: tuple[str, ...] = ()


def _read(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _index(data, collection, key):
    rows = data.get(collection, []) if isinstance(data, Mapping) else data
    if not isinstance(rows, list):
        raise ValueError("Unsupported canonical collection")
    result = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get(key), str) or not row[key]:
            raise ValueError("Invalid canonical ID")
        if row[key] in result:
            raise ValueError("Ambiguous canonical ID")
        result[row[key]] = row
    return result


def validate_project_target(job, project: Path, scope: ProjectScope | None = None):
    """Resolve an output to an existing shot or an entity present in a scene.

    Scope is a restriction, never a source of IDs. Missing/ambiguous registries
    fail closed. Old shot plans need not declare project_id or scene_id.
    """
    project = Path(project)
    project_id = _read(project / "project.yaml")["project_id"]
    if job.get("project_id", project_id) != project_id:
        raise ValueError("Cross-project cloud target")
    shots = _index(_read(project / "shots/shots.yaml"), "shots", "shot_id")
    scenes = {row["scene_id"] for row in shots.values()}
    sources = {
        "character": ("characters/characters.yaml", "characters", "character_id"),
        "location": ("locations/locations.yaml", "locations", "location_id"),
        "prop": ("props/props.yaml", "props", "prop_id"),
    }
    def entity_index(kind):
        source, collection, key = sources[kind]
        return _index(_read(project / source), collection, key)
    if scope is not None:
        if (not scope.scene_ids or len(set(scope.scene_ids)) != len(scope.scene_ids)
                or len(set(scope.entity_ids)) != len(scope.entity_ids)
                or not set(scope.scene_ids) <= scenes):
            raise ValueError("Invalid canonical project scope")
        known_entities = set()
        for kind in sources:
            # Unused absent categories are permitted; requested IDs are not.
            if (project / sources[kind][0]).exists():
                ids = set(entity_index(kind))
                if ids & known_entities:
                    raise ValueError("Ambiguous cross-category canonical entity_id")
                known_entities.update(ids)
        if not set(scope.entity_ids) <= known_entities:
            raise ValueError("Unknown canonical entity_id in scope")
    if job.get("job_kind", "shot_render") == "shot_render":
        shot = shots.get(job["shot_id"])
        if shot is None:
            raise ValueError("Unknown canonical shot_id")
        scene_id = shot["scene_id"]
        if job.get("scene_id", scene_id) != scene_id:
            raise ValueError("Shot/scene mismatch")
    else:
        scene_id = job["scene_id"]
        kind = job["entity_type"]
        entities = entity_index(kind)
        entity_id = job["entity_id"]
        if entity_id not in entities:
            raise ValueError("Unknown canonical entity_id")
        relevant = [row for row in shots.values() if row["scene_id"] == scene_id]
        def present(row):
            if kind == "character":
                return entity_id in row.get("characters", [])
            if kind == "prop":
                return entity_id in row.get("prop_ids", row.get("props", []))
            return (entity_id == row.get("location_id")
                    or entity_id in row.get("secondary_location_ids", []))
        if not any(present(row) for row in relevant):
            raise ValueError("Entity absent from canonical scene")
        if scope is not None and entity_id not in scope.entity_ids:
            raise ValueError("Entity outside reviewed scope")
    if scene_id not in scenes or (scope is not None and scene_id not in scope.scene_ids):
        raise ValueError("Scene outside reviewed scope")
    return project_id, scene_id
