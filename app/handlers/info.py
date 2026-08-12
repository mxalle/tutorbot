from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.lesson_service import get_debts, get_today_lessons
from app.services.student_service import get_students_by_tutor
from app.utils.time import get_weekday_name

router = Router()


@router.message(Command("students"))
@router.message(F.text == "📋 Список учеников")
async def list_students(message: types.Message, session: AsyncSession) -> None:
    students = await get_students_by_tutor(session, message.from_user.id)
    if not students:
        await message.answer("У вас пока нет учеников. Добавьте первого через /add")
        return

    lines = []
    for index, student in enumerate(students, 1):
        lines.append(
            f"{index}. <b>{student.name}</b> — {student.price}₽, "
            f"{get_weekday_name(student.weekday)} в {student.lesson_time.strftime('%H:%M')}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("debts"))
@router.message(F.text == "💰 Долги")
async def show_debts(message: types.Message, session: AsyncSession) -> None:
    debts = await get_debts(session, message.from_user.id)
    if not debts:
        await message.answer("🎉 Долгов нет!")
        return

    lines = ["<b>Долги учеников:</b>\n"]
    total = 0
    for student, count, amount in debts:
        lines.append(f"• {student.name}: {count} занятий — {amount}₽")
        total += amount

    lines.append(f"\n<b>Итого:</b> {total}₽")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("plan"))
async def show_plan(message: types.Message, session: AsyncSession) -> None:
    lessons = await get_today_lessons(session, message.from_user.id)
    if not lessons:
        await message.answer("Сегодня занятий нет. Можно отдохнуть ☕️")
        return

    lines = ["<b>План на сегодня:</b>\n"]
    for lesson in lessons:
        lines.append(
            f"• {lesson.lesson_datetime.strftime('%H:%M')} — {lesson.student.name} "
            f"({lesson.student.price}₽)"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")
