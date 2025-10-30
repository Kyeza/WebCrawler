import sys
from dataclasses import dataclass
from typing import Dict, List, TextIO

from webcrawler_arnoldkyeza.core.datastore.database_manager import DatabaseManager


@dataclass
class CrawlReportPrinter:
    database_manager: DatabaseManager

    def build_report(self) -> Dict[str, List[str]]:
        """
        Build a mapping of visited (crawled) page URL -> list of links extracted on that page.
        """
        return self.database_manager.get_crawled_urls_with_extracted()

    def print_report(self, stream: TextIO | None = None) -> None:
        """
        Print the visited link and the links extracted on that page.
        Format:
          Visited: <url>
          Extracted:
          - <child1>
          - <child2>
        """
        if stream is None:
            stream = sys.stdout

        report = self.build_report()
        for visited_url, extracted in report.items():
            print(f"Visited: {visited_url}", file=stream)
            print("Extracted:", file=stream)
            if not extracted:
                print("- (none)", file=stream)
            else:
                for child in extracted:
                    print(f"- {child}", file=stream)
            print("", file=stream)
