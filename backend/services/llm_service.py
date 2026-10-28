from __future__ import annotations
import logging
import os
import asyncio
import httpx
from typing import Optional
from config.settings import Settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM synthesis supporting Gemini, Groq, NVIDIA, and OpenAI."""

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.nvidia_key = os.environ.get("NVIDIA_API_KEY")
        provider_pref = (os.environ.get("LLM_PROVIDER") or "").lower()

        self.client = None
        self.active_provider = None

        # 1. Prefer Gemini if GEMINI_API_KEY is present or LLM_PROVIDER is gemini
        if self.gemini_key and (provider_pref in ("gemini", "google") or not self.groq_key):
            try:
                from openai import AsyncOpenAI
                base_url = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
                self.client = AsyncOpenAI(
                    api_key=self.gemini_key,
                    base_url=base_url,
                    http_client=httpx.AsyncClient(timeout=8.0),
                )
                self.active_provider = "gemini"
                logger.info("Initialized Gemini client via OpenAI-compatible endpoint")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

        # 2. Try Groq if GROQ_API_KEY is present
        if not self.client and self.groq_key:
            try:
                from groq import AsyncGroq
                self.client = AsyncGroq(api_key=self.groq_key, timeout=8.0)
                self.active_provider = "groq"
                logger.info("Initialized Groq LLM client")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")

        # 3. Try Standard OpenAI
        if not self.client and self.openai_key:
            try:
                from openai import AsyncOpenAI
                base_url = os.environ.get("OPENAI_BASE_URL") or None
                self.client = AsyncOpenAI(
                    api_key=self.openai_key,
                    base_url=base_url,
                    http_client=httpx.AsyncClient(timeout=8.0),
                )
                self.active_provider = "openai"
                logger.info("Initialized OpenAI LLM client")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

        # 4. Try NVIDIA NIM
        if not self.client and self.nvidia_key:
            try:
                from openai import AsyncOpenAI
                base_url = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
                self.client = AsyncOpenAI(
                    api_key=self.nvidia_key,
                    base_url=base_url,
                    http_client=httpx.AsyncClient(timeout=8.0),
                )
                self.active_provider = "nvidia"
                logger.info("Initialized NVIDIA client")
            except Exception as e:
                logger.error(f"Failed to initialize NVIDIA client: {e}")

    async def generate_reasoning_async(
        self,
        system_prompt: str,
        user_data: str,
        model: Optional[str] = None,
    ) -> str:
        """Generates reasoning/synthesis from the LLM based on deterministic data."""
        if not self.client:
            return "Deterministic assessment complete (LLM key not configured)."

        # Map / resolve model based on active provider
        if self.active_provider == "gemini":
            configured = os.environ.get("LLM_MODEL") or "gemini-2.0-flash"
            if model and "gemini" in model.lower():
                selected_model = model
            elif "gemini" in configured.lower():
                selected_model = configured
            else:
                selected_model = "gemini-2.0-flash"

        elif self.active_provider == "groq":
            configured = os.environ.get("LLM_MODEL_FAST") or "llama-3.3-70b-versatile"
            if model and ("llama" in model.lower() or "mixtral" in model.lower()):
                selected_model = model
            else:
                selected_model = configured

        else:
            selected_model = model or getattr(Settings, "LLM_MODEL_FAST", "gpt-4o-mini")

        try:
            call_coro = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_data}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            response = await asyncio.wait_for(call_coro, timeout=8.0)
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"LLM call fallback ({self.active_provider}/{selected_model}): {e}")
            return f"Deterministic assessment generated. ({str(e)[:100]})"
