import io
import logging

from aiogram import Router, F
from aiogram.types import Message

from src._shared import respond_to_transcript
from services.transcription import transcribe_video

logger = logging.getLogger(__name__)

router = Router(name="video")

# F.video       — обычное видео, отправленное как файл/видеосообщение
# F.video_note  — видео-кружочек (круглое видео в Telegram)
_VIDEO_FILTER = F.video | F.video_note


@router.message(_VIDEO_FILTER)
async def handle_video(message: Message) -> None:
    await message.bot.send_chat_action(message.chat.id, "typing")

    video_obj = message.video or message.video_note
    file = await message.bot.get_file(video_obj.file_id)

    buffer = io.BytesIO()
    await message.bot.download_file(file.file_path, destination=buffer)
    mp4_bytes = buffer.getvalue()

    try:
        transcript = await transcribe_video(mp4_bytes)
    except Exception:
        logger.exception("Не удалось распознать речь в видеосообщении")
        await message.answer(
            "Не получилось распознать речь в видео. Попробуйте ещё раз."
        )
        return

    await respond_to_transcript(message, transcript)
