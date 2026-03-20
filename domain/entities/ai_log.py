from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AILog:
    batch_id: int
    answer: bool       # True = 답변 필요, False = 불필요
    reason: str        # AI가 판단한 근거
    latency_ms: int    # AI 응답 시간 (밀리초)
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
