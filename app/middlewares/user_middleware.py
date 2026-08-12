from typing import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.services.user_service import get_or_create_user


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[None]],
        event: TelegramObject,
        data: dict,
    ) -> None:
        update: Update = event
        user = None
        if update.message:
            user = update.message.from_user
        elif update.callback_query:
            user = update.callback_query.from_user

        if user is not None and "session" in data:
            await get_or_create_user(
                data["session"],
                telegram_id=user.id,
                username=user.username,
                full_name=user.full_name or user.username or str(user.id),
            )

        return await handler(event, data)
