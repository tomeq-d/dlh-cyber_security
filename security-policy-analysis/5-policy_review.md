# RetailMax Corporation - Policy Review & Compliance Gap Analysis

## Document Control
| Field | Value |
| :--- | :--- |
| **Document ID** | RE-GAP-2026-001 |
| **Version** | 1.0 |
| **Effective Date** | 2026-06-24 |
| **Assessor** | Lead Cyber Security Consultant |
| **Target Frameworks** | PCI-DSS v4.0, ISO/IEC 27001:2022, SOC 2 Type II |
| **Classification** | Confidential / Internal Use Only |

---

## 🏢 EXECUTIVE SUMMARY

### Context & Objective
RetailMax Corporation is actively preparing for an aggressive compliance rollout encompassing PCI-DSS v4.0 certification, ISO/IEC 27001:2022 alignment, and a SOC 2 Type II audit baseline. To establish a secure baseline ahead of these formal assessments, a rigorous policy evaluation and gap analysis were executed against RetailMax’s existing security policy inventory. 

### Key Findings & Critical Gaps
The assessment revealed structural gaps across the policy infrastructure that present immediate blockers to certification:
* **Severe Policy Omissions:** RetailMax completely lacks formal documentation for an Incident Response Policy, a Data Classification Policy, and an Access Control Policy. These omissions constitute automatic failures under PCI-DSS Milestone 1 and ISO 27001 Annex A.
* **Stale Core Policies:** The active documentation suite is dangerously outdated. The Information Security Policy has not been formally reviewed or updated since 2019, and the Password Policy (2020) fails to account for current multi-factor authentication (MFA) standards and modern NIST SP 800-63B password complexity baselines.
* **Lack of Measurement:** No current policies feature operational metrics, key performance indicators (KPIs), or integrated monitoring frameworks, capping organizational maturity at an ad-hoc or purely reactive level.

### Strategic Path Forward
To remediate these gaps, RetailMax must transition from its current fragmented approach to a centralized governance model. The immediate priority over the next 90 days must be drafting and enforcing the missing foundational policies, followed by a wholesale modernization of legacy documents. Over the next 12 months, the focus must shift to continuous technical enforcement, comprehensive workforce training, and auditing mechanism deployment to achieve audit readiness.

---

## 📊 PART A: GAP ANALYSIS MATRIX (PCI-DSS v4.0 Baseline)

| PCI-DSS Requirement | Requirement Summary | Status | Document Impact & Remediating Actions Required |
| :--- | :--- | :--- | :--- |
| **Requirement 1** | Install and maintain network security controls (Firewalls/Routers). | **Partial Gap** | Information Security Policy (2019) lacks explicit architecture review cadences. Action: Update policy to mandate quarterly network mapping and change windows. |
| **Requirement 2** | Apply secure configurations to all system components (No default passwords). | **Gap** | Password Policy (2020) fails to address vendor default password sanitation. Action: Update policy to mandate default password elimination before deployment. |
| **Requirement 3** | Protect stored account data (Cardholder Data/CHD encryption). | **Critical Gap** | Data Classification Policy is Missing. Action: Author and implement a Data Classification Policy defining CHD and strict AES-256 storage baselines. |
| **Requirement 4** | Protect cardholder data with strong cryptography during transmission. | **Critical Gap** | No operational standard mandates TLS 1.3/SFTP profiles over public links. Action: Define explicit transmission standards within the Data Classification suite. |
| **Requirement 5** | Protect all systems and networks from malicious software. | **Partial Gap** | Acceptable Use Policy (2021) notes anti-malware but lacks enforcement teeth. Action: Mandate automated, tamper-resistant EDR tools on endpoints. |
| **Requirement 6** | Develop and maintain secure systems and software application profiles. | **Gap** | Modern secure coding frameworks (OWASP Top 10) are absent from current policy. Action: Insert rigorous secure lifecycle hooks within the Information Security Policy. |
| **Requirement 7** | Restrict access to system components and cardholder data by business need-to-know. | **Critical Gap** | Access Control Policy is Missing. Action: Author a dedicated Access Control Policy defining Least Privilege and explicit job-role matrix assignments. |
| **Requirement 8** | Identify users and authenticate access to system components (MFA). | **Critical Gap** | Current documentation lacks phishing-resistant MFA mandates for administrative pathways. Action: Overhaul Password Policy to enforce multi-factor profiles. |
| **Requirement 9** | Restrict physical access to system components and cardholder data environments. | **Gap** | Physical data storage, visitor logging, and security camera retention are omitted. Action: Build dedicated physical security sections within the Access Control Policy. |
| **Requirement 10** | Log and monitor all access to system components and cardholder data. | **Critical Gap** | Audit log tracking and SIEM ingestion requirements are entirely undocumented. Action: Embed explicit 1-year log retention mandates within the Access Control Policy. |
| **Requirement 11** | Test security of systems and networks regularly (Vulnerability Scanning). | **Gap** | Internal/external penetration testing cadences are not operationally mandated. Action: Incorporate quarterly scan mandates within the Information Security Policy. |
| **Requirement 12** | Support information security with organizational policies and programs. | **Critical Gap** | Incident Response Policy is Missing; annual policy reviews are neglected. Action: Draft an Incident Response Policy and establish an Executive Risk Board. |

---

## 📈 PART B: POLICY MATURITY ASSESSMENT

The maturity of RetailMax's current program is evaluated using the Capability Maturity Model Integration (CMMI) scale:

* Level 0: Non-existent
* Level 1: Initial
* Level 2: Developing
* Level 3: Defined
* Level 4: Managed
* Level 5: Optimized

### 📋 Detailed Maturity Inventory

#### 1. Information Security Policy
* **Current Maturity Level:** Level 2 - Developing
* **Justification:** The policy was documented in 2019, but it has not been aligned with evolving business expansions or hybrid cloud infrastructure. It lacks continuous enforcement mechanisms and metric definitions.

#### 2. Password Policy
* **Current Maturity Level:** Level 1 - Initial
* **Justification:** While a document exists (2020), it represents legacy ad-hoc concepts. It lacks modern MFA controls and fails to address the hybrid/remote environments actively used today.

#### 3. Acceptable Use Policy (AUP)
* **Current Maturity Level:** Level 2 - Developing
* **Justification:** The 2021 framework details high-level expectations, but onboarding verification logs are handled inconsistently across departments, and automated web-filtering blocks do not actively map back to policy text.

#### 4. Incident Response Policy
* **Current Maturity Level:** Level 0 - Non-existent
* **Justification:** No formal policy, operational runbooks, table-top validation testing profiles, or CSIRT definitions exist.

#### 5. Data Classification Policy
* **Current Maturity Level:** Level 0 - Non-existent
* **Justification:** There is no systematic categorization for public, corporate internal, or sensitive cardholder/PII datasets.

#### 6. Access Control Policy
* **Current Maturity Level:** Level 0 - Non-existent
* **Justification:** User provisioning processes, quarterly privilege entitlement certifications, and least-privilege matrices are completely undocumented.

---

## 🛠️ PART C: PRIORITIZED RECOMMENDATIONS

| Priority | Recommendation Action | Justification Baseline | Complexity / Effort | Timeline |
| :---: | :--- | :--- | :---: | :---: |
| **1** | Draft & Deploy Incident Response Policy | Essential for PCI-DSS Req 12 and SOC 2. Establishes the CSIRT and prevents uncoordinated data breach disclosures. | Medium | 3 Weeks |
| **2** | Draft & Deploy Data Classification Policy | Foundational requirement for tracking and encrypting Cardholder Data (CHD) and satisfying privacy mandates. | Medium | 4 Weeks |
| **3** | Draft & Deploy Access Control Policy | Establishes the legal and operational ground rules for RBAC, MFA, and mandatory user credential auditing. | High | 4 Weeks |
| **4** | Modernize Password Policy to Modern Standards | Remediates severe vulnerability vectors by enforcing robust MFA and NIST complexity baselines across systems. | Low | 2 Weeks |
| **5** | Overhaul General Information Security Policy | Re-aligns corporate governance with ISO 27001 leadership expectations and embeds secure SDLC loops. | High | 6 Weeks |
| **6** | Revise & Automate Acceptable Use Policy (AUP) | Restores operational compliance by embedding signature requirements into the employee onboarding workflow. | Low | 2 Weeks |
| **7** | Deploy Continuous Security Training & Metrics | Transitions the program from Level 3 (Defined) to Level 4 (Managed) via documented metric verification dashboards. | Medium | Continuous |

---

## 🗺️ PART D: 12-MONTH IMPLEMENTATION ROADMAP

### High-Level Phases
* Phase 1: Foundations (Months 1-3) -> Draft Missing Policies, Establish CSIRT, Finalize Core Baselines.
* Phase 2: Integration (Months 4-6) -> Legacy Policy Overhaul, Deploy DLP & RBAC Syncs, Implement Technical MFA.
* Phase 3: Enforcement (Months 7-9) -> Mandatory Staff Training, Identity Access Audits, Collect Policy KPIs.
* Phase 4: Optimization (Months 10-12) -> Tabletop Simulations, Internal Mock Audits, Formal Attestation Ready.

### 📅 Phase Details & Deliverables

#### Phase 1: Foundational Policy Assembly (Months 1 - 3)
* **Objective:** Remediate all Level 0 critical omissions by authoring core framework documentation.
* **Deliverables:**
  * Formalized and approved Incident Response, Data Classification, and Access Control policies.
  * Formal chartering of the Cyber Security Incident Response Team (CSIRT).
  * Explicit identification and mapping of Cardholder Data Environment (CDE) data stores.

#### Phase 2: Modernization & Technical Integration (Months 4 - 6)
* **Objective:** Overhaul outdated legacy frameworks and synchronize them with technical infrastructure controls.
* **Deliverables:**
  * Comprehensive replacement of the 2019/2020 Information Security and Password policies.
  * Active integration of Data Loss Prevention (DLP) parameters mirroring the new Data Classification Policy.
  * Mandatory technical enforcement of multi-factor authentication (MFA) across all corporate and CDE access points.

#### Phase 3: Operational Enforcement & Training (Months 7 - 9)
* **Objective:** Embed policies into daily operations and validate workforce compliance.
* **Deliverables:**
  * Universal deployment of security awareness training tied to the updated AUP.
  * Completion of the first comprehensive, automated identity and access entitlement review across all internal departments.
  * Deployment of centralized dashboards to track policy exception registries and operational security metrics.

#### Phase 4: Validation, Audit Preparation & Optimization (Months 10 - 12)
* **Objective:** Continuous testing of security controls to achieve compliance readiness for external assessors.
* **Deliverables:**
  * Execution of a live, facilitated tabletop exercise testing the Incident Response infrastructure.
  * Completion of a full internal mock audit assessing PCI-DSS v4.0 and ISO 27001 control sets.
  * Package final compliance evidence artifacts to transition into formal external audit cycles.
