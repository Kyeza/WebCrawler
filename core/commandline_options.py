import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class CrawlerConfig:
    start_url: str
    number_of_workers: Optional[int] = field(default=4)
    max_depth: Optional[int] = field(default=50)
    log_level: Optional[str] = field(default="INFO")
    database: Optional[Path] = field(default=Path("crawler.sqlite"))


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
        default=Path("crawler.sqlite"),
        help="Database path (default: crawler.sqlite)"
    )

    args, _ = parser.parse_known_args(argv)

    return CrawlerConfig(
        start_url=args.start_url,
        number_of_workers=args.number_of_workers,
        max_depth=args.max_depth,
        log_level=args.log_level,
        database=args.database,
    )

