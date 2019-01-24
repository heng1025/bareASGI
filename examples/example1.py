from bareasgi import Application, text_reader, text_writer
from bareasgi.types import (
    Scope,
    Info,
    RouteMatches,
    Content,
    Reply,
    WebSocket
)


async def http_request_callback(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        reply: Reply) -> None:
    print('Start', scope, info, matches)
    text = await text_reader(content)
    print(text)
    await reply(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))
    print('End')


async def web_socket_request_callback(scope: Scope, info: Info, matches: RouteMatches, web_socket: WebSocket) -> None:
    print('Start', scope, info, matches, web_socket)
    print('End')


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_route_handler.add({'GET', 'POST', 'PUT', 'DELETE'}, '/{path}', http_request_callback)
    app.ws_route_handler.add('/{path}', web_socket_request_callback)

    uvicorn.run(app, port=9009)
