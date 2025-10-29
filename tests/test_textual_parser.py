import pytest

from webcrawler_arnoldkyeza.core.extractor.content_parser.textual_parser import TextualParser
from webcrawler_arnoldkyeza.core.extractor.content_parser.parser_result import ParserResult


def test_textual_parser_parses_basic_html_with_links():
    html = (
        """
        <html>
          <head>
            <title>Hello World</title>
          </head>
          <body>
            <h1>Welcome</h1>
            <p>Some paragraph.</p>
            <a href="https://example.com/page">Example</a>
            <a href="/relative/path">Rel</a>
            <a>No href here</a>
          </body>
        </html>
        """
    )

    result = TextualParser.parse(html)

    assert isinstance(result, ParserResult)
    # Title is lowercased and spaces become underscores
    assert result.title == "hello_world"
    # Body text is captured; we don't assert exact formatting, just key substrings
    assert "Welcome" in result.content
    assert "Some paragraph." in result.content
    # hrefs are extracted in DOM order; missing href yields None
    assert result.extracted_urls == [
        "https://example.com/page",
        "/relative/path",
        None,
    ]


def test_textual_parser_handles_no_links():
    html = (
        """
        <html>
          <head><title>Empty</title></head>
          <body>
            <div>No anchors here</div>
          </body>
        </html>
        """
    )

    result = TextualParser.parse(html)

    assert result.title == "empty"
    assert isinstance(result.extracted_urls, list)
    assert result.extracted_urls == []
