import asyncio
from typing import Optional, AsyncIterable, Tuple, Sequence
import logging
from baretypes import (
    HttpInternalError,
    HttpDisconnectError,
    Scope,
    Info,
    Send,
    Receive,
    Headers,
    HttpRouter,
    Context,
    HttpMiddlewareCallback
)
from .middleware import mw
from .utils import anext

logger = logging.getLogger(__name__)


async def _body_iterator(receive: Receive, body: bytes, more_body: bool) -> AsyncIterable[bytes]:
    yield body
    while more_body:
        request = await receive()
        request_type = request['type']
        logger.debug(f'Received {request_type}', extra=request)

        if request_type == 'http.request':
            body, more_body = request.get('body', b''), request.get('more_body', False)
            yield body
        elif request_type == 'http.disconnect':
            raise HttpDisconnectError
        else:
            logger.error(f'Failed to understand request type "{request_type}', extra=request)
            raise HttpInternalError


class HttpInstance:

    def __init__(self, scope: Scope, context: Context, info: Info) -> None:
        self.scope = scope
        self.info = info
        # Find the route.
        http_router: HttpRouter = context['router']
        self.request_callback, self.matches = http_router.resolve(scope['method'], scope['path'])
        # Apply middleware.
        middleware: Optional[Sequence[HttpMiddlewareCallback]] = context['middlewares']
        if middleware:
            self.request_callback = mw(*middleware, handler=self.request_callback)

    @property
    def _is_http_push_supported(self) -> bool:
        return self.scope['http_version'] == '2' and 'http.response.push' in self.scope.get('extensions', {})

    async def _send_response(
            self,
            send: Send,
            status: int,
            headers: Optional[Headers] = None,
            body: Optional[AsyncIterable[bytes]] = None,
            pushes: Optional[Sequence[Tuple[str, Headers]]] = None
    ) -> None:
        # Create and send the start response.
        response_start = {'type': 'http.response.start', 'status': status}
        if headers:
            response_start['headers'] = headers
        logger.debug(f'Sending "http.response.start" with status {status}', extra=response_start)
        await send(response_start)

        if pushes is not None and self._is_http_push_supported:
            for push_path, push_headers in pushes:
                logger.debug(f'sending "http.response.push" for path "{push_path}')
                await send({
                    'type': 'http.response.push',
                    'path': push_path,
                    'headers': push_headers
                })

        # Create and send the response body.
        response_body = {'type': 'http.response.body'}

        # If we don't get a body, just send the basic response.
        try:
            buf = await anext(body) if body else None
        except StopAsyncIteration:
            buf = None
        if buf is None:
            logger.debug(f'Sending "http.response.body" with empty body', extra=response_body)
            await send(response_body)
            return

        # Continue to get and send the body until exhausted.
        while buf is not None:
            response_body['body'] = buf
            try:
                buf = await anext(body)
                response_body['more_body'] = True
            except StopAsyncIteration:
                buf = None
                response_body['more_body'] = False
            logger.debug(f'Sending "http.response.body" with more_body="{response_body["more_body"]}',
                         extra=response_body)
            if len(response_body['body']) > 0:
                await send(response_body)

    async def __call__(self, receive: Receive, send: Send) -> None:

        logger.debug('start handling request')

        try:
            request = await receive()
            if request['type'] != 'http.request':
                raise HttpInternalError('Expected http.request')

            response = await self.request_callback(
                self.scope,
                self.info,
                self.matches,
                _body_iterator(receive, request.get('body', b''), request.get('more_body', False))
            )

            send_task = asyncio.create_task(self._send_response(send, *response))
            receive_task = asyncio.create_task(receive())
            tasks = [send_task, receive_task]

            is_connected = True

            while is_connected:

                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = pending

                if receive_task in done:
                    request = receive_task.result()
                    if request['type'] != 'http.disconnect':
                        raise HttpInternalError('Expected http.disconnect')

                    logger.debug('diconnecting')

                    for task in pending:
                        task.cancel()

                    is_connected = False

            logger.debug('finish handling request')
        except:
            logger.exception('Failed to process http request')
