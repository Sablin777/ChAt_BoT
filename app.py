import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from src import common, voice, video, text


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher()

    # Порядок важен: специфичные роутеры (voice, video) должны идти раньше
    # общего текстового catch-all роутера, иначе он перехватит всё.
    dp.include_router(common.router)
    dp.include_router(voice.router)
    dp.include_router(video.router)
    dp.include_router(text.router)

    logging.info("Бот запущен, начинаю polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
