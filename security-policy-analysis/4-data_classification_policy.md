# HealthPlus Medical Group - Data Classification Policy & Standards

## Document Control
| Field | Value |
| :--- | :--- |
| **Policy ID** | POL-DATA-004 |
| **Version** | 1.0 |
| **Effective Date** | 2026-06-24 |
| **Review Date** | 2027-06-24 |
| **Policy Owner** | Chief Information Security Officer (CISO) & Data Protection Officer (DPO) |
| **Approved By** | Executive Health Compliance Board |
| **Classification** | Internal Use Only |

---

### 1. Purpose
This Data Classification Policy defines the operational mandates for identifying, categorizing, and protecting informational assets processed by HealthPlus Medical Group. Strict data lifecycle safeguards ensure unwavering compliance with HIPAA Security/Privacy Rules, GDPR, and state-level healthcare privacy regulations.

### 2. Scope
* **2.1 Applicability:** This policy governs all workforce members, clinical staff, research associates, administrative employees, and third-party business associates.
* **2.2 Covered Assets:** All data generated, processed, or hosted by HealthPlus, including electronic Protected Health Information (ePHI), employee records, operational metrics, and physical printouts.
* **2.3 Exclusions:** None.

---

### 3. Policy Statements

#### 3.1 Data Classification Structure
HealthPlus data assets are organized into four distinct sensitivity tiers. All data is classified at its highest level of risk by default.
* **PUBLIC:** Information approved by Corporate Communications for unrestricted community distribution.
* **INTERNAL:** Non-public corporate data that supports day-to-day administrative or business tasks but lacks highly sensitive or personal identifiers.
* **CONFIDENTIAL:** Private employee, financial, or tactical business data that could damage operations or violate legal compliance frameworks if leaked.
* **RESTRICTED:** Highly sensitive clinical data, credentials, or regulatory data assets. Unauthorized disclosure would trigger severe legal penalties (e.g., HIPAA violations), massive financial remediation, or directly compromise patient safety.

#### 3.2 Labeling and File Conventions
* **3.2.1 Digital Metadata:** Digital assets classified as Internal, Confidential, or Restricted must be programmatically labeled using cloud-native data loss prevention (DLP) metadata tags.
* **3.2.2 Document Indicators:** Static digital files (e.g., PDFs) and physical prints must feature a prominent classification tag in the header and footer (e.g., `[RESTRICTED - MEDICAL DATA]`).
* **3.2.3 File Naming Constraints:** Confidential and Restricted files must avoid descriptive PII/PHI strings in the actual filename (e.g., use `Patient_ID_10442_Chart.pdf` instead of `John_Doe_HIV_Test.pdf`).

#### 3.3 Storage Governance
* **3.3.1 Approved Repositories:** Classified data assets must reside only on corporate-managed networks, sanctioned Electronic Health Record (EHR) environments, or approved enterprise cloud infrastructure.
* **3.3.2 Prohibited Locations:** Storing Confidential or Restricted data on local employee desktops, personal unencrypted USB drives, or unsanctioned consumer cloud storage (e.g., personal Google Drive) is strictly prohibited.

#### 3.4 Transmission Rules
* **3.4.1 Electronic Distribution:** Restricted data must never be shared via standard unencrypted email, corporate SMS, or consumer chat tools. Communication must occur exclusively within secure clinical message workflows or encrypted portals.
* **3.4.2 Secure File Transfer:** External transfers of confidential datasets to verified entities must execute over Secure File Transfer Protocols (SFTP) utilizing cryptographic keys or authenticated corporate transport pathways.

#### 3.5 Disposal and Sanitization
* **3.5.1 Physical Deconstruction:** Printed Confidential or Restricted files must be deposited into locked collection bins and shredded into micro-cut particles meeting DIN 66399 Level P-4 or higher standards.
* **3.5.2 Digital Erasure:** Repurposed or decommissioned hardware containing electronic storage media must undergo multi-pass cryptographic erasure or physical destruction according to NIST SP 800-88 Rev. 1 Guidelines.

#### 3.6 Access Control Framework
* **3.6.1 Access Philosophy:** Access privileges across all authenticated vectors must strictly mirror Least Privilege principles and verifiable "Need-to-Know" operational grounds.
* **3.6.2 Credential Baselines:** Access to Confidential or Restricted environments requires a distinct corporate login actively reinforced by phishing-resistant Multi-Factor Authentication (MFA).
* **3.6.3 Access Validation Timelines:** Department heads and compliance auditors must complete formal user access entitlement evaluations every 90 days for Restricted assets, and every 180 days for Confidential repositories.

---

### 4. Roles and Responsibilities
* **Data Protection Officer (DPO):** Reviews data lifecycle rules, audits privacy frameworks, and coordinates responses to regulatory audits.
* **Data Owners (Department Heads):** Assign classification baselines to emerging datasets and validate access lists regularly.
* **IT Security Team:** Implements infrastructure DLP tags, enforces baseline storage access lists, and orchestrates encryption layers.
* **Data Custodians (All System Users):** Actively handle data according to its assigned tier and immediately flag data mishandling risks.

### 5. Compliance
* **5.1 Monitoring:** Automated endpoint DLP platforms monitor unauthorized data duplication, transmission, or printing.
* **5.2 Reporting:** Data protection metric logs are presented to the Risk Committee every month.
* **5.3 Auditing:** Unannounced technical data audits assess sample repository access lists and labeling rates.

### 6. Enforcement
* **6.1 Violations:** Compromising patient confidentiality via policy negligence can trigger professional suspension, termination of employment, and independent civil/criminal prosecution under federal HIPAA rules.
* **6.2 Reporting Violations:** Report suspected data handling violations immediately to privacy-hotline@healthplusmed.com.

### 7. Exceptions
* **7.1 Process:** Data workflow modifications require a written risk evaluation and joint approval by the CISO and DPO.
* **7.2 Duration:** Approved data control exceptions expire after a maximum duration of 1 year.

### 8. Definitions
* **Protected Health Information (PHI):** Any health status, healthcare provision, or payment data that can be linked to a specific individual.

### 9. Related Documents
HIPAA Security Standard Workbook; Access Control Matrix Guide; Media Destruction Standard.

### 10. Revision History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-06-24 | CISO & DPO Office | Initial Release. |

### 11. Acknowledgment
Workforce members acknowledge that respecting patient data classification guidelines is an uncompromisable condition of maintaining clinical and operational access.

---

## 🛠️ SECTION I: DATA HANDLING REQUIREMENTS MATRIX

| Requirement Framework | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED |
| :--- | :--- | :--- | :--- | :--- |
| **Visual/DLP Labeling** | Optional | Optional | **Mandatory** | **Mandatory (Header/Footer)** |
| **Encryption at Rest** | No | Optional | **Mandatory (AES-256)** | **Mandatory (FIPS 140-2 Validated)** |
| **Encryption in Transit** | No | **Mandatory (TLS 1.2)** | **Mandatory (TLS 1.3)** | **Mandatory (HTTPS/TLS + SFTP)** |
| **Access Control Baseline** | Public Access Allowed | Authenticated Internal Staff | Role-Based Access Control (RBAC) | Explicit Need-to-Know + Phishing-Resistant MFA |
| **Data Retention Horizon** | Variable | 3 Years | 7 Years (Financials) | Minimum 7 Years (Medical Charts) |

---

## 📋 SECTION II: EMPLOYEE QUICK REFERENCE GUIDE

### 🛑 STOP & CHECK: What Data Are You Handling?

#### 1. RESTRICTED (Maximum Security)
* **What it includes:** Patient Medical Records (PHI), EHR chart notes, diagnostic results, lab orders, system root credentials, and encryption keys.
* **Storage Rule:** ONLY within the official certified EHR system or designated secure clinical repositories. **NEVER** save to your desktop, personal cloud, or unencrypted USB drives.
* **Sharing Rule:** **NEVER** send via standard Outlook email, Teams chat, or SMS text. Use only the integrated, secure clinical messaging portal.
* **Disposal:** Physical papers must immediately go into the locked gray shredding bins.

#### 2. CONFIDENTIAL (High Security)
* **What it includes:** Employee PII (Social Security Numbers, home addresses), payroll spreadsheets, unreleased clinical research data, and financial performance reports.
* **Storage Rule:** Approved departmental SharePoint directories or secure enterprise file shares.
* **Sharing Rule:** Can be sent internally to authorized personnel via encrypted email. Use secure corporate file transfer protocols for approved external third parties.
* **Disposal:** Must be shredded physically; digital instances must be deleted permanently.

#### 3. INTERNAL (Standard Business)
* **What it includes:** Internal operational memos, clinical shift schedules, facilities management updates, and organizational hierarchies.
* **Storage Rule:** Standard HealthPlus corporate networks and intranet folders.
* **Sharing Rule:** Intended for internal workforce distribution only. Do not share externally without manager sign-off.
* **Disposal:** Standard digital deletion; recycling or shredding for physical copies.

#### 4. PUBLIC (Open Access)
* **What it includes:** Patient educational flyers, marketing materials, public-facing website copy, and press releases.
* **Storage Rule:** Any designated repository, including public-facing web servers.
* **Sharing Rule:** Free distribution allowed without strict cryptographic restrictions.
* **Disposal:** Standard trash or recycling bins.

---
💡 *Unsure how to classify a specific file? Err on the side of caution and treat it as **Confidential**, or check in with your supervisor or the Data Protection Office at data-compliance@healthplusmed.com.*
