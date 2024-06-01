"""Contain functions required for configuration of the project components."""
from functools import partial

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from tinkoff_qna.config import HttpServerConfig
from tinkoff_qna.database.dependencies import get_session
from tinkoff_qna.database.repository import DbRepository
from tinkoff_qna.database.sa_utils import create_engine, create_session_maker
from tinkoff_qna.lms.rubert.get_answer import BertModel
from tinkoff_qna.services import HelperService

from .config import AppConfig, WebConfig
from .depends_stub import Stub
from .router import router


class MsgResponse(BaseModel):
    """Represent a simple string message response.

    Attributes:
        msg (str): The message itself.
    """

    msg: str


def initialise_routers(app: FastAPI) -> None:
    """Include all routers to the app.

    Args:
        app (FastAPI): The FastAPI instance.
    """
    app.include_router(router)


def initialise_dependencies(app: FastAPI, web_cfg: WebConfig) -> None:
    """Initialise the dependencies in the app.

    Args:
        app (FastAPI): The FastAPI instance.
        web_cfg (WebConfig): The web config instance.
    """
    engine = create_engine(web_cfg.db.uri)
    session_factory = create_session_maker(engine)
    helper_service = HelperService(
        db_repo=DbRepository(session_factory),
        rubert_model=BertModel(web_cfg.db.uri, web_cfg.llm_api_key)
    )

    app.dependency_overrides[Stub(AsyncSession)] = partial(get_session, session_factory)
    app.dependency_overrides[Stub(WebConfig)] = lambda: web_cfg

    app.dependency_overrides[Stub(HelperService)] = lambda: helper_service


def create_app(app_cfg: AppConfig) -> FastAPI:
    """Create a FastAPI instance.

    Args:
        app_cfg (WebConfig): The app configuration.

    Returns:
        FastAPI: The created FastAPI instance.
    """
    app = FastAPI(
        title=app_cfg.title,
        description=app_cfg.description,
        version=app_cfg.version,
    )
    return app


def create_http_server(
        app: FastAPI, http_server_cfg: HttpServerConfig
) -> uvicorn.Server:
    """Create uvicorn HTTP server instance.

    Args:
        app (FastAPI): The FastAPI instance.
        http_server_cfg (HttpServerConfig): The HTTP server configuration.

    Returns:
        uvicorn.Server: The created Uvicorn server instance.
    """
    uvicorn_config = uvicorn.Config(
        app,
        host=http_server_cfg.host,
        port=http_server_cfg.port,
        log_level=http_server_cfg.log_level,
    )
    return uvicorn.Server(uvicorn_config)
