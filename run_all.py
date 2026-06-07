"""Run all generation scripts non-interactively with --demo and save to output/."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import GenerationRun, utcnow
from db.session import get_session
from paths import OUTPUT_DIR, PROJECT_ROOT

LOG_PATH = OUTPUT_DIR / "run-all.log"

from scripts_config import GENERATION_SCRIPTS as SCRIPTS, resolve_script_name, script_name_variants


@dataclass(frozen=True)
class ScriptResult:
    script: str
    exit_code: int
    elapsed_s: float
    artifacts: tuple[str, ...]


def _log(message: str, *, log_file) -> None:
    line = message.rstrip()
    print(line, flush=True)
    log_file.write(line + "\n")
    log_file.flush()


def migrate_db() -> int:
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


def fix_stale_running() -> int:
    session = get_session()
    runs = session.scalars(select(GenerationRun).where(GenerationRun.status == "running")).all()
    for run in runs:
        run.status = "failed"
        run.error_message = "interrupted (process did not finish)"
        run.completed_at = utcnow()
    session.commit()
    count = len(runs)
    session.close()
    return count


def latest_artifacts(script_name: str) -> tuple[str, ...]:
    session = get_session()
    names = script_name_variants(script_name)
    run = session.scalars(
        select(GenerationRun)
        .options(selectinload(GenerationRun.artifacts))
        .where(GenerationRun.script_name.in_(names))
        .order_by(GenerationRun.started_at.desc())
        .limit(1)
    ).first()
    session.close()
    if run is None or run.status != "completed":
        return ()
    return tuple(a.file_path for a in run.artifacts)


def run_script(script: str, *, log_file) -> ScriptResult:
    _log(f"\n{'=' * 60}\n[{_timestamp()}] Running {script} --demo\n{'=' * 60}", log_file=log_file)
    started = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    proc = subprocess.Popen(
        ["uv", "run", "python", script, "--demo"],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        _log(line.rstrip("\n"), log_file=log_file)
    returncode = proc.wait()
    elapsed = time.perf_counter() - started
    artifacts = latest_artifacts(script) if returncode == 0 else ()
    status = "OK" if returncode == 0 else f"FAIL ({returncode})"
    _log(f"[{_timestamp()}] {script}: {status} in {elapsed:.1f}s", log_file=log_file)
    if artifacts:
        for path in artifacts:
            _log(f"  -> {path}", log_file=log_file)
    return ScriptResult(script, returncode, elapsed, artifacts)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def _print_summary(results: list[ScriptResult], *, log_file) -> None:
    _log(f"\n{'=' * 60}\nSummary", log_file=log_file)
    total = sum(r.elapsed_s for r in results)
    ok = sum(1 for r in results if r.exit_code == 0)
    _log(f"  {ok}/{len(results)} succeeded  total time {total:.1f}s", log_file=log_file)
    _log(f"  log: {LOG_PATH}", log_file=log_file)
    _log(f"  output: {OUTPUT_DIR}", log_file=log_file)
    for result in results:
        mark = "ok" if result.exit_code == 0 else "FAIL"
        _log(f"  [{mark:4}] {result.elapsed_s:6.1f}s  {result.script}", log_file=log_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run all generation scripts with --demo.")
    parser.add_argument(
        "--from",
        dest="from_script",
        metavar="SCRIPT",
        help="Resume from this script (skip earlier ones), e.g. ideogram-character.py",
    )
    parser.add_argument(
        "--only",
        dest="only_script",
        metavar="SCRIPT",
        help="Run a single script only",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Keep running remaining scripts after a failure",
    )
    return parser


def select_scripts(args: argparse.Namespace) -> tuple[str, ...]:
    if args.only_script:
        resolved = resolve_script_name(args.only_script)
        if resolved not in SCRIPTS:
            raise SystemExit(f"Unknown script: {args.only_script}. Choices: {', '.join(SCRIPTS)}")
        return (resolved,)

    if args.from_script:
        resolved = resolve_script_name(args.from_script)
        if resolved not in SCRIPTS:
            raise SystemExit(f"Unknown script: {args.from_script}. Choices: {', '.join(SCRIPTS)}")
        index = SCRIPTS.index(resolved)
        return SCRIPTS[index:]

    return SCRIPTS


def main() -> int:
    args = build_parser().parse_args()
    scripts = select_scripts(args)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    stale = fix_stale_running()
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        _log(f"\n{'#' * 60}\n[{_timestamp()}] run_all.py started ({len(scripts)} script(s))", log_file=log_file)
        if stale:
            _log(f"  marked {stale} stale 'running' record(s) as failed", log_file=log_file)

        if migrate_db() != 0:
            _log("Migration failed.", log_file=log_file)
            return 1

        results: list[ScriptResult] = []
        failures: list[str] = []

        for script in scripts:
            outcome = run_script(script, log_file=log_file)
            results.append(outcome)
            if outcome.exit_code != 0:
                failures.append(f"{script} (exit {outcome.exit_code})")
                if not args.continue_on_error:
                    _log(f"\nStopping early (use --continue-on-error to run all).", log_file=log_file)
                    break

        _print_summary(results, log_file=log_file)

        if failures:
            _log("\nFailed:", log_file=log_file)
            for name in failures:
                _log(f"  - {name}", log_file=log_file)
            _log(f"\nResume with: uv run python run_all.py --from {failures[0].split()[0]}", log_file=log_file)
            return 1

        _log("\nAll scripts completed successfully.", log_file=log_file)
        return 0


if __name__ == "__main__":
    sys.exit(main())
