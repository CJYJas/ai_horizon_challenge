import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from backend.database import get_session

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_llm():
    """
    LLM client: prefer OpenRouter (any model via OPENROUTER_MODEL / LLM_MODEL).
    Falls back to direct OpenAI when only OPENAI_API_KEY is set.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    model = (
        os.getenv("OPENROUTER_MODEL")
        or os.getenv("LLM_MODEL")
        or "google/gemini-2.0-flash-001"
    )
    temperature = float(os.getenv("LLM_TEMPERATURE", "0"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1500"))

    api_key = openrouter_key
    base_url = os.getenv("LLM_BASE_URL")

    if not api_key and openai_key and openai_key.startswith("sk-or"):
        api_key = openai_key
        base_url = base_url or OPENROUTER_BASE_URL

    if api_key and (openrouter_key or (openai_key and openai_key.startswith("sk-or")) or base_url == OPENROUTER_BASE_URL):
        base_url = base_url or OPENROUTER_BASE_URL
        extra = {}
        referer = os.getenv("OPENROUTER_HTTP_REFERER")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if referer or app_name:
            extra["default_headers"] = {
                **({"HTTP-Referer": referer} if referer else {}),
                **({"X-Title": app_name} if app_name else {}),
            }
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            base_url=base_url,
            **extra,
        )

    if openai_key:
        direct_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        return ChatOpenAI(
            model=direct_model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=openai_key,
        )

    raise RuntimeError(
        "No LLM API key configured. Set OPENROUTER_API_KEY or OPENAI_API_KEY in backend/.env"
    )
