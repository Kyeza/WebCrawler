# WebCrawler

A concurrent CLI web crawler built for the Monzo take‑home challenge.

## Overview
Given a starting URL, the crawler visits each URL it finds on the same domain and prints:
- the URL visited
- a list of links found on that page

It is limited to a single subdomain. For example, starting at https://monzo.com/ will crawl pages on monzo.com, but not external links (e.g., facebook.com) or other subdomains (e.g., community.monzo.com).

## Requirements
- Python 3.12+

## Installation
You can run the project directly from source.

Option A: with a virtual environment

### On Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### On Windows
```bash
python.exe -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

Option B: install as a package (editable)
```bash
# Create a virtual environment as described above and activate it, then;
pip install -e .
```


## Usage
Run the crawler as a module:

### On Linux/macOS
```bash
PYTHONPATH=src python -m webcrawler_arnoldkyeza.webcrawler "https://monzo.com" --max-depth 5
```

### On Windows
```bash
$env:PYTHONPATH="src"; python -m webcrawler_arnoldkyeza.webcrawler "https://monzo.com" --max-depth 5
```

CLI options:
- --number-of-workers INT    Number of concurrent worker tasks (default: 4)
- --max-depth INT            Maximum crawl depth (default: 50)
- --log-level LEVEL          Logging level (default: INFO)
- --database PATH            Path to SQLite database file (default: crawler.sqlite at project root)
- --blob-storage-path PATH   Path to store fetched page blobs (default: core/datastore/blobs)

Notes:
- The crawler persists state in a local SQLite database (default: ./crawler.sqlite).
- A Redis-like in-memory store (fakeredis) is used for duplicate elimination during runs.
- Blob storage saves raw-fetched content for later parsing/inspection.

## Running Tests
- pip install -r requirements.txt
- pytest -q

## Test Coverage
You can run tests with coverage like so:

```bash
# Show terminal summary and generate HTML report in htmlcov/
pytest --cov=webcrawler_arnoldkyeza --cov-report=term-missing --cov-report=html
```

To open the HTML report, open htmlcov/index.html in your browser after the run.

## Project Structure
- src/webcrawler_arnoldkyeza/webcrawler.py           Entry point (main) and composition root
- src/webcrawler_arnoldkyeza/core/commandline_options.py  CLI parsing and config
- src/webcrawler_arnoldkyeza/core/...                 Core modules: fetching, parsing, scheduling, storage
- tests/                                              Test suite (pytest)

## License
MIT License. See LICENSE for details.



