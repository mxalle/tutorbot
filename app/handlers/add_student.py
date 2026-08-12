from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_add_more_schedule_keyboard, get_confirm_keyboard, get_weekday_keyboard
from app.services.student_service import create_student
from app.states import AddStudent
from app.utils.time import get_weekday_name, parse_price, parse_time

router = Router()


@router.message(Command("add"))
@router.message(F.text == "➕ Добавить ученика")
async def start_add_student(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AddStudent.name)
    await message.answer("Введите имя ученика:")


@router.message(AddStudent.name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddStudent.price)
    await message.answer("Введите стоимость одного занятия в рублях (например, 1500):")


@router.message(AddStudent.price)
async def process_price(message: types.Message, state: FSMContext) -> None:
    price = parse_price(message.text)
    if price is None or price <= 0:
        await message.answer("Введите корректную сумму в рублях, например 1500:")
        return

    await state.update_data(price=price)
    await state.update_data(schedules=[])
    await state.set_state(AddStudent.schedule_weekday)
    await message.answer("Выберите день недели занятия:", reply_markup=get_weekday_keyboard())


@router.callback_query(AddStudent.schedule_weekday, F.data.startswith("weekday:"))
async def process_schedule_weekday(callback: types.CallbackQuery, state: FSMContext) -> None:
    weekday = int(callback.data.split(":")[1])
    await state.update_data(current_weekday=weekday)
    await state.set_state(AddStudent.schedule_time)
    await callback.message.edit_text("Введите время занятия (например, 18:30):")


@router.message(AddStudent.schedule_time)
async def process_schedule_time(message: types.Message, state: FSMContext) -> None:
    lesson_time = parse_time(message.text)
    if lesson_time is None:
        await message.answer("Введите время в формате ЧЧ:ММ, например 18:30:")
        return

    data = await state.get_data()
    schedules = data.get("schedules", [])
    schedules.append({"weekday": data["current_weekday"], "lesson_time": lesson_time})
    await state.update_data(schedules=schedules)

    await state.set_state(AddStudent.add_more_schedule)
    schedule_text = "\n".join(
        f"• {get_weekday_name(s['weekday'])} в {s['lesson_time'].strftime('%H:%M')}"
        for s in schedules
    )
    await message.answer(
        f"Добавлено расписание:\n{schedule_text}\n\nДобавить ещё занятие в неделю?",
        reply_markup=get_add_more_schedule_keyboard(),
    )


@router.callback_query(AddStudent.add_more_schedule, F.data.startswith("schedule:"))
async def process_add_more_schedule(callback: types.CallbackQuery, state: FSMContext) -> None:
    answer = callback.data.split(":")[1]
    if answer == "more":
        await state.set_state(AddStudent.schedule_weekday)
        await callback.message.edit_text("Выберите день недели занятия:", reply_markup=get_weekday_keyboard())
        return

    data = await state.get_data()
    schedules = data.get("schedules", [])
    if not schedules:
        await state.set_state(AddStudent.schedule_weekday)
        await callback.message.edit_text(
            "Нужно добавить хотя бы одно занятие. Выберите день недели:",
            reply_markup=get_weekday_keyboard(),
        )
        return

    schedule_text = "\n".join(
        f"• {get_weekday_name(s['weekday'])} в {s['lesson_time'].strftime('%H:%M')}"
        for s in schedules
    )
    text = (
        f"Проверьте данные:\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Цена:</b> {data['price']} ₽\n"
        f"<b>Расписание:</b>\n{schedule_text}\n\n"
        f"Всё верно?"
    )
    await state.set_state(AddStudent.confirm)
    await callback.message.edit_text(text, reply_markup=get_confirm_keyboard(prefix="student"))


@router.callback_query(AddStudent.confirm, F.data.startswith("student:"))
async def process_confirm(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    answer = callback.data.split(":")[1]
    if answer == "no":
        await state.clear()
        await callback.message.edit_text("Добавление отменено.")
        return

    data = await state.get_data()
    await create_student(
        session,
        tutor_id=callback.from_user.id,
        name=data["name"],
        price=data["price"],
        schedules=data["schedules"],
    )
    await state.clear()
    await callback.message.edit_text(f"✅ Ученик <b>{data['name']}</b> добавлен!", parse_mode="HTML")
