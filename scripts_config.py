"""Generation script registry — single source of truth for batch runs and status."""

from __future__ import annotations

SCRIPTS_BY_MODALITY: dict[str, tuple[str, ...]] = {
    "image": (
        "scripts/image/flux.py",
        "scripts/image/nano_banana.py",
        "scripts/image/ideogram_character.py",
    ),
    "video": (
        "scripts/video/seedance.py",
        "scripts/video/wan.py",
    ),
    "voice": (
        "scripts/voice/kling.py",
    ),
    "model_3d": (
        "scripts/model_3d/trellis2.py",
        "scripts/model_3d/hunyuan.py",
    ),
}

GENERATION_SCRIPTS: tuple[str, ...] = tuple(
    script for scripts in SCRIPTS_BY_MODALITY.values() for script in scripts
)

# Pre-scripts/ layout — for --from resume and matching older DB rows
LEGACY_SCRIPT_ALIASES: dict[str, str] = {
    "fal-ai-inference.py": "scripts/image/flux.py",
    "nano-banana.py": "scripts/image/nano_banana.py",
    "ideogram-character.py": "scripts/image/ideogram_character.py",
    "kling-create-voice.py": "scripts/voice/kling.py",
    "trellis2-3d.py": "scripts/model_3d/trellis2.py",
    "hunyuan-3d.py": "scripts/model_3d/hunyuan.py",
    "seeddance-video.py": "scripts/video/seedance.py",
    "wan-inference.py": "scripts/video/wan.py",
}


def resolve_script_name(name: str) -> str:
    """Map legacy flat filenames to scripts/ paths."""
    return LEGACY_SCRIPT_ALIASES.get(name, name)


def script_name_variants(canonical_path: str) -> tuple[str, ...]:
    """All DB script_name values for one script (current path + legacy aliases)."""
    legacy = tuple(old for old, new in LEGACY_SCRIPT_ALIASES.items() if new == canonical_path)
    return (canonical_path, *legacy)
