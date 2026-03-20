"""
Message, MessageBatch Repository의 PostgreSQL 구현체.
Message는 discord_msg_id UNIQUE 제약이 있어 중복 저장을 방지한다.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.message import Message, MessageBatch
from domain.repositories.message_repository import (
    MessageBatchRepository,
    MessageRepository,
)
from infrastructure.db.mapper import (
    batch_to_entity,
    batch_to_model,
    message_to_entity,
    message_to_model,
)
from infrastructure.db.models import Message as MessageModel
from infrastructure.db.models import MessageBatch as MessageBatchModel


class PostgresMessageRepository(MessageRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, message: Message) -> Message:
        model = message_to_model(message)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return message_to_entity(model)

    async def get_by_discord_id(self, discord_msg_id: int) -> Message | None:
        result = await self._session.execute(
            select(MessageModel).where(MessageModel.discord_msg_id == discord_msg_id)
        )
        row = result.scalar_one_or_none()
        return message_to_entity(row) if row else None

    async def get_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> list[Message]:
        """
        created_at 오름차순으로 반환하여 시간 순서대로 컨텍스트를 구성할 수 있게 한다.
        """
        result = await self._session.execute(
            select(MessageModel)
            .where(
                MessageModel.channel_id == channel_id,
                MessageModel.created_at >= since,
            )
            .order_by(MessageModel.created_at.asc())
        )
        return [message_to_entity(r) for r in result.scalars().all()]


class PostgresMessageBatchRepository(MessageBatchRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, batch: MessageBatch) -> MessageBatch:
        model = batch_to_model(batch)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return batch_to_entity(model)

    async def get_by_id(self, batch_id: int) -> MessageBatch | None:
        result = await self._session.execute(
            select(MessageBatchModel).where(MessageBatchModel.id == batch_id)
        )
        row = result.scalar_one_or_none()
        return batch_to_entity(row) if row else None
