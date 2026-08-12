from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.lesson_service import mark_lesson_cancelled, mark_lesson_completed

router = Router()


@router.callback_query(F.data.startswith("lesson:"))
async def process_lesson_callback(callback: types.CallbackQuery, session: AsyncSession) -> None:
    parts = callback.data.split(":")
    lesson_id = int(parts[1])
    action = parts[2]

    if action == "paid":
        await mark_lesson_completed(session, lesson_id, is_paid=True)
        await callback.message.edit_text("✅ Занятие отмечено как прошедшее и оплаченное.")
    elif action == "debt":
        await mark_lesson_completed(session, lesson_id, is_paid=False)
        await callback.message.edit_text("📝 Занятие отмечено как прошедшее, но не оплаченное.")
    elif action == "cancel":
        await mark_lesson_cancelled(session, lesson_id)
        await callback.message.edit_text("❌ Занятие отменено.")

    await callback.answer()
