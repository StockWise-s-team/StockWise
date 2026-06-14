from dataclasses import dataclass, field
import json
import unicodedata
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
        """Audit LLM response for safety, forbidden promises, and disclaimers."""
        reviewed_answer = answer
        updated_flags = list(risk_flags)

        msg = self._normalized(user_message)
        if self._contains_any(msg, ["all-in", "all in", "mua ngay", "ban ngay", "bao gio mua"]):
            self._add_flag(updated_flags, "DIRECT_BUY_SELL_COMMAND")
        if self._contains_any(msg, ["dam bao", "cam ket", "chac chan"]):
            self._add_flag(updated_flags, "GUARANTEED_RETURN")

        normalized_answer = self._normalized(answer)
        has_disclaimer = self._contains_any(
            normalized_answer,
            ["luu y", "khuyen nghi", "rui ro", "tham khao", "disclaimer"],
        )

        if intent in {"STOCK_OVERVIEW", "PRICE_EXPLANATION", "PORTFOLIO_RISK", "CALCULATION"} and not has_disclaimer:
            reviewed_answer += (
                "\n\n*Thông tin trên chỉ mang tính chất tham khảo, không phải khuyến nghị đầu tư.*"
            )
            has_disclaimer = True
            self._add_flag(updated_flags, "MISSING_DISCLAIMER")

        if self._contains_any(
            normalized_answer,
            ["cam ket lai", "chac chan thang", "bao lo", "cam ket loi nhuan", "dam bao lai"],
        ):
            self._add_flag(updated_flags, "UNREALISTIC_GUARANTEE")

        is_safe = True
        if "UNREALISTIC_GUARANTEE" in updated_flags:
            is_safe = False
        if "DIRECT_BUY_SELL_COMMAND" in updated_flags and "MISSING_DISCLAIMER" in updated_flags:
            is_safe = False

        return RiskReviewResult(
            answer=reviewed_answer,
            risk_flags=updated_flags,
            is_safe=is_safe,
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
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        parsed = json.loads(content.strip())

        return RiskReviewResult(
            answer=parsed.get("answer", ""),
            risk_flags=parsed.get("risk_flags", []),
            is_safe=parsed.get("is_safe", True),
            has_disclaimer=parsed.get("has_disclaimer", False),
        )

    def _normalized(self, value: str) -> str:
        decomposed = unicodedata.normalize("NFD", value or "")
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").lower()

    def _contains_any(self, value: str, phrases: list[str]) -> bool:
        return any(phrase in value for phrase in phrases)

    def _add_flag(self, flags: list[str], flag: str) -> None:
        if flag not in flags:
            flags.append(flag)
