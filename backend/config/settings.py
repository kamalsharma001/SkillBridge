from __future__ import annotations
import os
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(**kwargs) -> bool:
        return False

# Load .env from ai-career-engine root directory
load_dotenv(override=True)

class Settings:
    """Centralized deployment settings and API key management for AI Career Engine."""

    # Primary AI / LLM Provider Configuration - NVIDIA Nemotron as default
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    GEMINI_BASE_URL: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    GEMINI_THINKING_LEVEL: str = os.getenv("GEMINI_THINKING_LEVEL", "low")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

    LLM_MODEL_FAST: str = os.getenv("LLM_MODEL_FAST", LLM_MODEL)
    LLM_MODEL_MEDIUM: str = os.getenv("LLM_MODEL_MEDIUM", LLM_MODEL)
    LLM_PARALLEL_REQUESTS: int = int(os.getenv("LLM_PARALLEL_REQUESTS", "2"))
    
    AGENT_MODELS = {
        "skill_analysis": LLM_MODEL_FAST,
        "career_research": LLM_MODEL_FAST,
        "industry_intelligence": LLM_MODEL_FAST,
        "learning": LLM_MODEL_FAST,
        "opportunity": LLM_MODEL_FAST,
        "profile_intelligence": LLM_MODEL_FAST,
    }

    # NVIDIA Nemotron / NVIDIA NIM API (Primary)
    NVIDIA_API_KEY: Optional[str] = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")

    # Optional Alternative LLM Provider (OpenAI Fallback)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")

    # OpenRouter Provider
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # Live Job Market Data API Keys (Optional for real-time market ingestion)
    ADZUNA_APP_ID: Optional[str] = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY: Optional[str] = os.getenv("ADZUNA_APP_KEY")
    JOOBLE_API_KEY: Optional[str] = os.getenv("JOOBLE_API_KEY")

    # Deployment Environment Config
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---- Data Source Configuration ----
    # "json" = local JSON test fixtures for tests only
    # "hana" = SAP HANA Cloud production data
    DATA_SOURCE: str = os.getenv("DATA_SOURCE", "hana")
    ENABLE_LLM_SYNTHESIS: bool = os.getenv("ENABLE_LLM_SYNTHESIS", "False").lower() in ("true", "1", "t")

    # ---- SAP HANA Cloud Connection ----
    HANA_HOST: Optional[str] = os.getenv("HANA_HOST")
    HANA_PORT: int = int(os.getenv("HANA_PORT", "443"))
    HANA_USER: Optional[str] = os.getenv("HANA_USER")
    HANA_PASSWORD: Optional[str] = os.getenv("HANA_PASSWORD")
    HANA_ENCRYPT: bool = os.getenv("HANA_ENCRYPT", "true").lower() in ("true", "1")
    HANA_SSL_VALIDATE: bool = os.getenv("HANA_SSL_VALIDATE", "true").lower() in ("true", "1", "t")

    @classmethod
    def get_active_llm_key(cls) -> Optional[str]:
        """Returns the primary active LLM API key (NVIDIA first, then Gemini, then OpenAI)."""
        return cls.NVIDIA_API_KEY or cls.GEMINI_API_KEY or cls.OPENAI_API_KEY


settings = Settings()

