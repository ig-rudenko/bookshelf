import time
from typing import Callable
from uuid import uuid4

from fastapi import Response, Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware


class AsyncIteratorWrapper:
    """The following is a utility class that transforms a
    regular iterable to an asynchronous one.

    link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для обработки запросов и ответов с целью журналирования
    """

    def __init__(self, app: FastAPI, *, logger) -> None:
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        request_id: str = str(uuid4())
        logging_dict = {
            "X-API-REQUEST-ID": request_id  # X-API-REQUEST-ID maps each request-response to a unique ID
        }

        response, response_dict = await self._log_response(
            call_next, request, request_id
        )
        request_dict = await self._log_request(request)
        logging_dict["request"] = request_dict
        logging_dict["response"] = response_dict

        self._logger.info(request_id, **logging_dict)

        return response

    @staticmethod
    async def _log_request(request: Request) -> dict:
        """Logs request part"""
        request_logging = {
            "method": request.method,
            "url": {
                "path": request.url.path,
                "query": request.query_params,
            },
            "client": {
                "address": request.client.host,
                "port": request.client.port,
            },
            "user_agent": {
                "original": request.headers.get("User-Agent"),
            },
        }
        return request_logging

    async def _log_response(
        self, call_next: Callable, request: Request, request_id: str
    ) -> tuple[Response, dict]:
        """Logs response part

        :param call_next: Callable (To execute the actual path function and get response back)
        :param request: Request
        :param request_id: str (uuid)
        :return: Response, dict
        """

        start_time = time.perf_counter()
        response = await self._execute_request(call_next, request, request_id)
        finish_time = time.perf_counter()

        overall_status = "successful" if response.status_code < 400 else "failed"
        execution_time = finish_time - start_time

        response_logging = {
            "status": overall_status,
            "status_code": response.status_code,
            "time_taken": f"{execution_time:0.4f}s",
            "mime_type": response.headers.get("Content-Type"),
        }

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

        # try:
        #     resp_body = json.loads(resp_body[0].decode())
        # except:
        #     resp_body = str(resp_body)

        response_logging["body"] = {
            # "content": resp_body,  # No content
            "bytes": sum(map(len, resp_body)),
        }

        return response, response_logging

    async def _execute_request(
        self, call_next: Callable, request: Request, request_id: str
    ) -> Response:
        """Executes the actual path function using call_next.
        It also injects "X-API-Request-ID" header to the response.

        :param call_next: Callable (To execute the actual path function and get response back)
        :param request: Request
        :param request_id: str (uuid)
        :return: Response
        """
        try:
            response: Response = await call_next(request)

            # Kickback X-Request-ID
            response.headers["X-API-Request-ID"] = request_id
            return response

        except Exception as e:
            self._logger.exception(
                {"path": request.url.path, "method": request.method, "reason": e}
            )
