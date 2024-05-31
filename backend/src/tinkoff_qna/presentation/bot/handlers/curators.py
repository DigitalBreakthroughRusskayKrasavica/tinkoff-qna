from aiogram import Router, types, Bot, F

from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tinkoff_qna.presentation.bot.filters import SupportTechFilter
from tinkoff_qna.presentation.bot.states import NewPairForm
from tinkoff_qna.services import HelperService

router = Router()

CANCEL_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='stop_appending')]]
)


@router.message(SupportTechFilter(), Command('new_pair'))
async def add_new_pair(msg: types.Message, state: FSMContext):
    await state.set_state(NewPairForm.question)
    await msg.answer('Введите новый вопрос', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.question))
async def get_question(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(question=msg.text)
    await state.set_state(NewPairForm.category)

    try:
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    except Exception:
        pass
    await msg.answer('Введите категорию этого вопроса', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.category))
async def get_question_category(msg: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(category=msg.text)
    await state.set_state(NewPairForm.answer)

    try:
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    except Exception:
        pass
    await msg.answer('Введите ответ для этого вопроса', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.answer))
async def get_answer(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    data = await state.get_data()
    question, category, answer = data['question'], data['category'], msg.text

    await service.add_new_pair(question, category, answer)

    await state.clear()

    try:
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    except Exception:
        pass
    await msg.answer(
        text='Добавлена новая пара вопрос-ответ:\n\n'
             f"'{question}' : '{answer}'"
    )


@router.callback_query(StateFilter(NewPairForm), F.data == 'stop_appending')
async def cancel_appending(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    try:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    except Exception:
        pass
    await bot.send_message(chat_id=callback.from_user.id, text='Вы отменили процесс добавления пары')


@router.message(Command('set_model'))
async def set_other_model(msg: types.Message):
    with open('current_model', 'r') as f:
        current_model = f.read().rstrip()
    await msg.answer(
        text='Выберите модель, которая будет отвечать на вопросы\n\n'
             f"Текущая: {current_model}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Rubert', callback_data='set_model-rubert'),
                    InlineKeyboardButton(text='Rasa', callback_data='set_model-rasa'),
                ]
            ]
        )
    )


@router.callback_query(F.data.startswith('set_model'))
async def set_model(callback: types.CallbackQuery, bot: Bot):
    model = callback.data.split('-')[1]
    with open('current_model', 'w') as f:
        f.write(model)

    try:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    except Exception:
        pass
    await bot.send_message(callback.from_user.id, f"Выставлена модель '{model}'")
