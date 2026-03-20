from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Alert:
    ai_log_id: int
    sent_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
