import argparse
from pathlib import Path

import yaml

from budget import budget_state, save_budget

from manifest import save_manifest
from pipeline.director import FilmDirector


def main():
    parser = argparse.ArgumentParser(
        prog="film-director"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("project")

    manifest = sub.add_parser("manifest")
    manifest.add_argument("project")

    budget = sub.add_parser("budget", help="Offline low/mean/high estimates for three cloud tiers; no spending")
    budget.add_argument("project")
    budget.add_argument("--assumptions", type=Path, help="YAML sizing assumptions (budget-assumptions.schema.yaml)")

    dashboard = sub.add_parser("dashboard", help="Local read-only web dashboard for every project; no ComfyUI required")
    dashboard.add_argument("--projects-root", type=Path, default=Path("projects"), help="Directory containing project folders")
    dashboard.add_argument("--port", type=int, default=8765, help="Local HTTP port (default: 8765)")

    args = parser.parse_args()

    if args.command == "dashboard":
        from dashboard.server import serve

        serve(args.projects_root, port=args.port)
        return

    root = Path(args.project)

    if args.command == "status":
        director = FilmDirector(root)

        for stage, value in director.status().items():
            print(
                f"{stage:15} "
                f"{'READY' if value else 'MISSING'}"
            )

        print(f"\nnext: {director.next_stage()}")
        print(f"budget: {budget_state(root)['reason']}")

    elif args.command == "manifest":
        print(save_manifest(root))

    elif args.command == "budget":
        if not (root / "story" / "story.yaml").is_file():
            parser.error("Create the story before estimating the screenplay/production budget")
        assumptions = yaml.safe_load(args.assumptions.read_text(encoding="utf-8")) if args.assumptions else None
        report = save_budget(root, assumptions)
        print("USD — estimation seulement, aucune dépense autorisée")
        for tier, row in report["tiers"].items():
            print(f"{tier:15} bas={row['low']['total_usd']:.4f} moyen={row['mean']['total_usd']:.4f} haut={row['high']['total_usd']:.4f}")
        print(f"Tarifs: {report['pricing_status']}; rapport: {root / 'budget' / 'estimate.md'}")
        print("En attente de revue utilisateur ; decision.yaml n'a pas été créé.")


if __name__ == "__main__":
    main()
