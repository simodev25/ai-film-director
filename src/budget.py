"""Offline preliminary estimates, before screenplay. Estimates never authorize spending."""
from __future__ import annotations

import math
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml

from cloud_policy import DEFAULT_CONFIG, SCHEMAS, TIERS, file_sha256, load_cloud_policy, pricing_is_current
from validation import validate_data


def default_assumptions(project: Path) -> dict:
    """Explicit rough sizing, not a shot list or a prediction of model success."""
    root = Path(project)
    project_data = _read_mapping(root / "project.yaml") if (root / "project.yaml").is_file() else {}
    story = _read_mapping(root / "story" / "story.yaml")
    duration = project_data.get("duration_seconds") or story.get("format", {}).get("target_duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Provide positive duration_seconds in project.yaml, story.format, or an assumptions file")
    return {
        "duration_seconds": duration,
        "images": math.ceil(duration / 8) + 12,
        "references_per_image": 4,
        "video_fraction": 1.0,
        "audio_seconds": duration,
        "text_input_tokens": 10000,
        "text_output_tokens": 2000,
        "attempts": {"low": 1, "mean": 2, "high": 4},
        "contingency_fraction": 0.20,
    }


def _read_mapping(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return data


def _validate_assumptions(data: dict) -> None:
    validate_data(data, SCHEMAS / "budget-assumptions.schema.yaml")
    # JSON Schema's numbers alone do not reliably exclude YAML .nan / .inf.
    for key, value in data.items():
        if isinstance(value, (float, int)) and not math.isfinite(value):
            raise ValueError(f"Non-finite assumption: {key}")
    values = data["attempts"]
    if any(not math.isfinite(v) for v in values.values()):
        raise ValueError("Attempts must be finite")
    if not values["low"] <= values["mean"] <= values["high"]:
        raise ValueError("Attempts must satisfy low <= mean <= high")


def _money(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def _d(value: float | int) -> Decimal:
    return Decimal(str(value))


def _video_volume(seconds: float, capabilities: dict) -> tuple[float, int]:
    """Fill maximum-length clips then round the last clip to a supported duration.

    Preliminary aggregate sizing only: actual shot boundaries/overlap need a new quote.
    """
    if seconds == 0:
        return 0, 0
    durations = capabilities.get("durations")
    maximum = max(durations) if durations else capabilities["max_duration_seconds"]
    full = math.floor(seconds / maximum)
    remainder = seconds - full * maximum
    if math.isclose(remainder, 0, abs_tol=1e-9):
        return full * maximum, full
    tail = min(v for v in durations if v >= remainder) if durations else max(capabilities["min_duration_seconds"], math.ceil(remainder))
    return full * maximum + tail, full + 1


def estimate_budget(project: Path, assumptions: dict | None = None, *, config_path: Path = DEFAULT_CONFIG, as_of: date | None = None) -> dict:
    root = Path(project)
    if not (root / "story" / "story.yaml").is_file():
        raise ValueError("Story required before budget estimation")
    policy = load_cloud_policy(config_path)
    inputs = assumptions if assumptions is not None else default_assumptions(root)
    _validate_assumptions(inputs)
    project_file = root / "project.yaml"
    project_data = _read_mapping(project_file) if project_file.exists() else {}
    report = {
        "version": 1,
        "project_id": project_data.get("project_id", root.name),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "story_sha256": file_sha256(root / "story" / "story.yaml"),
        "project_sha256": file_sha256(project_file) if project_file.exists() else None,
        "retrospective": (root / "screenplay" / "screenplay.yaml").is_file(),
        "pricing_checked_at": policy["pricing_checked_at"],
        "pricing_status": "current_snapshot" if pricing_is_current(policy, as_of) else "refresh_required",
        "pricing_config_sha256": file_sha256(config_path),
        "pricing_sources": list(policy["sources"]),
        "currency": "USD",
        "scope": "planning_only_not_spend_consent",
        "assumptions": inputs,
        "tiers": {},
        "caveats": [
            "Estimation préliminaire, pas un devis, une facture ni une autorisation de dépense.",
            "Moyen = hypothèse de reprises choisie, pas une moyenne empirique ni une probabilité.",
            "Dimensions et tarifs correspondent aux réglages indiqués ; aucun changement de résolution automatique.",
            "Images et références Google : conversions estimatives des tokens ; texte/raisonnement image exclus.",
            "Budget texte limité aux tokens facturés spécifiés ; contexte GPT inférieur à 272000 tokens.",
            "Vidéo : arrondi des durées d'appels, hors limites réelles des shots et marges de raccord.",
            "Audio : secondes de sources générées, pas durée mixée ; sons réutilisables et silences ne sont pas des appels.",
            "Hors taxes, frais de crédits, licences, musique facultative, prises Foley, travail de montage/mixage.",
            "Pas de qualité ni de continuité garantie. Recalculer après le découpage et avant chaque lot payant.",
            "Sans fichier d'hypothèses : images = plafond(durée/8) images de plans + 12 illustrations de référence provisoires ; pas un découpage réel.",
        ],
    }
    for name in TIERS:
        tier = policy["tiers"][name]
        refs = inputs["references_per_image"]
        if refs > tier["image"]["capabilities"]["max_references"]:
            raise ValueError(f"Too many image references for {name}")
        seconds, clips = _video_volume(inputs["duration_seconds"] * inputs["video_fraction"], tier["video"]["capabilities"])
        text = tier["text"]["pricing"]
        image = tier["image"]["pricing"]
        base = {
            "text_usd": (_d(inputs["text_input_tokens"]) * _d(text["input_per_million"]) + _d(inputs["text_output_tokens"]) * _d(text["output_per_million"])) / Decimal(1000000),
            "image_usd": _d(inputs["images"]) * (_d(image["output_per_image"]) + _d(refs) * _d(image["input_per_reference"])),
            "video_usd": _d(seconds) * _d(tier["video"]["pricing"]["output_per_second"]),
            "audio_usd": _d(inputs["audio_seconds"]) * _d(tier["audio"]["pricing"]["output_per_second"]),
        }
        row = {
            "models": {medium: tier[medium]["model"] for medium in ("text", "image", "video", "audio")},
            "settings": {"image_resolution": tier["image"]["defaults"]["resolution"], "video_resolution": tier["video"]["defaults"]["resolution"], "native_video_audio": False},
            "video_billable_seconds_per_pass": seconds,
            "video_clips_per_pass": clips,
        }
        for case, attempts in inputs["attempts"].items():
            parts = {key: value * _d(attempts) for key, value in base.items()}
            subtotal = sum(parts.values(), Decimal(0))
            contingency = subtotal * _d(inputs["contingency_fraction"])
            row[case] = {"attempts": attempts, **{key: _money(value) for key, value in parts.items()}, "subtotal_usd": _money(subtotal), "contingency_usd": _money(contingency), "total_usd": _money(subtotal + contingency)}
        report["tiers"][name] = row
    validate_data(report, SCHEMAS / "budget-estimate.schema.yaml")
    return report


def budget_markdown(report: dict) -> str:
    lines = ["# Estimation avant scénario", "", "**Estimation uniquement — aucune dépense autorisée.**", "", f"Projet : {report['project_id']} · USD · tarifs vérifiés : {report['pricing_checked_at']} · {report['pricing_status']}", "", "## Hypothèses", ""]
    lines.extend(f"- `{key}` : {value}" for key, value in report["assumptions"].items())
    lines += ["", "Sources des tarifs :", *[f"- {source}" for source in report["pricing_sources"]]]
    if report["retrospective"]:
        lines += ["", "**Revue rétrospective : scénario existant conservé intact ; cette estimation ne le réécrit pas.**"]
    lines += ["", "## Trois gammes — bas / moyen / haut", "", "| Gamme | Images / vidéo | Bas | Moyen | Haut |", "|---|---|---:|---:|---:|"]
    for name, tier in report["tiers"].items():
        values = [f"{tier[case]['total_usd']:.4f} $" for case in ("low", "mean", "high")]
        lines.append(f"| {name} | {tier['settings']['image_resolution']} / {tier['settings']['video_resolution']} | {' | '.join(values)} |")
    for name, tier in report["tiers"].items():
        lines += ["", f"### {name} — détail moyen", "", f"Modèles : {tier['models']}", "", f"Vidéo par passe : {tier['video_billable_seconds_per_pass']} s facturables / {tier['video_clips_per_pass']} clips estimés."]
        lines.extend(f"- {key} : {value:.6f} $" for key, value in tier["mean"].items() if key.endswith("_usd"))
    lines += ["", "## Limites", "", *[f"- {text}" for text in report["caveats"]], "", "## Décision", "", "Faire choisir la gamme et le plafond par l'utilisateur, puis enregistrer budget/decision.yaml avec le hash SHA-256 de estimate.yaml et la référence de son accord. Ne jamais créer un accord automatiquement. Cette revue autorise la planification du scénario, pas les appels cloud.", ""]
    return "\n".join(lines)


def save_budget(project: Path, assumptions: dict | None = None, *, config_path: Path = DEFAULT_CONFIG, as_of: date | None = None) -> dict:
    report = estimate_budget(project, assumptions, config_path=config_path, as_of=as_of)
    directory = Path(project) / "budget"
    directory.mkdir(parents=True, exist_ok=True)
    # Never write decision.yaml. A changed estimate invalidates an old decision's hash.
    (directory / "estimate.yaml").write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (directory / "estimate.md").write_text(budget_markdown(report), encoding="utf-8")
    return report


def budget_state(project: Path, *, config_path: Path = DEFAULT_CONFIG, as_of: date | None = None) -> dict:
    state = {"estimated": False, "reviewed": False, "reason": "missing_estimate"}
    root = Path(project)
    estimate = root / "budget" / "estimate.yaml"
    decision = root / "budget" / "decision.yaml"
    try:
        policy = load_cloud_policy(config_path)
        report = _read_mapping(estimate)
        validate_data(report, SCHEMAS / "budget-estimate.schema.yaml")
        _validate_assumptions(report["assumptions"])
        # Recompute instead of trusting edited totals or substituted models.
        expected = estimate_budget(root, report["assumptions"], config_path=config_path, as_of=as_of)
        for key in ("project_id", "story_sha256", "project_sha256", "pricing_config_sha256", "pricing_sources", "pricing_checked_at", "tiers"):
            if report[key] != expected[key]:
                raise ValueError(f"Estimate does not match {key}")
        state["estimated"] = True
        if not pricing_is_current(policy, as_of) or report["pricing_status"] != "current_snapshot":
            return {**state, "reason": "pricing_refresh_required"}
        if not decision.exists():
            return {**state, "reason": "awaiting_user_review"}
        approval = _read_mapping(decision)
        validate_data(approval, SCHEMAS / "budget-decision.schema.yaml")
        if not math.isfinite(approval["max_spend_usd"]):
            raise ValueError("Budget ceiling must be finite")
        if approval["estimate_sha256"] != file_sha256(estimate):
            return {**state, "reason": "estimate_changed"}
        return {**state, "reviewed": True, "reason": "reviewed_planning_only"}
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        return {**state, "reason": f"invalid_or_missing_budget: {exc}"}
    except Exception as exc:
        # Invalid schema/format errors also fail closed for status and next_stage.
        return {**state, "reason": f"invalid_budget: {exc}"}


def require_budget_review(project: Path, *, selected_tier: str | None = None, **kwargs) -> None:
    state = budget_state(project, **kwargs)
    if not state["reviewed"]:
        raise ValueError(f"Budget review required before screenplay: {state['reason']}")
    if selected_tier is not None:
        decision = _read_mapping(Path(project) / "budget" / "decision.yaml")
        if decision["selected_tier"] != selected_tier:
            raise ValueError("Requested tier differs from explicitly reviewed tier; renewed review required")
