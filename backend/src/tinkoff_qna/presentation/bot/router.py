import asyncio


import speech_recognition as sr

import subprocess

from aiogram import Router, Bot, F
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
import datetime

router = Router(name=__name__)


@router.message(Command('help'))
async def help(msg: types.Message):
    await msg.answer("""Чтобы задать ваш вопрос, просто введите его текстом
    
Прямо сейчас бот работает в интерактивном режиме и 
вы можете стать как специалистом тех. поддержки при
помощи команды /become_tech_support или клиентом командой /become_client

❗️Специалист тех. поддержки не может задавать вопросы

Если ответ от бота не устроил, то клиент всегда может обратиться к специалисту тех. поддержки,
нажав на кнопку 'Связаться с тех. поддержкой', которая находится под каждым ответом.
""")

@router.message(Command('become_tech_support'))
async def become_tech_support(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.SUPPORT_TECHNICIAN)

    await bot.set_my_commands(get_support_technician_commands(), BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь специалист тех. поддержки\n❗️Специалист тех. поддержки не может задавать вопросы")


@router.message(Command('become_client'))
async def become_client(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    await service.change_role(msg.chat.id, Role.CLIENT)
    
    await bot.set_my_commands(COMMON_COMMANDS, BotCommandScopeChat(chat_id=msg.chat.id))
    await msg.answer("Вы теперь клиент")
    


@router.message(F.text, ~SupportTechFilter())
async def get_question(msg: types.Message, service: HelperService, bot: Bot):
    question = msg.text

    await bot.send_message(msg.from_user.id, '🤔Нейросеть задумалась')
    try:
        ans, links = await service.get_answer_with_links(question)
        if links:
            links = '\n'.join(links)
            links = f'\n\nПохожее:\n{links}\n\nОтвет не устроил?'
        else:
            links = ""

        await bot.delete_message(msg.from_user.id, msg.message_id + 1)
        await msg.answer(
            text=f"{ans}{links}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Связаться с тех. поддержкой",
                            callback_data=f'start_conversation-{msg.chat.id}-{msg.message_id}'
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


# 0.2532536602930813

@router.message(F.voice, ~SupportTechFilter())
async def get_question_by_audio(msg: types.Message, service: HelperService, bot: Bot):
    await bot.send_message(msg.from_user.id, '🤔Нейросеть задумалась')

    file_info = await bot.get_file(msg.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    filename = f'audio_{datetime.datetime.now()}.ogg'
    with open(filename, 'wb') as f:
        f.write(downloaded_file.read())

    dest_filename = filename.replace('.ogg', '.wav')
    process = subprocess.run(['ffmpeg', '-i', filename, dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong")

    question = transcribe_audio(dest_filename)

    try:
        ans, links = await service.get_answer_with_links(question)
        links = '\n'.join(links)

        await bot.delete_message(msg.from_user.id, msg.message_id + 1)
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


# initialize the recognizer
r = sr.Recognizer()

def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened, language="ru-RU")
    return text
