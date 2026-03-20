from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Feedback:
    ai_log_id: int
    is_correct: bool        # 사용자가 AI 판단이 맞았다고 평가하면 True
    note: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
