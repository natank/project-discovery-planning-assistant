"""Lazy CrewAI model construction."""

from crewai import LLM

from project_discovery_assistant.config import Settings


def build_llm(settings: Settings | None = None) -> LLM:
    """Build a configured CrewAI LLM without loading provider settings at import."""
    resolved = settings or Settings()
    api_key = resolved.require_provider()
    return LLM(
        model=resolved.model_name,
        api_key=api_key,
        base_url=resolved.openai_base_url,
        provider="openai",
    )
