"""Create a Kling voice clone from an audio sample URL on fal.ai."""

import importlib.util
from pathlib import Path

_bootstrap_spec = importlib.util.spec_from_file_location(
    "scripts._bootstrap",
    Path(__file__).resolve().parents[1] / "_bootstrap.py",
)
assert _bootstrap_spec and _bootstrap_spec.loader
_bootstrap = importlib.util.module_from_spec(_bootstrap_spec)
_bootstrap_spec.loader.exec_module(_bootstrap)
_bootstrap.install()

import argparse

from api_errors import run_cli
from generation_runner import run_fal_generation
from wan_prompt import collect_kling_voice_input, demo_kling_voice_input

MODEL_ID = "fal-ai/kling-video/create-voice"
OUTPUT_STEM = "kling-voice"
SCRIPT_NAME = "scripts/voice/kling.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Kling create-voice via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use default demo voice URL (non-interactive)")
    args = parser.parse_args()

    voice_input = demo_kling_voice_input() if args.demo else collect_kling_voice_input()

    print(f"Sending request to {MODEL_ID} via fal.ai...")
    print(f"Voice URL: {voice_input.voice_url}\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={"voice_url": voice_input.voice_url},
        prompt=voice_input.voice_url,
        output_stem=OUTPUT_STEM,
        default_ext=".json",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    run_cli(main)
