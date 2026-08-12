import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import init_db
from app.handlers import add_student, common, info, lesson_callback
from app.middlewares.db_session import DbSessionMiddleware
from app.scheduler.jobs import ask_after_lesson_job, daily_plan_job, remind_before_lesson_job, schedule_lessons_job

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await init_db()
    await schedule_lessons_job()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.include_router(common.router)
    dp.include_router(add_student.router)
    dp.include_router(info.router)
    dp.include_router(lesson_callback.router)

    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.add_job(schedule_lessons_job, "cron", hour=0, minute=5)
    scheduler.add_job(remind_before_lesson_job, "interval", minutes=1, args=[bot])
    scheduler.add_job(ask_after_lesson_job, "interval", minutes=5, args=[bot])
    scheduler.add_job(daily_plan_job, "cron", hour=8, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
