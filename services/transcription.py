"""
Транскрибирование голоса через Hugging Face Inference API.

Поддерживаются:
- голосовые сообщения Telegram (OGG/Opus)
- видеосообщения и видео-кружочки Telegram (MP4 — звуковая дорожка
  извлекается из видео перед распознаванием)

Модель распознавания речи (Whisper) надёжнее всего работает с WAV,
поэтому перед отправкой в HF Inference API любой входной формат
конвертируется в WAV через ffmpeg (обёртка pydub).

Запрос отправляется напрямую через `requests` (а не через
`huggingface_hub.InferenceClient`), т.к. клиент не выставляет заголовок
Content-Type для сырых байт, а новый роутер Hugging Face
(router.huggingface.co) требует его явно — без него сервер отвечает
400 Bad Request "Content type None not supported".

Требования:
- Установленный в системе ffmpeg (`apt install ffmpeg` / `brew install ffmpeg`)
- Токен Hugging Face с правом "Make calls to Inference Providers"
"""

import asyncio
import io
import json
import logging

import requests
from pydub import AudioSegment

from config import settings

logger = logging.getLogger(__name__)

_API_URL_TEMPLATE = "https://router.huggingface.co/hf-inference/models/{model}"


def _convert_to_wav(source_bytes: bytes, input_format: str) -> bytes:
    """
    Конвертирует аудио- или видеофайл в WAV (16kHz, mono) — формат,
    с которым стабильно работает большинство ASR-моделей на HF.

    ffmpeg (через pydub) сам вытаскивает звуковую дорожку из видео,
    отдельно ничего "вырезать" не нужно — достаточно указать формат
    контейнера (например "mp4" для видео и видео-кружочков).
    """
    audio = AudioSegment.from_file(io.BytesIO(source_bytes), format=input_format)
    audio = audio.set_frame_rate(16000).set_channels(1)

    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    return wav_buffer.getvalue()


def _call_hf_asr(wav_bytes: bytes) -> str:
    url = _API_URL_TEMPLATE.format(model=settings.hf_asr_model)
    headers = {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": "audio/wav",
    }

    response = requests.post(url, headers=headers, data=wav_bytes, timeout=60)

    if response.status_code == 503:
        # Модель "холодная" — HF просит подождать, пока она поднимется
        raise RuntimeError(
            "Модель распознавания речи сейчас загружается на серверах "
            "Hugging Face (cold start). Попробуйте через 15-20 секунд."
        )

    response.raise_for_status()

    payload = response.json()
    # Обычный ответ ASR: {"text": "..."}
    if isinstance(payload, dict) and "text" in payload:
        return payload["text"].strip()

    logger.warning("Неожиданный формат ответа от HF ASR: %s", json.dumps(payload)[:500])
    return str(payload).strip()


async def _transcribe(source_bytes: bytes, input_format: str) -> str:
    """
    Общая логика: конвертировать в WAV → отправить в HF ASR → вернуть текст.

    Конвертация и сетевой запрос синхронные — оборачиваем в
    asyncio.to_thread, чтобы не блокировать event loop бота.
    """
    wav_bytes = await asyncio.to_thread(_convert_to_wav, source_bytes, input_format)

    try:
        return await asyncio.to_thread(_call_hf_asr, wav_bytes)
    except Exception:
        logger.exception("Ошибка при обращении к Hugging Face ASR")
        raise


async def transcribe_voice(ogg_bytes: bytes) -> str:
    """Распознаёт голосовое сообщение Telegram (OGG/Opus)."""
    return await _transcribe(ogg_bytes, input_format="ogg")


async def transcribe_video(mp4_bytes: bytes) -> str:
    """
    Распознаёт речь из видео (обычное видео-сообщение или
    видео-кружочек Telegram). Оба формата — MP4-контейнер,
    звуковая дорожка извлекается автоматически при конвертации.
    """
    return await _transcribe(mp4_bytes, input_format="mp4")
