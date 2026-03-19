from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel


class DiscordConfig(BaseModel):
    bot_token: str
    my_user_id: int


class OllamaConfig(BaseModel):
    model: str = "ax4light"
    host: str = "http://localhost:11434"


class BufferConfig(BaseModel):
    max_minutes: int = 30
    max_messages: int = 30


class CooldownConfig(BaseModel):
    minutes: int = 30


class DatabaseConfig(BaseModel):
    url: str


class AppConfig(BaseModel):
    discord: DiscordConfig
    ollama: OllamaConfig
    buffer: BufferConfig
    cooldown: CooldownConfig
    database: DatabaseConfig


@lru_cache
def get_config() -> AppConfig:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
