from aiohttp import web

from give_money_bot import __version__
from give_money_bot.config import cfg
from give_money_bot.utils.prometheus_middleware import metrics


async def version(request: web.Request) -> web.Response:
    return web.json_response({"version": __version__})


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def init_web_server() -> web.Application:
    app = web.Application()
    app.add_routes(
        [
            web.get('/metrics', metrics),
            web.get(f"{cfg.bot_url_path}/version", version),
            web.get(f"{cfg.bot_url_path}/health", health),
        ]
    )

    return app
