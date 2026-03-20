"""
Feedback Repository의 PostgreSQL 구현체.
ai_log_id당 하나의 피드백만 허용되며,
이미 존재하는 경우 save() 시 DB 제약 위반 에러가 발생한다.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.feedback import Feedback
from domain.repositories.feedback_repository import FeedbackRepository
from infrastructure.db.mapper import feedback_to_entity, feedback_to_model
from infrastructure.db.models import Feedback as FeedbackModel


class PostgresFeedbackRepository(FeedbackRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, feedback: Feedback) -> Feedback:
        model = feedback_to_model(feedback)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return feedback_to_entity(model)

    async def get_by_ai_log_id(self, ai_log_id: int) -> Feedback | None:
        result = await self._session.execute(
            select(FeedbackModel).where(FeedbackModel.ai_log_id == ai_log_id)
        )
        row = result.scalar_one_or_none()
        return feedback_to_entity(row) if row else None
