from __future__ import annotations

from pathlib import Path

from budget import budget_state, require_budget_review

STAGES = [
    "story",
    "budget",
    "screenplay",
    "characters",
    "locations",
    "props",
    "storyboard",
    "shots",
    "images",
    "videos",
    "audio",
    "final",
]


def _dir_has_files(path: Path, pattern: str = "*.yaml") -> bool:
    # support both flat prompts/images/*.yaml and model subfolders prompts/images/<model>/*.yaml
    return path.is_dir() and any(path.rglob(pattern))


class FilmDirector:
    def __init__(self, project_root: Path):
        self.root = Path(project_root)

    def status(self) -> dict[str, bool]:
        root = self.root
        return {
            "story": (root / "story" / "story.yaml").is_file(),
            "budget": budget_state(root)["reviewed"],
            "screenplay": (root / "screenplay" / "screenplay.yaml").is_file(),
            "characters": (root / "characters" / "characters.yaml").is_file(),
            "locations": (root / "locations" / "locations.yaml").is_file(),
            "props": (root / "props" / "props.yaml").is_file(),
            "storyboard": (root / "storyboard" / "storyboard.yaml").is_file(),
            "shots": (root / "shots" / "shots.yaml").is_file(),
            "images": _dir_has_files(root / "prompts" / "images"),
            "videos": _dir_has_files(root / "prompts" / "videos"),
            "audio": _dir_has_files(root / "prompts" / "audio"),
            "final": (root / "final" / "film.mp4").is_file(),
        }

    def next_stage(self) -> str:
        status = self.status()
        for stage in STAGES:
            if not status.get(stage, False):
                return stage
        return "complete"

    def require_stage(self, stage: str, *, selected_tier: str | None = None) -> None:
        if stage not in STAGES:
            raise ValueError(f"Unknown stage: {stage}")
        if stage != "story" and not (self.root / "story" / "story.yaml").is_file():
            raise ValueError("Story required before further planning")
        if stage not in {"story", "budget"}:
            require_budget_review(self.root, selected_tier=selected_tier)
