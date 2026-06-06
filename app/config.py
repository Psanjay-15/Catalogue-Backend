from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

SERVER_ROOT = Path(__file__).resolve().parent.parent      
PROJECT_ROOT = SERVER_ROOT.parent                          

load_dotenv(SERVER_ROOT / ".env", override=False)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _env_str(name: str, default: str) -> str:
    value = _env(name, default)
    return value if value is not None else default


def _env_path(name: str, default: Path) -> Path:
    value = _env(name)
    return Path(value) if value is not None else default


class Settings:

    def __init__(self) -> None:
        # --- Database ---
        self.database_url: str = _env("DATABASE_URL")

        # --- LLM ---
        self.gemini_api_key: str | None = _env("GEMINI_API_KEY")
        self.openai_api_key: str | None = _env("OPENAI_API_KEY")
        self.anthropic_api_key: str | None = _env("ANTHROPIC_API_KEY")
        self.ollama_base_url: str = _env_str("OLLAMA_BASE_URL", "http://localhost:11434")

        self.default_llm_provider: str = _env_str("DEFAULT_LLM_PROVIDER", "gemini")

        self.cors_origins: str = _env_str(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        )

        self.templates_dir: Path = _env_path("TEMPLATES_DIR", PROJECT_ROOT / "templates")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
