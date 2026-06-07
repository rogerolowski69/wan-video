"""Generate an image with FLUX dev on fal.ai using an interactive prompt."""

import argparse

from api_errors import run_cli
from generation_runner import run_fal_generation
from wan_prompt import collect_fal_image_prompt, demo_image_prompt

MODEL_ID = "fal-ai/flux/dev"
OUTPUT_STEM = "flux-dev"
SCRIPT_NAME = "fal-ai-inference.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="FLUX dev image generation via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use random demo prompt (non-interactive)")
    args = parser.parse_args()

    image_prompt = demo_image_prompt() if args.demo else collect_fal_image_prompt()

    print(f"Sending request to {MODEL_ID} via fal.ai...\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={"prompt": image_prompt.prompt},
        prompt=image_prompt.prompt,
        output_stem=OUTPUT_STEM,
        default_ext=".png",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    run_cli(main)
