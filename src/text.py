import logging

from aiogram import Router
from aiogram.types import Message

from services.history import add_message, get_history
from services.llm import ask_llm

logger = logging.getLogger(__name__)

router = Router(name="text")


@router.message()
async def handle_text(message: Message) -> None:
    if not message.text:
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    history = get_history(message.chat.id)
    try:
        reply = await ask_llm(history, message.text)
    except Exception:
        logger.exception("Не удалось получить ответ от LLM")
        await message.answer(
            "Извините, не получилось получить ответ от модели. Попробуйте ещё раз."
        )
        return

    add_message(message.chat.id, "user", message.text)
    add_message(message.chat.id, "assistant", reply)

    await message.answer(reply)
