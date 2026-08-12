from datetime import time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Lesson, LessonStatus, Student, StudentSchedule
from app.utils.time import get_next_lesson_datetime


async def create_student(
    session: AsyncSession,
    tutor_id: int,
    name: str,
    price: float,
    schedules: list[dict],
    timezone: str = "Europe/Moscow",
) -> Student:
    student = Student(
        tutor_id=tutor_id,
        name=name,
        price=Decimal(str(price)),
        timezone=timezone,
    )
    session.add(student)
    await session.flush()

    for schedule in schedules:
        student_schedule = StudentSchedule(
            student_id=student.id,
            weekday=schedule["weekday"],
            lesson_time=schedule["lesson_time"],
        )
        session.add(student_schedule)

        next_lesson_datetime = get_next_lesson_datetime(
            schedule["weekday"], schedule["lesson_time"], timezone
        )
        lesson = Lesson(
            student_id=student.id,
            lesson_date=next_lesson_datetime.date(),
            lesson_datetime=next_lesson_datetime,
            status=LessonStatus.SCHEDULED,
        )
        session.add(lesson)

    await session.commit()
    return student


async def get_students_by_tutor(session: AsyncSession, tutor_id: int) -> list[Student]:
    result = await session.execute(
        select(Student)
        .where(Student.tutor_id == tutor_id, Student.is_active == True)
        .options(selectinload(Student.schedules))
    )
    return list(result.scalars().all())


async def get_student_by_id(session: AsyncSession, student_id: int) -> Student | None:
    result = await session.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()
