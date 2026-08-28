# websec_0x0C — NexusShop XSS Assessment

Web application security project for Holberton Cybersecurity Academy. This project involves identifying and exploiting Cross-Site Scripting (XSS) vulnerabilities across a deliberately vulnerable e-commerce platform, NexusShop (`http://web0x0c.hbtn`), spanning Reflected, Stored, and DOM-based attack vectors — followed by a professional penetration test report.

## Project Structure

```
web_application_security/websec_0x0C/
├── README.md                      # This file
├── 0-flag.txt                     # Task 0 flag
├── 2-flag.txt                     # Task 1 flag
├── 3-flag.txt                     # Task 2 flag
├── 4-flag.txt                     # Task 3 flag
├── 5-flag.txt                     # Task 4 flag
├── 6-flag.txt                     # Task 5 flag
├── 7-flag.txt                     # Task 6 flag
└── Security_Report/
    ├── SECURITY_REPORT.md         # Task 7 — full penetration test report
    ├── task0-01-console-payload.png
    ├── task0-02-network-response.png
    └── task0-03-flag-response.png
```

## Tasks Overview

| Task | Title | Type | Status |
|------|-------|------|--------|
| 0 | Reflected XSS - Basic Search | Reflected | ✅ Flag captured |
| 1 | Reflected XSS - JavaScript Context | Reflected (JS-context breakout) | ✅ Flag captured |
| 2 | Stored XSS - Product Reviews | Stored | ✅ Flag captured |
| 3 | Stored XSS - User Profile | Stored (DOM sink via `innerHTML`) | ✅ Flag captured |
| 4 | Stored XSS - Markdown Editor | Stored (sanitizer bypass) | ✅ Flag captured |
| 5 | DOM XSS - URL Hash Hijack | DOM-based | ✅ Flag captured |
| 6 | DOM XSS - postMessage Abuse | DOM-based (unsafe `postMessage` handler) | ✅ Flag captured |
| 7 | Penetration Test Report | — | ✅ [SECURITY_REPORT.md](Security_Report/SECURITY_REPORT.md) |

Each task (0–6) targets a distinct XSS vulnerability class across three escalating stages (increasingly strict filtering/sanitization), requiring a different bypass technique at each stage. Task 7 consolidates all seven findings into a formal report with technical detail, evidence, real-world impact analysis, and remediation guidance for each vulnerability.

## Full Write-Up

For the complete technical breakdown of each vulnerability — location, attack vector, payloads, evidence, impact, and remediation — see [`Security_Report/SECURITY_REPORT.md`](Security_Report/SECURITY_REPORT.md).

## Environment

- Target: NexusShop (`http://web0x0c.hbtn`) — intentionally vulnerable training application
- Tooling: Kali Linux, Firefox DevTools (Console, Network, Sources, Elements)
- Methodology: manual source-to-sink tracing per vulnerability, followed by stage-by-stage filter/sanitizer bypass

## Disclaimer

This project targets a lab environment built for educational purposes as part of the Holberton Cybersecurity Academy curriculum. All testing was performed against an intentionally vulnerable application with authorization implied by the coursework context. None of the techniques documented here were used against production systems.

