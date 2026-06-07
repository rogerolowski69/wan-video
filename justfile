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

# Interactive CLI studio — launch any model from one menu
menu:
    {{python}} menu.py

studio: menu

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
    {{python}} scripts/image/flux.py {{args}}

nano *args:
    {{python}} scripts/image/nano_banana.py {{args}}

ideogram *args:
    {{python}} scripts/image/ideogram_character.py {{args}}

kling *args:
    {{python}} scripts/voice/kling.py {{args}}

trellis *args:
    {{python}} scripts/model_3d/trellis2.py {{args}}

hunyuan *args:
    {{python}} scripts/model_3d/hunyuan.py {{args}}

seedance *args:
    {{python}} scripts/video/seedance.py {{args}}

wan *args:
    {{python}} scripts/video/wan.py {{args}}

# --- Generation (non-interactive demo prompts) ---

demo-flux:
    {{python}} scripts/image/flux.py --demo

demo-nano:
    {{python}} scripts/image/nano_banana.py --demo

demo-ideogram:
    {{python}} scripts/image/ideogram_character.py --demo

demo-kling:
    {{python}} scripts/voice/kling.py --demo

demo-trellis:
    {{python}} scripts/model_3d/trellis2.py --demo

demo-hunyuan:
    {{python}} scripts/model_3d/hunyuan.py --demo

demo-seedance:
    {{python}} scripts/video/seedance.py --demo

demo-wan provider="fal-ai":
    {{python}} scripts/video/wan.py --demo --provider {{provider}}

# Migrate DB, then run all scripts with --demo (log: output/run-all.log)
run-all: migrate
    {{python}} run_all.py

# Resume run-all from a specific script (skips earlier ones)
run-all-from script:
    {{python}} run_all.py --from {{script}} --continue-on-error

# Run all scripts; continue past individual failures
run-all-continue: migrate
    {{python}} run_all.py --continue-on-error

# Setup: sync deps + migrate
setup: sync migrate

# Start FastAPI server (Railway / local)
serve:
    {{python}} api.py

# --- Docker ---

# Full stack: UI, API, Postgres, MinIO
docker-up:
    docker compose up --build

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f
