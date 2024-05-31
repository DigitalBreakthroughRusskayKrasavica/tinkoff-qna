"""Provide classes and functions for loading an application config."""
import logging
from dataclasses import dataclass

import toml

logger = logging.getLogger(__name__)

# You can replace this consts values with your own awesome ones :D
DEFAULT_SERVER_HOST: str = "0.0.0.0"
DEFAULT_SERVER_PORT: int = 8000
DEFAULT_SERVER_LOG_LEVEL: str = "info"


@dataclass(frozen=True)
class HttpServerConfig:
    """Represent the http server configuration.

    Attributes:
        host (str): The host of the server.
        port (int): The port of the server.
        log_level (str): The logging level of the server
    """

    host: str = DEFAULT_SERVER_HOST
    port: int = DEFAULT_SERVER_PORT
    log_level: str = DEFAULT_SERVER_LOG_LEVEL


@dataclass
class DbConfig:
    """Represent the database configuration.

    Attributes:
        user (str): The username for the database connection.
        password (str): The password for the database connection.
        name (str): The name of the database.
        host (str): The host IP address for the database.
        port (int): The port number for the database.
    """

    user: str
    password: str
    name: str
    host: str
    port: int

    def __post_init__(self) -> None:
        """Initialise database URI."""
        self.uri = (
            f"postgresql+asyncpg://{self.user}:{self.password}@"  # noqa
            f"{self.host}:{self.port}/{self.name}"  # noqa
        )


@dataclass
class RedisConfig:
    host: str
    port: str

    def __post_init__(self):
        self.dsn = f"redis://{self.host}:{self.port}/0"


def load_db_config(config_path: str) -> DbConfig:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)
    return DbConfig(**data["db"])
