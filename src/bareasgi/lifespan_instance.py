from typing import List, Optional
from bareasgi.types import (
    Context,
    Info,
    Scope,
    Send,
    Receive,
    LifespanHandler
)


class LifespanInstance:

    def __init__(self, scope: Scope, context: Optional[Context] = None, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.context = context or {}
        self.info = info or {}


    async def __call__(self, receive: Receive, send: Send) -> None:
        # The lifespan scope exists for the duration of the event loop, and only exits on 'lifespan.shutdown'.
        request = None
        while request and request['type'] != 'lifespan.shutdown':
            # Fetch the lifespan request
            request = await receive()

            # Run the handlers for this action.
            handlers: List[LifespanHandler] = self.context.get(request['type'], [])
            for handler in handlers:
                await handler(self.scope, self.info, request)

            # Send the response
            await send({'type': f'{request["type"]}.complete'})