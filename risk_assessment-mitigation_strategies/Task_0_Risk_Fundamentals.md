# Task 0: Risk Fundamentals
**Project:** Risk Assessment & Mitigation Strategies  
**Role:** Risk Analyst, TechCorp  

---

## Learning Objective
Calculate risk using both qualitative and quantitative methods to evaluate potential business impact and select appropriate response strategies.

---

## Scenario Overview
* **Risk:** SQL injection vulnerability in customer database
* **Asset Value:** $2,000,000 (Customer Records)
* **Exposure Factor (EF):** 40% (0.40)
* **Annual Rate of Occurrence (ARO):** 0.3 (Once every ~3.3 years)

---

## Calculations & Analysis

### 1. Qualitative Assessment
* **Threat:** Malicious exploitation of database via SQL injection.
* **Vulnerability:** Unsanitized input fields in the web application user interface.
* **Likelihood:** **Medium** (Mapped from ARO of 0.3).
* **Impact:** **High** (Exposure of core customer database worth $2M).
* **Risk Level:** **High** (Determined using the Risk Matrix: Medium Likelihood × High Impact).

### 2. Quantitative Calculations
* **Single Loss Expectancy (SLE):**
  $$	ext{SLE} = 	ext{Asset Value} 	imes 	ext{Exposure Factor}$$
  $$	ext{SLE} = \$2,000,000 	imes 0.40 = \$800,000$$

* **Annualized Loss Expectancy (ALE):**
  $$	ext{ALE} = 	ext{SLE} 	imes 	ext{ARO}$$
  $$	ext{ALE} = \$800,000 	imes 0.3 = \$240,000$$

### 3. Risk Treatment
* **Strategy:** **Mitigate**
* **Justification:** Remediate the technical flaw through parameterized queries/prepared statements, input validation, and deployment of a Web Application Firewall (WAF).

---

## Task 0 Deliverable Table

| Component | Answer | Details / Calculation |
| :--- | :--- | :--- |
| **Threat** | SQL injection attack | Unauthorized access and data exfiltration attempt |
| **Vulnerability** | Unsanitized input fields | Flaw in web application code |
| **Likelihood** | Medium | Based on ARO = 0.3 |
| **Impact** | High | $2,000,000 core database asset |
| **Risk Level** | High | Matrix: Medium Likelihood × High Impact |
| **SLE** | **$800,000** | `$2,000,000 × 0.40` |
| **ALE** | **$240,000** | `$800,000 × 0.3` |
| **Treatment** | Mitigate | Code remediation & input sanitization |

---

## Reference: Risk Matrix

| Likelihood \ Impact | Low Impact | Medium Impact | High Impact |
| :--- | :--- | :--- | :--- |
| **High Likelihood** | Medium | High | **Critical** |
| **Medium Likelihood** | Low | Medium | **High** |
| **Low Likelihood** | Low | Low | Medium |
