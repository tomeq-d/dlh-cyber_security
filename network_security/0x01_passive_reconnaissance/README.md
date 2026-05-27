# Network Security: Passive Reconnaissance

## Task Summary Table

| Task | Title | Description | File |
| :--- | :--- | :--- | :--- |
| 0 | Shodan IP | Identify target host details using Shodan search filters. | `0-shodan.txt` |
| 1 | Shodan Country | Filter target host instances by specific country codes. | `1-country.txt` |
| 2 | Shodan Ports | Find open port profiles indexed via Shodan search. | `2-ports.txt` |
| 3 | Shodan Honeypot | Detect honeypots using framework scoring metrics. | `3-honeypot.txt` |
| 4 | Dig A | Resolve IPv4 addresses using the dig utility. | `4-a.txt` |
| 5 | Dig MX | Query mail server domains configured for the network. | `5-mx.txt` |
| 6 | Dig ANY | Retrieve all public DNS zone resource records. | `6-any.txt` |
| 7 | Catch the flag - TXT | Extract hidden token data from root TXT records. | `100-flag.txt` |
| 8 | Catch the flag - NS | Enumerate and audit authoritative Name Server records. | `101-flag.txt` |
| 9 | Catch the flag - MX | Isolate hidden flags from secondary Mail Server domains. | `102-flag.txt` |

### Environment & Tools
* **Shodan CLI:** Used for passive asset tracking and server banner intelligence.
* **Dig (Domain Information Groper):** Used to query private DNS records over an active OpenVPN connection (`tun0`).
