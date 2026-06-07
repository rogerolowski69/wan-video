"""Launch generation scripts as background subprocess jobs."""

from __future__ import annotations

import os
import subprocess
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from paths import PROJECT_ROOT
from scripts_config import GenerationModel, get_model

_lock = threading.Lock()
_jobs: dict[str, JobRecord] = {}


@dataclass
class JobRecord:
    job_id: str
    model_id: str
    script_path: str
    demo: bool
    status: str
    started_at: str
    exit_code: int | None = None
    error: str | None = None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_command(model: GenerationModel, *, demo: bool, provider: str | None) -> list[str]:
    cmd = ["uv", "run", "python", model.path]
    if demo:
        cmd.append("--demo")
    if model.id == "wan" and provider:
        cmd.extend(["--provider", provider])
    return cmd


def _run_subprocess(job_id: str, cmd: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            check=False,
        )
        with _lock:
            job = _jobs[job_id]
            job.exit_code = result.returncode
            job.status = "completed" if result.returncode == 0 else "failed"
            if result.returncode != 0:
                job.error = f"Process exited with code {result.returncode}"
    except Exception as exc:
        with _lock:
            job = _jobs[job_id]
            job.status = "failed"
            job.error = str(exc)


def start_model_job(
    model_id: str,
    *,
    demo: bool = True,
    provider: str | None = None,
) -> JobRecord:
    model = get_model(model_id)
    if model is None:
        raise ValueError(f"Unknown model: {model_id}")

    job_id = uuid.uuid4().hex[:12]
    record = JobRecord(
        job_id=job_id,
        model_id=model_id,
        script_path=model.path,
        demo=demo,
        status="running",
        started_at=_utcnow_iso(),
    )
    cmd = _build_command(model, demo=demo, provider=provider)

    with _lock:
        _jobs[job_id] = record

    thread = threading.Thread(target=_run_subprocess, args=(job_id, cmd), daemon=True)
    thread.start()
    return record


def start_run_all(*, continue_on_error: bool = True) -> JobRecord:
    job_id = uuid.uuid4().hex[:12]
    record = JobRecord(
        job_id=job_id,
        model_id="run-all",
        script_path="run_all.py",
        demo=True,
        status="running",
        started_at=_utcnow_iso(),
    )
    cmd = ["uv", "run", "python", "run_all.py"]
    if continue_on_error:
        cmd.append("--continue-on-error")

    with _lock:
        _jobs[job_id] = record

    thread = threading.Thread(target=_run_subprocess, args=(job_id, cmd), daemon=True)
    thread.start()
    return record


def get_job(job_id: str) -> JobRecord | None:
    with _lock:
        return _jobs.get(job_id)


def list_jobs(limit: int = 20) -> list[JobRecord]:
    with _lock:
        jobs = sorted(_jobs.values(), key=lambda j: j.started_at, reverse=True)
    return jobs[:limit]


def job_to_dict(job: JobRecord) -> dict[str, object]:
    return {
        "job_id": job.job_id,
        "model_id": job.model_id,
        "script": job.script_path,
        "demo": job.demo,
        "status": job.status,
        "started_at": job.started_at,
        "exit_code": job.exit_code,
        "error": job.error,
    }
