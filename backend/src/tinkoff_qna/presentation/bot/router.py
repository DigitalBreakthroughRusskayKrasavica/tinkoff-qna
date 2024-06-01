import asyncio

from aiogram import Router, Bot
from aiogram.filters import CommandStart

from aiogram import types
from aiogram.filters import StateFilter, Command

from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommandScopeChat

from tinkoff_qna import exceptions
from tinkoff_qna.services import HelperService
from tinkoff_qna.models import Role

from tinkoff_qna.presentation.bot.commands import get_support_technician_commands, COMMON_COMMANDS

from tinkoff_qna.presentation.bot.filters import SupportTechFilter

router = Router(name=__name__)


@router.message(Command('become_tech_support'))
async def become_tech_support(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.SUPPORT_TECHNICIAN)

    await bot.set_my_commands(get_support_technician_commands(), BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь специалист тех. поддержки")


@router.message(Command('become_client'))
async def become_client(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.CLIENT)
    
    await bot.set_my_commands(COMMON_COMMANDS, BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь клиент")
    


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
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        
        links = '\n'.join(links)
        await msg.answer(
            text=f"{ans}.\n\nПохожее:\n{links}\n\nОтвет не устроил?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Связаться с тех. поддержкой",
                            callback_data=f'start_conversation-{msg.chat.id}'
                        )
                    ]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    except exceptions.InvalidQuestion as e:
        pass
    except exceptions.QuestionNeedsСlarification as e:
        pass

