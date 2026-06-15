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
            return (
                "Tôi chỉ hỗ trợ các câu hỏi liên quan đến thị trường chứng khoán Việt Nam và danh mục đầu tư. "
                "Để so sánh, phân tích hoặc tra cứu cổ phiếu, vui lòng cung cấp mã cổ phiếu cụ thể (Ví dụ: FPT, ACB, HPG) "
                "để tôi có thể truy xuất và đối chiếu dữ liệu chính xác cho bạn."
            )

        def get_successful_results(tool_name: str) -> list[ToolResult]:
            return [r for r in results if r.tool_name == tool_name and r.success]

        def get_first_successful_result(tool_name: str) -> ToolResult | None:
            found = get_successful_results(tool_name)
            return found[0] if found else None

        missing = [result.error_message for result in results if not result.success and result.error_message]
        sections: list[str] = []

        market_results = get_successful_results("market_data")
        for market in market_results:
            latest = market.data.get("latest_price")
            if latest:
                sections.append(
                    f"Dữ liệu thị trường {latest['symbol']}: giá đóng cửa gần nhất {_number(latest['close'])} "
                    f"vào ngày {latest['trade_date']}; khối lượng {_number(latest['volume'])}."
                )
                ratios = market.data.get("financial_ratios", [])
                if ratios:
                    ratio = ratios[0]
                    sections.append(
                        f"Chỉ số tài chính {latest['symbol']} kỳ {ratio.get('period')}: P/E {_number(ratio.get('pe_ratio'))}, "
                        f"P/B {_number(ratio.get('pb_ratio'))}, EPS {_number(ratio.get('eps'))}."
                    )

        wiki_results = get_successful_results("wiki_reader")
        for wiki in wiki_results:
            summary = wiki.data.get("wiki_data", {}).get("summary")
            symbol = wiki.data.get("symbol") or ""
            if summary:
                sections.append(f"Bối cảnh doanh nghiệp {symbol}: {summary}")

        news_results = get_successful_results("news_search")
        for news in news_results:
            symbol = news.data.get("symbol") or ""
            titles = [article["title"] for article in news.data.get("articles", [])]
            if titles:
                sections.append(f"Tin gần đây đã lưu trong hệ thống cho {symbol}: " + "; ".join(titles))

        portfolio = get_first_successful_result("portfolio_reader")
        if portfolio:
            sections.append(
                f"Danh mục hiện có {len(portfolio.data.get('holdings', []))} mã, "
                f"giá trị theo dữ liệu gần nhất {_number(portfolio.data.get('total_value', 0))}, "
                f"lãi/lỗ chưa thực hiện {_number(portfolio.data.get('unrealized_pnl', 0))}."
            )

        tracked = get_first_successful_result("tracked_symbols_reader")
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

        calculation = get_first_successful_result("calculator")
        if calculation:
            sections.append(f"Kết quả phép tính {calculation.data['operation']}: {_number(calculation.data['result'])}.")

        charting_results = get_successful_results("charting")
        for charting in charting_results:
            symbol = charting.data.get("symbol") or ""
            sections.append(
                f"Đã tạo dữ liệu biểu đồ {symbol} với "
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
