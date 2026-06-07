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

| Script | Model |
|--------|-------|
| `fal-ai-inference.py` | FLUX dev |
| `nano-banana.py` | Nano Banana 2 |
| `ideogram-character.py` | Ideogram Character |
| `kling-create-voice.py` | Kling voice |
| `trellis2-3d.py` | Trellis 2 (image→3D) |
| `hunyuan-3d.py` | Hunyuan3D |
| `seeddance-video.py` | Seedance video |
| `wan-inference.py` | Wan 2.2 T2V (HF Inference) |

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
uv run python fal-ai-inference.py --demo
```
