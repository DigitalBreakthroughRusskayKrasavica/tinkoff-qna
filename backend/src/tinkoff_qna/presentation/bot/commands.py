from typing import List

from aiogram.types import BotCommand

COMMON_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="become_student", description="[Interactive] Стать студентом"),
    BotCommand(command="become_curator", description="[Interactive] Стать куратором"),
]


def get_curator_commands() -> List[BotCommand]:
    return [
        *COMMON_COMMANDS,
        BotCommand(command="new_pair", description="Добавить пару вопрос-ответ"),
        BotCommand(command="set_model", description="Сменить модель"),
    ]
