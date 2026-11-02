"""Unified LLM client wrapper for GenAI orchestration."""

from app.core.config import settings
from openai import OpenAI


def get_llm_client(provider: str = "groq") -> OpenAI:
    """
    Returns an OpenAI-compatible client for the specified provider.
    Groq is used for ultra-low latency, OpenAI for complex reasoning.
    """
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
        )
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment.")
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
