"""Generate video with Wan 2.2 T2V via Hugging Face Inference API."""

from __future__ import annotations

import argparse
import os

from huggingface_hub import InferenceClient

from db.record import GenerationRecorder
from env_utils import load_env_file, require_env
from output_utils import make_run_stem, output_path, resolve_output_path, save_video_result
from wan_prompt import collect_video_prompt, demo_video_prompt

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
SCRIPT_NAME = "wan-inference.py"
DEFAULT_PROVIDER = "fal-ai"
OUTPUT_BASENAME = "wan-inference"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wan 2.2 text-to-video via Hugging Face Inference providers.",
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("HF_INFERENCE_PROVIDER", DEFAULT_PROVIDER),
        help=f"Inference provider (default: {DEFAULT_PROVIDER}). "
        "Run `uv run python test_api.py --model Wan-AI/Wan2.2-T2V-A14B-Diffusers` to list live providers.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output video path (default: output/wan-inference-run<ID>.mp4, unique per run).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use random demo prompt (non-interactive)",
    )
    return parser


def main() -> None:
    load_env_file()
    args = build_parser().parse_args()
    require_env("HF_TOKEN")

    video_prompt = demo_video_prompt() if args.demo else collect_video_prompt("inference")

    print(f"Sending request to {args.provider} via Hugging Face Inference API...")
    print("(Remote endpoints use your positive prompt string; quality cues belong in the prompt.)\n")

    with GenerationRecorder(
        script_name=SCRIPT_NAME,
        model_id=MODEL_ID,
        backend="hf_inference",
        prompt=video_prompt.prompt,
        provider=args.provider,
    ) as recorder:
        client = InferenceClient(provider=args.provider, api_key=os.environ["HF_TOKEN"])
        video = client.text_to_video(video_prompt.prompt, model=MODEL_ID)

        print("\nGeneration complete.")
        print(f"Result type: {type(video).__name__}")
        assert recorder.run_id is not None
        dest = (
            resolve_output_path(args.output)
            if args.output
            else output_path(make_run_stem(OUTPUT_BASENAME, recorder.run_id), ".mp4")
        )
        save_video_result(video, dest)
        recorder.register_artifact(dest)
        print(f"Saved to {dest}")


if __name__ == "__main__":
    main()
