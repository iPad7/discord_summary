from abc import ABC, abstractmethod

from domain.entities.feedback import Feedback


class FeedbackRepository(ABC):

    @abstractmethod
    async def save(self, feedback: Feedback) -> Feedback:
        """
        AI 판단에 대한 피드백을 저장한다.
        대시보드 품질 검증 페이지에서 맞음/틀림 평가 시 호출된다.
        ai_log_id당 하나의 피드백만 허용된다.
        """
        ...

    @abstractmethod
    async def get_by_ai_log_id(self, ai_log_id: int) -> Feedback | None:
        """
        AI 로그 ID로 피드백을 조회한다.
        대시보드에서 해당 판단에 이미 피드백이 달렸는지 확인할 때 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...
