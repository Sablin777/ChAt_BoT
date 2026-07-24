"""
Простое хранилище истории диалогов в памяти процесса.

Для продакшена это стоит заменить на Redis/БД — при перезапуске
бота вся история сейчас теряется, а при нескольких инстансах
бота (например, за балансировщиком) данные не будут общими.
"""

from collections import defaultdict, deque
from typing import Deque, Dict, List

from config import settings

Message = Dict[str, str]  # {"role": "user"|"assistant", "content": "..."}

_history: Dict[int, Deque[Message]] = defaultdict(
    lambda: deque(maxlen=settings.history_limit)
)


def get_history(chat_id: int) -> List[Message]:
    return list(_history[chat_id])


def add_message(chat_id: int, role: str, content: str) -> None:
    _history[chat_id].append({"role": role, "content": content})


def reset_history(chat_id: int) -> None:
    _history[chat_id].clear()
