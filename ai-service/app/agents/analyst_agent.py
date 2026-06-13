import logging
from typing import Any, Dict
from app.agents.base_agent import BaseAgent
from app.models.llm_factory import configured_providers_for_model_type, get_llm, LLMProvider
from app.streaming.sse_manager import SSEManager

logger = logging.getLogger(__name__)


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
                async for chunk in llm.astream([("human", draft)]):
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
        for token in draft.split(" "):
            await sink.emit_token(token + " ")
        return draft
