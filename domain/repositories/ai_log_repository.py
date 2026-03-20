from abc import ABC, abstractmethod

from domain.entities.ai_log import AILog


class AILogRepository(ABC):
    @abstractmethod
    async def save(self, ai_log: AILog) -> AILog: ...

    @abstractmethod
    async def get_by_id(self, ai_log_id: int) -> AILog | None: ...

    @abstractmethod
    async def get_recent(self, limit: int = 50) -> list[AILog]: ...
