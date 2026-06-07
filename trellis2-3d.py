"""Convert a 2D image to 3D with Trellis 2 on fal.ai."""

import argparse

from generation_runner import run_fal_generation
from wan_prompt import collect_trellis2_input, demo_trellis2_input

MODEL_ID = "fal-ai/trellis-2"
OUTPUT_STEM = "trellis2"
SCRIPT_NAME = "trellis2-3d.py"


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
    main()
