#!/usr/bin/env python3
"""DNS resolver module."""

import socket


def resolve_domain_to_ipv4(domain_name):
    """Resolve a domain name to its IPv4 address."""
    try:
        return socket.gethostbyname(domain_name)
    except socket.gaierror:
        return None
    except Exception as error:
        return str(error)


if __name__ == "__main__":
    pass
