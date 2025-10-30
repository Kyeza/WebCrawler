import datetime
from pathlib import Path

import pytest

from webcrawler_arnoldkyeza.core.datastore.database_manager import DatabaseManager
from webcrawler_arnoldkyeza.core.enums.url_status_type import UrlStatusType
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_crawler.sqlite"


@pytest.fixture
def db(db_path: Path) -> DatabaseManager:
    return DatabaseManager(db_path)


def make_url(
    url: str,
    normalized_url: str,
    *,
    priority: int = 1,
    update_frequency: int = 1,
    last_crawled_at: datetime.datetime | None = None,
    status: UrlStatusType = UrlStatusType.PENDING,
    parent_url_id: int | None = None,
    error_message: str | None = None,
    depth: int = 0,
) -> Url:
    return Url(
        url=url,
        normalized_url=normalized_url,
        priority=priority,
        update_frequency=update_frequency,
        last_crawled_at=last_crawled_at,
        status=status,
        parent_url_id=parent_url_id,
        error_message=error_message,
        depth=depth,
    )


def test_init_creates_db_file_and_schema(db_path: Path) -> None:
    assert not db_path.exists()

    manager = DatabaseManager(db_path)

    assert db_path.exists()

    test_url = make_url("https://example.com", "https://example.com")
    manager.insert_url(test_url)
    fetched_url: Url = manager.get_url(test_url.normalized_url)

    assert fetched_url is not None
    assert fetched_url.normalized_url == test_url.normalized_url


def test_insert_url_and_get_url(db: DatabaseManager) -> None:
    test_url = make_url("https://example.com/a", "https://example.com/a", priority=5)

    db.insert_url(test_url)

    fetched_url = db.get_url(test_url.normalized_url)

    assert fetched_url is not None
    assert fetched_url.url == test_url.url
    assert fetched_url.normalized_url == test_url.normalized_url
    assert fetched_url.priority == test_url.priority


def test_insert_duplicate_is_ignored(db: DatabaseManager) -> None:
    test_url = make_url("https://example.com/a", "https://example.com/a")

    db.insert_url(test_url)
    db.insert_url(test_url)

    with db._connect() as conn:
        cur = conn.execute(
            "SELECT COUNT(1) AS num_of_urls FROM urls WHERE normalized_url = ?",
            (test_url.normalized_url,),
        )
        result = cur.fetchone()
    assert result is not None
    assert result["num_of_urls"]  == 1


def test_url_exists_true_false(db: DatabaseManager) -> None:
    norm = "https://example.com/exists"
    assert db.url_exists(norm) is False

    db.insert_url(make_url(norm, norm))
    assert db.url_exists(norm) is True


def test_get_pending_urls_filters_orders_and_limits(db: DatabaseManager) -> None:
    db.insert_url(make_url("https://example.com/p1", "norm1", priority=1))
    db.insert_url(make_url("https://example.com/p3", "norm3", priority=3))
    db.insert_url(make_url("https://example.com/p2", "norm2", priority=2))
    completed = make_url("https://example.com/done", "done", status=UrlStatusType.COMPLETED)
    db.insert_url(completed)

    results = db.get_pending_urls(limit=2)

    assert len(results) == 2

    first, second = results
    assert first.status == UrlStatusType.PENDING.value
    assert second.status == UrlStatusType.PENDING.value
    assert first.priority <= second.priority
    assert {first.normalized_url, second.normalized_url}.isdisjoint({completed.normalized_url})


def test_update_url_status(db: DatabaseManager) -> None:
    test_norm_url = "https://example.com/to-start"
    db.insert_url(make_url(test_norm_url, test_norm_url))

    fetched_url_before_update = db.get_url(test_norm_url)
    assert fetched_url_before_update is not None
    assert fetched_url_before_update.status == UrlStatusType.PENDING.value

    db.update_url_status(test_norm_url, UrlStatusType.IN_PROGRESS)

    fetched_url_after_update = db.get_url(test_norm_url)
    assert fetched_url_after_update is not None
    assert fetched_url_after_update.status == UrlStatusType.IN_PROGRESS.value


def test_mark_url_as_crawled_updates_timestamp_and_status(db: DatabaseManager) -> None:
    test_norm_url = "https://example.com/crawl"
    db.insert_url(make_url(test_norm_url, test_norm_url))

    last_crawled_at_time = datetime.datetime(2025, 1, 1, 12, 0, 0)
    db.mark_url_as_crawled(test_norm_url, last_crawled_at_time)

    fetched_url = db.get_url(test_norm_url)
    assert fetched_url is not None
    last = fetched_url.last_crawled_at
    status = fetched_url.status
    assert last == last_crawled_at_time.isoformat()
    assert status == UrlStatusType.COMPLETED


def test_update_url_on_failed_sets_status_and_error_message(db: DatabaseManager) -> None:
    test_norm_url = "https://example.com/fail"
    db.insert_url(make_url(test_norm_url, test_norm_url))

    msg = "Network timeout error"
    db.update_url_on_failed(test_norm_url, msg)

    fetched_url = db.get_url(test_norm_url)
    assert fetched_url is not None
    status = fetched_url.status
    err = fetched_url.error_message
    assert status == UrlStatusType.FAILED
    assert err == msg


def test_has_active_urls_false_when_empty(db: DatabaseManager) -> None:
    assert db.has_active_urls() is False


def test_has_active_urls_true_with_pending_and_in_progress(db: DatabaseManager) -> None:
    # Pending
    pending_norm = "https://example.com/pending"
    db.insert_url(make_url(pending_norm, pending_norm, status=UrlStatusType.PENDING))
    assert db.has_active_urls() is True

    # In progress
    in_prog_norm = "https://example.com/inprog"
    db.insert_url(make_url(in_prog_norm, in_prog_norm, status=UrlStatusType.IN_PROGRESS))
    assert db.has_active_urls() is True

    # Mark all as completed
    db.mark_url_as_crawled(pending_norm, datetime.datetime(2025, 1, 1))
    db.mark_url_as_crawled(in_prog_norm, datetime.datetime(2025, 1, 1))
    assert db.has_active_urls() is False

def test_get_crawled_urls_with_extracted_returns_mapping(db: DatabaseManager) -> None:
    # Insert a parent that is completed
    parent_norm = "https://example.com"
    parent = make_url(parent_norm, parent_norm, status=UrlStatusType.COMPLETED)
    db.insert_url(parent)
    # Fetch parent row id
    parent_row = db.get_url(parent_norm)
    assert parent_row is not None

    # Insert two children for that parent
    child1_norm = "https://example.com/a"
    child2_norm = "https://example.com/b"
    db.insert_url(make_url(child1_norm, child1_norm, parent_url_id=parent_row.url_id, depth=1))
    db.insert_url(make_url(child2_norm, child2_norm, parent_url_id=parent_row.url_id, depth=1))

    # Insert another completed parent with no children
    other_parent_norm = "https://example.com/empty"
    db.insert_url(make_url(other_parent_norm, other_parent_norm, status=UrlStatusType.COMPLETED))

    mapping = db.get_crawled_urls_with_extracted()

    assert parent_norm in mapping
    assert mapping[parent_norm] == [child1_norm, child2_norm]
    assert other_parent_norm in mapping
    assert mapping[other_parent_norm] == []
