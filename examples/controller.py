import json
import logging
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_reader,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


class InfoController:

    def add_routes(self, app: Application):
        app.http_router.add({'GET'}, '/info', self.get_info)
        app.http_router.add({'POST'}, '/info', self.set_info)


    async def get_info(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        text = json.dumps(info)
        return 200, [(b'content-type', b'application/json')], text_writer(text)


    async def set_info(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        text = await text_reader(content)
        data = json.loads(text)
        info.update(data)
        return 204, None, None


if __name__ == "__main__":
    import uvicorn

    app = Application(info={'name': 'Michael Caine'})

    info_controller = InfoController()
    info_controller.add_routes(app)

    uvicorn.run(app, port=9009)