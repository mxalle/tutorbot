from datetime import datetime, timedelta
from decimal import Decimal

import pytz
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Lesson, LessonStatus, Payment, Student, StudentSchedule
from app.utils.time import get_next_lesson_datetime


async def create_weekly_lessons(session: AsyncSession, look_ahead_weeks: int = 4) -> None:
    """Создаёт занятия на ближайшие недели для активных учеников по их расписанию."""
    result = await session.execute(
        select(Student)
        .where(Student.is_active == True)
        .options(selectinload(Student.schedules))
    )
    students = result.scalars().all()

    today_utc = datetime.utcnow().date()

    for student in students:
        tz = pytz.timezone(student.timezone)

        for schedule in student.schedules:
            last_lesson_result = await session.execute(
                select(Lesson)
                .where(Lesson.student_id == student.id)
                .order_by(Lesson.lesson_date.desc())
                .limit(1)
            )
            last_lesson = last_lesson_result.scalar_one_or_none()

            if last_lesson is None:
                start_date = today_utc
            else:
                start_date = last_lesson.lesson_date + timedelta(days=1)

            current_week_start = start_date - timedelta(days=start_date.weekday())
            for week in range(look_ahead_weeks):
                lesson_date = current_week_start + timedelta(days=schedule.weekday, weeks=week)
                if lesson_date < today_utc:
                    continue

                exists_result = await session.execute(
                    select(Lesson).where(
                        and_(Lesson.student_id == student.id, Lesson.lesson_date == lesson_date)
                    )
                )
                if exists_result.scalar_one_or_none():
                    continue

                local_dt = tz.localize(datetime.combine(lesson_date, schedule.lesson_time))
                lesson_datetime = local_dt.astimezone(pytz.utc).replace(tzinfo=None)
                lesson = Lesson(
                    student_id=student.id,
                    lesson_date=lesson_date,
                    lesson_datetime=lesson_datetime,
                    status=LessonStatus.SCHEDULED,
                )
                session.add(lesson)

    await session.commit()


async def get_today_lessons(session: AsyncSession, tutor_id: int) -> list[Lesson]:
    today = datetime.utcnow().date()
    result = await session.execute(
        select(Lesson)
        .join(Student)
        .where(
            and_(
                Student.tutor_id == tutor_id,
                Lesson.lesson_date == today,
                Lesson.status == LessonStatus.SCHEDULED,
            )
        )
        .options(selectinload(Lesson.student))
        .order_by(Lesson.lesson_datetime)
    )
    return list(result.scalars().all())


async def get_debts(session: AsyncSession, tutor_id: int) -> list[tuple[Student, int, Decimal]]:
    """Возвращает список (ученик, количество неоплаченных занятий, сумма долга)."""
    result = await session.execute(
        select(Student)
        .where(Student.tutor_id == tutor_id, Student.is_active == True)
        .order_by(Student.name)
    )
    students = result.scalars().all()

    debts = []
    for student in students:
        count_result = await session.execute(
            select(func.count(Lesson.id)).where(
                and_(
                    Lesson.student_id == student.id,
                    Lesson.status == LessonStatus.COMPLETED,
                    Lesson.is_paid == False,
                )
            )
        )
        count = count_result.scalar() or 0
        if count > 0:
            amount = student.price * count
            debts.append((student, count, amount))

    return debts


async def mark_lesson_completed(session: AsyncSession, lesson_id: int, is_paid: bool) -> None:
    result = await session.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(selectinload(Lesson.student))
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        return

    lesson.status = LessonStatus.COMPLETED
    lesson.is_paid = is_paid
    if is_paid:
        lesson.paid_at = datetime.utcnow()
        payment = Payment(lesson_id=lesson.id, amount=lesson.student.price)
        session.add(payment)
    await session.commit()


async def mark_lesson_cancelled(session: AsyncSession, lesson_id: int) -> None:
    result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        return

    lesson.status = LessonStatus.CANCELLED
    await session.commit()
