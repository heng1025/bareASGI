from datetime import datetime
from bareasgi import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse
)
from bareasgi.application import DEFAULT_NOT_FOUND_RESPONSE
from bareasgi.basic_router import BasicHttpRouter


# noinspection PyUnusedLocal
async def ok_handler(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 200, None, None, None


def test_literal_paths():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/bar/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum')
    assert handler is not None


def test_literal_path_with_trailing_slash():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/bar/grum/', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum/')
    assert handler is not None


def test_variable_paths():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/{name}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum')
    assert handler is not None
    assert 'name' in matches
    assert matches['name'] == 'bar'


def test_variable_path_with_type():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/{id:int}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/123/grum')
    assert handler is not None
    assert 'id' in matches
    assert matches['id'] == 123


def test_variable_path_with_type_and_format():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/{date_of_birth:datetime:%Y-%m-%d}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/2001-12-31/grum')
    assert handler is not None
    assert 'date_of_birth' in matches
    assert matches['date_of_birth'] == datetime(2001, 12, 31)


def test_path_type():
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/ui/{rest:path}', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/ui/index.html')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == 'index.html'

    handler, matches = basic_route_handler.resolve('GET', '/ui/')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == ''

    handler, matches = basic_route_handler.resolve('GET', '/ui/folder/other.html')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == 'folder/other.html'
