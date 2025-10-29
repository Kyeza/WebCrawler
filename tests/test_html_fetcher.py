import asyncio
import pytest
import requests

from webcrawler_arnoldkyeza.core.html_fetcher.html_fetcher import HTMLFetcher
from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.http_handler import (
    HTTPProtocolHandler,
)
from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.protocol_handler import (
    ProtocolHandler,
)
from webcrawler_arnoldkyeza.core.html_fetcher.protocol_handlers.errrors import (
    UnsupportedContentTypeError,
)


def test_html_fetcher_delegates_to_handler(mocker):
    handler = mocker.Mock(spec=ProtocolHandler)
    handler.get_content = mocker.AsyncMock(return_value="fetched")
    fetcher = HTMLFetcher(handler=handler)
    data = "https://example.com"

    result = asyncio.run(fetcher.fetch(data))

    handler.get_content.assert_awaited_once_with(data)
    assert result == "fetched"


def test_http_handler_returns_none_for_non_http_schemes():
    handler = HTTPProtocolHandler()

    result = asyncio.run(handler.get_content("ftp://example.com/resource"))

    assert result is None


def test_http_handler_fetches_html_success(mocker):
    response = mocker.Mock()
    response.raise_for_status = mocker.Mock()
    response.headers = {"Content-Type": "text/html; charset=utf-8"}
    response.text = "<html><body>OK</body></html>"
    mocker.patch("requests.get", return_value=response)

    handler = HTTPProtocolHandler()

    content = asyncio.run(handler.get_content("https://example.com"))

    response.raise_for_status.assert_called_once()
    assert content == response.text


def test_http_handler_unsupported_content_type_raises(mocker):
    response = mocker.Mock()
    response.raise_for_status = mocker.Mock()
    response.headers = {"Content-Type": "application/json"}
    response.text = 'Content'
    mocker.patch("requests.get", return_value=response)

    handler = HTTPProtocolHandler()

    with pytest.raises(UnsupportedContentTypeError):
        asyncio.run(handler.get_content("https://example.com"))


def test_http_handler_request_exception_raises_value_error(mocker):
    mocker.patch("requests.get", side_effect=requests.RequestException("Error"))
    handler = HTTPProtocolHandler()

    with pytest.raises(ValueError) as err:
        asyncio.run(handler.get_content("https://example.com"))

    assert "Error fetching content" in str(err.value)
