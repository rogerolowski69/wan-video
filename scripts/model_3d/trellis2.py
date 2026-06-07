"""Convert a 2D image to 3D with Trellis 2 on fal.ai."""

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
from wan_prompt import collect_trellis2_input, demo_trellis2_input

MODEL_ID = "fal-ai/trellis-2"
OUTPUT_STEM = "trellis2"
SCRIPT_NAME = "scripts/model_3d/trellis2.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Trellis 2 image-to-3D via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use random demo input (non-interactive)")
    args = parser.parse_args()

    trellis_input = demo_trellis2_input() if args.demo else collect_trellis2_input()

    print(f"Sending request to {MODEL_ID} via fal.ai...")
    print(f"Image URL: {trellis_input.image_url}\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={"image_url": trellis_input.image_url},
        prompt=trellis_input.image_prompt,
        output_stem=OUTPUT_STEM,
        default_ext=".glb",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    run_cli(main)
