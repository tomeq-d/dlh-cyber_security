# Threat Modeling: Financial Trading Platform

## 1. CIA Priority Alignment & Trade-offs

### Most Critical Component: Integrity (10/10)
* **Reasoning:** Balance records, stock prices, and trade orders must be 100% accurate [1]. If an attacker modifies balances or changes transaction numbers, the platform loses regulatory licenses and faces instant collapse.

### Performance vs. Security Conflict
* **The Conflict:** Checking encryption keys and processing firewall logic takes time, which can slow down trades where sub-100ms latency is mandatory.
* **The Solution:** Offload heavy encryption work to specialized hardware accelerators at the network edge, and use ultra-fast, in-memory caches (like Redis) to check user login states instantly.

---

## 2. Threat Modeling: Automated Trading Rules

### Risk 1: Infinite Loop Trades
* **Description:** A bad or broken automation script gets caught in a loop, buying and selling a stock repeatedly until the account is drained by fees [2].
* **Mitigation:** Implement a code circuit breaker that stops a script if it executes too many times per minute or crosses a daily loss limit.

### Risk 2: Rule Alteration (Tampering)
* **Description:** An attacker modifies a user's automated rule parameters to force them to buy bad stocks at high prices from the attacker's account [2].
* **Mitigation:** Require multi-factor authentication (MFA) approval or a cryptographic signature every time an automated rule is added or changed.

### Risk 3: Race Conditions (Concurrency)
* **Description:** An attacker submits multiple withdrawal requests at the exact same millisecond to pull out more money than they actually have before the database updates [2].
* **Mitigation:** Use strict row-level database locking so the system processes transactions sequentially rather than at the same time.

---

## 3. Defense-in-Depth Framework

If an account is compromised, these 5 layers limit the damage [1]:
1. **Behavioral Analytics:** Detects sudden changes in location or trading habits and flags the account.
2. **Step-Up MFA:** Asks for an app token code before allowing any cash withdrawals or core rule changes.
3. **Velocity Limits:** Restricts the total amount of money that can leave the platform within a 24-hour window.
4. **Whitelisting & Delays:** Holds all transfers to any newly added bank accounts for 48 hours while notifying the user.
5. **Indelible Security Logs:** Streams all system actions to an unchangeable repository to record the attacker's moves for legal evidence.

---

## References
* [1] Financial Industry Regulatory Authority (FINRA). "Report on Cyber Security Practices." https://www.finra.org/
* [2] Software Engineering Institute (SEI) CERT. "CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')." https://cwe.mitre.org/data/definitions/362.html

