from __future__ import annotations

from typing import Any

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
    brief_storage_dir: str = "./data/processed/briefs"
    integration_backend: str = "mock"
    storage_backend: str = "file"
    crm_provider: str = "mock"
    ats_provider: str = "mock"
    doc_store_provider: str = "mock"

    ranking_strategy_version: str = "v1"
    ranking_weight_skill_match: float = 0.30
    ranking_weight_seniority_match: float = 0.20
    ranking_weight_sector_relevance: float = 0.20
    ranking_weight_functional_similarity: float = 0.15
    ranking_weight_location_alignment: float = 0.10
    ranking_weight_stability_signal: float = 0.05

    def ranking_weights(self) -> dict[str, float]:
        return {
            "skill_match": self.ranking_weight_skill_match,
            "seniority_match": self.ranking_weight_seniority_match,
            "sector_relevance": self.ranking_weight_sector_relevance,
            "functional_similarity": self.ranking_weight_functional_similarity,
            "location_alignment": self.ranking_weight_location_alignment,
            "stability_signal": self.ranking_weight_stability_signal,
        }

    def safe_dump(self) -> dict[str, Any]:
        data = self.model_dump()
        if data.get("anthropic_api_key"):
            data["anthropic_api_key"] = "***"
        return data


settings = Settings()
