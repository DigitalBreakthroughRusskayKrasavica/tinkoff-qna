import asyncio

from aiogram import Router, Bot
from aiogram.filters import CommandStart

from aiogram import types
from aiogram.filters import StateFilter, Command

from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommandScopeChat

from tinkoff_qna import exceptions
from tinkoff_qna.services import HelperService
from tinkoff_qna.models import Role

from tinkoff_qna.presentation.bot.commands import get_curator_commands, COMMON_COMMANDS

from tinkoff_qna.presentation.bot.filters import SupportTechFilter

router = Router(name=__name__)


@router.message(Command('become_curator'))
async def become_curator(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.CURATOR)

    await bot.set_my_commands(get_curator_commands(), BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь куратор")


@router.message(Command('become_student'))
async def become_student(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.STUDENT)
    
    await bot.set_my_commands(COMMON_COMMANDS, BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь студент")
    


@router.message(~SupportTechFilter())
async def get_question(msg: types.Message, state: FSMContext, service: HelperService):
    question = msg.text

    try:
        ans, links = await service.get_answer_with_links(question)
        if ans == 'Не получилось найти ответ - свяжитесь со специалистом техподдержки':
            return await msg.answer(
            text=ans,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Связаться со специалистом",
                            callback_data=f'start_conversation-{msg.chat.id}'
                        )
                    ]
                ]
            )
        )
        
        links = '\n'.join(links)
        await msg.answer(
            text=f"{ans}.\n\nПохожее:\n{links}\n\nОтвет не устроил?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Связаться со специалистом тех. поддержки",
                            callback_data=f'start_conversation-{msg.chat.id}'
                        )
                    ]
                ]
            )
        )
    except exceptions.InvalidQuestion as e:
        pass
    except exceptions.QuestionNeedsСlarification as e:
        pass

