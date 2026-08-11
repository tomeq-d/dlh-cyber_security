Pentest Networking — ACME Corp Lobby Engagement

Repository: dlh-cyber_security Directory: network_security/netsec_0x0a Track: CompTIA PenTest+ (PT0-003) — Cybersecurity Academy Lab platform: NetProbe CTF Lab (guided mode)

Overview

This project simulates a contracted penetration test against ACME Corp, starting from a single foothold in the reception lobby and ending in full Active Directory domain compromise. It follows a realistic engagement flow: reconnaissance → service enumeration → exploitation → post-exploitation → lateral movement, escalating from a misconfigured SNMP device all the way to Domain Admin, plus two standalone web/database exposure findings.

Each task below was solved inside the NetProbe lab terminal (kali@netprobe, attacker box 10.10.10.5), with flags captured automatically on successful completion and written to ~/flags/flagN.txt.

Environment
Item	Detail
Attacker box	Kali Linux, 10.10.10.5
Entry point	NetProbe web app (lab control panel, not a target)
Target org	ACME Corp — Lobby (192.168.0.0/24) and internal segments (10.0.x.x)
Access	Web-based terminal via tmux attach -t training
Tasks & Flags
#	Task	Vulnerability	CVE / Ref	CVSS
0	Lobby Reconnaissance	Default SNMP community string	CVE-1999-0517	7.5 (High)
1	IP Camera Takeover	Hikvision unauthenticated command injection	CVE-2021-36260	9.8 (Critical)
2	Wi-Fi Crack	WEP RC4 / weak IV statistical cryptanalysis	N/A (RFC 2144, 1997)	9.3
3	Server Room Pivot	SMBv1 remote code execution (EternalBlue)	CVE-2017-0144 (MS17-010)	9.8 (Critical)
4	Active Directory	Kerberoasting (SPN-based offline hash cracking)	N/A (AD design weakness)	—
5	The Perfect 10.0	Zerologon — Netlogon crypto flaw + DCSync	CVE-2020-1472	10.0 (Critical)
6	Database Exposure	MongoDB with authentication disabled	CWE-306	—
7	Apache RCE	Path traversal → CGI command injection	CVE-2021-41773	9.8 (Critical)
Methodology Summary
0 — Lobby Reconnaissance (Host Discovery)

Ping-swept the lobby subnet (nmap -sn), ran a combined TCP/UDP service scan against the discovered network-closet range, and confirmed SNMP running with the default public community string. Dumped the MIB tree with snmpwalk and located the flag in a custom OID (ACME-CUSTOM-MIB::assetTag.0).

Tools: nmap, onesixtyone, snmpwalk

1 — IP Camera Takeover (IoT Exploitation)

Fingerprinted a Hikvision camera via its HTTP Server header, confirmed factory-default credentials (admin:12345), then chained to an unauthenticated blind command injection in /SDK/webLanguage for root-level RCE — no credentials required. Extracted the device configuration archive and located the flag in a CustomTag field.

Tools: curl

2 — Wi-Fi Crack (WEP)

Enabled monitor mode, identified a WEP-secured AP, then used a fake-authentication + ARP-replay attack to force rapid IV generation. Ran the PTW statistical attack against the capture file to recover the key mathematically rather than by brute force.

Tools: airmon-ng, airodump-ng, aireplay-ng, aircrack-ng

3 — Server Room Pivot (EternalBlue)

Safely verified MS17-010 exposure with an NSE script before touching Metasploit, then used exploit/windows/smb/ms17_010_eternalblue to land a SYSTEM-level Meterpreter session on an unpatched Windows Server 2008 R2 host.

Tools: nmap (NSE), msfconsole / Meterpreter

4 — Active Directory (Kerberoasting)

From a low-privilege domain account, enumerated SPNs to find an over-privileged service account (svc_sql, member of Domain Admins), requested its TGS ticket, and cracked the RC4-HMAC hash offline with hashcat — a fully silent attack from the DC's perspective. Used the cracked credential for lateral movement.

Tools: impacket-GetUserSPNs, hashcat, impacket-psexec

5 — The Perfect 10.0 (Zerologon)

Exploited a zero-IV AES-CFB8 flaw in Netlogon to reset a Domain Controller's own machine account password to blank with zero starting credentials, then used that access to DCSync every credential hash in the domain and pass-the-hash directly to the primary DC.

Tools: zerologon_tester.py, set_empty_pw.py, impacket-secretsdump, impacket-wmiexec

6 — Database Exposure (MongoDB)

Identified a MongoDB instance bound openly with authentication disabled, connected without credentials, and browsed sensitive collections directly to locate exposed PII and the flag.

Tools: nmap (mongodb-info), mongosh, mongodump

7 — Apache RCE (Path Traversal)

Fingerprinted a vulnerable Apache 2.4.49 instance, used percent-encoded traversal (.%2e) to escape the web root and read /etc/passwd, then escalated to full remote code execution by piping an HTTP POST body into /bin/sh via mod_cgi.

Tools: curl

Key Takeaways
Defaults are the recurring theme — default SNMP strings, default IoT credentials, and default (disabled) database authentication account for three of the eight findings.
Legacy protocols remain catastrophic when unpatched — WEP, SMBv1, and Netlogon's pre-2020 implementation each collapse instantly once their design flaws are understood.
Low privilege is often enough — Kerberoasting and Zerologon both demonstrate that a single weak entry point (a low-privilege user, or zero credentials at all) can cascade to full domain compromise.
Safe checks before exploitation — every exploitation step in this engagement was preceded by a non-destructive verification (NSE scripts, zerologon_tester.py), consistent with professional pentest methodology.
Repository Structure
network_security/netsec_0x0a/
├── 0-flag.txt
├── 1-flag.txt
├── 2-flag.txt
├── 3-flag.txt
├── 4-flag.txt
├── 5-flag.txt
├── 6-flag.txt
├── 7-flag.txt
└── README.md
Disclaimer

All activity was performed against an isolated, purpose-built training environment (NetProbe CTF Lab). None of the techniques, credentials, or scripts referenced here should be used against systems without explicit written authorization.
