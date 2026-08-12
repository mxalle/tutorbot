from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import get_main_menu_keyboard
from app.services.user_service import get_or_create_user

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession) -> None:
    await get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "Привет! Я бот для репетиторов. Здесь можно вести учеников, занятия и долги.",
        reply_markup=get_main_menu_keyboard(),
    )
