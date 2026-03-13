from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    log_level: str = "INFO"

    anthropic_api_key: str | None = None

    database_url: str = "sqlite:///./data/app.db"
    chroma_persist_dir: str = "./data/vector_db"
    demo_data_dir: str = "./data/raw"
    audit_log_path: str = "./data/audit.jsonl"


settings = Settings()

