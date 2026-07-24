# Task 5: Mitigation Strategies
**Project:** Risk Assessment & Mitigation Strategies  
**Organization:** SecureBank (Online Banking Platform)  
**Objective:** Design a Defense-in-Depth Strategy against SQL Injection (SQLi) Attacks  
**Constraints:** Budget: $100,000 | Timeline: 90 Days (12 Weeks)  

---

## Learning Objective
Design a multi-layered defense-in-depth security architecture selecting technical, administrative, and physical controls while balancing budgetary and operational implementation constraints.

---

## Defense-in-Depth Control Selection

| Layer | Security Control Description | Control Type | Cost | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Network** | Web Application Firewall (WAF) deployment with managed SQLi rulesets | **Technical** | **$25,000** | **High** |
| **Host** | Host-based Intrusion Prevention System (HIPS) & Endpoint Detection & Response (EDR) | **Technical** | **$15,000** | **Medium** |
| **Application** | Source code remediation (Prepared Statements/Parameterized Queries) & SAST/DAST integration | **Technical** | **$35,000** | **High** |
| **Data** | Database Principle of Least Privilege (PoLP) configuration & sensitive data column encryption | **Technical** | **$15,000** | **High** |
| **Administrative** | Developer Secure Coding Training (OWASP Top 10) & mandatory code review policies | **Administrative** | **$10,000** | **Medium** |
| **TOTAL** | **Comprehensive 5-Layer Defense Control Package** | — | **$100,000** | **Within Budget** |

---

## Implementation Timeline (90 Days / 12 Weeks)

| Week Range | Strategic Milestones & Action Items |
| :--- | :--- |
| **Weeks 1–2** | **Assessment & Planning:** Audit current database query code, define WAF baseline policies, and configure Database Least Privilege access controls. |
| **Weeks 3–6** | **Core Technical Execution:** Remediate application source code with parameterized queries, deploy WAF rulesets in blocking mode, and install EDR agents. |
| **Weeks 7–12** | **Validation & Enablement:** Conduct DAST vulnerability scans, perform external penetration testing, rollout Secure Coding Training, and integrate SAST into CI/CD pipelines. |

---

## Success Metrics

* **Primary Metric:** **Zero (0) exploitable SQL injection vulnerabilities** detected during annual third-party penetration testing and automated CI/CD security scans.
* **Operational Metric:** **100% block rate** of SQL injection attacks at the Web Application Firewall layer with **< 0.01% false-positive rate** on legitimate user traffic.
