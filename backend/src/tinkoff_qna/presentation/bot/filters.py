from aiogram import types
from aiogram.filters import Filter
from tinkoff_qna.database.repository import DbRepository
from tinkoff_qna.models import Role


class SupportTechFilter(Filter):
    async def __call__(self, message: types.Message, repo: DbRepository) -> bool:
        user_id = message.chat.id
        user = await repo.get_user_by_id(user_id)

        return user.role == Role.SUPPORT_TECHNICIAN
