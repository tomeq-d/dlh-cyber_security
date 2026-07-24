# Task 1: Risk Identification
**Project:** Risk Assessment & Mitigation Strategies  
**Organization:** SecureBank (Online Banking Platform – 50,000 active users)  

---

## Learning Objective
Identify and document critical organizational assets, potential threats, and technical/operational vulnerabilities to build a comprehensive Risk Register using structured risk statements.

---

## Risk Register

| ID | Asset | Asset Category | Threat | Threat Category | Vulnerability | Risk Statement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | Customer Financial Records | Information | Data Exfiltration / Cyber Criminals | Adversarial | Unencrypted API endpoints transmitting sensitive financial data | The **cyber criminal** exploiting **unencrypted API endpoints** in **customer financial records** could cause **unauthorized access and widespread financial data exfiltration**. |
| **R2** | Core Database Server | Hardware | Data Center Power Grid Outage | Environmental | Lack of redundant uninterrupted power supply (UPS) and back-up diesel generator | The **power grid outage** exploiting **lack of redundant UPS systems** in **core database server hardware** could cause **extended service outage and database corruption**. |
| **R3** | Web Application Middleware | Software | Ransomware Deployment | Adversarial | Unpatched zero-day flaw in third-party software library | The **ransomware payload** exploiting **unpatched zero-day vulnerabilities** in **web application middleware** could cause **system lockouts and severe financial operational disruption**. |
| **R4** | Help Desk Support Team | People | Social Engineering / Vishing | Adversarial | Insufficient identity verification procedures during password reset calls | The **social engineering attacker** exploiting **insufficient identity verification procedures** in **help desk support staff** could cause **unauthorized account takeover of high-value client accounts**. |
| **R5** | Online Payment Gateway | Services | Hardware Microcode Failure | Structural | Single point of failure (SPOF) in core network routing equipment | The **hardware microcode failure** exploiting **single point of failure network topology** in **online payment gateway services** could cause **complete failure of digital payment processing**. |

---

## Summary of Asset & Threat Coverage

* **Asset Categories Covered:**
  1. **Information:** Customer Financial Records
  2. **Hardware:** Core Database Server
  3. **Software:** Web Application Middleware
  4. **People:** Help Desk Support Team
  5. **Services:** Online Payment Gateway

* **Threat Categories Covered:**
  1. **Adversarial:** Cyber Criminals / Ransomware / Social Engineering
  2. **Environmental:** Data Center Power Grid Outage
  3. **Structural:** Hardware Microcode / Equipment Failure
