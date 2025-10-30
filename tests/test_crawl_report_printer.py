from io import StringIO

import pytest
from webcrawler_arnoldkyeza.core.reporting.crawl_report_printer import CrawlReportPrinter
from webcrawler_arnoldkyeza.core.datastore.database_manager import DatabaseManager


@pytest.fixture
def mock_database_manager(mocker):
    return mocker.Mock(spec=DatabaseManager)


def test_build_report_delegates_to_db(mock_database_manager):
    data = {
        "https://example.com": ["https://example.com/a", "https://example.com/b"],
        "https://example.com/empty": [],
    }
    mock_database_manager.get_crawled_urls_with_extracted.return_value = data

    printer = CrawlReportPrinter(database_manager=mock_database_manager)

    assert printer.build_report() == data
    mock_database_manager.get_crawled_urls_with_extracted.assert_called_once()


def test_print_report_formats_output(mock_database_manager):
    data = {
        "https://example.com": ["https://example.com/a", "https://example.com/b"],
        "https://example.com/empty": [],
    }
    mock_database_manager.get_crawled_urls_with_extracted.return_value = data

    printer = CrawlReportPrinter(database_manager=mock_database_manager)
    buf = StringIO()
    printer.print_report(stream=buf)

    output = buf.getvalue().strip().splitlines()
    assert output[0] == "Visited: https://example.com"
    assert output[1] == "Extracted:"
    assert output[2] == "- https://example.com/a"
    assert output[3] == "- https://example.com/b"
    assert output[4] == ""
    assert output[5] == "Visited: https://example.com/empty"
    assert output[6] == "Extracted:"
    assert output[7] == "- (none)"
