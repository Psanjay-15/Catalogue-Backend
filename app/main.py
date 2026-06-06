"""uvicorn app.main:app --reload --port 8000"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.catalogs import router as catalogs_router
from app.api.v1.templates import router as templates_router
from app.config import settings
from app.core.database import create_all
from app.core.exceptions import CatalogMakerError
from app.core.logging import configure_logging, get_logger
from app.domain.schemas.responses import HealthResponse


configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting AI Catalog Maker server")
    await create_all()
    log.info("server ready")
    yield
    log.info("server shutting down")


app = FastAPI(
    title="AI Catalog Maker",
    description="Turn raw brand/product input into editable one-page catalogs.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CatalogMakerError)
async def catalog_error_handler(request: Request, exc: CatalogMakerError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "detail": str(exc)},
    )


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health() -> HealthResponse:
    return HealthResponse()


app.include_router(templates_router, prefix="/api/v1")
app.include_router(catalogs_router,  prefix="/api/v1")
