import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

REQUESTS = Counter(
    "givemoneybot_requests_total",
    "Total count of processed messages by method and user",
    ["user_id", "username", "method", "package"],
)

REQUESTS_PROCESSING_TIME = Histogram(
    "givemoneybot_requests_processing_time_seconds",
    "Histogram of requests processing time by method and user (in seconds)",
    ["user_id", "username", "method", "package"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "givemoneybot_requests_in_progress",
    "Gauge of requests by method and user currently being processed",
    ["user_id", "username", "method", "package"],
)


async def metrics(request: web.Request) -> web.Response:
    exposition = generate_latest()
    return web.Response(body=exposition, headers={'Content-Type': CONTENT_TYPE_LATEST})


class PrometheusMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = data['event_from_user'].id
        username = data['user'].name  # data['event_from_user'].username
        method = data['handler'].callback.__name__
        package = data['handler'].callback.__module__.split('.')[-2]

        REQUESTS_IN_PROGRESS.labels(user_id=user_id, username=username, method=method, package=package).inc()
        REQUESTS.labels(user_id=user_id, username=username, method=method, package=package).inc()

        before_time = time.perf_counter()
        response = await handler(event, data)
        after_time = time.perf_counter()

        REQUESTS_PROCESSING_TIME.labels(user_id=user_id, username=username, method=method, package=package).observe(
            after_time - before_time
        )
        REQUESTS_IN_PROGRESS.labels(user_id=user_id, username=username, method=method, package=package).dec()

        return response

    # async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
    #     method = request.method
    #     path_template, is_handled_path = self.get_path_template(request)
    #
    #     if self._is_path_filtered(is_handled_path):
    #         return await call_next(request)
    #
    #     REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).inc()
    #     REQUESTS.labels(method=method, path_template=path_template).inc()
    #
    #     before_time = time.perf_counter()
    #     try:
    #         response = await call_next(request)
    #     except BaseException as e:
    #         status_code = HTTP_500_INTERNAL_SERVER_ERROR
    #         EXCEPTIONS.labels(method=method, path_template=path_template, exception_type=type(e).__name__).inc()
    #         raise e from None
    #     else:
    #         status_code = response.status_code
    #         after_time = time.perf_counter()
    #         REQUESTS_PROCESSING_TIME.labels(method=method, path_template=path_template).observe(
    #             after_time - before_time
    #         )
    #     finally:
    #         RESPONSES.labels(method=method, path_template=path_template, status_code=status_code).inc()
    #         REQUESTS_IN_PROGRESS.labels(method=method, path_template=path_template).dec()
    #
    #     return response
