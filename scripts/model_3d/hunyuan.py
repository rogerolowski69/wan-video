"""Convert a 2D image to 3D with Hunyuan 3D Rapid on fal.ai."""

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
from wan_prompt import collect_hunyuan3d_input, demo_hunyuan3d_input

MODEL_ID = "fal-ai/hunyuan-3d/v3.1/rapid/image-to-3d"
OUTPUT_STEM = "hunyuan3d"
SCRIPT_NAME = "scripts/model_3d/hunyuan.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Hunyuan 3D Rapid via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use random demo input (non-interactive)")
    args = parser.parse_args()

    hunyuan_input = demo_hunyuan3d_input() if args.demo else collect_hunyuan3d_input()

    print(f"Sending request to {MODEL_ID} via fal.ai...")
    print(f"Image URL: {hunyuan_input.image_url}\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={"input_image_url": hunyuan_input.image_url},
        prompt=hunyuan_input.image_prompt,
        output_stem=OUTPUT_STEM,
        default_ext=".glb",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    run_cli(main)
