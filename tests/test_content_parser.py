import pytest

from webcrawler_arnoldkyeza.core.extractor.content_parser.content_parser import (
    ContentParser,
)

def test_content_parser_parse_returns_none_by_default():
    parser = ContentParser()
    assert parser.parse("anything") is None
