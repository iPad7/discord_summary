"""
Alert Repository의 PostgreSQL 구현체.
exists_recent_by_channel()은 Alert → AILog → MessageBatch → Message 경로로
JOIN하여 channel_id와 sent_at을 필터링한다.
"""

from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.alert import Alert
from domain.repositories.alert_repository import AlertRepository
from infrastructure.db.mapper import alert_to_entity, alert_to_model
from infrastructure.db.models import AILog as AILogModel
from infrastructure.db.models import Alert as AlertModel
from infrastructure.db.models import Message as MessageModel
from infrastructure.db.models import MessageBatch as MessageBatchModel


class PostgresAlertRepository(AlertRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, alert: Alert) -> Alert:
        model = alert_to_model(alert)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return alert_to_entity(model)

    async def exists_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> bool:
        """
        Alert → AILog → MessageBatch → Message 순으로 JOIN하여
        sent_at >= since이고 트리거 메시지의 channel_id가 일치하는
        알림이 존재하면 True를 반환한다.
        """
        stmt = select(
            exists()
            .where(AlertModel.sent_at >= since)
            .where(AlertModel.ai_log_id == AILogModel.id)
            .where(AILogModel.batch_id == MessageBatchModel.id)
            .where(MessageBatchModel.trigger_msg_id == MessageModel.id)
            .where(MessageModel.channel_id == channel_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar()
