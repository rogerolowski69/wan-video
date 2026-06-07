"""Inspect and import generation run history from the database."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import GenerationRun, utcnow
from db.record import GenerationRecorder
from db.session import get_session
from env_utils import load_env_file
from paths import OUTPUT_DIR

SCRIPT_NAMES: tuple[str, ...] = (
    "fal-ai-inference.py",
    "nano-banana.py",
    "ideogram-character.py",
    "kling-create-voice.py",
    "trellis2-3d.py",
    "hunyuan-3d.py",
    "seeddance-video.py",
    "wan-inference.py",
)


def list_runs(*, limit: int = 20, status: str | None = None) -> int:
    session = get_session()
    stmt = (
        select(GenerationRun)
        .options(selectinload(GenerationRun.artifacts))
        .order_by(GenerationRun.started_at.desc())
        .limit(limit)
    )
    if status:
        stmt = stmt.where(GenerationRun.status == status)

    runs = session.scalars(stmt).all()
    session.close()

    if not runs:
        print("No generation runs recorded yet.")
        return 0

    for run in runs:
        artifacts = ", ".join(a.file_path for a in run.artifacts) or "(none)"
        prompt_preview = (run.prompt or "")[:80]
        if run.prompt and len(run.prompt) > 80:
            prompt_preview += "..."
        print(
            f"[{run.id}] {run.status:<9} {run.script_name}  model={run.model_id}\n"
            f"     started={run.started_at.isoformat()}  artifacts={artifacts}\n"
            f"     prompt={prompt_preview or '(none)'}"
        )
        if run.error_message:
            print(f"     error={run.error_message}")

    return 0


def show_status() -> int:
    """Show latest completed run per script."""
    session = get_session()
    print(f"Database: {session.bind.url}\n")
    print(f"{'Script':<28} {'Status':<10} {'Last run':<28} Artifacts")
    print("-" * 90)

    for script_name in SCRIPT_NAMES:
        run = session.scalars(
            select(GenerationRun)
            .options(selectinload(GenerationRun.artifacts))
            .where(GenerationRun.script_name == script_name)
            .order_by(GenerationRun.started_at.desc())
            .limit(1)
        ).first()

        if run is None:
            print(f"{script_name:<28} {'—':<10} {'never':<28} —")
            continue

        artifact_count = len(run.artifacts)
        started = run.started_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{script_name:<28} {run.status:<10} {started:<28} {artifact_count} file(s)")

    session.close()
    return 0


def mark_stale_running() -> int:
    """Mark interrupted runs still in 'running' status as failed."""
    session = get_session()
    runs = session.scalars(select(GenerationRun).where(GenerationRun.status == "running")).all()
    for run in runs:
        run.status = "failed"
        run.error_message = "interrupted (process did not finish)"
        run.completed_at = utcnow()
    session.commit()
    count = len(runs)
    session.close()
    print(f"Marked {count} stale run(s) as failed.")
    return 0


def import_output_folder() -> int:
    """Backfill DB records for files already in output/ (no API re-run)."""
    if not OUTPUT_DIR.is_dir():
        print(f"Output folder not found: {OUTPUT_DIR}")
        return 1

    json_files = sorted(OUTPUT_DIR.glob("*.json"))
    imported = 0
    covered: set[Path] = set()

    if not json_files and not any(OUTPUT_DIR.iterdir()):
        print("No files to import in output/.")
        return 0

    for json_path in json_files:
        stem = json_path.stem
        group_files = sorted(OUTPUT_DIR.glob(f"{stem}*"))
        if not group_files:
            continue

        covered.update(group_files)
        with GenerationRecorder(
            script_name=f"import:{stem}",
            model_id=stem,
            backend="import",
            prompt=f"imported from output/{stem}",
        ) as recorder:
            recorder.register_artifacts(group_files)
            imported += 1

    orphans = sorted(
        path
        for path in OUTPUT_DIR.iterdir()
        if path.is_file() and path not in covered
    )
    for orphan in orphans:
        with GenerationRecorder(
            script_name=f"import:{orphan.stem}",
            model_id=orphan.stem,
            backend="import",
            prompt=f"imported from output/{orphan.name}",
        ) as recorder:
            recorder.register_artifact(orphan)
            imported += 1

    print(f"Imported {imported} output group(s) from {OUTPUT_DIR}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generation run history")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="List recent generation runs")
    list_cmd.add_argument("--limit", type=int, default=20)
    list_cmd.add_argument("--status", choices=["running", "completed", "failed"])

    sub.add_parser("status", help="Latest run status per script")
    sub.add_parser("import-output", help="Import existing output/ files into the database")
    sub.add_parser("fix-stale", help="Mark interrupted 'running' records as failed")

    return parser


def main() -> int:
    load_env_file()
    args = build_parser().parse_args()

    if args.command == "list":
        return list_runs(limit=args.limit, status=args.status)
    if args.command == "status":
        return show_status()
    if args.command == "import-output":
        return import_output_folder()
    if args.command == "fix-stale":
        return mark_stale_running()

    return 1


if __name__ == "__main__":
    sys.exit(main())
