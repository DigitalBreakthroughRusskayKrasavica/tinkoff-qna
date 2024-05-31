from typing import Any, Awaitable, Callable, Dict, Tuple

from aiogram import BaseMiddleware, Bot, types
from aiogram.enums.message_entity_type import MessageEntityType
from aiogram.types import BotCommandScopeChat, TelegramObject

from tinkoff_qna.presentation.bot.commands import get_curator_commands
from tinkoff_qna.database.repository import DbRepository
from tinkoff_qna.models import Role

WELCOME_MESSAGE = """Добро пожаловать в бот для поддержки студентов!
"""

COMMAND_START = "/start"


class AuthMiddleware(BaseMiddleware):
    def __init__(self, repo: DbRepository, curator_secret_key: str):
        self._curator_secret_key = curator_secret_key
        self._repo = repo

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        msg: types.Message,  # type: ignore[override]
        data: Dict[str, Any],
    ) -> Any:
        if not msg.bot:
            return

        role: Role
        chat_id = msg.chat.id
        bot = msg.bot

        user_exists = await self._repo.user_exists(chat_id)

        if not self._msg_is_command_start(msg):
            if not user_exists:
                await self._repo.add_user(chat_id, Role.CLIENT)
            return await handler(msg, data)

        if not user_exists:
            commands, role = [], Role.CLIENT

            if not msg.text:
                return

            _, arg = self._parse_command(msg.text)
            if arg == self._curator_secret_key:
                commands, role = get_curator_commands(), Role.SUPPORT_TECHNICIAN

            await self._repo.add_user(chat_id, role)

            await bot.set_my_commands(commands, BotCommandScopeChat(chat_id=chat_id))
            return await bot.send_message(
                chat_id=chat_id,
                text=WELCOME_MESSAGE
                if role == Role.CLIENT
                else WELCOME_MESSAGE + "\nВаша роль: 'Специалист Техподдержки'",
            )

        user = await self._repo.get_user_by_id(chat_id)
        return await bot.send_message(
            chat_id=chat_id,
            text='Задайте ваш вопрос'
            if user.role == Role.CLIENT
            else "Добро пожаловать снова.\nВаша роль: 'Cпециалист Техподдержки'",
        )

    def _msg_is_command_start(self, msg: types.Message) -> bool:
        if not msg.entities:
            return False

        msg_type = msg.entities[0].type
        if msg_type != MessageEntityType.BOT_COMMAND:
            return False

        if not msg.text:
            return False

        command, _ = self._parse_command(msg.text)
        return command == COMMAND_START

    @staticmethod
    def _parse_command(text: str) -> Tuple[str, str]:
        try:
            command, arg = text.split(maxsplit=1)
        except ValueError:
            command, arg = text, ""
        return command, arg
        