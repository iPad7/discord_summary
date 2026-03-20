from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.message import Message, MessageBatch


class MessageRepository(ABC):

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """
        메시지를 저장한다.
        봇이 감시 채널에서 메시지를 수신할 때마다 호출된다.
        """
        ...

    @abstractmethod
    async def get_by_discord_id(self, discord_msg_id: int) -> Message | None:
        """
        Discord 메시지 ID로 메시지를 조회한다.
        중복 저장 방지를 위해 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...

    @abstractmethod
    async def get_recent_by_channel(
        self, channel_id: int, since: datetime
    ) -> list[Message]:
        """
        특정 채널에서 since 이후 수신된 메시지 목록을 반환한다.
        AI 판단에 넘길 컨텍스트 버퍼를 구성할 때 호출된다.
        결과는 created_at 오름차순으로 정렬된다.
        """
        ...


class MessageBatchRepository(ABC):

    @abstractmethod
    async def save(self, batch: MessageBatch) -> MessageBatch:
        """
        메시지 배치를 저장한다.
        AI 판단 요청 직전에 컨텍스트 구성 정보를 기록할 때 호출된다.
        """
        ...

    @abstractmethod
    async def get_by_id(self, batch_id: int) -> MessageBatch | None:
        """
        배치 ID로 메시지 배치를 조회한다.
        AI 로그 조회 시 어떤 컨텍스트로 판단했는지 확인할 때 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...
