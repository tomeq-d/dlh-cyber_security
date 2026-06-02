#!/usr/bin/env python3
"""Port scanner module."""

import socket


def check_port(host, port):
    """Check if a TCP port is open on a host."""
    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        # Check port
        result = sock.connect_ex((host, port))

        sock.close()

        return result == 0

    except Exception:
        return False


if __name__ == "__main__":
    pass
