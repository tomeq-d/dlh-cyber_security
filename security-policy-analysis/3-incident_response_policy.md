# GlobalTech Manufacturing - Incident Response Policy

## Document Control
| Field | Value |
| :--- | :--- |
| **Policy ID** | POL-IR-003 |
| **Version** | 1.0 |
| **Effective Date** | 2026-06-24 |
| **Review Date** | 2027-06-24 |
| **Policy Owner** | Chief Information Security Officer (CISO) |
| **Approved By** | Executive Risk Committee |
| **Classification** | Confidential / Internal |

---

### 1. Purpose
This Incident Response Policy establishes a rigorous operational framework to detect, contain, eradicate, and recover from security incidents affecting GlobalTech Manufacturing. The goal is to minimize downtime, safeguard human life, protect operational technology (OT/IoT) assembly lines, and ensure compliance with ISO 27001, GDPR, and international maritime and manufacturing regulations.

### 2. Scope
* **2.1 Applicability:** This policy applies to all 2,000 employees, contractors, third-party logistics providers, and operational managers across all 5 international manufacturing plants.
* **2.2 Covered Assets:** All corporate IT assets (ERP systems, corporate networks, cloud platforms) and OT/IoT environments (SCADA networks, programmable logic controllers [PLCs], smart industrial sensors).
* **2.3 Exclusions:** None.

---

### 3. Policy Statements

#### 3.1 Incident Response Team (CSIRT) Structure
GlobalTech establishes a permanent Cyber Security Incident Response Team (CSIRT) organized under the following matrixed responsibilities:
* **Incident Response Manager (IRM):** Coordinates the tactical execution of response workflows, declares severity levels, and holds authority over system isolation commands.
* **Security Analysts:** Execute technical investigation, forensics ingestion, and run log correlations.
* **IT Support / OT Engineers:** Provide local asset maps and execute technical isolation commands across IT and factory floor networks.
* **Legal Counsel:** Evaluates regulatory breach obligations (GDPR notifications) and handles liability frameworks.
* **Communications/PR:** Controls all public statements, internal updates, and stakeholder announcements.
* **Executive Sponsor:** Authorizes major asset shutdowns and allocates emergency funding.

#### 3.2 Detection and Reporting
* **3.2.1 Detection Streams:** Incidents are proactively flagged through automated security orchestrators (SIEM/XDR), OT anomaly network monitors, external threat intelligence feeds, or manual user tickets.
* **3.2.2 Reporting Requirements:** Any worker who uncovers a suspected network anomaly, ransomware note, unapproved device attached to a PLC, or a lost corporate endpoint must report it to the Security Operations Center (SOC) within 15 minutes.
* **3.2.3 Information Ingestion:** Triage reports must document: initial discovery timestamp, symptoms observed, impacted machinery/systems, and indicators of compromise (IOCs) if known.

#### 3.3 Response Procedures (NIST IR Lifecycle)
* **3.3.1 Containment:** Fast-acting short-term mitigation (e.g., VLAN isolation) must prioritize human safety and operational plant integrity. System administrators must balance rapid containment with forensic evidence preservation.
* **3.3.2 Eradication:** Technical groups will execute full root-cause evaluations, eliminate persistent backdoors, and validate that malicious payloads are removed before staging system rollouts.
* **3.3.3 Recovery:** Teams will restore workloads using verified-clean backups, validate systems with continuous baseline monitoring, and run strict functional and security tests before bringing production lines back online.

#### 3.4 Evidence Handling & Chain of Custody
* **3.4.1 Preservation Integrity:** Forensic disk images and memory dumps must be collected prior to system modification or shutdown. Hash signatures (SHA-256) must be calculated immediately upon ingestion.
* **3.4.2 Chain of Custody (CoC):** A formal document tracking form must capture who handled physical hardware or digital evidence images, including exact timestamps and storage locker confirmations.

#### 3.5 Post-Incident Activities
* **3.5.1 Lessons Learned:** Within 5 business days of incident closure, the IRM will convene a mandatory debriefing with all CSIRT stakeholders to evaluate procedural gaps and update technical controls.
* **3.5.2 Formal Documentation:** A comprehensive review must be assembled and archived to satisfy compliance obligations.

---

### 4. Roles and Responsibilities
* **CISO:** Owns the Incident Response Program, briefs executive leadership, and reviews monthly metrics.
* **Incident Response Manager:** Runs active containment bridges and owns the deployment of response playbooks.
* **Local Plant Managers:** Ensure that local technical support teams execute CSIRT instructions immediately on the factory floors.
* **All Users:** Participate in annual response simulations and promptly flag security anomalies.

### 5. Compliance
* **5.1 Monitoring:** SIEM triggers continuously monitor access records and network paths for suspicious behavior.
* **5.2 Reporting:** Aggregated incident tracking summaries are compiled quarterly for audit assessment.
* **5.3 Auditing:** Annual incident simulations and external penetration testing sessions validate response capabilities.

### 6. Enforcement
* **6.1 Violations:** Intentionally ignoring reporting rules, tampering with forensics, or leaking breach metrics may result in severe disciplinary actions up to termination.
* **6.2 Reporting Violations:** Report policy deviations directly to the internal audit hotline at ir-compliance@globaltechmfg.com.

### 7. Exceptions
* **7.1 Process:** Workarounds must be authorized by the CISO following a formal risk assessment.
* **7.2 Cadence:** Exceptions expire after 6 months and require full re-evaluation to remain active.

### 8. Definitions
* **Operational Technology (OT):** Hardware and software that detects or causes changes in physical processes through direct control of industrial equipment.

### 9. Related Documents
Business Continuity and Disaster Recovery (BCDR) Plan; GDPR Notification Guide; OT Firewall Configuration Standard.

### 10. Revision History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-06-24 | CISO Office | Initial Release. |

### 11. Acknowledgment
Employees acknowledge that adhering to incident discovery, reporting, and containment workflows is a binding condition of employment.

---

## 📊 SECTION I: INCIDENT CLASSIFICATION MATRIX

| Severity | Description | Response Time | Target Examples |
| :--- | :--- | :--- | :--- |
| **Critical** | Active exploitation of OT/SCADA systems causing active plant shutdowns, safety threat to personnel, or widespread corporate ransomware execution. | **< 15 Minutes** | Active malware spread across factory PLCs, safety system override, or complete ERP system encryption. |
| **High** | Successful compromise of high-value business assets, cloud infrastructure data exfiltration, or targeted phishing compromise of administrative accounts. | **< 1 Hour** | Exfiltration of GDPR-regulated customer PII data, unauthorized modifications to source repositories, or localized server failure. |
| **Medium** | Isolated malware infections on single non-critical endpoints, repeated login failures, or suspicious server telemetry without confirmed data loss. | **< 4 Hours** | Standard malware alert on an engineering workstation or a brute-force attack detected on an edge firewall. |
| **Low** | Near-miss events, minor policy non-compliance, spam distribution runs, or a single employee reporting a suspicious unclicked link. | **< 24 Hours** | A single user receiving a phishing mail or an employee tracking a lost bit locker-encrypted smartphone. |

---

## 📢 SECTION II: COMMUNICATION PLAN

| Stakeholder | When to Notify | Method | Key Objective |
| :--- | :--- | :--- | :--- |
| **Executive Management** | Immediately for Critical/High events; daily summaries during active incidents. | Secure Internal Video Bridge / Out-of-band Messaging App. | Align on business impact, cost parameters, and business continuity sign-offs. |
| **Legal Counsel** | Within 2 hours of declaring a High or Critical data breach. | Direct Phone Line / Secure Corporate Email. | Assess reporting obligations, review draft notifications, and protect evidence under privilege. |
| **Regulators (GDPR/Data Privacy)** | Within 72 hours of defining a confirmed PII data breach. | Secure Regulatory Ingestion Portal. | Satisfy compliance mandates with initial incident parameters and planned mitigation updates. |
| **Affected Users** | Upon containment validation and under guidance from Legal and PR teams. | Mass Broadcast Email / Internal Communication Dashboards. | Detail the operational impact, outline remediation steps, and prevent panic. |

---

## 📝 SECTION III: INCIDENT REPORT TEMPLATE

```text
GLOBALTECH MANUFACTURING - INCIDENT REPORT FORM
--------------------------------------------------------------------------------
1. GENERAL ADMINISTRATIVE INFORMATION
Report Date:                     Incident Tracking ID:
Prepared By:                     Job Title/Role:
Contact Phone/Email:             Incident Status: [ ] Active [ ] Contained [ ] Closed

2. INITIAL DETECTION AND TRIAGE DETAILS
Detection Timestamp:             Reporting Source: [ ] SIEM [ ] User [ ] External
Impacted Systems / Machinery:
Impacted Countries/Plants:       Estimated Severity Level: [ ] Crit [ ] High [ ] Med [ ] Low

3. INCIDENT DESCRIPTION AND NATURE
Provide a detailed summary of the observed behavior, anomalies, or error codes (Attach log snippets if available):
--------------------------------------------------------------------------------

4. TECHNICAL DETAILS (IOCs)
File Hashes (SHA-256):
Source IP/Domain Addresses:
Impacted Accounts/Credentials:

5. CONTAINMENT STRATEGY EXECUTED
Short-Term Isolation Steps:
Evidence Preserved: [ ] Memory Dump [ ] Disk Image [ ] Firewall Logs [ ] None
Timestamp of Containment:

6. SIGN-OFF & APPROVALS
Incident Manager Name:           Signature:                       Date:
