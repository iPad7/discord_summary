from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.alert import Alert


class AlertRepository(ABC):
    @abstractmethod
    async def save(self, alert: Alert) -> Alert: ...

    # 쿨다운 확인: 해당 채널에서 since 이후 발송된 알림이 있으면 True
    @abstractmethod
    async def exists_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> bool: ...
