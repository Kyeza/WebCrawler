import asyncio
import pytest

from webcrawler_arnoldkyeza.core.datastore.database_manager import DatabaseManager
from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.scheduler.errors import InvalidSeedUrlError
from webcrawler_arnoldkyeza.core.scheduler.scheduler import Scheduler
from webcrawler_arnoldkyeza.core.scheduler.models.url_frontier import UrlFrontier
from webcrawler_arnoldkyeza.core.scheduler.models.url import Url


@pytest.fixture
def url_frontier() -> UrlFrontier:
    return UrlFrontier()


@pytest.fixture
def mock_database_manager(mocker):
    return mocker.Mock(spec=DatabaseManager)


@pytest.fixture
def mock_duplicate_eliminator(mocker):
    de = mocker.Mock(spec=DuplicateEliminator)
    de.is_duplicate_url.return_value = False
    return de


@pytest.fixture
def scheduler(url_frontier, mock_database_manager, mock_duplicate_eliminator):
    return Scheduler(
        url_frontier=url_frontier,
        database_manager=mock_database_manager,
        duplicate_eliminator=mock_duplicate_eliminator,
    )


@pytest.mark.asyncio
async def test_scheduler_initialization(scheduler, url_frontier, mock_database_manager, mock_duplicate_eliminator):
    pending = [
        Url(url="https://example.com/a", normalized_url="https://example.com/a", priority=5, depth=0),
        Url(url="https://example.com/b", normalized_url="https://example.com/b", priority=2, depth=0),
    ]
    mock_database_manager.get_pending_urls.return_value = pending

    await scheduler.initialize(seed_url="https://example.com", max_depth=3)

    assert scheduler.seed_url == "https://example.com"
    assert scheduler._max_depth == 3
    mock_database_manager.insert_url.assert_called_once()

    items = []
    while not url_frontier.queue.empty():
        items.append(url_frontier.queue.get_nowait())

    assert set(items) == {
        (0, "https://example.com"),
        (5, "https://example.com/a"),
        (2, "https://example.com/b"),
    }


@pytest.mark.asyncio
async def test_initialize_raises_on_invalid_seed_url(scheduler, url_frontier, mock_database_manager,
                                                     mock_duplicate_eliminator):
    with pytest.raises(InvalidSeedUrlError) as exc:
        await scheduler.initialize(seed_url="mailto:user@example.com", max_depth=3)

    assert "mailto:user@example.com" in str(exc.value)
    mock_database_manager.insert_url.assert_not_called()
    assert url_frontier.queue.empty()


@pytest.mark.asyncio
async def test_scheduler_initialization_with_invalid_max_depth(scheduler, url_frontier, mock_database_manager,
                                                               mock_duplicate_eliminator):
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        await scheduler.initialize(seed_url="https://example.com", max_depth="not-an-int")


@pytest.mark.asyncio
async def test_enqueue_url_skips_invalid_url(scheduler, url_frontier, mock_database_manager, mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"

    await scheduler.enqueue_url("mailto:user@example.com")

    mock_database_manager.insert_url.assert_not_called()
    assert url_frontier.queue.qsize() == 0


@pytest.mark.asyncio
async def test_enqueue_url_skips_cross_subdomain(scheduler, url_frontier, mock_database_manager,
                                                 mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"

    await scheduler.enqueue_url("https://other.com/page")

    mock_database_manager.insert_url.assert_not_called()
    assert url_frontier.queue.qsize() == 0


@pytest.mark.asyncio
async def test_enqueue_url_skips_when_depth_exceeds_max(scheduler, url_frontier, mock_database_manager,
                                                        mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"
    scheduler._max_depth = 1

    await scheduler.enqueue_url("https://example.com/page", depth=2)

    mock_database_manager.insert_url.assert_not_called()
    assert url_frontier.queue.qsize() == 0


@pytest.mark.asyncio
async def test_enqueue_url_skips_when_duplicate(scheduler, url_frontier, mock_database_manager,
                                                mock_duplicate_eliminator):
    mock_duplicate_eliminator.is_duplicate_url.return_value = True

    scheduler.seed_url = "https://example.com"

    await scheduler.enqueue_url("https://example.com/page")

    mock_database_manager.insert_url.assert_not_called()
    assert url_frontier.queue.qsize() == 0


@pytest.mark.asyncio
async def test_enqueue_url_inserts_and_enqueues_when_valid(scheduler, url_frontier, mock_database_manager,
                                                           mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"

    await scheduler.enqueue_url("HTTP://Example.com/path/?b=2&a=1", depth=2)

    mock_database_manager.insert_url.assert_called_once()
    item = url_frontier.queue.get_nowait()
    assert item == (2, "http://example.com/path?a=1&b=2")


@pytest.mark.asyncio
async def test_get_next_url_returns_item_and_updates_depth(scheduler, url_frontier, mock_database_manager,
                                                           mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"

    url_frontier.queue.put_nowait((3, "https://example.com/child"))

    depth, url = await scheduler.get_next_url()

    assert depth == 3
    assert url == "https://example.com/child"
    assert scheduler._current_depth == 3


@pytest.mark.asyncio
async def test_get_next_url_returns_none_when_finished(scheduler, url_frontier, mock_database_manager,
                                                       mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"
    scheduler._max_depth = 0
    scheduler._current_depth = 0

    depth, url = await scheduler.get_next_url()
    assert depth is None and url is None


@pytest.mark.asyncio
async def test_get_next_url_timeout_returns_none(scheduler, url_frontier, mock_database_manager,
                                                 mock_duplicate_eliminator):
    scheduler.seed_url = "https://example.com"

    depth, url = await scheduler.get_next_url()
    assert depth is None and url is None


def test_scheduler_completion(scheduler, url_frontier, mock_database_manager, mock_duplicate_eliminator):
    scheduler._current_depth = 1
    scheduler._max_depth = 5
    assert scheduler.finished() is False

    scheduler._current_depth = 5
    scheduler._max_depth = 5
    url_frontier.queue.put_nowait((0, "https://example.com"))
    assert scheduler.finished() is False

    url_frontier.queue.get_nowait()
    assert scheduler.finished() is True


def test_finished_true_when_queue_empty_and_no_active_urls(scheduler, url_frontier, mock_database_manager, mock_duplicate_eliminator):
    # Simulate empty queue and no active URLs in DB
    scheduler._current_depth = 0
    scheduler._max_depth = 5
    assert url_frontier.queue.empty()
    mock_database_manager.has_active_urls.return_value = False
    assert scheduler.finished() is True


def test_finished_false_when_queue_empty_but_active_urls_exist(scheduler, url_frontier, mock_database_manager, mock_duplicate_eliminator):
    scheduler._current_depth = 0
    scheduler._max_depth = 5
    assert url_frontier.queue.empty()
    mock_database_manager.has_active_urls.return_value = True
    assert scheduler.finished() is False


@pytest.mark.asyncio
async def test_completing_in_progress_crawling_waits_until_task_done(scheduler, url_frontier, mock_database_manager,
                                                                     mock_duplicate_eliminator):
    await url_frontier.queue.put((0, "https://example.com"))

    join_task = asyncio.create_task(scheduler.completing_in_progress_crawling())

    await asyncio.sleep(0)
    assert not join_task.done()

    scheduler.queue_task_done()

    await asyncio.wait_for(join_task, timeout=0.5)
    assert join_task.done()
