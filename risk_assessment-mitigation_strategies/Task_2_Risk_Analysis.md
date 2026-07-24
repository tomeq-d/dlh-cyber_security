# Task 2: Risk Analysis
**Project:** Risk Assessment & Mitigation Strategies  
**Vulnerability:** Unauthenticated Remote Code Execution (RCE) on Web Server  

---

## Learning Objective
Calculate CVSS scores and Annualized Loss Expectancy (ALE) for quantitative and qualitative vulnerability evaluation.

---

## Given Data
* **Asset Value (AV):** $500,000
* **Exposure Factor (EF):** 80% (0.80)
* **Annual Rate of Occurrence (ARO):** 0.2

---

## 1. CVSS v3.1 Assessment

| CVSS Metric | Your Value | Justification |
| :--- | :--- | :--- |
| **Attack Vector** | **N** (Network) | Vulnerability is exploitable remotely over the network without local access. |
| **Attack Complexity** | **L** (Low) | No specialized conditions or complex setups required for exploitation. |
| **Privileges Required** | **N** (None) | Unauthenticated execution; attacker requires no user/admin credentials. |
| **User Interaction** | **N** (None) | Vulnerability can be exploited without any interaction from a user. |
| **Scope** | **U** (Unchanged) | Exploitation impacts the vulnerable component directly without crossing security boundaries. |
| **Confidentiality** | **H** (High) | RCE allows attackers to read all confidential data on the web server. |
| **Integrity** | **H** (High) | Attacker can modify any system files, configurations, or application code. |
| **Availability** | **H** (High) | Complete control permits attackers to shut down or render the server unavailable. |

### CVSS Results
* **CVSS Vector String:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`
* **CVSS Base Score:** **9.8**
* **Severity:** **Critical**

---

## 2. Financial Metrics (ALE Calculation)

| Financial Metric | Calculation | Result |
| :--- | :--- | :--- |
| **SLE** | `Asset Value × Exposure Factor` = `$500,000 × 0.80` | **$400,000** |
| **ALE** | `SLE × ARO` = `$400,000 × 0.2` | **$80,000** |

---

## Deliverable Summary Table

| Metric Category | Assessment / Calculation | Value |
| :--- | :--- | :--- |
| **CVSS v3.1 Base Score** | Base Score: 9.8 (Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) | **Critical** |
| **Single Loss Expectancy (SLE)** | `$500,000 × 0.80` | **$400,000** |
| **Annualized Loss Expectancy (ALE)** | `$400,000 × 0.2` | **$80,000** |
