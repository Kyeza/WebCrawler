import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "crawler.sqlite"
DEFAULT_BLOB_STORAGE_PATH = PROJECT_ROOT / "src/webcrawler_arnoldkyeza/core/datastore/blobs"

@dataclass
class CrawlerConfig:
    start_url: str
    number_of_workers: Optional[int] = field(default=4)
    max_depth: Optional[int] = field(default=50)
    log_level: Optional[str] = field(default="INFO")
    database: Optional[Path] = field(default=DEFAULT_DATABASE_PATH)
    blob_storage_path: Optional[Path] = field(default=DEFAULT_BLOB_STORAGE_PATH)


def parse_command_line_options(argv: Optional[list[str]] = None) -> CrawlerConfig:
    parser = argparse.ArgumentParser(description="Web Crawler", usage="%(prog)s [options] start_url")
    parser.add_argument("start_url", type=str, help="The starting URL for the crawler")
    parser.add_argument(
        "--number-of-workers",
        type=int,
        default=4,
        help="Number of concurrent worker tasks (default: 4)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=50,
        help="Maximum depth to crawl (default: 50)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help="Database path (default: crawler.sqlite)"
    )
    parser.add_argument(
        "--blob-storage-path",
        type=Path,
        default=DEFAULT_BLOB_STORAGE_PATH,
        help="Blob storage path (default: core/datastore/blobs)"
    )

    args, _ = parser.parse_known_args(argv)

    database_path = args.database
    if database_path != DEFAULT_DATABASE_PATH and not database_path.is_absolute():
        database_path = (PROJECT_ROOT / database_path).resolve()

    return CrawlerConfig(
        start_url=args.start_url,
        number_of_workers=args.number_of_workers,
        max_depth=args.max_depth,
        log_level=args.log_level,
        database=database_path,
    )

