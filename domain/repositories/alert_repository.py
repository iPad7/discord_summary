from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.alert import Alert


class AlertRepository(ABC):

    @abstractmethod
    async def save(self, alert: Alert) -> Alert:
        """
        알림 발송 기록을 저장한다.
        Discord DM 발송 성공 직후 호출된다.
        """
        ...

    @abstractmethod
    async def exists_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> bool:
        """
        특정 채널에서 since 이후 발송된 알림이 있는지 확인한다.
        중복 알림 방지를 위한 쿨다운 체크 시 호출된다.
        Alert → AILog → MessageBatch → Message 경로로 JOIN하여
        channel_id와 sent_at 조건으로 필터링한다.
        """
        ...
