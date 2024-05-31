from aiogram.fsm.state import State, StatesGroup


class Conversation(StatesGroup):
    active = State()


class NewPairForm(StatesGroup):
    question = State()
    category = State()
    answer = State()

