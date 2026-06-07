"""Generation script registry — single source of truth for batch runs, UI, and CLI menu."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationModel:
    id: str
    path: str
    label: str
    modality: str
    model_id: str
    backend: str
    description: str
    emoji: str
    just_recipe: str


MODEL_CATALOG: tuple[GenerationModel, ...] = (
    GenerationModel(
        id="flux",
        path="scripts/image/flux.py",
        label="FLUX Dev",
        modality="image",
        model_id="fal-ai/flux/dev",
        backend="fal_direct",
        description="High-quality text-to-image via fal.ai FLUX dev.",
        emoji="🖼️",
        just_recipe="flux",
    ),
    GenerationModel(
        id="nano",
        path="scripts/image/nano_banana.py",
        label="Nano Banana 2",
        modality="image",
        model_id="fal-ai/nano-banana-2",
        backend="fal_direct",
        description="Photorealistic and stylized images with strong composition control.",
        emoji="🍌",
        just_recipe="nano",
    ),
    GenerationModel(
        id="ideogram",
        path="scripts/image/ideogram_character.py",
        label="Ideogram Character",
        modality="image",
        model_id="fal-ai/ideogram/character",
        backend="fal_direct",
        description="Place a reference character into a new scene.",
        emoji="👤",
        just_recipe="ideogram",
    ),
    GenerationModel(
        id="seedance",
        path="scripts/video/seedance.py",
        label="Seedance 2.0",
        modality="video",
        model_id="bytedance/seedance-2.0/text-to-video",
        backend="fal_direct",
        description="Text-to-video with smooth motion and cinematic quality.",
        emoji="🎞️",
        just_recipe="seedance",
    ),
    GenerationModel(
        id="wan",
        path="scripts/video/wan.py",
        label="Wan 2.2 T2V",
        modality="video",
        model_id="Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        backend="hf_inference",
        description="Wan 2.2 text-to-video via Hugging Face Inference providers.",
        emoji="🎬",
        just_recipe="wan",
    ),
    GenerationModel(
        id="kling",
        path="scripts/voice/kling.py",
        label="Kling Voice",
        modality="voice",
        model_id="fal-ai/kling-video/create-voice",
        backend="fal_direct",
        description="Create a voice clone from an audio sample URL.",
        emoji="🎙️",
        just_recipe="kling",
    ),
    GenerationModel(
        id="trellis",
        path="scripts/model_3d/trellis2.py",
        label="Trellis 2",
        modality="model_3d",
        model_id="fal-ai/trellis-2",
        backend="fal_direct",
        description="Image-to-3D mesh generation (GLB).",
        emoji="📦",
        just_recipe="trellis",
    ),
    GenerationModel(
        id="hunyuan",
        path="scripts/model_3d/hunyuan.py",
        label="Hunyuan 3D",
        modality="model_3d",
        model_id="fal-ai/hunyuan-3d/v3.1/rapid/image-to-3d",
        backend="fal_direct",
        description="Rapid image-to-3D with Hunyuan 3D.",
        emoji="🧊",
        just_recipe="hunyuan",
    ),
)

MODEL_BY_ID: dict[str, GenerationModel] = {m.id: m for m in MODEL_CATALOG}
MODEL_BY_PATH: dict[str, GenerationModel] = {m.path: m for m in MODEL_CATALOG}

SCRIPTS_BY_MODALITY: dict[str, tuple[str, ...]] = {}
for model in MODEL_CATALOG:
    SCRIPTS_BY_MODALITY.setdefault(model.modality, [])
    SCRIPTS_BY_MODALITY[model.modality].append(model.path)
SCRIPTS_BY_MODALITY = {k: tuple(v) for k, v in SCRIPTS_BY_MODALITY.items()}

GENERATION_SCRIPTS: tuple[str, ...] = tuple(m.path for m in MODEL_CATALOG)

MODALITY_LABELS: dict[str, str] = {
    "image": "Image",
    "video": "Video",
    "voice": "Voice",
    "model_3d": "3D",
}

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


def get_model(model_id: str) -> GenerationModel | None:
    return MODEL_BY_ID.get(model_id)


def resolve_script_name(name: str) -> str:
    if name in MODEL_BY_ID:
        return MODEL_BY_ID[name].path
    return LEGACY_SCRIPT_ALIASES.get(name, name)


def script_name_variants(canonical_path: str) -> tuple[str, ...]:
    legacy = tuple(old for old, new in LEGACY_SCRIPT_ALIASES.items() if new == canonical_path)
    return (canonical_path, *legacy)


def catalog_payload() -> dict[str, object]:
    labels = {m.path: m.label for m in MODEL_CATALOG}
    models = [
        {
            "id": m.id,
            "path": m.path,
            "label": m.label,
            "modality": m.modality,
            "modality_label": MODALITY_LABELS.get(m.modality, m.modality),
            "model_id": m.model_id,
            "backend": m.backend,
            "description": m.description,
            "emoji": m.emoji,
            "just_recipe": m.just_recipe,
        }
        for m in MODEL_CATALOG
    ]
    return {
        "scripts": list(GENERATION_SCRIPTS),
        "by_modality": {k: list(v) for k, v in SCRIPTS_BY_MODALITY.items()},
        "labels": labels,
        "modality_labels": MODALITY_LABELS,
        "models": models,
    }
