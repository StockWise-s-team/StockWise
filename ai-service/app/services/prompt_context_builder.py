from decimal import Decimal
from typing import Any

from app.models.schemas import ToolResult


def _number(value: Any) -> str:
    if isinstance(value, (int, float, Decimal)):
        return f"{float(value):,.2f}"
    return str(value)


class PromptContextBuilder:
    def build_answer(
        self,
        intent: str,
        symbols: list[str],
        results: list[ToolResult],
        user_message: str = "",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        context_sections = self._conversation_context(user_message, conversation_history or [])
        if intent == "GREETING":
            return "Xin chào. Tôi có thể hỗ trợ tra cứu dữ liệu cổ phiếu Việt Nam, danh mục, biểu đồ và phép tính lãi lỗ."
        if intent == "OUT_OF_SCOPE":
            return "Tôi chỉ hỗ trợ các câu hỏi liên quan đến thị trường chứng khoán Việt Nam và danh mục đầu tư."

        successful = {result.tool_name: result for result in results if result.success}
        missing = [result.error_message for result in results if not result.success and result.error_message]
        sections: list[str] = []
        market = successful.get("market_data")
        if market:
            latest = market.data["latest_price"]
            sections.append(
                f"Dữ liệu thị trường {latest['symbol']}: giá đóng cửa gần nhất {_number(latest['close'])} "
                f"vào ngày {latest['trade_date']}; khối lượng {_number(latest['volume'])}."
            )
            ratios = market.data.get("financial_ratios", [])
            if ratios:
                ratio = ratios[0]
                sections.append(
                    f"Chỉ số tài chính kỳ {ratio.get('period')}: P/E {_number(ratio.get('pe_ratio'))}, "
                    f"P/B {_number(ratio.get('pb_ratio'))}, EPS {_number(ratio.get('eps'))}."
                )
        wiki = successful.get("wiki_reader")
        if wiki:
            summary = wiki.data.get("wiki_data", {}).get("summary")
            if summary:
                sections.append(f"Bối cảnh doanh nghiệp: {summary}")
        news = successful.get("news_search")
        if news:
            titles = [article["title"] for article in news.data.get("articles", [])]
            sections.append("Tin gần đây đã lưu trong hệ thống: " + "; ".join(titles))
        portfolio = successful.get("portfolio_reader")
        if portfolio:
            sections.append(
                f"Danh mục hiện có {len(portfolio.data.get('holdings', []))} mã, "
                f"giá trị theo dữ liệu gần nhất {_number(portfolio.data.get('total_value', 0))}, "
                f"lãi/lỗ chưa thực hiện {_number(portfolio.data.get('unrealized_pnl', 0))}."
            )
        tracked = successful.get("tracked_symbols_reader")
        if tracked:
            user_symbols = tracked.data.get("user_tracked_symbols", [])
            system_symbols = tracked.data.get("system_tracked_symbols", [])
            active_symbols = tracked.data.get("tracked_symbols", [])
            scope = tracked.data.get("selection_scope")
            if scope == "user":
                sections.append(
                    "User tracked symbols: "
                    + ", ".join(user_symbols)
                    + ". System/data-pipeline tracked symbols: "
                    + ", ".join(system_symbols)
                    + "."
                )
            else:
                sections.append(
                    "The user has no custom tracked-symbol selection. System/data-pipeline tracked symbols: "
                    + ", ".join(active_symbols)
                    + "."
                )
        calculation = successful.get("calculator")
        if calculation:
            sections.append(f"Kết quả phép tính {calculation.data['operation']}: {_number(calculation.data['result'])}.")
        charting = successful.get("charting")
        if charting:
            sections.append(
                f"Đã tạo dữ liệu biểu đồ {charting.data['symbol']} với "
                f"{len(charting.data.get('series', []))} điểm OHLCV đã kiểm chứng."
            )
        if missing:
            sections.append("Dữ liệu còn thiếu: " + " ".join(missing))
        if not sections:
            symbol_text = ", ".join(symbols) or "mã được hỏi"
            sections.append(f"Chưa đủ dữ liệu đã kiểm chứng để trả lời về {symbol_text}.")
        return self._join_sections(context_sections, "\n\n".join(sections))

    def _conversation_context(self, user_message: str, history: list[dict[str, str]]) -> list[str]:
        sections: list[str] = []
        if history:
            lines: list[str] = []
            for item in history[-8:]:
                role = "User" if item.get("role") == "user" else "Assistant"
                content = str(item.get("content", "")).strip()
                if content:
                    lines.append(f"{role}: {content}")
            if lines:
                sections.append(
                    "Conversation history for follow-up context. Use it only when relevant and do not repeat it verbatim:\n"
                    + "\n".join(lines)
                )
        if user_message:
            sections.append(f"Current user question: {user_message}")
        return sections

    def _join_sections(self, context_sections: list[str], answer_context: str) -> str:
        if not context_sections:
            return answer_context
        return "\n\n".join([*context_sections, "Grounded data context:\n" + answer_context])
