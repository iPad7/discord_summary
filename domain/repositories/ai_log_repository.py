from abc import ABC, abstractmethod

from domain.entities.ai_log import AILog


class AILogRepository(ABC):

    @abstractmethod
    async def save(self, ai_log: AILog) -> AILog:
        """
        AI 판단 결과를 저장한다.
        Ollama로부터 YES/NO 응답을 받은 직후 호출된다.
        """
        ...

    @abstractmethod
    async def get_by_id(self, ai_log_id: int) -> AILog | None:
        """
        AI 로그 ID로 판단 결과를 조회한다.
        대시보드에서 특정 판단 결과 상세 조회 시 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...

    @abstractmethod
    async def get_recent(self, limit: int = 50) -> list[AILog]:
        """
        최근 AI 판단 결과 목록을 반환한다.
        대시보드 AI 로그 페이지의 전체 목록 조회 시 호출된다.
        결과는 created_at 내림차순으로 정렬된다.
        """
        ...

    @abstractmethod
    async def get_recent_by_channel(
        self, channel_id: int, limit: int = 50
    ) -> list[AILog]:
        """
        특정 채널의 최근 AI 판단 결과 목록을 반환한다.
        대시보드에서 채널별 판단 이력 필터링 시 호출된다.
        MessageBatch → Message 경로로 JOIN하여 channel_id를 필터링한다.
        결과는 created_at 내림차순으로 정렬된다.
        """
        ...
