import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Переменная окружения {name} не задана. "
            f"Скопируйте .env.example в .env и заполните значения."
        )
    return value


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    openrouter_api_key: str
    openrouter_model: str
    hf_token: str
    hf_asr_model: str
    system_prompt: str
    history_limit: int


def load_settings() -> Settings:
    return Settings(
        telegram_token=_require("TELEGRAM_BOT_TOKEN"),
        openrouter_api_key=_require("OPENROUTER_API_KEY"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        hf_token=_require("HF_TOKEN"),
        hf_asr_model=os.getenv("HF_ASR_MODEL", "openai/whisper-large-v3"),
        system_prompt=os.getenv(
            "SYSTEM_PROMPT",
            "Ты — дружелюбный ассистент в Telegram. Отвечай кратко и по делу.",
        ),
        history_limit=int(os.getenv("HISTORY_LIMIT", "20")),
    )


settings = load_settings()
