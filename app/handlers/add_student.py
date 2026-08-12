from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_confirm_keyboard, get_weekday_keyboard
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
    await message.answer("Введите стоимость одного занятия (например, 1500):")


@router.message(AddStudent.price)
async def process_price(message: types.Message, state: FSMContext) -> None:
    price = parse_price(message.text)
    if price is None or price <= 0:
        await message.answer("Введите корректную сумму, например 1500:")
        return

    await state.update_data(price=price)
    await state.set_state(AddStudent.weekday)
    await message.answer("Выберите день недели занятия:", reply_markup=get_weekday_keyboard())


@router.callback_query(AddStudent.weekday, F.data.startswith("weekday:"))
async def process_weekday(callback: types.CallbackQuery, state: FSMContext) -> None:
    weekday = int(callback.data.split(":")[1])
    await state.update_data(weekday=weekday)
    await state.set_state(AddStudent.time)
    await callback.message.edit_text("Введите время занятия (например, 18:30):")


@router.message(AddStudent.time)
async def process_time(message: types.Message, state: FSMContext) -> None:
    lesson_time = parse_time(message.text)
    if lesson_time is None:
        await message.answer("Введите время в формате ЧЧ:ММ, например 18:30:")
        return

    await state.update_data(time=lesson_time)
    data = await state.get_data()

    text = (
        f"Проверьте данные:\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Цена:</b> {data['price']}\n"
        f"<b>День:</b> {get_weekday_name(data['weekday'])}\n"
        f"<b>Время:</b> {data['time'].strftime('%H:%M')}\n\n"
        f"Всё верно?"
    )
    await state.set_state(AddStudent.confirm)
    await message.answer(text, reply_markup=get_confirm_keyboard(prefix="student"), parse_mode="HTML")


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
        weekday=data["weekday"],
        lesson_time=data["time"],
    )
    await state.clear()
    await callback.message.edit_text(f"✅ Ученик <b>{data['name']}</b> добавлен!", parse_mode="HTML")
