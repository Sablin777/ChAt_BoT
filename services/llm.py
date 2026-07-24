"""
Клиент для LLM через OpenRouter.

OpenRouter предоставляет OpenAI-совместимый API, поэтому
используем обычный пакет `openai`, просто указывая другой base_url.
Документация: https://openrouter.ai/docs
"""

import logging

from openai import AsyncOpenAI

from config import settings
from services.history import Message

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
    default_headers={
        # Необязательные, но рекомендуемые OpenRouter заголовки —
        # используются для отображения бота в их рейтингах/статистике.
        "HTTP-Referer": "https://github.com/",
        "X-Title": "Telegram LLM Bot",
    },
)


async def ask_llm(history: list[Message], user_message: str) -> str:
    """
    Отправляет историю диалога + новое сообщение пользователя в LLM
    через OpenRouter и возвращает текст ответа.
    """
    messages = [{"role": "system", "content": settings.system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await _client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
    except Exception:
        logger.exception("Ошибка при обращении к OpenRouter")
        raise

    choice = response.choices[0]
    return choice.message.content or ""
