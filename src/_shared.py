"""
Общая логика для обработчиков, которые получают распознанный текст
(из голосового, видео или видео-кружочка) и должны отправить его в LLM.

Вынесено отдельно, чтобы handlers/voice.py и handlers/video.py не
дублировали один и тот же код "показать распознанный текст → спросить
LLM → сохранить историю → ответить".
"""

import logging

from aiogram.types import Message

from services.history import add_message, get_history
from services.llm import ask_llm

logger = logging.getLogger(__name__)


async def respond_to_transcript(message: Message, transcript: str) -> None:
    """Показывает пользователю распознанный текст и отвечает через LLM."""
    if not transcript:
        await message.answer("Не удалось разобрать речь в сообщении 🤔")
        return

    await message.answer(f"🗣 Распознано: «{transcript}»")

    history = get_history(message.chat.id)
    try:
        reply = await ask_llm(history, transcript)
    except Exception:
        logger.exception("Не удалось получить ответ от LLM")
        await message.answer(
            "Извините, не получилось получить ответ от модели. Попробуйте ещё раз."
        )
        return

    add_message(message.chat.id, "user", transcript)
    add_message(message.chat.id, "assistant", reply)

    await message.answer(reply)
