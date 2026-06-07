"""Record generation runs and output artifacts in the database."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from db.models import GenerationRun, OutputArtifact, utcnow
from db.session import get_session
from paths import PROJECT_ROOT

MEDIA_KINDS = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".gif": "image",
    ".mp4": "video",
    ".webm": "video",
    ".wav": "audio",
    ".glb": "model_3d",
    ".obj": "model_3d",
    ".zip": "archive",
    ".json": "json",
}


def classify_file_kind(path: Path) -> str:
    return MEDIA_KINDS.get(path.suffix.lower(), "other")


def relative_project_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


class GenerationRecorder:
    """Context manager that tracks a single generation run."""

    def __init__(
        self,
        *,
        script_name: str,
        model_id: str,
        backend: str,
        prompt: str | None = None,
        provider: str | None = None,
    ) -> None:
        self.script_name = script_name
        self.model_id = model_id
        self.backend = backend
        self.prompt = prompt
        self.provider = provider
        self.run_id: int | None = None
        self._session = get_session()

    def __enter__(self) -> GenerationRecorder:
        run = GenerationRun(
            script_name=self.script_name,
            model_id=self.model_id,
            backend=self.backend,
            provider=self.provider,
            prompt=self.prompt,
            status="running",
        )
        self._session.add(run)
        self._session.commit()
        self._session.refresh(run)
        self.run_id = run.id
        return self

    def __exit__(self, exc_type, exc, _tb) -> None:
        run = self._session.get(GenerationRun, self.run_id)
        if run is None:
            self._session.close()
            return

        run.completed_at = utcnow()
        if exc_type is None:
            run.status = "completed"
        else:
            run.status = "failed"
            run.error_message = str(exc)

        self._session.commit()
        self._session.close()

    def register_artifact(self, path: Path) -> None:
        if self.run_id is None:
            return

        resolved = path.resolve()
        size = resolved.stat().st_size if resolved.is_file() else None
        artifact = OutputArtifact(
            run_id=self.run_id,
            file_path=relative_project_path(path),
            file_kind=classify_file_kind(path),
            file_size_bytes=size,
        )
        self._session.add(artifact)
        self._session.commit()

    def register_artifacts(self, paths: list[Path]) -> None:
        for path in paths:
            self.register_artifact(path)


@contextmanager
def generation_recorder(
    *,
    script_name: str,
    model_id: str,
    backend: str,
    prompt: str | None = None,
    provider: str | None = None,
) -> Iterator[GenerationRecorder]:
    with GenerationRecorder(
        script_name=script_name,
        model_id=model_id,
        backend=backend,
        prompt=prompt,
        provider=provider,
    ) as recorder:
        yield recorder
