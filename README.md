# wan-video

API-backed inference scripts for image, video, 3D, and voice generation via [fal.ai](https://fal.ai) and [Hugging Face Inference](https://huggingface.co/docs/inference-providers).

## Local setup

```powershell
uv sync
just setup          # sync + migrate
just test-keys      # verify HF_TOKEN and FAL_KEY
just run-all        # run all 8 scripts with --demo (~20–40 min)
just runs-status    # latest status per script
```

Copy `.env.example` to `.env` and set `HF_TOKEN` and `FAL_KEY`.

## Generation Studio

**Web UI** (http://localhost:3000 with Docker, or `just serve` + `npm run dev` in `frontend/`):
- **Studio** — central menu to launch any model with one click (demo mode)
- **Runs** — full history
- **Gallery** — all outputs from MinIO

**CLI menu** (terminal):

```powershell
just menu
# or: uv run python menu.py
```

Pick a model by number, choose demo or interactive prompts, or run the full batch.

### Scripts

```
scripts/
  image/          flux, nano_banana, ideogram_character
  video/          seedance, wan
  voice/          kling
  model_3d/       trellis2, hunyuan
```

| Just recipe | Script | Model |
|-------------|--------|-------|
| `just flux` | `scripts/image/flux.py` | FLUX dev |
| `just nano` | `scripts/image/nano_banana.py` | Nano Banana 2 |
| `just ideogram` | `scripts/image/ideogram_character.py` | Ideogram Character |
| `just kling` | `scripts/voice/kling.py` | Kling voice |
| `just trellis` | `scripts/model_3d/trellis2.py` | Trellis 2 (image→3D) |
| `just hunyuan` | `scripts/model_3d/hunyuan.py` | Hunyuan3D |
| `just seedance` | `scripts/video/seedance.py` | Seedance video |
| `just wan` | `scripts/video/wan.py` | Wan 2.2 T2V (HF Inference) |

Outputs land in `output/` with unique `-run<ID>` suffixes, uploaded to **MinIO** when configured. Run history is stored in Postgres (Docker) or SQLite (local).

## Docker Compose (UI + MinIO + Postgres)

Full stack: React frontend, FastAPI, PostgreSQL, MinIO object storage.

```powershell
copy .env.example .env   # set HF_TOKEN, FAL_KEY
docker compose up --build
```

| Service | URL |
|---------|-----|
| **Web UI** | http://localhost:3000 |
| **MinIO Console** | http://localhost:9001 (minioadmin / minioadmin) |
| **MinIO S3 API** | http://localhost:9000 |

All generation artifacts are uploaded to the `wan-video` bucket under `output/`. The UI loads media via `/api/files/...` (proxied to MinIO).

Run a generation while stack is up (from host):

```powershell
just flux --demo
```

Ensure `.env` includes `MINIO_ENDPOINT=http://localhost:9000` for local CLI uploads to MinIO.

### Frontend dev (hot reload)

```powershell
# Terminal 1
just serve

# Terminal 2
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` to the backend.

## Deploy on Railway

1. Push this repo to GitHub and connect it in [Railway](https://railway.app).
2. Set environment variables:
   - `HF_TOKEN` — Hugging Face token
   - `FAL_KEY` — fal.ai API key
   - `DATABASE_URL` *(optional)* — Postgres URL for persistent run history; defaults to SQLite on the container filesystem
3. Railway builds from `Dockerfile` and starts the FastAPI app on `$PORT`.

Endpoints:

- `GET /health` — liveness check
- `GET /runs` — recent generation runs
- `GET /scripts` — available CLI scripts
- `GET /docs` — OpenAPI UI

Run generations locally or via Railway shell:

```bash
just flux --demo
# or: uv run python scripts/image/flux.py --demo
```
