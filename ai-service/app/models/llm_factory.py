from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from app.config import settings


class LLMProvider(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"


def get_llm(provider: LLMProvider = LLMProvider.GROQ, temperature: float = 0.0):
    """Get LLM instance.

    Args:
        provider: LLM provider (groq, gemini, openai).
        temperature: Model temperature (0.0 for deterministic routing).

    Returns:
        LangChain chat model instance.
    """
    if provider == LLMProvider.GROQ:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.GROQ_API_KEY,
            temperature=temperature,
        )
    elif provider == LLMProvider.GEMINI:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        return ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )


def get_streaming_llm(provider: LLMProvider = LLMProvider.GROQ, temperature: float = 0.7):
    """Get LLM instance with streaming enabled.

    Args:
        provider: LLM provider.
        temperature: Model temperature (0.7 for creative responses).

    Returns:
        LangChain chat model instance with streaming.
    """
    if provider == LLMProvider.GROQ:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.GROQ_API_KEY,
            temperature=temperature,
        )
    elif provider == LLMProvider.GEMINI:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
        )
    else:
        return ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
            streaming=True,
        )
