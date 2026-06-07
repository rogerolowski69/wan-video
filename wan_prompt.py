"""
Interactive prompt builder and prompt-engineering guides.

Shared by all generation scripts in this project. Press Enter at the first field
to pick a random curated demo prompt optimized for that model.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal


def _pick_random(examples: tuple[str, ...]) -> str:
    """Return a random curated example prompt."""
    return random.choice(examples)


def _join_prompt_parts(parts: list[str]) -> str:
    return ". ".join(part.rstrip(".") for part in parts if part) + "."


WAN_VIDEO_EXAMPLES: tuple[str, ...] = (
    "A red fox trots through fallen leaves in a misty autumn forest at dawn, breath visible "
    "in the cold air. Low tracking shot following from behind, cinematic, smooth motion, "
    "sharp focus, golden hour light filtering through bare branches.",
    "An elderly baker in a flour-dusted apron kneads dough on a wooden counter in a sunlit "
    "kitchen, steam rising from a nearby kettle. Slow dolly in, warm documentary style, "
    "consistent lighting, high detail, gentle handheld sway.",
    "An astronaut in a white EVA suit drifts above Earth, slowly rotating to face the camera, "
    "blue planet curvature and thin atmosphere glow behind. Wide cinematic shot, smooth "
    "zero-gravity motion, crisp focus, high-contrast rim lighting.",
    "Rain streaks down a neon-lit Tokyo alley at night while a woman in a yellow coat walks "
    "away under a clear umbrella, puddles reflecting pink and blue signs. Tracking shot from "
    "behind, cinematic, smooth motion, moody atmosphere, sharp focus.",
    "A tabby cat sits on a windowsill watching goldfish swim in a bowl, tail twitching, "
    "afternoon sun casting soft shadows across the room. Static medium shot, cozy domestic "
    "feel, warm natural light, sharp focus, subtle ambient motion.",
)

FLUX_IMAGE_EXAMPLES: tuple[str, ...] = (
    "Close-up portrait of a cute puppy's face, big expressive brown eyes, wet nose, soft "
    "floppy ears, detailed fluffy fur. Warm studio lighting, Pixar-style 3D animation, "
    "vibrant colors, shallow depth of field, sharp focus, high detail render.",
    "A misty mountain lake at sunrise, pine forests reflected in still water, low fog "
    "drifting across the surface. Wide landscape, cinematic photography, golden hour, "
    "muted teal and amber palette, sharp focus, high detail.",
    "A cyberpunk street market at night, vendors under neon signs, steam rising from food "
    "stalls, light rain on wet pavement. Eye-level street photography, magenta and cyan "
    "accents, cinematic composition, sharp focus.",
    "A still life of oranges and a copper pitcher on a rustic wooden table, morning window "
    "light casting long shadows. Classical oil-painting style, warm palette, soft gradients, "
    "fine texture detail, sharp focus.",
    "Portrait of an elderly craftsman in a workshop, weathered hands holding a carved wooden "
    "tool, warm tungsten light, shallow depth of field. Documentary photo style, high detail, "
    "natural skin texture, sharp focus on hands.",
)

NANO_BANANA_EXAMPLES: tuple[str, ...] = (
    "Action shot of a black Labrador swimming in a sunlit inground suburban pool. Camera at "
    "the waterline, frame split: above water the dog holds a yellow tennis ball; below water "
    "paws paddle through clear turquoise water. Photorealistic, sharp focus, natural daylight.",
    "Macro shot of espresso pouring into a ceramic cup, crema swirling, split focus between "
    "stream and surface ripples. Warm café lighting, photorealistic, high detail, editorial "
    "food photography style.",
    "A hummingbird frozen mid-hover beside a red hibiscus flower, wings blurred slightly, "
    "beak approaching the stamen. Telephoto macro, photorealistic, soft bokeh background, "
    "sharp focus on the bird's eye, natural daylight.",
    "A rainy city street at dusk, reflections of traffic lights on wet asphalt, lone cyclist "
    "crossing the frame. Eye-level photorealistic shot, moody atmosphere, sharp focus, vivid "
    "color reflections.",
    "A chef flambéing vegetables in a pan, orange flame rising, stainless kitchen background "
    "softly blurred. Action frozen at peak flame, photorealistic, warm tungsten light, "
    "magazine culinary photography style.",
)

FLUX_KLEIN_EXAMPLES: tuple[str, ...] = (
    "A cinematic black forest cabin at night, mist rolling through pine trees, moonlight "
    "on snow, ultra detailed, moody atmosphere.",
    "Neon jellyfish drifting in a dark aquarium, bioluminescent blue and purple glow, "
    "macro close-up, sharp focus, vivid colors.",
    "A vintage red bicycle leaning against a weathered brick wall, afternoon sun, shallow "
    "depth of field, warm tones, sharp detail.",
    "Steam rising from a handmade ceramic tea cup on a wooden table, soft window light, "
    "macro composition, cozy atmosphere, high detail.",
    "Aurora borealis over a frozen lake, stars visible, wide landscape, crisp reflections "
    "on ice, cinematic, vibrant green and violet sky.",
)

SEEDANCE_VIDEO_EXAMPLES: tuple[str, ...] = (
    "An octopus finds a football in the ocean and excitedly calls its octopus friends to "
    "come and play. Cut scene to an octopus football game under the sea, bubbles rising, "
    "sun rays filtering through water, playful energy, cinematic, smooth motion.",
    "A paper airplane launched from a rooftop sails through a sunlit city canyon, weaving "
    "between buildings, gliding over traffic. Dynamic tracking shot, warm golden hour light, "
    "smooth motion, sharp focus, whimsical mood.",
    "Time-lapse of a rose blooming in a garden from tight bud to full flower, dew on petals, "
    "bees arriving. Static close-up, natural daylight shifting soft to warm, smooth temporal "
    "flow, macro detail, vivid colors.",
    "A chef transforms flour into fresh pasta: kneading dough, rolling sheets, cutting "
    "tagliatelle, plating with sauce and basil. Kitchen documentary style, warm lighting, "
    "smooth motion between steps, high detail.",
    "A surfer rides a giant turquoise wave at sunset, carving along the face, spray catching "
    "golden light. Low-angle water-level tracking shot, cinematic, smooth motion, dramatic "
    "atmosphere, sharp focus.",
)

IDEOGRAM_CHARACTER_EXAMPLES: tuple[str, ...] = (
    "Place the character as a stealthy ninja superhero on a rain-slicked Tokyo rooftop at "
    "night, crouched in a dynamic ready stance, black tactical suit, flowing cape, mask, "
    "katana at the hip. Neon skyline through fog, wet tiles reflecting magenta and cyan, "
    "low-angle hero shot, dramatic rim lighting, sharp focus, high detail.",
    "Place the character as an astronaut standing on a red Mars ridge at sunset, reflective "
    "visor catching orange light, dust settling around boots, Earth small in the sky. Wide "
    "cinematic composition, epic scale, sharp focus, moody atmosphere, high detail.",
    "Place the character as a medieval knight in torchlit castle hall, polished armor "
    "catching firelight, cape over one shoulder, hand resting on sword hilt. Three-quarter "
    "portrait, dramatic chiaroscuro, cinematic, sharp focus, rich textures.",
    "Place the character as a 1920s jazz singer on a smoky stage, sequined dress, microphone "
    "in hand, mid-performance gesture, spotlight from above. Art-deco theater background, "
    "warm golden light, cinematic composition, sharp focus, high detail.",
    "Place the character as a deep-sea diver exploring a coral-covered shipwreck, bubbles "
    "rising, flashlight beam cutting through blue water, fish schooling nearby. Wide "
    "underwater shot, cinematic, sharp focus, vivid marine colors.",
)

TRELLIS2_SOURCE_EXAMPLES: tuple[str, ...] = (
    "A red vintage alarm clock with twin bells, centered on pure white background, 3/4 angle, "
    "studio product photography, soft even lighting, sharp focus, clean silhouette.",
    "A matte green ceramic vase with narrow neck, centered on neutral gray background, "
    "isometric 3/4 view, studio lighting, single object, sharp focus, no clutter.",
    "A leather hiking boot with orange laces, 3/4 side angle on white background, product "
    "photo, even lighting, sharp focus, clean silhouette, high detail.",
    "A wooden toy rocket ship with red fins, centered on soft gradient background, slight "
    "3/4 view, studio shot, sharp focus, single isolated object.",
    "A brass desk lamp with green glass shade, 3/4 angle on plain white, product photography, "
    "soft shadows, sharp focus, single object, high detail.",
)

HUNYUAN3D_SOURCE_EXAMPLES: tuple[str, ...] = (
    "A rustic wooden treasure chest with metal bands and ornate lock, centered on neutral "
    "gray background, 3/4 view, studio product lighting, sharp focus, clean silhouette.",
    "A glossy red apple with stem and leaf, centered on white background, slight 3/4 angle, "
    "soft studio light, single object, sharp focus, high detail.",
    "A classic arcade joystick with red ball top, centered on gray background, 3/4 view, "
    "even lighting, sharp focus, clean silhouette, no clutter.",
    "A stacked set of three hardcover books tied with twine, 3/4 angle on white background, "
    "studio lighting, single object group, sharp focus, high detail.",
    "A chrome teapot with curved spout, centered on soft gradient background, 3/4 view, "
    "product photo, sharp focus, clean silhouette, even lighting.",
)

KLING_VOICE_URL_EXAMPLES: tuple[str, ...] = (
    "https://v3b.fal.media/files/b/0a867736/_Wo19V-XrOVYZt6jKE8t5_kling_video.wav",
)

DEFAULT_KLING_VOICE_URL = KLING_VOICE_URL_EXAMPLES[0]


@dataclass(frozen=True)
class ImageTo3DInput:
    """Input bundle for fal.ai image-to-3D models."""

    image_url: str
    image_prompt: str


DEFAULT_TRELLIS2_IMAGE_URL = (
    "https://v3b.fal.media/files/b/0a86b60d/xkpao5B0uxmH0tmJm0HVL_2fe35ce1-fe44-475b-b582-6846a149537c.png"
)

DEFAULT_HUNYUAN3D_IMAGE_URL = (
    "https://v3b.fal.media/files/b/0a865ab1/omYcawLUo4RZbO8J6ZgZR.png"
)

DEFAULT_IDEOGRAM_REFERENCE_URL = (
    "https://v3b.fal.media/files/kangaroo/0rinwnj_Kn9Fsu2dK-aKm_image.png"
)


@dataclass(frozen=True)
class ImagePrompt:
    """Structured prompt for fal.ai text-to-image models (e.g. FLUX)."""

    prompt: str


@dataclass(frozen=True)
class CharacterPrompt:
    """Prompt bundle for fal.ai Ideogram Character (scene + reference identity)."""

    prompt: str
    reference_image_urls: list[str]


@dataclass(frozen=True)
class VoiceInput:
    """Input bundle for fal.ai Kling voice creation."""

    voice_url: str


@dataclass(frozen=True)
class VideoPrompt:
    """Structured prompt bundle for Wan T2V generation."""

    prompt: str
    negative_prompt: str


# Wan models respond well to this default negative prompt (from official examples).
DEFAULT_NEGATIVE_PROMPT = (
    "Bright tones, overexposed, static, blurred details, subtitles, style, works, "
    "paintings, images, static, overall gray, worst quality, low quality, "
    "JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, "
    "poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, "
    "still picture, messy background, three legs, many people in the background, "
    "walking backwards"
)


def print_diffusers_guide() -> None:
    """Educational overview for local Diffusers pipelines."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR LOCAL DIFFUSERS (Wan T2V)
================================================================================

Video diffusion models read your prompt as a sequence of visual concepts. Unlike
LLM chat, there is no dialog — every word nudges pixels across many frames.

STRUCTURED PROMPT ANATOMY (recommended order)
  1. Subject    — who or what is on screen (a red fox, an astronaut, a ceramic mug)
  2. Action     — what happens over time (walks, pours tea, turns to camera)
  3. Scene      — where it happens (rainy Tokyo alley, sunlit kitchen, Mars crater)
  4. Camera     — how we see it (slow dolly in, handheld tracking, aerial wide)
  5. Style      — look and medium (cinematic, documentary, 35mm film, anime)
  6. Lighting   — mood via light (golden hour, neon reflections, soft overcast)
  7. Details    — textures, color palette, atmosphere (muted teal palette, steam)

TECHNIQUES THAT WORK WELL
  • Be specific, not vague — "elderly baker in flour-dusted apron" beats "person".
  • Use motion verbs — video models need temporal cues: walking, stirring, drifting.
  • One clear idea per clip — avoid cramming unrelated scenes into one prompt.
  • Comma-separated descriptors — models treat these as parallel attributes.
  • Match camera words to motion — "static tripod" vs "smooth gimbal follow".
  • Avoid contradictions — "bright sunny night" confuses both CLIP/T5 encoders.

NEGATIVE PROMPTS (Diffusers-only superpower)
  Local pipelines accept a negative_prompt that steers away from artifacts: blur,
  static frames, deformities, subtitles, watermark-like text. Wan ships with a
  strong default negative prompt — use it unless you have a reason to trim it.

PARAMETERS YOU CONTROL LOCALLY
  height, width, num_frames, guidance_scale, num_inference_steps, seed.
  Prompt quality still matters most; parameters fine-tune fidelity and motion.

DIFFUSERS vs REMOTE INFERENCE
  Diffusers gives full control (negative prompt, frame count, scheduler tweaks) at
  the cost of GPU memory and setup. Remote providers trade control for speed and
  zero local hardware — see the inference script guide for that path.

Press Enter at Subject for a random curated demo prompt.
"""
    )


def print_inference_guide() -> None:
    """Educational overview for Hugging Face Inference API / fal-ai providers."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR INFERENCE PROVIDERS (HF InferenceClient + fal-ai)
================================================================================

Remote text-to-video sends a single prompt string to a hosted Wan endpoint. The
provider runs the model for you — no local GPU, but fewer knobs than Diffusers.

WHAT TO OPTIMIZE IN YOUR PROMPT STRING
  Because you typically cannot pass negative_prompt or low-level scheduler args,
  front-load quality cues directly in the positive prompt:

  • Lead with the main subject and action in the first sentence.
  • Add camera and lighting in the same paragraph — providers do not "remember"
    context across calls; everything must live in one self-contained description.
  • Include quality anchors inline: "cinematic", "sharp focus", "smooth motion",
    "consistent lighting" — do not rely on a separate negative prompt.
  • Keep it readable prose OR dense comma-separated tags; both work if consistent.

STRUCTURED PROMPT ANATOMY (same as local — still applies)
  Subject → Action → Scene → Camera → Style → Lighting → Details

PROVIDER-SPECIFIC TIPS
  • One request = one clip — write the full scene each time.
  • Shorter prompts can drift; very long prompts may dilute focus. Aim for 1–3
    rich sentences or ~40–120 tokens of concrete visual detail.
  • Avoid requesting on-screen text, logos, or subtitles — hosted models struggle
    with legible typography and may burn steps on garbage tokens.
  • Latency and cost scale with resolution/length — precise prompts reduce retries.

WHEN TO USE INFERENCE vs DIFFUSERS
  Use Inference when you want fast iteration without a GPU. Use Diffusers when you
  need negative prompts, exact frame counts, reproducible seeds, or fine control.

Press Enter at Subject for a random curated demo prompt.
"""
    )


def print_fal_image_guide() -> None:
    """Educational overview for fal.ai direct text-to-image (FLUX)."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR FAL.AI TEXT-TO-IMAGE (FLUX)
================================================================================

FLUX reads one self-contained prompt per image. There is no negative prompt on
most fal endpoints — bake quality and exclusions into the positive description.

STRUCTURED PROMPT ANATOMY (recommended order)
  1. Subject     — who or what (a ceramic teapot, a mountain biker, a tabby cat)
  2. Pose/mood   — expression, posture, gesture (leaning forward, laughing, serene)
  3. Scene       — environment (misty forest trail, minimalist studio, rainy street)
  4. Framing     — shot type (close-up portrait, wide establishing, bird's-eye)
  5. Style       — medium or look (oil painting, Pixar 3D, editorial photo, anime)
  6. Lighting    — light quality (golden hour, soft window light, neon rim light)
  7. Details     — texture, palette, quality cues (sharp focus, 8k, muted pastels)

TECHNIQUES THAT WORK WELL
  • Lead with the subject — the first phrase anchors composition.
  • One scene, one moment — still images work best with a single clear idea.
  • Quality anchors inline — "sharp focus", "high detail", "cinematic composition".
  • Style references beat vague words — "Pixar-style 3D" beats "cartoon".
  • Avoid on-image text — FLUX struggles with legible typography and logos.
  • Comma clauses and short sentences both work; stay consistent within a prompt.

FAL DIRECT vs HF INFERENCE
  fal_client talks straight to fal queue API using FAL_KEY. You pick the exact
  endpoint (e.g. fal-ai/flux/dev) and pass a prompt dict — fast to iterate, no
  local GPU. Press Enter at Subject for a random curated demo prompt.
"""
    )


def print_flux_klein_guide() -> None:
    """Educational overview for FLUX.2 Klein local/fast generation."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR FLUX.2 KLEIN (black-forest-labs)
================================================================================

Klein is a distilled 9B model optimized for speed (4 steps, guidance_scale=1.0).
Prompts should be concise but vivid — every word counts at low step counts.

STRUCTURED PROMPT ANATOMY
  1. Subject    — the main focus (cabin, jellyfish, bicycle)
  2. Scene/mood — atmosphere (misty night, cozy, epic)
  3. Lighting   — moonlight, neon glow, window light
  4. Style cues — cinematic, macro, ultra detailed
  5. Composition — wide landscape, close-up, shallow depth of field

TECHNIQUES THAT WORK WELL
  • Keep prompts to 1-2 sentences — Klein responds fast, not verbose.
  • Strong nouns and adjectives beat long prose chains.
  • Avoid on-image text — Klein struggles with legible typography.
  • At guidance_scale=1.0, quality words in the prompt do the heavy lifting.

Press Enter at Subject for a random curated demo prompt.
"""
    )


def print_seedance_guide() -> None:
    """Educational overview for Seedance 2.0 text-to-video."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR SEEDANCE 2.0 (text-to-video)
================================================================================

Seedance generates video from a single text prompt. It supports multi-beat scenes
with phrases like "Cut scene to..." for sequence changes within one generation.

STRUCTURED PROMPT ANATOMY
  1. Subject(s)   — who or what (octopus, chef, surfer)
  2. Action arc   — what happens, can span multiple beats
  3. Scene        — ocean, kitchen, wave, city
  4. Transitions  — "Cut scene to..." for scene changes
  5. Camera       — tracking shot, time-lapse, low angle
  6. Style/mood   — cinematic, playful, documentary
  7. Quality cues — smooth motion, sharp focus, natural light

TECHNIQUES THAT WORK WELL
  • One paragraph with clear temporal flow — beginning, middle, optional cut.
  • Motion verbs throughout — swimming, carving, blooming, gliding.
  • Keep each beat visually concrete — avoid abstract concepts.
  • Quality anchors inline — cinematic, smooth motion, high detail.

Press Enter at Subject for a random curated demo prompt.
"""
    )


def print_kling_voice_guide() -> None:
    """Educational overview for Kling voice creation."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR KLING CREATE VOICE (audio input)
================================================================================

Kling Create Voice clones a voice from an audio sample URL — not from text.
Your "prompt" is choosing a high-quality reference recording.

WHAT MAKES A GOOD VOICE SAMPLE
  1. Clear speech     — minimal background noise, no music overlay
  2. Consistent mic   — one speaker, steady volume, no clipping
  3. Natural pacing   — conversational speed, full sentences
  4. Clean format     — WAV/MP3 URL accessible to fal servers
  5. Sufficient length — enough audio for the model to capture timbre

WORKFLOW
  • Paste your own voice sample URL, or press Enter to use the default below.

DEFAULT VOICE URL (fal-hosted sample, clear speech):
  https://v3b.fal.media/files/b/0a867736/_Wo19V-XrOVYZt6jKE8t5_kling_video.wav
"""
    )


def print_nano_banana_guide() -> None:
    """Educational overview for fal.ai Nano Banana 2 text-to-image."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR NANO BANANA 2 (fal.ai)
================================================================================

Nano Banana 2 excels at photorealistic images and precise spatial composition —
including tricky shots like split-level above/below water or through-glass views.

STRUCTURED PROMPT ANATOMY (recommended order)
  1. Subject     — who or what (black Labrador, vintage motorcycle, barista)
  2. Pose/mood   — action or expression (swimming, mid-pour, laughing)
  3. Scene       — environment (suburban pool, rainy street, cafe interior)
  4. Framing     — camera placement (waterline split, over-shoulder, macro)
  5. Style       — look (photorealistic, editorial, cinematic still)
  6. Lighting    — light quality (natural daylight, golden hour, soft overcast)
  7. Details     — clarity cues (sharp focus, high detail, vivid colors)

TECHNIQUES THAT WORK WELL
  • Describe spatial relationships explicitly — "above water / below water",
    "foreground / background", "left half / right half".
  • One frozen moment — action shots work; describe the peak instant, not a story arc.
  • Photorealism anchors — "photorealistic", "natural daylight", "sharp focus".
  • Specific camera placement — "camera at waterline", "eye-level", "low angle".
  • Avoid on-image text and logos — models struggle with readable typography.

Press Enter at Subject for a random curated demo prompt (split-level pool shot).
"""
    )


def print_trellis2_guide() -> None:
    """Educational overview for Trellis 2 image-to-3D on fal.ai."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR TRELLIS 2 (IMAGE → 3D)
================================================================================

Trellis 2 does not take a text prompt directly — it converts a 2D image URL into
a 3D model. "Prompt engineering" here means crafting or choosing the SOURCE IMAGE.

WHAT MAKES A GOOD SOURCE IMAGE
  1. Single object     — one subject, centered, not a full scene or crowd
  2. Clear silhouette  — full object visible, minimal overlap or occlusion
  3. Plain background  — white, gray, or simple gradient; avoid busy environments
  4. 3/4 or isometric  — show depth; flat front-only views lose geometry cues
  5. Even lighting     — soft studio light; harsh shadows hide surface detail
  6. Sharp focus       — blur and noise confuse structure reconstruction

WORKFLOW
  • Describe your object below — we build a 2D image prompt you can generate with
    fal-ai-inference.py or nano-banana.py, then paste the resulting image URL here.
  • Or press Enter at Object for a random demo image prompt + demo URL.

Press Enter at Object for a random curated demo.
"""
    )


def print_hunyuan3d_guide() -> None:
    """Educational overview for Hunyuan 3D Rapid image-to-3D on fal.ai."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR HUNYUAN 3D RAPID (IMAGE → 3D)
================================================================================

Hunyuan 3D Rapid converts a 2D image URL into a 3D asset. Like Trellis, the key is
choosing or generating a strong SOURCE IMAGE — not writing a video-style scene prompt.

WHAT MAKES A GOOD SOURCE IMAGE
  1. Single object     — one subject fills most of the frame (>50% recommended)
  2. Simple background — plain white, gray, or soft gradient
  3. Clear front or 3/4 view — enough depth cues for geometry reconstruction
  4. Even lighting     — avoid harsh shadows that hide surface detail
  5. Sharp focus       — blur and noise reduce mesh and texture quality
  6. No text/logos     — typography does not reconstruct well in 3D

WORKFLOW
  • Describe your object — we build a 2D image prompt for fal-ai-inference.py or
    nano-banana.py, then paste the resulting image URL here.
  • Or press Enter at Object for a random demo image prompt + demo URL.

Note: Hunyuan also offers text-to-3d on fal; this script uses the image-to-3d path.

Press Enter at Object for a random curated demo.
"""
    )


def _ask(label: str, hint: str = "", required: bool = False) -> str:
    """Prompt the user for one field."""
    suffix = f" [{hint}]" if hint else ""
    while True:
        value = input(f"  {label}{suffix}: ").strip()
        if value or not required:
            return value
        print("    (This field is required — please enter a value.)")


def build_structured_prompt(
    *,
    include_negative: bool = True,
    demo_examples: tuple[str, ...] = WAN_VIDEO_EXAMPLES,
) -> VideoPrompt:
    """
    Interactively collect scene elements and assemble a Wan-friendly prompt.

    Uses a structured interview so beginners learn prompt anatomy while building.
    """
    print("\n--- Build your scene (Enter at Subject for random demo) ---\n")

    subject = _ask("Subject", "who or what — Enter alone for random demo")
    if not subject:
        prompt = _pick_random(demo_examples)
        print("\n--- Random demo prompt ---")
        print(f"  {prompt}\n")
        negative_prompt = ""
        if include_negative:
            use_default_negative = input(
                "Use Wan default negative prompt? [Y/n]: "
            ).strip().lower()
            negative_prompt = (
                DEFAULT_NEGATIVE_PROMPT
                if use_default_negative in ("", "y", "yes")
                else input("  Enter custom negative prompt (or Enter for default): ").strip()
                or DEFAULT_NEGATIVE_PROMPT
            )
        return VideoPrompt(prompt=prompt, negative_prompt=negative_prompt)

    action = _ask("Action", "what happens over time — use motion verbs")
    scene = _ask("Scene / environment", "where it takes place")
    camera = _ask("Camera / motion", "e.g. slow dolly in, tracking shot, wide aerial")
    style = _ask("Visual style", "e.g. cinematic, documentary, 35mm film")
    lighting = _ask("Lighting / mood", "e.g. golden hour, neon, soft overcast")
    details = _ask("Extra details", "textures, palette, atmosphere")

    parts: list[str] = []

    if action:
        parts.append(f"{subject} {action}".strip())
    else:
        parts.append(subject)

    if scene:
        parts.append(scene)

    if camera:
        parts.append(camera)

    if style:
        parts.append(style)

    if lighting:
        parts.append(lighting)

    if details:
        parts.append(details)

    prompt = _join_prompt_parts(parts)

    print("\n--- Assembled prompt ---")
    print(f"  {prompt}\n")

    negative_prompt = ""
    if include_negative:
        use_default_negative = input(
            "Use Wan default negative prompt? [Y/n]: "
        ).strip().lower()

        if use_default_negative in ("", "y", "yes"):
            negative_prompt = DEFAULT_NEGATIVE_PROMPT
        else:
            custom = input("  Enter custom negative prompt (or Enter for none): ").strip()
            negative_prompt = custom or DEFAULT_NEGATIVE_PROMPT

    return VideoPrompt(prompt=prompt, negative_prompt=negative_prompt)


def build_structured_video_prompt(
    *,
    demo_examples: tuple[str, ...],
    label: str = "video",
) -> ImagePrompt:
    """Generic structured builder for text-to-video models (Seedance, etc.)."""
    print(f"\n--- Build your {label} (Enter at Subject for random demo) ---\n")

    subject = _ask("Subject", "who or what — Enter alone for random demo")
    if not subject:
        prompt = _pick_random(demo_examples)
        print("\n--- Random demo prompt ---")
        print(f"  {prompt}\n")
        return ImagePrompt(prompt=prompt)

    action = _ask("Action / story", "what happens — motion verbs, optional cut scenes")
    scene = _ask("Scene / environment", "where it takes place")
    camera = _ask("Camera / motion", "tracking shot, time-lapse, aerial, etc.")
    style = _ask("Visual style", "cinematic, documentary, playful")
    lighting = _ask("Lighting / mood", "golden hour, neon, soft overcast")
    details = _ask("Extra details", "textures, palette, quality cues")

    parts: list[str] = []
    if action:
        parts.append(f"{subject} {action}".strip())
    else:
        parts.append(subject)
    for field in (scene, camera, style, lighting, details):
        if field:
            parts.append(field)

    prompt = _join_prompt_parts(parts)
    print("\n--- Assembled prompt ---")
    print(f"  {prompt}\n")
    return ImagePrompt(prompt=prompt)


def collect_video_prompt(backend: Literal["diffusers", "inference"]) -> VideoPrompt:
    """Print backend-specific education, then run the interactive builder."""
    if backend == "diffusers":
        print_diffusers_guide()
    else:
        print_inference_guide()

    return build_structured_prompt(include_negative=(backend == "diffusers"))


def build_structured_image_prompt(
    *,
    demo_examples: tuple[str, ...] = FLUX_IMAGE_EXAMPLES,
) -> ImagePrompt:
    """Interactively collect still-image elements and assemble a generation prompt."""
    print("\n--- Build your image (Enter at Subject for random demo) ---\n")

    subject = _ask("Subject", "who or what — Enter alone for random demo")
    if not subject:
        prompt = _pick_random(demo_examples)
        print("\n--- Random demo prompt ---")
        print(f"  {prompt}\n")
        return ImagePrompt(prompt=prompt)

    pose = _ask("Pose / mood", "expression, posture, gesture")
    scene = _ask("Scene / environment", "where it takes place")
    framing = _ask("Framing", "e.g. close-up portrait, wide shot, bird's-eye")
    style = _ask("Visual style", "e.g. Pixar 3D, oil painting, editorial photo")
    lighting = _ask("Lighting / mood", "e.g. golden hour, soft window light, neon")
    details = _ask("Extra details", "textures, palette, quality cues")

    parts: list[str] = []

    if pose:
        parts.append(f"{subject}, {pose}".strip(", "))
    else:
        parts.append(subject)

    if scene:
        parts.append(scene)

    if framing:
        parts.append(framing)

    if style:
        parts.append(style)

    if lighting:
        parts.append(lighting)

    if details:
        parts.append(details)

    prompt = _join_prompt_parts(parts)

    print("\n--- Assembled prompt ---")
    print(f"  {prompt}\n")

    return ImagePrompt(prompt=prompt)


def collect_fal_image_prompt() -> ImagePrompt:
    """Print fal image guide, then run the interactive builder."""
    print_fal_image_guide()
    return build_structured_image_prompt(demo_examples=FLUX_IMAGE_EXAMPLES)


def collect_nano_banana_prompt() -> ImagePrompt:
    """Print Nano Banana guide, then run the interactive builder."""
    print_nano_banana_guide()
    return build_structured_image_prompt(demo_examples=NANO_BANANA_EXAMPLES)


def collect_flux_klein_prompt() -> ImagePrompt:
    """Print FLUX Klein guide, then run the interactive builder."""
    print_flux_klein_guide()
    return build_structured_image_prompt(demo_examples=FLUX_KLEIN_EXAMPLES)


def collect_seedance_prompt() -> ImagePrompt:
    """Print Seedance guide, then run the interactive builder."""
    print_seedance_guide()
    return build_structured_video_prompt(
        demo_examples=SEEDANCE_VIDEO_EXAMPLES,
        label="Seedance video",
    )


def build_image_to_3d_input(
    *,
    default_image_url: str,
    demo_examples: tuple[str, ...],
    model_label: str = "3D",
) -> ImageTo3DInput:
    """Interactively collect object description and image URL for image-to-3D APIs."""
    print(f"\n--- Build your {model_label} source (Enter at Object for random demo) ---\n")

    obj = _ask("Object", "what to convert to 3D — Enter alone for random demo")
    if not obj:
        image_prompt = _pick_random(demo_examples)
        print(f"\n--- Random demo image prompt ({model_label}) ---")
        print(f"  {image_prompt}\n")
        print("--- Demo image URL ---")
        print(f"  {default_image_url}\n")
        return ImageTo3DInput(image_url=default_image_url, image_prompt=image_prompt)

    angle = _ask("View / angle", "e.g. 3/4 view, isometric, slight side angle")
    background = _ask("Background", "e.g. pure white, neutral gray, simple gradient")
    lighting = _ask("Lighting", "e.g. soft studio, even product lighting")
    details = _ask("Extra details", "materials, colors, style cues")

    parts: list[str] = [obj]

    if angle:
        parts.append(angle)

    if background:
        parts.append(f"on {background}" if not background.startswith("on ") else background)

    parts.append("single isolated object, centered, clean silhouette, sharp focus")

    if lighting:
        parts.append(lighting)

    if details:
        parts.append(details)

    image_prompt = _join_prompt_parts(parts)

    print("\n--- Suggested 2D image prompt ---")
    print(f"  {image_prompt}")
    print("\n  Generate this with fal-ai-inference.py or nano-banana.py, then paste the URL.\n")

    image_url = _ask("Image URL", "https://... or Enter to use demo URL")
    if not image_url:
        image_url = default_image_url
        print(f"  Using demo URL: {image_url}\n")

    return ImageTo3DInput(image_url=image_url, image_prompt=image_prompt)


def build_trellis2_input() -> ImageTo3DInput:
    """Interactively collect object description and image URL for Trellis 2."""
    return build_image_to_3d_input(
        default_image_url=DEFAULT_TRELLIS2_IMAGE_URL,
        demo_examples=TRELLIS2_SOURCE_EXAMPLES,
        model_label="Trellis 2",
    )


def collect_trellis2_input() -> ImageTo3DInput:
    """Print Trellis 2 guide, then run the interactive builder."""
    print_trellis2_guide()
    return build_trellis2_input()


def collect_hunyuan3d_input() -> ImageTo3DInput:
    """Print Hunyuan 3D guide, then run the interactive builder."""
    print_hunyuan3d_guide()
    return build_image_to_3d_input(
        default_image_url=DEFAULT_HUNYUAN3D_IMAGE_URL,
        demo_examples=HUNYUAN3D_SOURCE_EXAMPLES,
        model_label="Hunyuan 3D",
    )


def print_ideogram_character_guide() -> None:
    """Educational overview for Ideogram Character on fal.ai."""
    print(
        """
================================================================================
 PROMPT ENGINEERING FOR IDEOGRAM CHARACTER (fal.ai)
================================================================================

Ideogram Character keeps a person's likeness from reference_image_urls while placing
them into a NEW scene described by your text prompt. You control two inputs:

  • Reference image URL — locks face, body type, and identity
  • Scene prompt — describes where they are, what they wear, and how the shot looks

STRUCTURED PROMPT ANATOMY (recommended order)
  1. Placement     — "Place the character as..." or "Place the character in..."
  2. Role / look   — costume, persona (ninja superhero, astronaut, chef)
  3. Action / pose — crouched, walking, mid-leap, holding an object
  4. Scene         — rooftop, café, forest, studio
  5. Environment   — weather, time of day, background details
  6. Composition   — angle, framing, off-center, close-up
  7. Lighting/mood — rim light, golden hour, neon, cinematic

TECHNIQUES THAT WORK WELL
  • Start with "Place the character" — matches Ideogram's expected phrasing.
  • Describe the SCENE richly — the reference image handles identity.
  • Costume changes work — "dressed as a ninja superhero" transforms outfit while
    preserving likeness from the reference photo.
  • Write one continuous paragraph — Ideogram responds well to prose with detail.
  • Avoid requesting readable text in the image — logos and captions fail often.

Press Enter at Role / look for a random curated demo prompt.
"""
    )


def build_ideogram_character_prompt(
    *,
    demo_examples: tuple[str, ...] = IDEOGRAM_CHARACTER_EXAMPLES,
    default_reference_url: str = DEFAULT_IDEOGRAM_REFERENCE_URL,
) -> CharacterPrompt:
    """Interactively collect scene description and reference URL for Ideogram Character."""
    print("\n--- Build your character scene (Enter at Role for random demo) ---\n")

    role = _ask("Role / look", "e.g. ninja superhero — Enter alone for random demo")
    if not role:
        prompt = _pick_random(demo_examples)
        print("\n--- Random demo scene prompt ---")
        print(f"  {prompt}\n")
        print("--- Demo reference image URL ---")
        print(f"  {default_reference_url}\n")
        return CharacterPrompt(
            prompt=prompt,
            reference_image_urls=[default_reference_url],
        )

    action = _ask("Action / pose", "e.g. crouched ready stance, mid-leap, walking")
    scene = _ask("Scene / setting", "where they are — rooftop, café, forest")
    environment = _ask("Environment details", "weather, background, time of day")
    composition = _ask("Composition", "e.g. low-angle hero shot, off-center, wide")
    lighting = _ask("Lighting / mood", "e.g. neon rim light, golden hour, moody fog")
    details = _ask("Extra details", "textures, colors, style cues")

    parts: list[str] = [f"Place the character as {role}"]

    if action:
        parts.append(action)

    if scene:
        parts.append(f"in {scene}" if not scene.startswith("in ") else scene)

    if environment:
        parts.append(environment)

    if composition:
        parts.append(composition)

    if lighting:
        parts.append(lighting)

    if details:
        parts.append(details)

    prompt = _join_prompt_parts(parts)

    print("\n--- Assembled scene prompt ---")
    print(f"  {prompt}\n")

    reference_url = _ask("Reference image URL", "identity photo — Enter for demo URL")
    if not reference_url:
        reference_url = default_reference_url
        print(f"  Using demo reference: {reference_url}\n")

    return CharacterPrompt(prompt=prompt, reference_image_urls=[reference_url])


def collect_ideogram_character_prompt() -> CharacterPrompt:
    """Print Ideogram Character guide, then run the interactive builder."""
    print_ideogram_character_guide()
    return build_ideogram_character_prompt()


def build_kling_voice_input(
    *,
    default_voice_url: str = DEFAULT_KLING_VOICE_URL,
) -> VoiceInput:
    """Interactively collect voice sample URL for Kling Create Voice."""
    print("\n--- Voice sample URL ---")
    print(f"  Default: {default_voice_url}\n")

    voice_url = _ask("Voice URL", "paste URL or Enter for default")
    if not voice_url:
        voice_url = default_voice_url
        print(f"\n  Using default: {voice_url}\n")

    return VoiceInput(voice_url=voice_url)


def collect_kling_voice_input() -> VoiceInput:
    """Print Kling voice guide, then run the interactive builder."""
    print_kling_voice_guide()
    return build_kling_voice_input()


def demo_video_prompt() -> VideoPrompt:
    """Non-interactive random Wan video prompt for batch runs."""
    prompt = _pick_random(WAN_VIDEO_EXAMPLES)
    print(f"Demo prompt: {prompt}\n")
    return VideoPrompt(prompt=prompt, negative_prompt="")


def demo_image_prompt(examples: tuple[str, ...] = FLUX_IMAGE_EXAMPLES) -> ImagePrompt:
    """Non-interactive random image prompt for batch runs."""
    prompt = _pick_random(examples)
    print(f"Demo prompt: {prompt}\n")
    return ImagePrompt(prompt=prompt)


def demo_seedance_prompt() -> ImagePrompt:
    return demo_image_prompt(SEEDANCE_VIDEO_EXAMPLES)


def demo_ideogram_character_prompt() -> CharacterPrompt:
    prompt = _pick_random(IDEOGRAM_CHARACTER_EXAMPLES)
    print(f"Demo prompt: {prompt}\n")
    print(f"Demo reference: {DEFAULT_IDEOGRAM_REFERENCE_URL}\n")
    return CharacterPrompt(prompt=prompt, reference_image_urls=[DEFAULT_IDEOGRAM_REFERENCE_URL])


def demo_trellis2_input() -> ImageTo3DInput:
    image_prompt = _pick_random(TRELLIS2_SOURCE_EXAMPLES)
    print(f"Demo image prompt: {image_prompt}\n")
    print(f"Demo image URL: {DEFAULT_TRELLIS2_IMAGE_URL}\n")
    return ImageTo3DInput(image_url=DEFAULT_TRELLIS2_IMAGE_URL, image_prompt=image_prompt)


def demo_hunyuan3d_input() -> ImageTo3DInput:
    image_prompt = _pick_random(HUNYUAN3D_SOURCE_EXAMPLES)
    print(f"Demo image prompt: {image_prompt}\n")
    print(f"Demo image URL: {DEFAULT_HUNYUAN3D_IMAGE_URL}\n")
    return ImageTo3DInput(image_url=DEFAULT_HUNYUAN3D_IMAGE_URL, image_prompt=image_prompt)


def demo_kling_voice_input() -> VoiceInput:
    print(f"Demo voice URL: {DEFAULT_KLING_VOICE_URL}\n")
    return VoiceInput(voice_url=DEFAULT_KLING_VOICE_URL)
