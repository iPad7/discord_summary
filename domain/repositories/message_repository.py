from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.message import Message, MessageBatch


class MessageRepository(ABC):
    @abstractmethod
    async def save(self, message: Message) -> Message: ...

    @abstractmethod
    async def get_by_discord_id(self, discord_msg_id: int) -> Message | None: ...

    # 쿨다운·버퍼 판단에 사용: 특정 채널의 최근 N분 메시지 목록
    @abstractmethod
    async def get_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> list[Message]: ...


class MessageBatchRepository(ABC):
    @abstractmethod
    async def save(self, batch: MessageBatch) -> MessageBatch: ...

    @abstractmethod
    async def get_by_id(self, batch_id: int) -> MessageBatch | None: ...
