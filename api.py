"""Railway web entrypoint — health checks and generation run history."""

from __future__ import annotations

import json
import os

from fastapi import FastAPI, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import GenerationRun
from db.session import get_session
from env_utils import load_env_file
from scripts_config import GENERATION_SCRIPTS as SCRIPTS

load_env_file()

app = FastAPI(
    title="wan-video",
    version="0.1.0",
    description="fal.ai + Hugging Face inference — image, video, 3D, and voice generation",
)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "wan-video",
        "health": "/health",
        "runs": "/runs",
        "scripts": "/scripts",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> Response:
    missing = [name for name in ("HF_TOKEN", "FAL_KEY") if not os.environ.get(name)]
    if missing:
        body = {"status": "degraded", "missing_env": ",".join(missing)}
        return Response(
            content=json.dumps(body),
            media_type="application/json",
            status_code=503,
        )
    return Response(
        content=json.dumps({"status": "ok"}),
        media_type="application/json",
        status_code=200,
    )


@app.get("/scripts")
def list_scripts() -> dict[str, list[str]]:
    return {"scripts": list(SCRIPTS)}


@app.get("/runs")
def list_runs(limit: int = 20) -> list[dict[str, object]]:
    capped = min(max(limit, 1), 100)
    session = get_session()
    try:
        runs = session.scalars(
            select(GenerationRun)
            .options(selectinload(GenerationRun.artifacts))
            .order_by(GenerationRun.started_at.desc())
            .limit(capped)
        ).all()
        return [
            {
                "id": run.id,
                "script": run.script_name,
                "model": run.model_id,
                "backend": run.backend,
                "provider": run.provider,
                "status": run.status,
                "prompt": run.prompt,
                "started_at": run.started_at.isoformat(),
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "artifacts": [
                    {
                        "path": artifact.file_path,
                        "kind": artifact.file_kind,
                        "size_bytes": artifact.file_size_bytes,
                    }
                    for artifact in run.artifacts
                ],
            }
            for run in runs
        ]
    finally:
        session.close()


@app.get("/runs/{run_id}")
def get_run(run_id: int) -> dict[str, object]:
    session = get_session()
    try:
        run = session.scalars(
            select(GenerationRun)
            .options(selectinload(GenerationRun.artifacts))
            .where(GenerationRun.id == run_id)
        ).first()
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return {
            "id": run.id,
            "script": run.script_name,
            "model": run.model_id,
            "backend": run.backend,
            "provider": run.provider,
            "status": run.status,
            "error": run.error_message,
            "prompt": run.prompt,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "artifacts": [
                {
                    "path": artifact.file_path,
                    "kind": artifact.file_kind,
                    "size_bytes": artifact.file_size_bytes,
                }
                for artifact in run.artifacts
            ],
        }
    finally:
        session.close()


def main() -> None:
    import uvicorn

    load_env_file()
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
