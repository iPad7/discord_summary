"""
AILog Repository의 PostgreSQL 구현체.
get_recent_by_channel()은 AILog → MessageBatch → Message 경로로
JOIN하여 channel_id를 필터링한다.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.ai_log import AILog
from domain.repositories.ai_log_repository import AILogRepository
from infrastructure.db.mapper import ai_log_to_entity, ai_log_to_model
from infrastructure.db.models import AILog as AILogModel
from infrastructure.db.models import Message as MessageModel
from infrastructure.db.models import MessageBatch as MessageBatchModel


class PostgresAILogRepository(AILogRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ai_log: AILog) -> AILog:
        model = ai_log_to_model(ai_log)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return ai_log_to_entity(model)

    async def get_by_id(self, ai_log_id: int) -> AILog | None:
        result = await self._session.execute(
            select(AILogModel).where(AILogModel.id == ai_log_id)
        )
        row = result.scalar_one_or_none()
        return ai_log_to_entity(row) if row else None

    async def get_recent(self, limit: int = 50) -> list[AILog]:
        result = await self._session.execute(
            select(AILogModel)
            .order_by(AILogModel.created_at.desc())
            .limit(limit)
        )
        return [ai_log_to_entity(r) for r in result.scalars().all()]

    async def get_recent_by_channel(
        self, channel_id: int, limit: int = 50
    ) -> list[AILog]:
        """
        AILog → MessageBatch → Message 순으로 JOIN하여
        트리거 메시지의 channel_id로 필터링한다.
        """
        result = await self._session.execute(
            select(AILogModel)
            .join(MessageBatchModel, AILogModel.batch_id == MessageBatchModel.id)
            .join(MessageModel, MessageBatchModel.trigger_msg_id == MessageModel.id)
            .where(MessageModel.channel_id == channel_id)
            .order_by(AILogModel.created_at.desc())
            .limit(limit)
        )
        return [ai_log_to_entity(r) for r in result.scalars().all()]
