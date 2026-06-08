from typing import Any, Optional, Tuple, Type

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType

try:
    from python_socks import ProxyError, ProxyConnectionError, ProxyTimeoutError

    _PROXY_ERRORS: Tuple[Type[BaseException], ...] = (
        ProxyError,
        ProxyConnectionError,
        ProxyTimeoutError,
    )
except ImportError:  # pragma: no cover - python_socks is always installed via aiohttp-socks
    _PROXY_ERRORS = ()


class ResilientAiohttpSession(AiohttpSession):
    """``AiohttpSession`` that maps proxy/SOCKS errors to ``TelegramNetworkError``.

    aiogram only converts ``asyncio.TimeoutError`` and ``aiohttp.ClientError`` into
    ``TelegramNetworkError``. Errors raised by ``aiohttp_socks`` / ``python_socks``
    (e.g. ``ProxyTimeoutError`` when the SOCKS proxy is briefly unreachable) are plain
    ``Exception`` subclasses, so they escape both that conversion and aiogram's polling
    backoff loop — which only retries ``TelegramNetworkError``/``TelegramServerError``.

    The result was that a single proxy hiccup raised an unhandled exception inside the
    fire-and-forget ``start_polling`` task, killing it silently while the process (and the
    Docker container) kept running, so the bot never reconnected.

    Re-raising proxy errors as ``TelegramNetworkError`` lets aiogram's built-in
    retry/backoff handle them just like any other transient network failure.
    """

    async def make_request(
        self, bot: Bot, method: TelegramMethod[TelegramType], timeout: Optional[int] = None
    ) -> Any:
        try:
            return await super().make_request(bot, method, timeout=timeout)
        except _PROXY_ERRORS as e:
            raise TelegramNetworkError(
                method=method, message=f"Proxy error: {type(e).__name__}: {e}"
            ) from e
