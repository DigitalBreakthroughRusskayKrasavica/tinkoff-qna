import logging

from sqlalchemy import select, text, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tinkoff_qna.models import User, Role, QuestionAnswer

logger = logging.getLogger(__name__)


class DbRepository:
    __slots__ = ("_session_factory",)

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def user_exists(self, user_id: int) -> bool:
        async with self._session_factory() as session:
            stmt = select(User).where(User.telegram_id == user_id)
            res = await session.execute(stmt)
        return bool(res.scalar_one_or_none())

    async def add_user(self, user_id: int, role: Role = Role.CLIENT) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                session.add(User(telegram_id=user_id, role=role))

    async def get_user_by_id(self, user_id: int):
        async with self._session_factory() as session:
            user = await session.get_one(User, user_id)
        return user

    async def get_categories(self):
        async with self._session_factory() as session:
            stmt = select(QuestionAnswer.category)
            res = await session.scalars(stmt)
        return res.all()

    async def get_all_support_technicians(self):
        async with self._session_factory() as session:
            stmt = select(User.telegram_id).where(User.role == Role.SUPPORT_TECHNICIAN)
            res = await session.scalars(stmt)
        return res.all()

    async def add_new_pair(self, question, embeddings, category, answer):
        async with self._session_factory() as session:
            stmt = select(Answer.id).order_by(desc(Answer.id)).limit(1)
            ans_last_id = await session.scalar(stmt)

            ans = Answer(
                id=ans_last_id + 1,
                answer=answer
            )
            session.add(ans)
            await session.flush([ans])

            session.add(
                QuestionAnswer(
                    question=question,
                    embedding=embeddings,
                    category=category,
                    answer_class=ans.id,
                )
            )
            await session.commit()

    async def change_role(self, user_id, role):
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            user.role = role
            session.add(user)
            await session.commit()