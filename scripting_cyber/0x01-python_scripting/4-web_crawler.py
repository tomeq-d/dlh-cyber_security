#!/usr/bin/env python3
"""Web crawler module."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_website(start_url, max_depth=2, visited=None):
    """Recursively crawl a website and return visited URLs."""
    if visited is None:
        visited = set()

    try:
        if max_depth < 0:
            return visited

        # Parse starting domain
        base_domain = urlparse(start_url).netloc

        # Avoid revisiting URLs
        if start_url in visited:
            return visited

        visited.add(start_url)
        print(f"Crawling: {start_url}")

        # Fetch page
        response = requests.get(start_url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract links
        for link in soup.find_all("a", href=True):
            href = link.get("href")

            # Convert relative URL to absolute
            full_url = urljoin(start_url, href)

            # Check same domain
            parsed = urlparse(full_url)
            if parsed.netloc == base_domain:
                # Recursive call with reduced depth
                crawl_website(full_url, max_depth - 1, visited)

    except requests.exceptions.RequestException:
        return visited
    except Exception:
        return visited

    return visited


if __name__ == "__main__":
    pass
