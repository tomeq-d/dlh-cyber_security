# Task 4: Risk Assessment Methodologies
**Project:** Risk Assessment & Mitigation Strategies  
**Organization:** GlobalTech  
**Framework:** Factor Analysis of Information Risk (FAIR)  

---

## Learning Objective
Apply the FAIR quantitative risk analysis methodology to estimate threat event frequency, vulnerability, loss magnitudes, and annualized loss exposure for misconfigured cloud storage exposing 50,000 customer records.

---

## Scenario Overview
* **Risk Event:** Misconfigured cloud storage bucket exposing 50,000 customer records.
* **Impact Scale:** 50,000 individual customer records exposed.

---

## FAIR Quantitative Analysis

### 1. Threat & Vulnerability Metrics

| FAIR Component | Your Estimate | Reasoning |
| :--- | :--- | :--- |
| **Threat Event Frequency (TEF)** | **2.0 events/year** | External scanners, automated tools, and threat actors constantly probe public cloud assets (~2 explicit scanning/exposure attempts per year). |
| **Vulnerability (Vuln)** | **0.50** | Given existing cloud configuration controls, there is a 50% probability that a misconfigured bucket will exist and be exposed during a threat event. |
| **Loss Event Frequency (LEF)** | **1.0 event/year** | `TEF × Vuln = 2.0 × 0.50 = 1.0` (An expected 1 loss event per year). |

---

### 2. Loss Magnitude Breakdown

| Loss Category | Estimated Cost | Rationale / Calculation |
| :--- | :--- | :--- |
| **Response & Investigation** | **$50,000** | Digital forensics team, legal counsel retained for incident triage and containment. |
| **Notification Costs** | **$250,000** | $5 per record across 50,000 affected customer records (`50,000 × $5`). |
| **Regulatory Fines** | **$100,000** | Potential statutory penalties and compliance fines under privacy regulations (e.g., GDPR/CCPA). |
| **Reputation Damage** | **$100,000** | Estimated customer churn, PR management, and lost operational business trust. |
| **Total Loss Magnitude (LM)** | **$500,000** | `Sum of all loss categories ($50k + $250k + $100k + $100k)` |

---

### 3. Final Calculation

| Metric | Formula / Calculation | Value |
| :--- | :--- | :--- |
| **Annualized Risk (ALE)** | `LEF × Loss Magnitude` = `1.0 × $500,000` | **$500,000** |

---

## Risk Treatment Recommendation

* **Recommendation:** **Mitigate**
* **Justification:**  
  With an estimated **Annualized Risk of $500,000**, GlobalTech should immediately implement automated Cloud Security Posture Management (CSPM) tools, enforce strict Infrastructure-as-Code (IaC) security scanning in CI/CD pipelines, and mandate automated bucket policy enforcement (e.g., AWS S3 Block Public Access). Deploying CSPM and automated remediations typically costs between $15,000–$30,000 annually, yielding an immense net saving compared to the potential $500,000 annual loss exposure.
