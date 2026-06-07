"""Shared fal generation runner with DB recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from db.record import GenerationRecorder
from fal_utils import fal_subscribe
from output_utils import make_run_stem, save_fal_result


def run_fal_generation(
    *,
    script_name: str,
    model_id: str,
    arguments: dict[str, Any],
    prompt: str | None,
    output_stem: str,
    default_ext: str = ".bin",
) -> list[Path]:
    with GenerationRecorder(
        script_name=script_name,
        model_id=model_id,
        backend="fal_direct",
        prompt=prompt,
    ) as recorder:
        assert recorder.run_id is not None
        stem = make_run_stem(output_stem, recorder.run_id)
        result = fal_subscribe(model_id, arguments)
        paths = save_fal_result(result, stem, default_ext=default_ext)
        recorder.register_artifacts(paths)
        return paths
