#!/usr/bin/env python3
"""HTTP headers retrieval module."""

import requests


def get_http_headers(url):
    """Retrieve HTTP response headers from a URL."""
    try:
        response = requests.get(url)
        headers_dict = dict(response.headers)

        return {
            'status_code': response.status_code,
            'headers': headers_dict
        }

    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    pass
