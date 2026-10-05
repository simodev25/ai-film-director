#!/usr/bin/env python3
"""Crop a reference model sheet into isolated per-view PNGs (local, free, offline).

A model sheet (turnaround, expression, outfit, location layout, floor plan, prop
sheet) is generated/approved as ONE image; image/video models should be fed the
isolated view matching the shot angle, not the whole grid. This tool only crops
pixels with Pillow: no network, no ComfyUI, no generation, no spend.

Examples::

    # 1x4 turnaround -> front / three_quarter / profile / back
    python scripts/split_model_sheet.py SHEET.png --grid 1x4 \
        --views front,three_quarter,profile,back --out-dir references/views/char_marc

    # explicit boxes "left,top,right,bottom;..." (source pixels)
    python scripts/split_model_sheet.py SHEET.png --boxes "0,0,512,768;512,0,1024,768" \
        --views front,back --out-dir DIR

    # also record the views in projects/<p>/references/approved-references.yaml
    python scripts/split_model_sheet.py SHEET.png --grid 1x4 --views ... --out-dir DIR \
        --registry projects/p/references/approved-references.yaml --entity-id char_marc

Crops never overwrite an existing file unless ``--overwrite``; a registry entry
that already has ``views`` is only replaced with ``--replace-views``. The sheet's
SHA-256 must equal the registry entry's recorded ``sha256`` (the approved sheet).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

import yaml

VIEWS = ("front", "three_quarter", "profile", "back", "top", "other")
REPO = Path(__file__).resolve().parents[1]


class SheetError(ValueError):
    """Invalid sheet, layout, view list or registry binding."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_grid(text: str) -> tuple[int, int]:
    try:
        rows, cols = (int(part) for part in text.lower().split("x"))
    except ValueError as exc:
        raise SheetError(f"--grid must look like ROWSxCOLS, got {text!r}") from exc
    if rows < 1 or cols < 1:
        raise SheetError("--grid rows and cols must be >= 1")
    return rows, cols


def parse_boxes(text: str) -> list[tuple[int, int, int, int]]:
    boxes = []
    for chunk in (c for c in text.split(";") if c.strip()):
        try:
            box = tuple(int(v) for v in chunk.split(","))
        except ValueError as exc:
            raise SheetError(f"Invalid box {chunk!r}") from exc
        if len(box) != 4:
            raise SheetError(f"Box needs left,top,right,bottom: {chunk!r}")
        boxes.append(box)
    if not boxes:
        raise SheetError("--boxes is empty")
    return boxes


def grid_boxes(width: int, height: int, rows: int, cols: int, margin: int = 0,
               gutter: int = 0) -> list[tuple[int, int, int, int]]:
    """Row-major cells; integer-exact so cells cover the usable area without drift."""
    usable_w = width - 2 * margin - (cols - 1) * gutter
    usable_h = height - 2 * margin - (rows - 1) * gutter
    if usable_w < cols or usable_h < rows:
        raise SheetError("Margin/gutter leave no room for the requested grid")
    boxes = []
    for r in range(rows):
        top = margin + r * gutter + (usable_h * r) // rows
        bottom = margin + r * gutter + (usable_h * (r + 1)) // rows
        for c in range(cols):
            left = margin + c * gutter + (usable_w * c) // cols
            right = margin + c * gutter + (usable_w * (c + 1)) // cols
            boxes.append((left, top, right, bottom))
    return boxes


def check_boxes(boxes: Iterable[Sequence[int]], width: int, height: int) -> None:
    for box in boxes:
        left, top, right, bottom = box
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise SheetError(f"Box {list(box)} is outside the {width}x{height} sheet or empty")


def parse_views(text: str, count: int) -> list[str]:
    views = [v.strip() for v in text.split(",") if v.strip()]
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        raise SheetError(f"Unknown view(s) {unknown}; allowed: {', '.join(VIEWS)}")
    if len(views) != count:
        raise SheetError(f"{len(views)} view name(s) for {count} crop box(es); give exactly one per box")
    return views


def split_sheet(sheet: Path, out_dir: Path, boxes: Sequence[Sequence[int]], views: Sequence[str], *,
                prefix: str | None = None, labels: Sequence[str] | None = None,
                relative_to: Path | None = None, overwrite: bool = False) -> list[dict]:
    """Write one PNG per box and return approved-references ``views`` entries."""
    from PIL import Image  # local import: only this command needs Pillow

    sheet = Path(sheet)
    with Image.open(sheet) as image:
        image.load()
        width, height = image.size
        check_boxes(boxes, width, height)
        if len(views) != len(boxes):
            raise SheetError("One view name per crop box is required")
        if labels is not None and len(labels) != len(boxes):
            raise SheetError("One label per crop box is required")
        out_dir = Path(out_dir)
        stem = prefix or sheet.stem
        targets = [out_dir / f"{stem}_{i:02d}_{view}.png" for i, view in enumerate(views, 1)]
        existing = [str(t) for t in targets if t.exists()]
        if existing and not overwrite:
            raise SheetError(f"Refusing to overwrite existing crop(s): {existing} (use --overwrite)")
        out_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        for index, (box, view, target) in enumerate(zip(boxes, views, targets)):
            crop = image.crop(tuple(box))
            if crop.mode not in ("RGB", "RGBA", "L", "LA"):
                crop = crop.convert("RGBA" if "A" in crop.getbands() else "RGB")
            crop.save(target, format="PNG")
            asset = target.resolve()
            if relative_to is not None:
                asset_path = asset.relative_to(Path(relative_to).resolve()).as_posix()
            else:
                asset_path = target.as_posix()
            entry = {"view": view, "asset_path": asset_path, "sha256": sha256_file(target),
                     "box": [int(v) for v in box]}
            if labels is not None:
                entry["label"] = labels[index]
            entries.append(entry)
    return entries


def _leading_comments(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        if line.startswith("#") or (lines and not line.strip()):
            lines.append(line)
        else:
            break
    return "".join(lines)


def registry_row(data: dict, registry: Path, entity_id: str, sheet: Path, *,
                 replace_views: bool = False) -> dict:
    """The one approved row for this exact sheet (path + SHA-256); fail closed otherwise."""
    project_root = Path(registry).resolve().parents[1]
    sheet_hash = sha256_file(sheet)
    matches = [r for r in (data or {}).get("references", []) if r.get("entity_id") == entity_id
               and r.get("sha256") == sheet_hash]
    if len(matches) != 1:
        raise SheetError(f"No single approved reference for {entity_id} whose sha256 matches the sheet "
                         f"({sheet_hash}); approve/register the sheet first")
    row = matches[0]
    if (project_root / row["path"]).resolve() != Path(sheet).resolve():
        raise SheetError("Sheet path differs from the registered reference path")
    if row.get("views") and not replace_views:
        raise SheetError(f"{entity_id} already has views; use --replace-views to replace them")
    return row


def update_registry(registry: Path, entity_id: str, sheet: Path, views: list[dict], *,
                    sheet_type: str | None = None, replace_views: bool = False) -> dict:
    """Attach crop entries to the approved sheet's registry row, schema-validated."""
    registry = Path(registry)
    text = registry.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    row = registry_row(data, registry, entity_id, sheet, replace_views=replace_views)
    for entry in views:
        if Path(entry["asset_path"]).is_absolute():
            raise SheetError("Registry views need project-relative asset paths (--relative-to project root)")
    if sheet_type is not None:
        row["sheet_type"] = sheet_type
    row["views"] = views
    sys.path.insert(0, str(REPO / "src"))
    from validation import validate_data  # noqa: E402  (repository helper)

    validate_data(data, REPO / "schemas/approved-references.schema.yaml")
    registry.write_text(_leading_comments(text) + yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                        encoding="utf-8")
    return row


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("sheet", type=Path)
    layout = parser.add_mutually_exclusive_group(required=True)
    layout.add_argument("--grid", help="ROWSxCOLS, row-major order")
    layout.add_argument("--boxes", help="'left,top,right,bottom;...' in source pixels")
    parser.add_argument("--views", required=True, help=f"comma list, one per box: {', '.join(VIEWS)}")
    parser.add_argument("--labels", help="optional comma list of human labels, one per box")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--prefix", help="output file stem (default: sheet stem)")
    parser.add_argument("--margin", type=int, default=0, help="grid outer margin in pixels")
    parser.add_argument("--gutter", type=int, default=0, help="grid gap between cells in pixels")
    parser.add_argument("--relative-to", type=Path, help="write asset_path relative to this dir (project root)")
    parser.add_argument("--overwrite", action="store_true", help="allow replacing existing crop files")
    parser.add_argument("--registry", type=Path, help="approved-references.yaml to attach views to")
    parser.add_argument("--entity-id", help="registry entity whose approved sheet this is")
    parser.add_argument("--sheet-type", choices=["turnaround", "expression", "outfit", "location_layout",
                                                 "floor_plan", "prop_sheet"])
    parser.add_argument("--replace-views", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.registry and not args.entity_id:
            raise SheetError("--registry requires --entity-id")
        from PIL import Image

        with Image.open(args.sheet) as image:
            width, height = image.size
        if args.grid:
            rows, cols = parse_grid(args.grid)
            boxes = grid_boxes(width, height, rows, cols, args.margin, args.gutter)
        else:
            boxes = parse_boxes(args.boxes)
        views = parse_views(args.views, len(boxes))
        labels = [l.strip() for l in args.labels.split(",")] if args.labels else None
        relative_to = args.relative_to
        if args.registry:
            # Bind to the approved sheet BEFORE writing any crop file.
            registry_row(yaml.safe_load(args.registry.read_text(encoding="utf-8")), args.registry,
                         args.entity_id, args.sheet, replace_views=args.replace_views)
            if relative_to is None:
                relative_to = args.registry.resolve().parents[1]
        entries = split_sheet(args.sheet, args.out_dir, boxes, views, prefix=args.prefix, labels=labels,
                              relative_to=relative_to, overwrite=args.overwrite)
        if args.registry:
            update_registry(args.registry, args.entity_id, args.sheet, entries,
                            sheet_type=args.sheet_type, replace_views=args.replace_views)
    except SheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"views": entries}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
