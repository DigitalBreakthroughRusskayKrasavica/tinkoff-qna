from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DIMiddleware(BaseMiddleware):
    def __init__(self, **kwargs):
        super().__init__()
        self._on_inject = kwargs

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        for k, v in self._on_inject.items():
            data[k] = v
        return await handler(event, data)
