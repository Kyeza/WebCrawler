from unittest.mock import AsyncMock, MagicMock

import pytest
from webcrawler_arnoldkyeza.core.datastore.blob_storage import BlobStorage
from webcrawler_arnoldkyeza.core.datastore.database_manager import DatabaseManager
from webcrawler_arnoldkyeza.core.duplicate_eliminator.duplicate_eliminator import DuplicateEliminator
from webcrawler_arnoldkyeza.core.enums.url_status_type import UrlStatusType
from webcrawler_arnoldkyeza.core.scheduler.scheduler import Scheduler
from webcrawler_arnoldkyeza.core.service_host.crawler_worker import CrawlerWorker


@pytest.mark.asyncio
async def test_crawler_worker_processes_url_successfully(mocker):
    scheduler_mock = MagicMock(spec=Scheduler)
    scheduler_mock.finished.return_value = False
    scheduler_mock.get_next_url = AsyncMock(return_value=(0, "http://example.com"))

    duplicate_eliminator_mock = MagicMock(spec=DuplicateEliminator)
    duplicate_eliminator_mock.is_duplicate_content.return_value = False
    duplicate_eliminator_mock.filter_extracted_urls.return_value = []

    database_manager_mock = MagicMock(spec=DatabaseManager)
    database_manager_mock.get_url.return_value = MagicMock()

    blob_storage_mock = MagicMock(spec=BlobStorage)

    mocker.patch("webcrawler_arnoldkyeza.core.service_host.crawler_worker.HTMLFetcher", MagicMock())
    mocker.patch("webcrawler_arnoldkyeza.core.service_host.crawler_worker.Extractor", return_value=MagicMock())
    mocker.patch("webcrawler_arnoldkyeza.core.service_host.crawler_worker.HTTPProtocolHandler", MagicMock())
    mocker.patch("webcrawler_arnoldkyeza.core.service_host.crawler_worker.calculate_text_checksum",
                 return_value="checksum123")

    worker = CrawlerWorker(
        worker_id=1,
        scheduler=scheduler_mock,
        duplicate_eliminator=duplicate_eliminator_mock,
        database_manager=database_manager_mock,
        blob_storage=blob_storage_mock,
    )

    scheduler_mock.finished.side_effect = [False, True]

    await worker.run()

    scheduler_mock.get_next_url.assert_called_once()
    database_manager_mock.update_url_status.assert_called_once_with("http://example.com", UrlStatusType.IN_PROGRESS)
    blob_storage_mock.upload.assert_called_once()
    database_manager_mock.mark_url_as_crawled.assert_called_once()
    database_manager_mock.update_url_on_failed.assert_not_called()


@pytest.mark.asyncio
async def test_crawler_worker_handles_no_url_in_scheduler():
    scheduler_mock = MagicMock(spec=Scheduler)
    scheduler_mock.finished.return_value = False
    scheduler_mock.get_next_url = AsyncMock(return_value=(None, None))

    worker = CrawlerWorker(
        worker_id=1,
        scheduler=scheduler_mock,
        duplicate_eliminator=MagicMock(spec=DuplicateEliminator),
        database_manager=MagicMock(spec=DatabaseManager),
        blob_storage=MagicMock(spec=BlobStorage),
    )
    scheduler_mock.finished.side_effect = [False, True]

    await worker.run()

    scheduler_mock.get_next_url.assert_called_once()


@pytest.mark.asyncio
async def test_crawler_worker_handles_processing_error(mocker):
    scheduler_mock = MagicMock(spec=Scheduler)
    scheduler_mock.finished.return_value = False
    scheduler_mock.get_next_url = AsyncMock(return_value=(0, "http://example.com"))

    database_manager_mock = MagicMock(spec=DatabaseManager)
    blob_storage_mock = MagicMock(spec=BlobStorage)

    mocker.patch("webcrawler_arnoldkyeza.core.service_host.crawler_worker.HTMLFetcher", MagicMock(
        fetch=AsyncMock(side_effect=Exception("Error fetching content"))
    ))

    worker = CrawlerWorker(
        worker_id=1,
        scheduler=scheduler_mock,
        duplicate_eliminator=MagicMock(spec=DuplicateEliminator),
        database_manager=database_manager_mock,
        blob_storage=blob_storage_mock,
    )
    scheduler_mock.finished.side_effect = [False, True]

    await worker.run()

    database_manager_mock.update_url_on_failed.assert_called_once_with("http://example.com", "Error fetching content")
    blob_storage_mock.upload.assert_not_called()
