from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.config import settings


class LLMProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    GROQ = "groq"


def model_candidates(model_type: str) -> list[str]:
    if model_type == "analyst":
        return [settings.AI_ANALYST_PRIMARY_MODEL, settings.AI_ANALYST_FALLBACK_MODEL]
    if model_type == "safety":
        return [settings.AI_SAFETY_PRIMARY_MODEL, settings.AI_SAFETY_FALLBACK_MODEL]
    return [settings.AI_ROUTING_PRIMARY_MODEL, settings.AI_ROUTING_FALLBACK_MODEL]


def provider_for_model(model_name: str) -> LLMProvider:
    if "gemini" in model_name.lower():
        return LLMProvider.GEMINI
    return LLMProvider.OPENAI


def configured_providers_for_model_type(model_type: str = "routing") -> list[LLMProvider]:
    providers = []
    for model_name in model_candidates(model_type):
        provider = provider_for_model(model_name)
        has_credentials = (
            bool(settings.GEMINI_API_KEY)
            if provider == LLMProvider.GEMINI
            else bool(settings.OPENAI_API_KEY)
        )
        if has_credentials and provider not in providers:
            providers.append(provider)

    return providers or [LLMProvider.OPENAI]


def select_model(provider: LLMProvider, model_type: str) -> str:
    candidates = model_candidates(model_type)
    for model_name in candidates:
        if provider_for_model(model_name) == provider:
            return model_name
    return candidates[0]


def get_llm(provider: LLMProvider = LLMProvider.OPENAI, temperature: float = 0.7, model_type: str = "routing"):
    """Factory to get the appropriate LLM provider and model.

    Model order is configured per task as primary then fallback. The selected
    model determines which client to use so Gemini models do not get sent to
    an OpenAI-compatible endpoint, and vice versa.
    """
    model_name = select_model(provider, model_type)

    if provider == LLMProvider.GEMINI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            retries=0,
            request_timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
        )

    return ChatOpenAI(
        model=model_name,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=temperature,
        max_retries=1,
        timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
    )
