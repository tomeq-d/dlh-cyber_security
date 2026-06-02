#!/usr/bin/env python3
"""DNS records enumeration module."""

import dns.resolver


def query_dns_records(domain_name):
    """Query multiple DNS record types for a domain."""
    records = {}
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain_name, record_type)
            records[record_type] = answers
        except (dns.resolver.NoAnswer,
                dns.resolver.NXDOMAIN,
                dns.resolver.NoNameservers):
            continue
        except Exception:
            continue

    return records


if __name__ == "__main__":
    pass
