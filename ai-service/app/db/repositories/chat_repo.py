from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_session(self, session_id: str, user_id: str, title: str | None = None) -> ChatSession:
        result = await self.session.execute(select(ChatSession).where(ChatSession.id == UUID(session_id)))
        existing = result.scalar_one_or_none()
        if existing:
            if existing.user_id != user_id:
                raise PermissionError("Chat session does not belong to the current user.")
            return existing
        chat_session = ChatSession(id=UUID(session_id), user_id=user_id, title=title)
        self.session.add(chat_session)
        await self.session.commit()
        return chat_session

    async def get_session(self, session_id: str, user_id: str) -> ChatSession | None:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == UUID(session_id), ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        session_update = await self.session.execute(
            update(ChatSession)
            .where(ChatSession.id == UUID(session_id), ChatSession.user_id == user_id)
            .values(updated_at=func.now())
        )
        if not session_update.rowcount:
            raise PermissionError("Chat session does not belong to the current user.")
        message = ChatMessage(
            session_id=UUID(session_id),
            role=role,
            content=content,
            message_metadata=metadata or {},
        )
        self.session.add(message)
        await self.session.commit()
        return message

    async def load_history(self, session_id: str, limit: int) -> list[dict[str, str]]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == UUID(session_id))
            .order_by(ChatMessage.created_at.desc())
            .limit(max(1, min(limit, 50)))
        )
        messages = list(reversed(result.scalars().all()))
        return [{"role": message.role, "content": message.content} for message in messages]

    async def load_history_for_user(self, session_id: str, user_id: str, limit: int) -> list[dict[str, str]]:
        if not await self.get_session(session_id, user_id):
            raise PermissionError("Chat session does not belong to the current user.")
        return await self.load_history(session_id, limit)

    async def list_messages_for_user(self, session_id: str, user_id: str) -> list[ChatMessage]:
        if not await self.get_session(session_id, user_id):
            raise PermissionError("Chat session does not belong to the current user.")
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == UUID(session_id))
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_sessions(self, user_id: str) -> list[ChatSession]:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        result = await self.session.execute(
            delete(ChatSession).where(ChatSession.id == UUID(session_id), ChatSession.user_id == user_id)
        )
        await self.session.commit()
        return bool(result.rowcount)
