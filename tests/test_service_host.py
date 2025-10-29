from unittest.mock import AsyncMock, MagicMock

import pytest
from webcrawler_arnoldkyeza.core.commandline_options import CrawlerConfig
from webcrawler_arnoldkyeza.core.service_host.service_host import ServiceHost


@pytest.mark.asyncio
async def test_service_host_crawl_initializes_scheduler():
    mock_scheduler = AsyncMock()
    mock_deduplicator = MagicMock()
    mock_database = MagicMock()
    mock_blob_storage = MagicMock()
    config = CrawlerConfig(start_url="http://example.com", number_of_workers=2, max_depth=5)

    service_host = ServiceHost(
        scheduler=mock_scheduler,
        deduplicator=mock_deduplicator,
        database=mock_database,
        blob_storage=mock_blob_storage
    )

    await service_host.crawl(config)

    mock_scheduler.initialize.assert_called_once_with(config.start_url, config.max_depth)


@pytest.mark.asyncio
async def test_service_host_crawl_creates_workers(mocker):
    mock_scheduler = AsyncMock()
    mock_scheduler.finished.side_effect = [False, True]  # exit loop quickly
    mock_deduplicator = MagicMock()
    mock_database = MagicMock()
    mock_blob_storage = MagicMock()
    config = CrawlerConfig(start_url="http://example.com", number_of_workers=2, max_depth=5)

    run_mock = AsyncMock()
    cw_run_patch = mocker.patch(
        "webcrawler_arnoldkyeza.core.service_host.service_host.CrawlerWorker.run",
        return_value=run_mock
    )

    service_host = ServiceHost(
        scheduler=mock_scheduler,
        deduplicator=mock_deduplicator,
        database=mock_database,
        blob_storage=mock_blob_storage
    )

    await service_host.crawl(config)

    assert cw_run_patch.call_count == config.number_of_workers
    mock_scheduler.initialize.assert_called_once_with(config.start_url, config.max_depth)
    assert mock_scheduler.completing_in_progress_crawling.await_count == 1
