from datetime import datetime
from enum import StrEnum

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT, FLOAT
from sqlalchemy.orm import Mapped, mapped_column
from tinkoff_qna.database.base import Base


class Role(StrEnum):
    CLIENT = "client"
    SUPPORT_TECHNICIAN = "support_technician"


class User(Base):  # type: ignore[misc]
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, autoincrement=False
    )
    role: Mapped[Role] = mapped_column(default=Role.CLIENT)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


class QuestionAnswer(Base):
    __tablename__ = "question_answer"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column()
    source: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column(nullable=True)
    parent_title: Mapped[str] = mapped_column()
    product: Mapped[str] = mapped_column()
    parent_url: Mapped[str] = mapped_column()
    type_: Mapped[str] = mapped_column(name='type')
    embedding: Mapped[list[float]] = mapped_column(type_=ARRAY(FLOAT, dimensions=1))
    answer: Mapped[str] = mapped_column()
