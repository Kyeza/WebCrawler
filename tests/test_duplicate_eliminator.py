import fakeredis
import pytest

from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url
from webcrawler_arnoldkyeza.core.utils import normalize_url, calculate_text_checksum


@pytest.fixture
def fake_redis() -> fakeredis.FakeStrictRedis:
    return fakeredis.FakeStrictRedis()


@pytest.fixture
def duplicate_eliminator(fake_redis: fakeredis.FakeStrictRedis) -> DuplicateEliminator:
    return DuplicateEliminator(redis=fake_redis)


@pytest.fixture
def sample_html_content() -> str:
    return "<html><body>Hello World</body></html>"


@pytest.fixture
def extracted_urls() -> list[str]:
    return [
        "http://Example.com/path/?b=2&a=1",
        "http://example.com/path?a=1&b=2",
        # Unsupported scheme → dropped
        "mailto:user@example.com",
        # Non-default port → dropped by normalizer
        "http://example.com:8080/path",
        # Valid https without query (trailing slash removed)
        "https://example.com/path/",
        # Duplicates of http form
        "http://example.com/path",
        "http://example.com:80/path",
        # Another distinct https URL with sorted query params
        "https://example.com:443/path?c=3&b=2&a=1",
    ]



def test_is_duplicate_url(fake_redis, duplicate_eliminator):
    de = duplicate_eliminator
    redis = fake_redis
    original = "http://Example.com/path/?b=2&a=1"
    normalized = normalize_url(original)
    assert normalized == "http://example.com/path?a=1&b=2"

    assert de.is_duplicate_url(normalized) is False

    checksum = calculate_text_checksum(normalized)
    assert redis.sismember("crawler:visited_urls", checksum)

    assert de.is_duplicate_url(normalized) is True


def test_is_duplicate_content(fake_redis, duplicate_eliminator, sample_html_content):
    redis = fake_redis
    de = duplicate_eliminator
    content = sample_html_content

    assert de.is_duplicate_content(content) is False

    checksum = calculate_text_checksum(content)
    assert redis.sismember("crawler:seen_content", checksum)

    assert de.is_duplicate_content(content) is True


def test_filter_extracted_urls_filters_invalid_and_duplicates(fake_redis, duplicate_eliminator, extracted_urls):
    redis = fake_redis
    de = duplicate_eliminator
    parent_url_id = 123
    depth = 2

    filtered = de.filter_extracted_urls(extracted_urls, parent_url_id=parent_url_id, depth=depth)

    expected_norm = {
        "http://example.com/path?a=1&b=2",
        "http://example.com/path",
        "https://example.com/path",
        "https://example.com/path?a=1&b=2&c=3",
    }
    assert isinstance(filtered, list)
    assert {u.normalized_url for u in filtered} == expected_norm
    assert all(isinstance(u, Url) for u in filtered)
    assert all(u.parent_url_id == parent_url_id for u in filtered)
    assert all(u.depth == depth for u in filtered)

    for norm in expected_norm:
        checksum = calculate_text_checksum(norm)
        assert redis.sismember("crawler:visited_urls", checksum)

    # Running the filter again on already-seen URLs should yield nothing new
    filtered_again = de.filter_extracted_urls([
        "http://example.com/path?b=2&a=1",
        "https://example.com/path",
        "https://example.com/path?a=1&b=2&c=3",
    ], parent_url_id=parent_url_id, depth=depth)
    assert filtered_again == []
