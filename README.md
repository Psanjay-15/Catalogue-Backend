# AI Catalog Maker — FastAPI server

The Phase 2 backend service. Replaces the Phase 1 notebook with a proper HTTP API that a React frontend can drive.

## Run it (first-time setup)

```bash
# 1. Start Postgres (credentials baked into docker-compose.yml)
docker compose up -d postgres

# 2. Python env + deps
python -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. macOS: WeasyPrint + Playwright system libs
brew install pango
playwright install chromium

# 4. Env
cp .env.example .env
# Edit .env and set GEMINI_API_KEY (minimum). OpenAI/Anthropic keys optional.

# 5. Create database tables
python -m app.scripts.init_db

# 6. Render template previews + seed the templates table
#    (takes ~3-5 min on first run because Pollinations generates real AI images)
python -m app.scripts.generate_previews

# 7. Run the server
uvicorn app.main:app --reload --port 8000
```

Then open <http://localhost:8000/docs> for Swagger UI.

## Day-to-day

```bash
docker compose up -d postgres   # if not already running
uvicorn app.main:app --reload --port 8000
```

## Architecture overview

```
┌──────────┐  HTTP   ┌────────────┐
│  React   │ ──────► │  FastAPI   │     api/v1/  (thin routing)
│ frontend │ ◄────── │    app     │
└──────────┘         └──────┬─────┘
                            │ depends-on
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        domain/services   db/repos    static/ (PNGs + HTMLs)
        (orchestrator)   (CRUD via       served as files
              │           SQLAlchemy)
              │
   ┌──────────┼──────────┬─────────┬──────────┐
   ▼          ▼          ▼         ▼          ▼
 llm/    extractors/  renderers/ exporters/   (strategy adapters)
```

- **`api/`** — HTTP layer only. No business logic.
- **`domain/`** — Pure business logic. No FastAPI / SQLAlchemy imports.
- **`db/`** — SQLAlchemy models + repository pattern. Business code talks to repos, not the session.
- **`llm/`, `extractors/`, `renderers/`, `exporters/`** — All strategy patterns. Each has a `base.py` ABC, concrete implementations, and a `factory.py` that picks the right one. Swappable without touching callers.
- **`scripts/`** — One-shot ops scripts (init DB, generate previews).

## API at a glance

| Method | Path                                  | Returns                         |
|--------|---------------------------------------|---------------------------------|
| GET    | `/api/v1/templates`                   | List of 10 templates with PNG + HTML URLs |
| GET    | `/api/v1/templates/{id}`              | Single template detail          |
| GET    | `/api/v1/templates/{id}/preview.png`  | Thumbnail PNG                    |
| GET    | `/api/v1/templates/{id}/sample.html`  | Sample HTML rendered with Aurora Coffee data |
| POST   | `/api/v1/catalogs`                    | `{catalog_id, status}` — starts background job |
| GET    | `/api/v1/catalogs/{id}`               | Job status + metadata           |
| GET    | `/api/v1/catalogs/{id}/html`          | Generated HTML (text/html)      |
| GET    | `/api/v1/catalogs/{id}/pdf`           | Generated PDF (download)        |
| GET    | `/health`                             | `{"status":"ok"}`               |
