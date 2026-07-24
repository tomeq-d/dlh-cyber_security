# Task 6: Risk Monitoring and Review
**Project:** Risk Assessment & Mitigation Strategies  
**Organization:** SecureBank  
**Target Audience:** Executive Committee & Board of Directors (Quarterly Review)  

---

## Learning Objective
Design an executive-level risk monitoring dashboard that provides clear visibility into key risk metrics, high-priority threats, control performance, and strategic quarterly action items.

---

## Executive Risk Dashboard

### Section 1: Risk Summary

| Metric | Value |
| :--- | :--- |
| **Total Identified Risks** | **18** |
| **Critical Risks** | **1** |
| **High Risks** | **3** |
| **Medium Risks** | **8** |
| **Low Risks** | **6** |

---

### Section 2: Top 3 Risks

| Rank | Risk | Level | Owner | Status |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **SQL Injection in Customer Database** | **Critical** | Chief Information Security Officer (CISO) | **Mitigation in Progress** (75% Complete) |
| **2** | **Ransomware / Zero-Day Supply Chain Flaw** | **High** | Head of Infrastructure | **In Review** (Patch Deployment Scheduled) |
| **3** | **Unencrypted API Endpoints Exposing Financial Records** | **High** | Director of Application Security | **Mitigation in Progress** (WAF & Mutual TLS Active) |

---

### Section 3: Key Performance Indicators (KPIs)

| KPI | Target | Actual | Trend |
| :--- | :---: | :---: | :---: |
| **Avg. Mitigation Time (Critical Risks)** | < 14 Days | 9 Days | **↓** *(Improving / Decreasing)* |
| **Control Effectiveness Rate** | > 90% | 94% | **↑** *(Improving / Increasing)* |
| **Open High/Critical Action Items** | < 5 Items | 4 Items | **→** *(Stable / On Track)* |

---

### Section 4: Quarterly Action Items

* **Action 1:** Complete full deployment and validation testing of the Web Application Firewall (WAF) and code remediation for the SQL Injection vulnerability.
* **Action 2:** Conduct a third-party penetration test and FAIR-based re-assessment across all core online banking APIs.
* **Action 3:** Roll out mandatory secure coding training (OWASP Top 10) for all engineering staff and implement automated SAST scanning in the CI/CD pipeline.
