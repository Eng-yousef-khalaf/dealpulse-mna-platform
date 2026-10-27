"""
DealPulse M&A Platform - Base Scraper
Enterprise-grade base class providing exponential backoff retries, rate limiting,
custom user agents, session handling, and graceful failure recovery.
"""
import time
import requests
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

from src.config import HTTP_HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF, get_logger

class BaseScraper:
    def __init__(self, name: str, rate_limit_delay: float = 1.0):
        self.name = name
        self.rate_limit_delay = rate_limit_delay
        self.logger = get_logger(f"Scraper.{name}")
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def fetch_page(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Executes HTTP GET with retry logic and exponential backoff.
        Guarantees resilient data collection replacing fragile one-off fixes.
        """
        retries = 0
        backoff = RETRY_BACKOFF

        while retries < MAX_RETRIES:
            try:
                self.logger.info(f"Fetching: {url} (Attempt {retries + 1}/{MAX_RETRIES})")
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    time.sleep(self.rate_limit_delay)  # Responsible rate limiting
                    return response.text
                elif response.status_code in (429, 500, 502, 503, 504):
                    self.logger.warning(
                        f"Server returned status {response.status_code}. Backing off for {backoff:.1f}s..."
                    )
                    time.sleep(backoff)
                    backoff *= 2
                    retries += 1
                else:
                    self.logger.error(f"Non-retryable HTTP error {response.status_code} for {url}")
                    return None

            except (requests.RequestException, ConnectionError) as exc:
                self.logger.warning(f"Request failed ({exc}). Retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                retries += 1

        self.logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")
        return None

    def parse_soup(self, html_content: str) -> BeautifulSoup:
        """Parses raw HTML string with BeautifulSoup and lxml parser."""
        return BeautifulSoup(html_content, "lxml")
