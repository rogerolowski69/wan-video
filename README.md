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

## Scripts

Generation CLIs live under `scripts/` by modality:

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

Outputs land in `output/` with unique `-run<ID>` suffixes. Run history is stored in `data/wan_video.db`.

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
