from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.config import settings


class LLMProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


def get_llm(provider: LLMProvider = LLMProvider.GEMINI, temperature: float = 0.7):
    if provider == LLMProvider.GEMINI:
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
