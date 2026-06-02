#!/usr/bin/env python3
"""Network reconnaissance tool."""

import socket
import requests
import dns.resolver
from bs4 import BeautifulSoup


def dns_recon(domain):
    """Perform DNS reconnaissance."""
    try:
        # Resolve IP
        ip = socket.gethostbyname(domain)
        print(f"IP Address: {ip}")

        # Get MX records
        print("\nMX Records:")
        answers = dns.resolver.resolve(domain, 'MX')
        for rdata in answers:
            print(f"  {rdata.preference} {rdata.exchange}")

    except socket.gaierror:
        print("Failed to resolve domain")
    except Exception:
        print("Error retrieving DNS information")


def web_recon(domain):
    """Perform web reconnaissance."""
    url = f"http://{domain}"

    try:
        response = requests.get(url, timeout=5)

        print(f"\nStatus Code: {response.status_code}")

        print("\nImportant Headers:")
        headers = response.headers
        for key in ["Server", "Content-Type"]:
            if key in headers:
                print(f"  {key}: {headers[key]}")

        # Count links
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        print(f"\nTotal Links Found: {len(links)}")

    except requests.exceptions.RequestException:
        print("Failed to retrieve web data")


def port_scan(domain):
    """Check common ports."""
    ports = [80, 443]

    try:
        ip = socket.gethostbyname(domain)
        print(f"\nScanning common ports on {domain}...")

        print("Open ports:")
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)

                result = sock.connect_ex((ip, port))
                sock.close()

                if result == 0:
                    print(f"  Port {port}: OPEN")

            except Exception:
                continue

    except Exception:
        print("Failed to perform port scan")


if __name__ == "__main__":
    pass
