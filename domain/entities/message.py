from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    discord_msg_id: int
    channel_id: int
    author_id: int
    author_name: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


@dataclass
class MessageBatch:
    trigger_msg_id: int
    context_msg_ids: list[int]
    context_text: str
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
