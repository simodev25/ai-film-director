from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import jsonschema
import yaml
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7


@lru_cache(maxsize=None)
def _load_schema_cached(schema_str: str) -> dict:
    return yaml.safe_load(Path(schema_str).read_text(encoding="utf-8"))


def validate_file(data_file: Path, schema_file: Path) -> bool:
    data = yaml.safe_load(data_file.read_text(encoding="utf-8"))
    validate_data(data, schema_file)
    return True


def validate_data(data: object, schema_file: Path) -> None:
    """Validate data with local sibling schema references; never fetch schemas online."""
    path = Path(schema_file).resolve()
    schema = dict(_load_schema_cached(str(path)))
    schema.setdefault("$id", path.as_uri())
    resources = []
    for sibling in path.parent.glob("*.schema.yaml"):
        value = dict(_load_schema_cached(str(sibling.resolve())))
        value.setdefault("$id", sibling.resolve().as_uri())
        resources.append((sibling.resolve().as_uri(), Resource.from_contents(value, default_specification=DRAFT7)))
    registry = Registry().with_resources(resources)
    validator = jsonschema.validators.validator_for(schema)
    validator.check_schema(schema)
    validator(schema, registry=registry, format_checker=jsonschema.FormatChecker()).validate(data)
