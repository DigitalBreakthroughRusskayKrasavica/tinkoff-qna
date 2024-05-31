from typing import List

from aiogram.types import BotCommand

COMMON_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="become_client", description="[Interactive] Стать клиентом"),
    BotCommand(command="become_tech_support", description="[Interactive] Стать специалистом тех. поддержки"),
]


def get_support_technician_commands() -> List[BotCommand]:
    return [
        *COMMON_COMMANDS[:-1],
        BotCommand(command="new_pair", description="Добавить пару вопрос-ответ"),
        BotCommand(command="set_prompt", description="Выставить промпт для модели"),
    ]
