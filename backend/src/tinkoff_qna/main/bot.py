import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from tinkoff_qna.services import HelperService

from tinkoff_qna.presentation.bot.config import load_bot_config
from tinkoff_qna.presentation.bot.middlewares import DIMiddleware
from tinkoff_qna.presentation.bot.middlewares.auth import AuthMiddleware

from tinkoff_qna.database.repository import DbRepository
from tinkoff_qna.database.sa_utils import create_engine, create_session_maker
from tinkoff_qna.lms.rubert.get_answer import BertModel

from tinkoff_qna.presentation.bot.router import router
from tinkoff_qna.presentation.bot.handlers.curators import router as curator_router
from tinkoff_qna.presentation.bot.handlers.conversation import router as conversation_router

from redis.asyncio import Redis

DEFAULT_CONFIG_PATH = ".configs/app.toml"
LOGGING_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
    cfg = load_bot_config(os.getenv("CURATOR_SUPPORT_CONFIG_PATH") or DEFAULT_CONFIG_PATH)

    storage = RedisStorage.from_url(cfg.redis.dsn)
    storage.key_builder = DefaultKeyBuilder(with_destiny=True)

    dp = Dispatcher(storage=storage)
    dp.include_router(curator_router)
    dp.include_router(conversation_router)
    dp.include_router(router)

    engine = create_engine(cfg.db.uri)
    session_factory = create_session_maker(engine)

    db_repo = DbRepository(session_factory)
    bert_model = BertModel(cfg.db.uri)

    helper_service = HelperService(db_repo, bert_model)

    redis_connection = Redis.from_url(cfg.redis.dsn)

    dp.message.outer_middleware(AuthMiddleware(repo=db_repo, curator_secret_key=cfg.support_tech_auth_key))
    dp.update.outer_middleware(DIMiddleware(
        service=helper_service,
        repo=db_repo,
        redis_connection=redis_connection,
    ))

    bot = Bot(token=cfg.token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
