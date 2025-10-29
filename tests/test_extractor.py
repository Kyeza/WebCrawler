from webcrawler_arnoldkyeza.core.extractor.extractor import Extractor
from webcrawler_arnoldkyeza.core.extractor.content_parser.content_parser import ContentParser
from webcrawler_arnoldkyeza.core.extractor.content_parser.textual_parser import TextualParser
from webcrawler_arnoldkyeza.core.extractor.content_parser.parser_result import ParserResult


def test_extractor_delegates_to_parser(mocker):
    fake_parser = mocker.Mock(spec=ContentParser)
    expected = None
    fake_parser.parse.return_value = expected
    extractor = Extractor(parser=fake_parser)

    payload = "<html></html>"
    result = extractor.extract(payload)

    # Assert
    fake_parser.parse.assert_called_once_with(payload)
    assert result is expected


def test_extractor_with_textual_parser_integration():
    html = """
    <html>
      <head><title>Sample Title</title></head>
      <body>
        <a href="/link1">Link One</a>
        <a href="/link2">Link Two</a>
      </body>
    </html>
    """
    extractor = Extractor(parser=TextualParser())
    result = extractor.extract(html)

    assert isinstance(result, ParserResult)
    assert result.title == "sample_title"
    assert result.extracted_urls == ["/link1", "/link2"]
