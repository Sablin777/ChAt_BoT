import io
import logging

from aiogram import Router, F
from aiogram.types import Message

from src._shared import respond_to_transcript
from services.transcription import transcribe_voice

logger = logging.getLogger(__name__)

router = Router(name="voice")


@router.message(F.voice)
async def handle_voice(message: Message) -> None:
    await message.bot.send_chat_action(message.chat.id, "typing")

    voice = message.voice
    file = await message.bot.get_file(voice.file_id)

    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, destination=buffer)
    ogg_bytes = buffer.getvalue()

    try:
        transcript = await transcribe_voice(ogg_bytes)
    except Exception:
        logger.exception("Не удалось распознать голосовое сообщение")
        await message.answer(
            "Не получилось распознать голосовое сообщение. Попробуйте ещё раз."
        )
        return

    await respond_to_transcript(message, transcript)
