# wan-video — fal.ai + Hugging Face inference scripts
# https://github.com/casey/just

set dotenv-load := true
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set working-directory := '.'

python := "uv run python"
alembic := "uv run alembic"

# List available recipes
default:
    @just --list

# Install / sync dependencies (uv)
sync:
    uv sync

# --- Database ---

# Apply Alembic migrations
migrate:
    {{alembic}} upgrade head

# Create a new migration (pass message: just revision "add foo column")
revision message:
    {{alembic}} revision --autogenerate -m "{{message}}"

# Show current migration revision
db-current:
    {{alembic}} current

# --- Tests ---

# Smoke-test API keys only
test-keys:
    {{python}} test_api.py --keys

# Full dry-run smoke test (keys + all endpoints)
test:
    {{python}} test_api.py

# List configured API endpoints
test-list:
    {{python}} test_api.py --list

# --- Run history ---

# Latest status per generation script
runs-status:
    {{python}} runs.py status

# Recent generation runs
runs-list limit="20":
    {{python}} runs.py list --limit {{limit}}

# Backfill DB from existing output/ files
runs-import:
    {{python}} runs.py import-output

# Mark interrupted 'running' records as failed
runs-fix-stale:
    {{python}} runs.py fix-stale

# --- Generation (interactive — prompts in terminal) ---

flux *args:
    {{python}} fal-ai-inference.py {{args}}

nano *args:
    {{python}} nano-banana.py {{args}}

ideogram *args:
    {{python}} ideogram-character.py {{args}}

kling *args:
    {{python}} kling-create-voice.py {{args}}

trellis *args:
    {{python}} trellis2-3d.py {{args}}

hunyuan *args:
    {{python}} hunyuan-3d.py {{args}}

seedance *args:
    {{python}} seeddance-video.py {{args}}

wan *args:
    {{python}} wan-inference.py {{args}}

# --- Generation (non-interactive demo prompts) ---

demo-flux:
    {{python}} fal-ai-inference.py --demo

demo-nano:
    {{python}} nano-banana.py --demo

demo-ideogram:
    {{python}} ideogram-character.py --demo

demo-kling:
    {{python}} kling-create-voice.py --demo

demo-trellis:
    {{python}} trellis2-3d.py --demo

demo-hunyuan:
    {{python}} hunyuan-3d.py --demo

demo-seedance:
    {{python}} seeddance-video.py --demo

demo-wan provider="fal-ai":
    {{python}} wan-inference.py --demo --provider {{provider}}

# Migrate DB, then run all scripts with --demo (log: output/run-all.log)
run-all: migrate
    {{python}} run_all.py

# Resume run-all from a specific script (skips earlier ones)
run-all-from script:
    {{python}} run_all.py --from {{script}}

# Setup: sync deps + migrate
setup: sync migrate

# Start FastAPI server (Railway / local)
serve:
    {{python}} api.py
