"""Interactive CLI menu — central launcher for all generation models."""

from __future__ import annotations

import subprocess
import sys

from env_utils import load_env_file
from paths import PROJECT_ROOT
from scripts_config import MODEL_CATALOG, MODALITY_LABELS, GenerationModel


def _print_header() -> None:
    print("\n" + "=" * 56)
    print("  wan-video · Generation Studio")
    print("=" * 56)


def _print_menu() -> None:
    print("\nModels:\n")
    for index, model in enumerate(MODEL_CATALOG, start=1):
        mod = MODALITY_LABELS.get(model.modality, model.modality)
        print(f"  {index:2}. {model.emoji} {model.label:<22} [{mod}]")
    print(f"\n  {len(MODEL_CATALOG) + 1:2}. 🚀 Run all (--demo, continue on error)")
    print(f"  {len(MODEL_CATALOG) + 2:2}. 🌐 Open web UI (just serve + frontend)")
    print("\n  0. Exit")


def _run_model(model: GenerationModel, *, demo: bool) -> int:
    cmd = ["uv", "run", "python", model.path]
    if demo:
        cmd.append("--demo")
    print(f"\n→ {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def _run_all() -> int:
    cmd = ["uv", "run", "python", "run_all.py", "--continue-on-error"]
    print(f"\n→ {' '.join(cmd)}\n")
    return subprocess.run(cmd, cwd=PROJECT_ROOT).returncode


def main() -> int:
    load_env_file()

    while True:
        _print_header()
        _print_menu()
        choice = input(f"\nSelect [0–{len(MODEL_CATALOG) + 2}, d=demo all]: ").strip().lower()

        if choice in {"0", "q", "quit", "exit"}:
            print("Bye.")
            return 0

        if choice == "d":
            return _run_all()

        if not choice.isdigit():
            print("Invalid choice.")
            continue

        num = int(choice)
        if num == len(MODEL_CATALOG) + 1:
            return _run_all()

        if num == len(MODEL_CATALOG) + 2:
            print("\nStart the stack with:  just docker-up")
            print("Or locally:            just serve  (+ cd frontend && npm run dev)")
            continue

        if num < 1 or num > len(MODEL_CATALOG):
            print("Invalid choice.")
            continue

        model = MODEL_CATALOG[num - 1]
        mode = input(f"{model.label} — [D]emo or [I]nteractive? ").strip().lower()
        demo = mode != "i"
        code = _run_model(model, demo=demo)
        if code != 0:
            print(f"\nFinished with exit code {code}.")
        retry = input("\nReturn to menu? [Y/n] ").strip().lower()
        if retry in {"n", "no"}:
            return code


if __name__ == "__main__":
    sys.exit(main())
