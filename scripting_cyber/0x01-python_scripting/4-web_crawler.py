#!/usr/bin/env python3
"""Web crawler module."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_website(start_url, max_depth=2):
    """Recursively crawl a website and return visited URLs."""
    visited = set()

    def _crawl(url, depth):
        if depth < 0 or url in visited:
            return

        try:
            base_domain = urlparse(start_url).netloc
            parsed_url = urlparse(url)

            # Only crawl same domain
            if parsed_url.netloc != base_domain:
                return

            visited.add(url)
            print(f"Crawling: {url}")

            response = requests.get(url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link.get("href")
                full_url = urljoin(url, href)

                _crawl(full_url, depth - 1)

        except requests.exceptions.RequestException:
            return
        except Exception:
            return

    _crawl(start_url, max_depth)
    return visited


if __name__ == "__main__":
    pass
