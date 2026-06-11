from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "output"


class Settings:
    SITE_URL = "https://www.centauro.com.br"
    BROWSER_IMPERSONATE = "safari17_0"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_BACKOFF_SECONDS = 1.5
    PAGES_PER_TERM = 2
