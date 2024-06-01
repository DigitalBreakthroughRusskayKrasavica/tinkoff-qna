import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from redis.asyncio import Redis
from tinkoff_qna.presentation.bot.filters import SupportTechFilter
from tinkoff_qna.presentation.bot.states import Conversation
from tinkoff_qna.services import HelperService

logger = logging.getLogger(__name__)

router = Router()

CANCEL_KEYWORDS = "Завершить диалог"
CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=CANCEL_KEYWORDS)]], resize_keyboard=True
)


class IsActiveCurator(Filter):
    async def __call__(self, message: types.Message, redis_connection: Redis) -> bool:
        student_id = await redis_connection.get(message.from_user.id)
        return bool(student_id)


@router.callback_query(F.data.startswith("start_conversation"))
async def start_conversation(
        callback: types.CallbackQuery,
        state: FSMContext,
        bot: Bot,
        service: HelperService,
        redis_connection: Redis
) -> None:
    if not callback.data:
        logger.info("No callback data")
        return

    student_id = int(callback.data.split("-")[1])
    message_id = int(callback.data.split("-")[-1])

    curator_id = await service.find_unassigned_curator(redis_connection)
    if curator_id == 0:
        return await callback.message.answer("Нет свободных специалистов")

    await redis_connection.set(curator_id, student_id)

    await state.set_state(Conversation.active)
    await state.storage.set_state(
        key=StorageKey(bot_id=bot.id, chat_id=student_id, user_id=student_id),
        state=Conversation.active,
    )

    await state.update_data(curator_id=curator_id, first_message=True)

    if not callback.message:
        logger.info("No message")
        return

    await bot.edit_message_reply_markup(
        chat_id=student_id, message_id=callback.message.message_id, reply_markup=None
    )

    if not isinstance(callback.message, types.Message):
        logger.info("Message has incorrect type")
        return

    await bot.send_message(curator_id, text=f'Клиент {student_id} спрашивает:')
    await bot.copy_message(
        from_chat_id=student_id,
        message_id=message_id,
        chat_id=curator_id,
    )

    await callback.message.answer(
        "Диалог со специалистом начат", reply_markup=CANCEL_KEYBOARD
    )


@router.message(SupportTechFilter(), IsActiveCurator())
async def handle_curator_chat(
        message: types.Message, state: FSMContext, bot: Bot, redis_connection: Redis
) -> None:
    student_id = int(await redis_connection.get(message.chat.id))

    if message.text == CANCEL_KEYWORDS:
        await redis_connection.delete(message.chat.id)
        await state.storage.set_state(
            key=StorageKey(bot_id=message.bot.id, chat_id=student_id, user_id=student_id, thread_id=None,
                           business_connection_id=None, destiny='default')
        )

        await message.answer(
            "Диалог завершен", reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            chat_id=student_id,
            text="Специалист завершил диалог",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await bot.copy_message(
        from_chat_id=message.chat.id,
        chat_id=student_id,
        message_id=message.message_id,
        reply_markup=CANCEL_KEYBOARD,
    )
    return


@router.message(StateFilter(Conversation.active))
async def handle_student_chat(
        message: types.Message, state: FSMContext, bot: Bot, redis_connection: Redis
) -> None:
    student_id = message.chat.id

    data = await state.get_data()
    curator_id = data['curator_id']

    if message.text == CANCEL_KEYWORDS:
        await redis_connection.delete(curator_id)
        await state.clear()

        await message.answer(
            "Диалог завершен", reply_markup=types.ReplyKeyboardRemove()
        )
        await bot.send_message(
            chat_id=curator_id,
            text=f"Клиент {student_id} завершил диалог",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await bot.copy_message(
        from_chat_id=message.chat.id,
        chat_id=curator_id,
        message_id=message.message_id,
        reply_markup=CANCEL_KEYBOARD,
    )
