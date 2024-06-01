from dataclasses import dataclass

import toml
from tinkoff_qna.config import DbConfig, RedisConfig


@dataclass(frozen=True)
class BotConfig:
    token: str
    llm_api_key: str
    support_tech_auth_key: str
    db: DbConfig
    redis: RedisConfig



def load_bot_config(config_path: str) -> BotConfig:
    """Load configuration from a TOML file.

    Returns:
        Config: An instance of the Config class containing the loaded configuration.
    """
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)
    return BotConfig(
        llm_api_key=data['llm_api_key'],
        **data["bot"],
        db=DbConfig(**data["db"]),
        redis=RedisConfig(**data["redis"])
    )
