from abc import ABC, abstractmethod

from domain.entities.feedback import Feedback


class FeedbackRepository(ABC):
    @abstractmethod
    async def save(self, feedback: Feedback) -> Feedback: ...

    @abstractmethod
    async def get_by_ai_log_id(self, ai_log_id: int) -> Feedback | None: ...
