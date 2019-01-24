from abc import ABCMeta, abstractmethod
from typing import Mapping, AsyncIterable, AsyncGenerator, Union, AbstractSet
from typing import Any, Callable, Optional, Tuple, List
from typing import Awaitable

Scope = Mapping[str, Any]
Message = Mapping[str, Any]
Context = Optional[Mapping[str, Any]]
Info = Optional[Mapping[str, Any]]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

ASGIInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIInstance]

StartupHandler = Callable[[], Awaitable[None]]
ShutdownHandler = Callable[[], Awaitable[None]]
LifespanHandler = Callable[[Scope, Info, Message], Awaitable[None]]

Header = Tuple[bytes, bytes]
Headers = List[Header]

RouteMatches = Mapping[str, Any]
Content = AsyncIterable[bytes]
Reply = Callable[[int, List[Header], AsyncGenerator[bytes, None]], Awaitable[None]]


class WebSocket(metaclass=ABCMeta):

    @abstractmethod
    async def accept(self, subprotocol: Optional[str]) -> None:
        raise NotImplementedError


    @abstractmethod
    async def receive(self) -> Optional[Union[bytes, str]]:
        raise NotImplementedError


    @abstractmethod
    async def send(self, content: Union[bytes, str]) -> None:
        raise NotImplementedError


    @abstractmethod
    async def close(self, code: int = 1000) -> None:
        raise NotImplementedError


HttpRequestCallback = Callable[[Scope, Info, RouteMatches, Content, Reply], Awaitable[None]]
WebSocketRequestCallback = Callable[[Scope, Info, RouteMatches, WebSocket], Awaitable[None]]


# HttpRouteHandler = Callable[[Scope], Tuple[HttpRequestCallback, RouteMatches]]
# WebSocketRouteHandler = Callable[[Scope], Tuple[WebSocketRequestCallback, RouteMatches]]


class HttpRouteHandler(metaclass=ABCMeta):

    @abstractmethod
    def add(self, methods: AbstractSet[str], path: str, callback: HttpRequestCallback) -> None:
        raise NotImplementedError


    @abstractmethod
    def __call__(self, scope: Scope) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        raise NotImplementedError


class WebSocketRouteHandler(metaclass=ABCMeta):

    @abstractmethod
    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        raise NotImplementedError


    @abstractmethod
    def __call__(self, scope: Scope) -> Tuple[Optional[WebSocketRequestCallback], Optional[RouteMatches]]:
        raise NotImplementedError
