import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import init_db

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()


async def main() -> None:
    logger.info("Initializing database...")
    await init_db()
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
