import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.database import init_db
from app.handlers import add_student, common, info
from app.middlewares.db_session import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.include_router(common.router)
    dp.include_router(add_student.router)
    dp.include_router(info.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
