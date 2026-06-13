from dataclasses import dataclass, field
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


@dataclass
class RiskReviewResult:
    """Dataclass holding safety and compliance audit results."""
    answer: str
    risk_flags: list[str] = field(default_factory=list)
    is_safe: bool = True
    has_disclaimer: bool = False


class RiskManagerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "risk_manager"

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Handled by sanitize_answer in AdvisorService, which calls review() below.
        return state

    def review(
        self,
        answer: str,
        user_message: str,
        intent: str,
        risk_flags: list[str],
    ) -> RiskReviewResult:
        """Audit LLM response to check for safety, forbidden keywords, and add required disclaimers."""
        reviewed_answer = answer
        updated_flags = list(risk_flags)

        # 1. Check user message for direct buy/sell commands or guaranteed returns
        msg = user_message.lower()
        if "all-in" in msg or "all in" in msg or "mua ngay" in msg or "bán ngay" in msg or "bao gio mua" in msg:
            if "DIRECT_BUY_SELL_COMMAND" not in updated_flags:
                updated_flags.append("DIRECT_BUY_SELL_COMMAND")
        if "dam bao" in msg or "đảm bảo" in msg or "cam ket" in msg or "cam kết" in msg or "chac chan" in msg or "chắc chắn" in msg:
            if "GUARANTEED_RETURN" not in updated_flags:
                updated_flags.append("GUARANTEED_RETURN")

        # 2. Check for investment advice disclaimer
        has_disclaimer = (
            "lưu ý" in answer.lower() or
            "khuyến nghị" in answer.lower() or
            "rủi ro" in answer.lower() or
            "disclaimer" in answer.lower()
        )

        if intent in {"STOCK_OVERVIEW", "PRICE_EXPLANATION", "PORTFOLIO_RISK", "CALCULATION"} and not has_disclaimer:
            reviewed_answer += (
                "\n\n*Thông tin trên chỉ mang tính chất tham khảo, không phải khuyến nghị đầu tư.*"
            )
            has_disclaimer = True
            if "MISSING_DISCLAIMER" not in updated_flags:
                updated_flags.append("MISSING_DISCLAIMER")

        # 3. Simple safety checks in answer
        guarantee_words = ["cam kết lãi", "chắc chắn thắng", "bao lỗ", "cam kết lợi nhuận"]
        if any(word in answer.lower() for word in guarantee_words):
            if "UNREALISTIC_GUARANTEE" not in updated_flags:
                updated_flags.append("UNREALISTIC_GUARANTEE")

        return RiskReviewResult(
            answer=reviewed_answer,
            risk_flags=updated_flags,
            is_safe=True,
            has_disclaimer=has_disclaimer,
        )

    def sanitize(
        self,
        answer: str,
        user_message: str,
        intent: str,
    ) -> tuple[str, list[str], bool]:
        """Legacy sanitize method used in unit tests."""
        res = self.review(answer, user_message, intent, [])
        return res.answer, res.risk_flags, res.has_disclaimer

    async def review_with_llm(self, llm: Any, messages: list[tuple[str, str]]) -> RiskReviewResult:
        """Call LLM with given messages to obtain a structured risk review."""
        import json
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        # Clean markdown codeblock wrappers if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        parsed = json.loads(content)
        
        return RiskReviewResult(
            answer=parsed.get("answer", ""),
            risk_flags=parsed.get("risk_flags", []),
            is_safe=parsed.get("is_safe", True),
            has_disclaimer=parsed.get("has_disclaimer", False),
        )
