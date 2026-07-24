from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from services.history import reset_history

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я бот с подключённой LLM. Пиши мне текстом или отправляй "
        "голосовые сообщения — я их распознаю и отвечу.\n\n"
        "Команды:\n"
        "/help — справка\n"
        "/reset — очистить историю диалога"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Что я умею:\n"
        "• Отвечать на текстовые сообщения через LLM (OpenRouter)\n"
        "• Распознавать голосовые сообщения (Hugging Face Whisper) "
        "и отвечать на их содержание\n"
        "• Распознавать речь в видео и видео-кружочках — так же, "
        "как в голосовых\n\n"
        "/reset — начать диалог заново (очистить память)"
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    reset_history(message.chat.id)
    await message.answer("История диалога очищена. Начнём заново 🙂")
