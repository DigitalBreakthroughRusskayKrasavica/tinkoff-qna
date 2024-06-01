from aiogram import Bot, F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tinkoff_qna.presentation.bot.filters import SupportTechFilter
from tinkoff_qna.presentation.bot.states import NewPairForm, NewPromptForm
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
    await msg.answer('Введите категорию/тип этого вопроса', reply_markup=CANCEL_KEYBOARD)


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
    await state.update_data(answer=msg.text)
    await state.set_state(NewPairForm.url)

    try:
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id - 1)
    except Exception:
        pass
    await msg.answer('Введите ссылку для этого вопроса', reply_markup=CANCEL_KEYBOARD)


@router.message(StateFilter(NewPairForm.url))
async def get_answer(msg: types.Message, state: FSMContext, bot: Bot, service: HelperService):
    data = await state.get_data()
    question, category, answer, url = data['question'], data['category'], data['answer'], msg.text

    await service.add_new_pair(question, category, answer, url)

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


@router.message(Command('set_prompt'))
async def set_new_prompt(msg: types.Message, state: FSMContext):
    with open('current_prompt', 'r') as f:
        current_prompt = f.read().rstrip()
    await msg.answer(
        text='Введите новый промпт для модели\n\n'
             f"Текущий: '{current_prompt}'",
        reply_markup=CANCEL_KEYBOARD
    )
    await state.set_state(NewPromptForm.prompt)


@router.message(StateFilter(NewPromptForm.prompt))
async def set_prompt(msg: types.Message, state: FSMContext, bot: Bot):
    prompt = msg.text
    with open('current_prompt', 'w') as f:
        f.write(prompt)

    try:
        await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        pass

    await state.clear()
    await bot.send_message(msg.from_user.id, f"Выставлен новый промпт '{prompt}'")


@router.callback_query(StateFilter(NewPromptForm.prompt), F.data == 'stop_appending')
async def cancel_appending(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    try:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    except Exception:
        pass
    await bot.send_message(chat_id=callback.from_user.id, text='Вы отменили процесс изменения промпта')

