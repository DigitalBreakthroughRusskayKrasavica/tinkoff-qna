# You can replace this consts values with your own awesome ones :D
from dataclasses import dataclass

import toml

from tinkoff_qna.config import DbConfig, HttpServerConfig

DEFAULT_APP_TITLE: str = "tinkoff_qna"
DEFAULT_APP_DESCRIPTION: str = "Server part of the tinkoff_qna."
DEFAULT_APP_VERSION: str = "0.0.1"


@dataclass(frozen=True, kw_only=True)
class AppConfig:
    """Represent the web application configuration.

    Attributes:
        title (str): The title of the application.
        description (str): The description of the application.
        jwt_secret (str): The JWT secret key for authentication.
    """

    title: str = DEFAULT_APP_TITLE
    description: str = DEFAULT_APP_DESCRIPTION
    version: str = DEFAULT_APP_VERSION
    jwt_secret: str
    jwt_lifetime_seconds: int = 60 * 60


@dataclass(frozen=True, kw_only=True)
class WebConfig:
    app: AppConfig
    http_server: HttpServerConfig
    db: DbConfig


def load_web_config(config_path: str) -> WebConfig:
    """Load configuration from a TOML file.

    Returns:
        Config: An instance of the Config class containing the loaded configuration.
    """
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)
    return WebConfig(
        app=AppConfig(**data["app"]),
        http_server=HttpServerConfig(**data["http_server"]),
        db=DbConfig(**data["db"]),
    )

