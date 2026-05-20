from pydantic import ValidationError
import pytest

from app.models.schemas import ChatRequest


class TestChatRequest:
    """Unit tests for ChatRequest schema validation."""

    def test_valid_request(self):
        """Valid request with message only."""
        req = ChatRequest(message="Đánh giá FPT hôm nay")
        assert req.message == "Đánh giá FPT hôm nay"
        assert req.session_id is None

    def test_valid_request_with_session(self):
        """Valid request with session_id."""
        req = ChatRequest(
            message="Test",
            session_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert req.session_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_empty_message_rejected(self):
        """Empty message raises validation error."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_message_too_long(self):
        """Message over 2000 chars raises validation error."""
        with pytest.raises(ValidationError):
            ChatRequest(message="a" * 2001)

    def test_invalid_uuid_rejected(self):
        """Invalid UUID in session_id raises validation error."""
        with pytest.raises(ValidationError):
            ChatRequest(message="Test", session_id="not-a-uuid")
