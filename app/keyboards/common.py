from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.utils.time import WEEKDAYS


def get_weekday_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=day, callback_data=f"weekday:{index}")]
        for index, day in enumerate(WEEKDAYS)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_keyboard(prefix: str = "confirm") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data=f"{prefix}:no"),
            ]
        ]
    )


def get_add_more_schedule_keyboard(prefix: str = "schedule") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить ещё", callback_data=f"{prefix}:more"),
                InlineKeyboardButton(text="✅ Готово", callback_data=f"{prefix}:done"),
            ]
        ]
    )


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить ученика")],
            [KeyboardButton(text="📋 Список учеников"), KeyboardButton(text="💰 Долги")],
            [KeyboardButton(text="📅 План на сегодня")],
        ],
        resize_keyboard=True,
    )
