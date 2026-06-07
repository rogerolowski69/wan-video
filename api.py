"""Railway / Docker web entrypoint — health, runs, artifacts, generation jobs, and UI API."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth.deps import auth_required, get_optional_user, require_user, user_for_generation
from auth.routes import router as auth_router
from db.models import GenerationRun, OutputArtifact, User
from db.session import get_session
from env_utils import load_env_file
from job_runner import get_job, job_to_dict, list_jobs, start_model_job, start_run_all
from scripts_config import catalog_payload, get_model
from storage import artifact_public_url, ensure_bucket, fetch_object, is_minio_enabled, read_local_artifact

load_env_file()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_bucket()
    yield


app = FastAPI(
    title="wan-video",
    version="0.4.0",
    description="fal.ai + Hugging Face inference — image, video, 3D, and voice generation",
    lifespan=lifespan,
)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    demo: bool = True
    provider: str | None = Field(default=None, description="HF Inference provider (Wan only)")


class RunAllRequest(BaseModel):
    continue_on_error: bool = True


def _artifact_payload(artifact: OutputArtifact) -> dict[str, Any]:
    return {
        "path": artifact.file_path,
        "kind": artifact.file_kind,
        "size_bytes": artifact.file_size_bytes,
        "url": artifact_public_url(artifact.file_path),
    }


def _run_payload(run: GenerationRun) -> dict[str, Any]:
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
        "artifacts": [_artifact_payload(a) for a in run.artifacts],
    }


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "wan-video",
        "studio": "/catalog",
        "health": "/health",
        "runs": "/runs",
        "gallery": "/gallery",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> Response:
    missing = [name for name in ("HF_TOKEN", "FAL_KEY") if not os.environ.get(name)]
    body: dict[str, Any] = {
        "status": "ok" if not missing else "degraded",
        "storage": "minio" if is_minio_enabled() else "local",
    }
    if missing:
        body["missing_env"] = ",".join(missing)
    status = 200 if not missing else 503
    return Response(content=json.dumps(body), media_type="application/json", status_code=status)


@app.get("/catalog")
@app.get("/scripts")
def list_scripts() -> dict[str, object]:
    return catalog_payload()


@app.post("/generate/{model_id}")
def generate_model(
    model_id: str,
    body: GenerateRequest,
    user: User | None = Depends(user_for_generation),
) -> dict[str, object]:
    if get_model(model_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown model: {model_id}")
    try:
        job = start_model_job(
            model_id,
            demo=body.demo,
            provider=body.provider,
            user_id=user.id if user else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return job_to_dict(job)


@app.post("/generate/run-all")
def generate_run_all(
    body: RunAllRequest,
    user: User | None = Depends(user_for_generation),
) -> dict[str, object]:
    job = start_run_all(continue_on_error=body.continue_on_error, user_id=user.id if user else None)
    return job_to_dict(job)


@app.get("/jobs")
def jobs(limit: int = 20) -> list[dict[str, object]]:
    return [job_to_dict(j) for j in list_jobs(limit)]


@app.get("/jobs/{job_id}")
def job_status(job_id: str) -> dict[str, object]:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job)


@app.get("/runs")
def list_runs(
    limit: int = 50,
    status: str | None = None,
    user: User | None = Depends(get_optional_user),
) -> list[dict[str, Any]]:
    if auth_required() and user is None:
        raise HTTPException(status_code=401, detail="Login required")

    capped = min(max(limit, 1), 200)
    session = get_session()
    try:
        stmt = (
            select(GenerationRun)
            .options(selectinload(GenerationRun.artifacts))
            .order_by(GenerationRun.started_at.desc())
            .limit(capped)
        )
        if user is not None:
            stmt = stmt.where(GenerationRun.user_id == user.id)
        if status:
            stmt = stmt.where(GenerationRun.status == status)
        runs = session.scalars(stmt).all()
        return [_run_payload(run) for run in runs]
    finally:
        session.close()


@app.get("/runs/{run_id}")
def get_run(
    run_id: int,
    user: User | None = Depends(get_optional_user),
) -> dict[str, Any]:
    if auth_required() and user is None:
        raise HTTPException(status_code=401, detail="Login required")

    session = get_session()
    try:
        run = session.scalars(
            select(GenerationRun)
            .options(selectinload(GenerationRun.artifacts))
            .where(GenerationRun.id == run_id)
        ).first()
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        if user is not None and run.user_id is not None and run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Run not found")
        return _run_payload(run)
    finally:
        session.close()


@app.get("/gallery")
def gallery(
    limit: int = 100,
    user: User | None = Depends(get_optional_user),
) -> list[dict[str, Any]]:
    if auth_required() and user is None:
        raise HTTPException(status_code=401, detail="Login required")

    capped = min(max(limit, 1), 500)
    session = get_session()
    try:
        stmt = (
            select(OutputArtifact)
            .join(GenerationRun, OutputArtifact.run_id == GenerationRun.id)
            .where(OutputArtifact.file_kind.in_(("image", "video", "model_3d", "audio")))
            .order_by(OutputArtifact.created_at.desc())
            .limit(capped)
        )
        if user is not None:
            stmt = stmt.where(GenerationRun.user_id == user.id)
        rows = session.scalars(stmt).all()
        return [
            {
                "id": row.id,
                "run_id": row.run_id,
                "path": row.file_path,
                "kind": row.file_kind,
                "size_bytes": row.file_size_bytes,
                "url": artifact_public_url(row.file_path),
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    finally:
        session.close()


@app.get("/files/{file_path:path}")
def get_file(file_path: str) -> Response:
    if is_minio_enabled():
        try:
            body, content_type = fetch_object(file_path)
        except Exception as exc:
            raise HTTPException(status_code=404, detail="File not found") from exc
    else:
        local = read_local_artifact(file_path)
        if local is None:
            raise HTTPException(status_code=404, detail="File not found")
        body, content_type = local

    return Response(content=body, media_type=content_type)


def main() -> None:
    import uvicorn

    load_env_file()
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
