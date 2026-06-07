"""Download and save generation results to the output/ folder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from paths import OUTPUT_DIR, project_relative

MEDIA_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".wav", ".glb", ".obj", ".zip"}
)


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def output_path(stem: str, suffix: str = "") -> Path:
    """Return a path under output/ for a given file stem."""
    ensure_output_dir()
    return OUTPUT_DIR / f"{stem}{suffix}"


def resolve_output_path(path: Path | str) -> Path:
    """Resolve user-supplied output paths under project root when relative."""
    return project_relative(path)


def make_run_stem(base_stem: str, run_id: int) -> str:
    """Unique stem per DB run — avoids overwriting prior output files."""
    return f"{base_stem}-run{run_id}"


def _guess_extension(url: str, default: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in MEDIA_SUFFIXES:
        return suffix
    return default


def _collect_urls(obj: Any, urls: list[str]) -> None:
    if isinstance(obj, dict):
        url = obj.get("url")
        if isinstance(url, str) and url.startswith("http"):
            urls.append(url)
        for value in obj.values():
            _collect_urls(value, urls)
    elif isinstance(obj, list):
        for item in obj:
            _collect_urls(item, urls)


def save_video_result(video: object, dest: Path) -> Path:
    """Persist HF Inference text-to-video result (bytes or object with .save())."""
    ensure_output_dir()
    dest.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(video, "save"):
        video.save(dest)
    elif isinstance(video, bytes):
        dest.write_bytes(video)
    elif isinstance(video, (str, Path)):
        dest.write_bytes(Path(video).read_bytes())
    else:
        raise TypeError(
            f"Unexpected result type {type(video).__name__} — expected bytes or an object with .save()"
        )

    return dest


def _download(url: str, dest: Path) -> Path:
    response = requests.get(url, timeout=600)
    response.raise_for_status()
    dest.write_bytes(response.content)
    return dest


def save_fal_result(result: dict[str, Any], stem: str, *, default_ext: str = ".bin") -> list[Path]:
    """Save fal JSON metadata and download any media URLs found in the response."""
    out_dir = ensure_output_dir()
    saved: list[Path] = []

    json_path = out_dir / f"{stem}.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    saved.append(json_path)

    urls: list[str] = []
    _collect_urls(result, urls)
    seen: set[str] = set()
    unique_urls = [url for url in urls if not (url in seen or seen.add(url))]

    for index, url in enumerate(unique_urls):
        ext = _guess_extension(url, default_ext)
        name_suffix = f"-{index}" if index else ""
        dest = out_dir / f"{stem}{name_suffix}{ext}"
        saved.append(_download(url, dest))

    return saved
