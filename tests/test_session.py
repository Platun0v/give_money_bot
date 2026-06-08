import asyncio
from typing import Any

import pytest
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from python_socks import ProxyConnectionError, ProxyError, ProxyTimeoutError

from give_money_bot.utils.session import ResilientAiohttpSession


def _run(coro: Any) -> Any:
    return asyncio.new_event_loop().run_until_complete(coro)


@pytest.mark.parametrize(
    "exc",
    [
        ProxyTimeoutError("Proxy connection timed out: 60"),
        ProxyConnectionError("Could not connect to proxy"),
        ProxyError("generic proxy error"),
    ],
)
def test_proxy_error_becomes_network_error(monkeypatch: Any, exc: Exception) -> None:
    """Proxy/SOCKS errors must surface as TelegramNetworkError so aiogram retries them."""

    async def boom(self: Any, bot: Any, method: Any, timeout: Any = None) -> Any:
        raise exc

    monkeypatch.setattr(AiohttpSession, "make_request", boom)

    session = ResilientAiohttpSession(proxy="socks5://127.0.0.1:1080")
    with pytest.raises(TelegramNetworkError):
        _run(session.make_request(bot=object(), method=object()))


def test_non_proxy_error_passes_through(monkeypatch: Any) -> None:
    """Unrelated errors must not be swallowed/relabelled."""

    async def boom(self: Any, bot: Any, method: Any, timeout: Any = None) -> Any:
        raise ValueError("something else")

    monkeypatch.setattr(AiohttpSession, "make_request", boom)

    session = ResilientAiohttpSession(proxy="socks5://127.0.0.1:1080")
    with pytest.raises(ValueError):
        _run(session.make_request(bot=object(), method=object()))


def test_success_passes_through(monkeypatch: Any) -> None:
    async def ok(self: Any, bot: Any, method: Any, timeout: Any = None) -> Any:
        return "result"

    monkeypatch.setattr(AiohttpSession, "make_request", ok)

    session = ResilientAiohttpSession(proxy="socks5://127.0.0.1:1080")
    assert _run(session.make_request(bot=object(), method=object())) == "result"
