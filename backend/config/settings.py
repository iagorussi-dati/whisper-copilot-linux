"""Config persistence — replicates Rust settings module."""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict


CONFIG_DIR = Path.home() / ".whisper-copilot-lite"
CONFIG_FILE = CONFIG_DIR / "settings.json"


@dataclass
class Participant:
    name: str = ""
    role: str = ""


@dataclass
class AppConfig:
    transcription_provider: str = "groq"
    diarization_provider: str = "local"
    groq_api_key: str = ""
    aws_profile: str = "poc_iago"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    whisper_model: str = "whisper-large-v3-turbo"
    language: str = "pt"
    chunk_seconds: int = 60
    diarization_threshold: float = 0.25
    mic_device_id: str = ""
    monitor_device_id: str = ""
    my_name: str = ""
    participants: list = field(default_factory=list)
    suggestions_target: str = ""  # nome do participante que recebe as sugestões
    custom_system_prompt: str = ""  # system prompt customizado para sugestões
    global_hotkey: str = ""  # tecla para SUPER+tecla global (ex: "F9")
    snapshot_hotkey: str = "D"  # tecla para SUPER+tecla snapshot
    response_mode: str = "short"  # "short", "full", "research"
    auto_response: bool = True  # True = responde sozinho, False = espera instrução
    many_context: str = ""  # contexto para modo 'muitas pessoas'
    participant_mode: str = "named"  # "named", "many", "none"
    user_identity: str = ""  # quem é o usuário (modo 'none')
    extra_context: str = ""  # contexto adicional do usuário

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        parts = d.pop("participants", [])
        cfg = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        cfg.participants = [Participant(**p) if isinstance(p, dict) else p for p in parts]
        return cfg


def load_config() -> AppConfig | None:
    if not CONFIG_FILE.exists():
        return None
    try:
        data = json.loads(CONFIG_FILE.read_text())
        return AppConfig.from_dict(data)
    except Exception:
        return None


def save_config(config: AppConfig):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config.to_dict(), indent=2))
