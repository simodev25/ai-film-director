"""Canonical target checks, without creating IDs or changing project artifacts."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

import yaml
import jsonschema


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


SOURCES = {
    "character": ("characters/characters.yaml", "characters", "character_id"),
    "location": ("locations/locations.yaml", "locations", "location_id"),
    "prop": ("props/props.yaml", "props", "prop_id"),
}


def _inside(project, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("Exploratory evidence requires a project-relative path")
    path = (project / relative).resolve()
    if (not isinstance(relative, str) or Path(relative).is_absolute()
            or ".." in Path(relative).parts or not path.is_relative_to(project)
            or not path.is_file()):
        raise ValueError("Exploratory evidence must be an existing project-relative file")
    return path


def exploratory_target_evidence(job, project, scope):
    """Resolve typed sources, not caller IDs; hash source bytes and approved assets.

    An existing canonical category is authoritative. Only absent categories may
    use approved references corroborated by typed story declarations. Nothing
    here creates production entities, stages, scenes, or spend consent.
    """
    project = Path(project).resolve()
    project_id = _read(_inside(project, "project.yaml"))["project_id"]
    if job.get("project_id") != project_id:
        raise ValueError("Cross-project exploratory target")
    if (job.get("job_kind") != "reference_illustration" or job.get("modality") != "image"
            or any(k in job for k in ("scene_id", "shot_id", "segment_id"))):
        raise ValueError("Exploratory scope is only for standalone reference illustrations")
    if (scope is None or scope.scene_ids or not scope.entity_ids
            or len(set(scope.entity_ids)) != len(scope.entity_ids)):
        raise ValueError("Exploratory scope requires empty scene_ids and unique nonempty entity_ids")
    evidence = {}
    def read_source(relative):
        path = _inside(project, relative)
        evidence[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        data = _read(path)
        if isinstance(data, Mapping) and data.get("project_id", project_id) != project_id:
            raise ValueError("Cross-project exploratory source")
        return data
    read_source("project.yaml")
    story = read_source("story/story.yaml")
    approved = {}
    registry_path = project / "references/approved-references.yaml"
    if registry_path.exists():
        registry = read_source("references/approved-references.yaml")
        from validation import validate_data
        try:
            validate_data(registry, Path(__file__).resolve().parents[2] / "schemas/approved-references.schema.yaml")
        except jsonschema.ValidationError as exc:
            raise ValueError("Invalid approved reference registry schema") from exc
        if registry.get("registry_version") != 1 or registry.get("project_id") != project_id:
            raise ValueError("Invalid approved reference registry")
        orders = set()
        types = {}
        for row in registry.get("references", []):
            kind, entity = row["entity_type"], row["entity_id"]
            if kind not in SOURCES or not isinstance(entity, str) or not entity:
                raise ValueError("Invalid approved typed entity")
            if entity in types and types[entity] != kind:
                raise ValueError("Ambiguous approved entity type")
            types[entity] = kind
            if row["order"] in orders:
                raise ValueError("Ambiguous approved reference order")
            orders.add(row["order"])
            approval = registry.get("approval", {})
            if (not row.get("approved_at", approval.get("approved_at"))
                    or not str(row.get("consent_verbatim", approval.get("consent_verbatim", ""))).strip()):
                raise ValueError("Reference lacks existing user approval evidence")
            assets = [(row["path"], row["sha256"])] + [
                (v["asset_path"], v["sha256"]) for v in row.get("views", [])]
            for relative, expected in assets:
                path = _inside(project, relative)
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual != expected:
                    raise ValueError("Stale approved reference asset hash")
                evidence[relative] = actual
                approved[(kind, entity, relative)] = actual
    known = {}
    for kind, (relative, collection, key) in SOURCES.items():
        path = project / relative
        if path.exists():
            ids = _index(read_source(relative), collection, key)
        else:
            evidence[relative] = None  # Creating a canonical registry invalidates preparation.
            declarations = story.get(collection, [])
            if (not isinstance(declarations, list) or any(not isinstance(i, str) or not i for i in declarations)
                    or len(declarations) != len(set(declarations))):
                raise ValueError("Ambiguous typed story declarations")
            ids = {entity for k, entity, _ in approved if k == kind and entity in declarations}
        for entity in ids:
            if entity in known:
                raise ValueError("Ambiguous cross-category exploratory entity_id")
            known[entity] = kind
    if not set(scope.entity_ids) <= set(known):
        raise ValueError("Unknown exploratory entity_id in reviewed scope")
    if (job.get("entity_id") not in scope.entity_ids
            or known.get(job.get("entity_id")) != job.get("entity_type")):
        raise ValueError("Exploratory entity outside reviewed typed scope")
    for ref in job.get("references", []):
        identity = (ref.get("entity_type"), ref.get("entity_id"), ref.get("asset_path"))
        if (ref.get("role") != "reference" or ref.get("entity_id") not in scope.entity_ids
                or known.get(ref.get("entity_id")) != ref.get("entity_type")
                or identity not in approved or approved[identity] != ref.get("sha256")):
            raise ValueError("Exploratory reference not in approved typed asset evidence")
    digest = hashlib.sha256(json.dumps({"files": evidence, "scope": {
        "scene_ids": list(scope.scene_ids), "entity_ids": list(scope.entity_ids)},
        "ordered_references": job.get("references", [])}, sort_keys=True).encode()).hexdigest()
    return project_id, digest


def validate_project_target(job, project: Path, scope: ProjectScope | None = None):
    """Resolve an output to an existing shot or an entity present in a scene.

    Scope is a restriction, never a source of IDs. Missing/ambiguous registries
    fail closed. Old shot plans need not declare project_id or scene_id.
    """
    project = Path(project)
    if job.get("reference_scope") == "exploratory":
        project_id, digest = exploratory_target_evidence(job, project, scope)
        if job.get("target_evidence_sha256") != digest:
            raise ValueError("Exploratory target evidence changed; re-prepare and renew paid approval")
        return project_id, None
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
