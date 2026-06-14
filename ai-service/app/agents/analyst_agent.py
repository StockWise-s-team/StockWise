import logging
from typing import Any, Dict
from app.agents.base_agent import BaseAgent
from app.models.llm_factory import configured_providers_for_model_type, get_llm, LLMProvider
from app.streaming.sse_manager import SSEManager

logger = logging.getLogger(__name__)

ANALYST_SYSTEM_PROMPT = """You are an expert financial analyst specializing in the Vietnamese stock market.

Your task is to synthesize the provided financial metrics, historical prices, ratios, news summaries, and company wiki entries into a highly professional, accurate, and structured analysis.

## Core Directives:
1. **Internal Chain of Thought (CoT):** You must reason step-by-step internally before generating your final response. Check the user's query, identify target stock symbols, scan the grounded data context for facts, reconcile any conflicting figures, and ensure strict compliance with safety constraints.
2. **Language Matching:** Dynamically detect the language of the user's query (e.g., Vietnamese, English). Respond in the EXACT same language (including accents and proper grammar for Vietnamese).
3. **Strict Fact Grounding:** Rely ONLY on the provided "Grounded data context". Do not invent, extrapolate, or assume any figures or dates not explicitly present. If information is missing, state it clearly.
4. **Professional Presentation:** Use clean, structured Markdown. Render headers, bullet points, and tables matching a premium terminal style.
5. **Regulatory Compliance:** Never under any circumstances promise specific returns, guarantee profits, or provide direct buy/sell recommendations.

Do NOT output your internal chain of thought or step-by-step thinking process in the final response. Output ONLY the final aggregated summary and financial analysis in the matching language.
"""

LLM_UNAVAILABLE_MESSAGE = "Xin lỗi, hệ thống AI tạm thời không khả dụng. Vui lòng thử lại sau."


def configured_providers() -> list[LLMProvider]:
    """Get active LLM providers for the analyst agent."""
    return configured_providers_for_model_type("analyst")


def get_streaming_llm(provider: LLMProvider):
    """Retrieve the streaming LLM instance for a provider."""
    # ChatOpenAI and ChatGoogleGenerativeAI natively support streaming through astream
    return get_llm(provider=provider, temperature=0.3, model_type="analyst")


class AnalystAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "analyst"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Handled by advisor_service generate_answer node
        return state

    async def generate(
        self,
        draft: str,
        tool_results: list[dict],
        sink: SSEManager,
    ) -> str:
        """Call LLM to generate final response from context draft,

        supporting provider failover and streaming.
        """
        last_error = None
        for provider in configured_providers():
            try:
                llm = get_streaming_llm(provider)
                response_text = ""
                # Stream tokens using langchain's astream
                async for chunk in llm.astream([("system", ANALYST_SYSTEM_PROMPT), ("human", draft)]):
                    token = chunk.content
                    if token:
                        response_text += token
                        await sink.emit_token(token)
                return response_text
            except Exception as exc:
                last_error = exc
                logger.warning("Streaming LLM provider %s failed: %s", provider.value, exc)
                continue

        # Fallback if all providers fail
        logger.error("All streaming LLM providers failed: %s", last_error)
        for token in LLM_UNAVAILABLE_MESSAGE.split(" "):
            await sink.emit_token(token + " ")
        return LLM_UNAVAILABLE_MESSAGE
