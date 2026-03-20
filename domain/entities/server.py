from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Server:
    discord_id: int
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Channel:
    discord_id: int
    server_id: int
    name: str
    is_watched: bool = False
    created_at: datetime = field(default_factory=datetime.now)
