from datetime import datetime, timedelta

import pytz
from aiogram import Bot
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import Lesson, LessonStatus, Student
from app.services.lesson_service import create_weekly_lessons, mark_lesson_cancelled, mark_lesson_completed


async def schedule_lessons_job() -> None:
    async with async_session() as session:
        await create_weekly_lessons(session)


async def remind_before_lesson_job(bot: Bot) -> None:
    now = datetime.utcnow()
    window_start = now
    window_end = now + timedelta(minutes=1)

    async with async_session() as session:
        result = await session.execute(
            select(Lesson)
            .join(Student)
            .where(
                and_(
                    Lesson.status == LessonStatus.SCHEDULED,
                    Lesson.reminded_at.is_(None),
                    Lesson.lesson_datetime >= window_start,
                    Lesson.lesson_datetime <= window_end,
                )
            )
        )
        lessons = result.scalars().all()

        for lesson in lessons:
            text = (
                f"⏰ Через час занятие с <b>{lesson.student.name}</b> "
                f"в {lesson.lesson_datetime.strftime('%H:%M')}"
            )
            await bot.send_message(lesson.student.tutor_id, text, parse_mode="HTML")
            lesson.reminded_at = now
            await session.commit()


async def ask_after_lesson_job(bot: Bot) -> None:
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=5)
    window_end = now

    async with async_session() as session:
        result = await session.execute(
            select(Lesson)
            .join(Student)
            .where(
                and_(
                    Lesson.status == LessonStatus.SCHEDULED,
                    Lesson.lesson_datetime >= window_start,
                    Lesson.lesson_datetime <= window_end,
                )
            )
        )
        lessons = result.scalars().all()

        for lesson in lessons:
            from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Прошло и оплачено", callback_data=f"lesson:{lesson.id}:paid"),
                        InlineKeyboardButton(text="👍 Прошло, не оплачено", callback_data=f"lesson:{lesson.id}:debt"),
                    ],
                    [
                        InlineKeyboardButton(text="❌ Отменено", callback_data=f"lesson:{lesson.id}:cancel"),
                    ],
                ]
            )
            await bot.send_message(
                lesson.student.tutor_id,
                f"Занятие с <b>{lesson.student.name}</b> закончилось?",
                reply_markup=keyboard,
                parse_mode="HTML",
            )


async def daily_plan_job(bot: Bot) -> None:
    from app.services.lesson_service import get_today_lessons

    async with async_session() as session:
        result = await session.execute(select(Student.tutor_id).distinct())
        tutor_ids = [row[0] for row in result.all()]

        for tutor_id in tutor_ids:
            lessons = await get_today_lessons(session, tutor_id)
            if not lessons:
                await bot.send_message(tutor_id, "Доброе утро! Сегодня занятий нет ☕️")
                continue

            lines = ["<b>Доброе утро! План на сегодня:</b>\n"]
            for lesson in lessons:
                lines.append(
                    f"• {lesson.lesson_datetime.strftime('%H:%M')} — {lesson.student.name}"
                )
            await bot.send_message(tutor_id, "\n".join(lines), parse_mode="HTML")
