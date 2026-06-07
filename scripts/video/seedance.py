"""Generate video with Seedance 2.0 on fal.ai using an interactive prompt."""

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
from wan_prompt import collect_seedance_prompt, demo_seedance_prompt

MODEL_ID = "bytedance/seedance-2.0/text-to-video"
OUTPUT_STEM = "seedance"
SCRIPT_NAME = "scripts/video/seedance.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seedance 2.0 video generation via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use random demo prompt (non-interactive)")
    args = parser.parse_args()

    video_prompt = demo_seedance_prompt() if args.demo else collect_seedance_prompt()

    print(f"Sending request to {MODEL_ID} via fal.ai...\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={"prompt": video_prompt.prompt},
        prompt=video_prompt.prompt,
        output_stem=OUTPUT_STEM,
        default_ext=".mp4",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    run_cli(main)
