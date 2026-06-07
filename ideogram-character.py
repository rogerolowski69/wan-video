"""Place a reference character into a new scene with Ideogram Character on fal.ai."""

import argparse

from generation_runner import run_fal_generation
from wan_prompt import collect_ideogram_character_prompt, demo_ideogram_character_prompt

MODEL_ID = "fal-ai/ideogram/character"
OUTPUT_STEM = "ideogram-character"
SCRIPT_NAME = "ideogram-character.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ideogram Character via fal.ai")
    parser.add_argument("--demo", action="store_true", help="Use random demo prompt (non-interactive)")
    args = parser.parse_args()

    character_prompt = (
        demo_ideogram_character_prompt() if args.demo else collect_ideogram_character_prompt()
    )

    print(f"Sending request to {MODEL_ID} via fal.ai...\n")

    paths = run_fal_generation(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        arguments={
            "prompt": character_prompt.prompt,
            "reference_image_urls": character_prompt.reference_image_urls,
        },
        prompt=character_prompt.prompt,
        output_stem=OUTPUT_STEM,
        default_ext=".png",
    )

    print("\nGeneration complete.")
    for path in paths:
        print(f"  Saved {path}")


if __name__ == "__main__":
    main()
