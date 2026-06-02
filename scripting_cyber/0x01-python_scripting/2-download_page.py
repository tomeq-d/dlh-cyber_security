#!/usr/bin/env python3
"""Download and format a web page."""

import requests
from bs4 import BeautifulSoup


def download_page(url):
    """Download a web page and return formatted HTML."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.prettify()

    except requests.exceptions.RequestException as error:
        return str(error)


if __name__ == "__main__":
    pass
