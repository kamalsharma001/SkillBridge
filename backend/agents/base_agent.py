from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json

from models.schemas import AgentResult
from services.llm_service import LLMService


class BaseAgent(ABC):
    """Abstract Base Agent providing standardized execution context, timing, logging, and error handling."""

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        llm_service: Optional[LLMService] = None,
    ):
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"agent.{name}")
        self.llm_service = llm_service

    def execute(self, context: Any) -> AgentResult:
        """Executes the agent lifecycle with context validation, timing, and error safety."""
        start = time.perf_counter()
        try:
            self.validate_context(context)
            result = self.run(context)
            elapsed = time.perf_counter() - start
            self.logger.info("%s completed in %.3fs", self.name, elapsed)
            return result
        except Exception as exc:
            self.logger.exception("%s execution failed", self.name)
            # Re-raise critical exceptions so orchestrator can decide pipeline fate
            # Only catch and wrap expected validation/business logic errors
            if isinstance(exc, (ValueError, KeyError, TypeError)):
                return AgentResult(
                    agent=self.name,
                    status="error",
                    summary=f"Agent {self.name} encountered a validation error.",
                    errors=[str(exc)],
                )
            # For unexpected system errors, propagate
            raise

    def validate_context(self, context: Any) -> None:
        """Validates that context is provided."""
        if context is None:
            raise ValueError("Agent context must not be None.")

    async def synthesize_async(self, system_prompt: str, data: Any, model: str) -> str:
        """Calls the LLM service to synthesize the agent's deterministic output into a narrative concurrently."""
        if not self.llm_service:
            self.logger.warning("LLM Service not injected. Skipping synthesis.")
            return ""
        
        try:
            # Serialize the deterministic data to string (e.g. JSON)
            if not isinstance(data, str):
                # We use default=str to handle Pydantic objects or complex types gracefully if present
                user_data_str = json.dumps(data, indent=2, default=str)
            else:
                user_data_str = data
            
            self.logger.info(f"{self.name} is synthesizing reasoning via LLM using {model}...")
            return await self.llm_service.generate_reasoning_async(system_prompt, user_data_str, model)
        except Exception as exc:
            self.logger.error(f"Error during LLM synthesis in {self.name}: {exc}")
            # Return empty string on synthesis failure - don't pollute output with error messages
            return ""

    @abstractmethod
    def run(self, context: Any) -> AgentResult:
        """Core execution logic to be implemented by each agent subclass."""
        pass