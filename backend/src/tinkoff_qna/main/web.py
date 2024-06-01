"""Application entry point."""

import asyncio
import os
import sys

from tinkoff_qna.presentation.web.app_setup import (create_app,
                                                    create_http_server,
                                                    initialise_dependencies,
                                                    initialise_routers)
from tinkoff_qna.presentation.web.config import load_web_config

DEFAULT_CONFIG_PATH = ".configs/app.toml"


async def main() -> None:
    """Set up application and start http server."""
    config = load_web_config(os.getenv("TINKOFF_QNA_CONFIG_PATH") or DEFAULT_CONFIG_PATH)
    app = create_app(config.app)

    initialise_routers(app)
    initialise_dependencies(app, config)

    server = create_http_server(app, config.http_server)
    await server.serve()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
