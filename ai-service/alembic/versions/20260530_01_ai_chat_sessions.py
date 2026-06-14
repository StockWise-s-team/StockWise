"""add AI advisor chat sessions

Revision ID: 20260530_01
Revises:
Create Date: 2026-05-30
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260530_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_chat_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ai_chat_sessions_user_updated", "ai_chat_sessions", ["user_id", "updated_at"])
    op.create_table(
        "ai_chat_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant')"),
        sa.ForeignKeyConstraint(["session_id"], ["ai_chat_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ai_chat_messages_session_created", "ai_chat_messages", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_ai_chat_messages_session_created", table_name="ai_chat_messages")
    op.drop_table("ai_chat_messages")
    op.drop_index("idx_ai_chat_sessions_user_updated", table_name="ai_chat_sessions")
    op.drop_table("ai_chat_sessions")
