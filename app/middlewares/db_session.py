from typing import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database import async_session


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[None]],
        event: TelegramObject,
        data: dict,
    ) -> None:
        async with async_session() as session:
            data["session"] = session
            try:
                await handler(event, data)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
