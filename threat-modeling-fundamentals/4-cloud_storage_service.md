# Threat Modeling: Cloud Storage Service

## 1. Attack Surface Mapping & Entry Point Ranking

An attack surface includes all points where an untrusted user can interact with the system [1]. Here are the primary entry points ranked from highest to lowest risk.

### 1. File Upload / Ingestion Endpoints (Risk Level: Critical)
* **Justification:** This allows anonymous or authenticated users to upload binary blobs directly onto cloud storage arrays. It is the most exposed entry point for malware distribution, directory traversal, and resource exhaustion.

### 2. Public Link Generation & Sharing Engine (Risk Level: High)
* **Justification:** Public links bypass standard user authentication boundaries. If an attacker can guess or brute-force tokenized URLs, they gain direct access to private backend file clusters.

### 3. Authentication & API Gateway Endpoints (Risk Level: Medium-to-High)
* **Justification:** Handles all login, registration, and session control requests. It is a high-frequency target for credential stuffing, session hijacking, and brute-force attacks.

### 4. File Versioning & Metadata Retrieval Pipelines (Risk Level: Medium)
* **Justification:** Interacts heavily with internal database schemas to fetch past object versions. Exploitation here can lead to indirect resource leaks or race conditions.

### 5. Administrative Management Dashboards (Risk Level: Low-to-Medium)
* **Justification:** Hidden behind corporate network perimeters and strict access filters. However, if compromised via weak credentials, it grants full control over tenant data.

---

## 2. Threat Modeling: Storing Encryption Keys in the Database

Placing cryptographic encryption keys inside the same database housing the encrypted files completely invalidates the objective of encryption-at-rest. If an attacker breaks into the database (via an SQL injection or a leaked backup), they instantly gain access to both the lock and the key [2]. 

### Targeted STRIDE Threats

* **Information Disclosure (Category: High Priority)**
  * *Analysis:* A single database breach compromises both the files and the keys. The attacker can decrypt and read every private file across the platform instantly, resulting in catastrophic loss of confidentiality.
* **Tampering (Category: High Priority)**
  * *Analysis:* With direct access to keys and file records, an attacker can modify sensitive files or configurations, encrypt them again with the stolen keys, and completely mask their unauthorized alterations from integrity checking mechanisms.

---

## 3. Risk Matrix for Top 5 Identified Threats

The risk rating is calculated using a standard $1 	ext{ to } 5$ scoring rubric [3]:
$$	ext{Risk Score} = 	ext{Likelihood (1-5)} 	imes 	ext{Impact (1-5)}$$

* **Likelihood Scale:** 1 (Rare), 2 (Unlikely), 3 (Possible), 4 (Likely), 5 (Almost Certain)
* **Impact Scale:** 1 (Negligible), 2 (Minor), 3 (Moderate), 4 (Major), 5 (Catastrophic)
* **Risk Score Matrix:** 1–4 (Low), 5–12 (Medium), 15–25 (High/Critical)

| # | Identified Threat Description | STRIDE Category | Likelihood (1-5) | Impact (1-5) | Risk Score | Final Rating |
| :-: | :--- | :--- | :-: | :-: | :-: | :--- |
| **1** | **Malicious File Upload (Web Shell Execution)** | Tampering | 4 | 5 | **20** | **Critical** |
| **2** | **Encryption Key Leak from Database** | Information Disclosure | 3 | 5 | **15** | **High** |
| **3** | **Public Link Enumeration (Brute-Forcing)** | Information Disclosure | 4 | 3 | **12** | **Medium** |
| **4** | **Credential Stuffing on Auth Gateway** | Spoofing | 4 | 3 | **12** | **Medium** |
| **5** | **Race Condition on Versioning Storage** | Denial of Service | 2 | 3 | **6** | **Medium** |

### Explanatory Summary Matrix Diagram

```
      IMPACT ──► (1)         (2)         (3)         (4)         (5)
  LIKELIHOOD └───┴───────────┴───────────┴───────────┴───────────┴───
     (5)     |                                                  
     (4)     |                         [Threat 3,4]          [Threat 1]
     (3)     |                                               [Threat 2]
     (2)     |                         [Threat 5]               
     (1)     |                                                  
```

---

## References
* [1] OWASP Foundation. "OWASP Attack Surface Analysis Rules." https://owasp.org/www-community/Attack_Surface_Analysis_Rules
* [2] NIST. "Special Publication 800-57 Part 1: Recommendation for Key Management." https://csrc.nist.gov/
* [3] ISO/IEC 27005. "Information technology — Security techniques — Information security risk management." https://www.iso.org/

