import asyncio
import logging
import os
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('server_sent_events')


# noinspection PyUnusedLocal
async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 303, [(b'Location', b'/example1')], None


# noinspection PyUnusedLocal
async def test_page1(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 1</title>
  </head>
  <body>
    <h1>Example 1</h1>
    
    <p>This is simple<p>
  </body>
</html>

"""
    return 200, [(b'content-type', b'text/html')], text_writer(html)


# noinspection PyUnusedLocal
async def test_page2(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 2</title>
  </head>
  <body>
    <h1>Example 2</h1>

    <p>This is simple<p>
  </body>
</html>

"""
    return 200, [(b'content-type', b'text/html')], text_writer(html), None


if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/example1', test_page1)
    app.http_router.add({'GET'}, '/example2', test_page2)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    USE_UVICORN = False

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        config = Config()
        config.bind = ["ugsb-rbla01.bhdgsystematic.com:9009"]
        config.certfile = os.path.expanduser("~/.keys/ugsb-rbla01.crt")
        config.keyfile = os.path.expanduser("~/.keys/ugsb-rbla01.key")
        asyncio.run(serve(app, config))
