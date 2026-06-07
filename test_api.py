"""
Smoke-test API keys, model IDs, and endpoints used in this project.

Default mode is free/dry-run (no generation). Use --live to run a real request.

Examples:
  uv sync
  uv run python test_api.py
  uv run python test_api.py --list
  uv run python test_api.py --endpoint hf-wan-t2v
  uv run python test_api.py --keys
  uv run python test_api.py --model Wan-AI/Wan2.2-T2V-A14B-Diffusers --provider fal-ai
  uv run python test_api.py --live --endpoint hf-wan-t2v
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from env_utils import load_env_file

import requests
from huggingface_hub import HfApi, InferenceClient, whoami
from huggingface_hub.errors import HfHubHTTPError


FAL_QUEUE_BASE = "https://queue.fal.run"
FAL_AUTH_PROBE_APP = "fal-ai/__auth-probe-invalid__"


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    WARN = "WARN"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Status
    detail: str


@dataclass(frozen=True)
class EndpointConfig:
    id: str
    label: str
    backend: Literal["hf_inference", "fal_direct"]
    model: str
    key_env: str
    task: str
    source_file: str
    provider: str | None = None
    test_prompt: str = "A red balloon drifting across a clear blue sky, cinematic, smooth motion."


ENDPOINTS: tuple[EndpointConfig, ...] = (
    EndpointConfig(
        id="hf-wan-t2v",
        label="Wan 2.2 T2V via HF Inference (fal-ai provider)",
        backend="hf_inference",
        model="Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        key_env="HF_TOKEN",
        provider="fal-ai",
        task="text-to-video",
        source_file="wan-inference.py",
        test_prompt="A young man walking on a city street at dusk, cinematic tracking shot.",
    ),
    EndpointConfig(
        id="fal-flux",
        label="FLUX dev via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/flux/dev",
        key_env="FAL_KEY",
        task="text-to-image",
        source_file="fal-ai-inference.py",
    ),
    EndpointConfig(
        id="fal-nano-banana",
        label="Nano Banana 2 via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/nano-banana-2",
        key_env="FAL_KEY",
        task="text-to-image",
        source_file="nano-banana.py",
    ),
    EndpointConfig(
        id="fal-seedance",
        label="Seedance 2.0 T2V via fal.ai direct",
        backend="fal_direct",
        model="bytedance/seedance-2.0/text-to-video",
        key_env="FAL_KEY",
        task="text-to-video",
        source_file="seeddance-video.py",
    ),
    EndpointConfig(
        id="fal-ideogram-character",
        label="Ideogram Character via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/ideogram/character",
        key_env="FAL_KEY",
        task="text-to-image",
        source_file="ideogram-character.py",
    ),
    EndpointConfig(
        id="fal-trellis2",
        label="Trellis 2 image-to-3D via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/trellis-2",
        key_env="FAL_KEY",
        task="image-to-3d",
        source_file="trellis2-3d.py",
    ),
    EndpointConfig(
        id="fal-hunyuan3d",
        label="Hunyuan 3D Rapid via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/hunyuan-3d/v3.1/rapid/image-to-3d",
        key_env="FAL_KEY",
        task="image-to-3d",
        source_file="hunyuan-3d.py",
    ),
    EndpointConfig(
        id="fal-kling-voice",
        label="Kling create-voice via fal.ai direct",
        backend="fal_direct",
        model="fal-ai/kling-video/create-voice",
        key_env="FAL_KEY",
        task="voice-cloning",
        source_file="kling-create-voice.py",
    ),
)


def mask_secret(value: str | None) -> str:
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def print_results(results: list[CheckResult]) -> int:
    width = max(len(r.name) for r in results) if results else 10
    failures = 0
    for result in results:
        icon = {
            Status.PASS: "[OK]",
            Status.FAIL: "[FAIL]",
            Status.SKIP: "[SKIP]",
            Status.WARN: "[WARN]",
        }[result.status]
        print(f"{icon} {result.name:<{width}}  {result.detail}")
        if result.status == Status.FAIL:
            failures += 1
    print()
    return failures


def check_env_var(name: str) -> CheckResult:
    value = os.environ.get(name)
    if not value:
        return CheckResult(name, Status.FAIL, f"{name} missing from environment / .env")
    return CheckResult(name, Status.PASS, f"set ({mask_secret(value)})")


def check_hf_token() -> CheckResult:
    token = os.environ.get("HF_TOKEN")
    if not token:
        return CheckResult("HF_TOKEN auth", Status.FAIL, "HF_TOKEN not set")
    try:
        account = whoami(token=token)
    except HfHubHTTPError as exc:
        return CheckResult("HF_TOKEN auth", Status.FAIL, f"Hub rejected token: {exc}")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("HF_TOKEN auth", Status.FAIL, str(exc))

    name = account.get("name") or account.get("fullname") or "unknown"
    orgs = ", ".join(org.get("name", "?") for org in account.get("orgs", [])) or "none"
    return CheckResult("HF_TOKEN auth", Status.PASS, f"user={name}, orgs={orgs}")


def check_fal_key() -> CheckResult:
    key = os.environ.get("FAL_KEY")
    if not key:
        return CheckResult("FAL_KEY auth", Status.FAIL, "FAL_KEY not set")

    if not re.fullmatch(r"[0-9a-f-]{36}:[0-9a-f]{32}", key, flags=re.IGNORECASE):
        return CheckResult(
            "FAL_KEY auth",
            Status.WARN,
            "unexpected format (expected uuid:hex); still probing API",
        )

    try:
        response = requests.post(
            f"{FAL_QUEUE_BASE}/{FAL_AUTH_PROBE_APP}",
            headers={"Authorization": f"Key {key}"},
            json={"prompt": "probe"},
            timeout=20,
        )
    except requests.RequestException as exc:
        return CheckResult("FAL_KEY auth", Status.FAIL, f"network error: {exc}")

    if response.status_code == 401:
        detail = response.json().get("detail", response.text) if response.text else "unauthorized"
        return CheckResult("FAL_KEY auth", Status.FAIL, f"invalid credentials ({detail})")

    if response.status_code == 404:
        return CheckResult("FAL_KEY auth", Status.PASS, "credentials accepted by fal queue API")

    return CheckResult(
        "FAL_KEY auth",
        Status.WARN,
        f"unexpected HTTP {response.status_code}: {response.text[:120]}",
    )


def check_hf_model(model: str, provider: str | None) -> list[CheckResult]:
    results: list[CheckResult] = []
    api = HfApi(token=os.environ.get("HF_TOKEN"))

    try:
        info = api.model_info(model, expand=["inferenceProviderMapping"])
    except HfHubHTTPError as exc:
        results.append(CheckResult(f"model {model}", Status.FAIL, f"not found or inaccessible: {exc}"))
        return results

    results.append(
        CheckResult(
            f"model {model}",
            Status.PASS,
            f"exists on Hub (pipeline_tag={info.pipeline_tag or 'n/a'})",
        )
    )

    mappings = info.inference_provider_mapping or []
    if not mappings:
        results.append(
            CheckResult(
                f"inference providers ({model})",
                Status.WARN,
                "no inferenceProviderMapping on Hub",
            )
        )
        return results

    provider_lines = [
        f"{m.provider} -> {m.provider_id} [{m.status}, {m.task}]" for m in mappings
    ]
    results.append(
        CheckResult(
            f"inference providers ({model})",
            Status.PASS,
            "; ".join(provider_lines),
        )
    )

    if provider:
        match = next((m for m in mappings if m.provider == provider), None)
        if match is None:
            available = ", ".join(m.provider for m in mappings)
            results.append(
                CheckResult(
                    f"provider {provider}",
                    Status.FAIL,
                    f"not mapped for this model (available: {available})",
                )
            )
        elif match.status != "live":
            results.append(
                CheckResult(
                    f"provider {provider}",
                    Status.WARN,
                    f"mapped but status={match.status}, provider_id={match.provider_id}",
                )
            )
        else:
            results.append(
                CheckResult(
                    f"provider {provider}",
                    Status.PASS,
                    f"live at {match.provider_id} ({match.task})",
                )
            )

    return results


def check_fal_endpoint(endpoint: str, key_env: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not os.environ.get(key_env):
        results.append(CheckResult(f"fal endpoint {endpoint}", Status.FAIL, f"{key_env} not set"))
        return results

    if "/" not in endpoint or endpoint.startswith("/") or " " in endpoint:
        results.append(
            CheckResult(
                f"fal endpoint {endpoint}",
                Status.FAIL,
                "invalid format (expected owner/model, e.g. fal-ai/flux/dev)",
            )
        )
        return results

    owner, _, name = endpoint.partition("/")
    if not owner or not name:
        results.append(CheckResult(f"fal endpoint {endpoint}", Status.FAIL, "missing owner or model name"))
        return results

    results.append(
        CheckResult(
            f"fal endpoint {endpoint}",
            Status.PASS,
            f"format OK ({owner}/{name}); dry-run skips queue probe - use --live to confirm",
        )
    )
    return results


def run_live_hf(endpoint: EndpointConfig) -> CheckResult:
    token = os.environ.get(endpoint.key_env)
    if not token:
        return CheckResult(f"live {endpoint.id}", Status.FAIL, f"{endpoint.key_env} not set")

    client = InferenceClient(provider=endpoint.provider, api_key=token)
    try:
        video = client.text_to_video(endpoint.test_prompt, model=endpoint.model)
    except Exception as exc:  # noqa: BLE001
        return CheckResult(f"live {endpoint.id}", Status.FAIL, str(exc))

    output_path = Path(f"test_output_{endpoint.id}.mp4")
    if hasattr(video, "save"):
        video.save(output_path)
        return CheckResult(f"live {endpoint.id}", Status.PASS, f"saved {output_path}")
    return CheckResult(
        f"live {endpoint.id}",
        Status.WARN,
        f"completed but unexpected return type: {type(video).__name__}",
    )


def run_live_fal(endpoint: EndpointConfig) -> CheckResult:
    key = os.environ.get(endpoint.key_env)
    if not key:
        return CheckResult(f"live {endpoint.id}", Status.FAIL, f"{endpoint.key_env} not set")

    try:
        response = requests.post(
            f"{FAL_QUEUE_BASE}/{endpoint.model}",
            headers={"Authorization": f"Key {key}"},
            json={"prompt": endpoint.test_prompt},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return CheckResult(f"live {endpoint.id}", Status.FAIL, str(exc))

    request_id = payload.get("request_id", "unknown")
    return CheckResult(
        f"live {endpoint.id}",
        Status.PASS,
        f"queued request_id={request_id} (poll status URL in response)",
    )


def run_endpoint_checks(endpoint: EndpointConfig, *, live: bool) -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(check_env_var(endpoint.key_env))

    if endpoint.backend == "hf_inference":
        results.extend(check_hf_model(endpoint.model, endpoint.provider))
        if live:
            results.append(run_live_hf(endpoint))
    else:
        results.extend(check_fal_endpoint(endpoint.model, endpoint.key_env))
        if live:
            results.append(run_live_fal(endpoint))

    return results


def list_endpoints() -> None:
    print("\nConfigured endpoints:\n")
    for ep in ENDPOINTS:
        provider = f", provider={ep.provider}" if ep.provider else ""
        print(f"  {ep.id}")
        print(f"    {ep.label}")
        print(f"    model={ep.model}")
        print(f"    key={ep.key_env}{provider}")
        print(f"    task={ep.task}, source={ep.source_file}")
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke-test API keys, models, and endpoints.")
    parser.add_argument("--list", action="store_true", help="List configured endpoints.")
    parser.add_argument(
        "--endpoint",
        action="append",
        dest="endpoints",
        metavar="ID",
        help="Run checks for one endpoint id (repeatable). Default: all.",
    )
    parser.add_argument("--keys", action="store_true", help="Test API keys only.")
    parser.add_argument("--model", help="Check a custom Hugging Face model id on the Hub.")
    parser.add_argument(
        "--provider",
        help="When using --model, verify this inference provider mapping (e.g. fal-ai).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run a real generation request (may incur cost / GPU time).",
    )
    return parser


def main() -> int:
    load_env_file()
    args = build_parser().parse_args()

    if args.list:
        list_endpoints()
        return 0

    print("API smoke test\n" + "=" * 60)

    results: list[CheckResult] = []

    if args.keys or (not args.endpoints and not args.model):
        results.extend(
            [
                check_env_var("HF_TOKEN"),
                check_env_var("FAL_KEY"),
                check_hf_token(),
                check_fal_key(),
            ]
        )

    if args.model:
        results.extend(check_hf_model(args.model, args.provider))

    selected = ENDPOINTS
    if args.endpoints:
        known = {ep.id for ep in ENDPOINTS}
        unknown = set(args.endpoints) - known
        if unknown:
            print(f"Unknown endpoint id(s): {', '.join(sorted(unknown))}")
            print("Use --list to see valid ids.")
            return 2
        selected = tuple(ep for ep in ENDPOINTS if ep.id in set(args.endpoints))

    if args.endpoints or (not args.keys and not args.model):
        for endpoint in selected:
            print(f"\n{endpoint.label} [{endpoint.id}]")
            print("-" * 60)
            results.extend(run_endpoint_checks(endpoint, live=args.live))

    if args.live:
        print("\nNote: --live may queue paid inference jobs.")

    failures = print_results(results)
    if failures:
        print(f"{failures} check(s) failed.")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
