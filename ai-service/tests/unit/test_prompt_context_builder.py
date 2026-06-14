from app.services.prompt_context_builder import PromptContextBuilder


def test_grounded_builder_does_not_invent_missing_market_data():
    answer = PromptContextBuilder().build_answer("STOCK_OVERVIEW", ["FPT"], [])
    assert "Chưa đủ dữ liệu" in answer
    assert "giá đóng cửa" not in answer


def test_builder_includes_recent_conversation_history_for_followups():
    answer = PromptContextBuilder().build_answer(
        "STOCK_OVERVIEW",
        ["FPT"],
        [],
        user_message="So what changed?",
        conversation_history=[
            {"role": "user", "content": "Review FPT first."},
            {"role": "assistant", "content": "FPT has strong software services exposure."},
        ],
    )

    assert "Conversation history for follow-up context" in answer
    assert "User: Review FPT first." in answer
    assert "Assistant: FPT has strong software services exposure." in answer
    assert "Current user question: So what changed?" in answer
