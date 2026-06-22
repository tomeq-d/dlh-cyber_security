# Threat Modeling: Healthcare Mobile App

## 1. Critical Asset Identification (CIA Triad)

### Most Critical Asset: Protected Health Information (PHI)
The most critical asset is patient data (medical records, prescriptions, and messages) [1].

* **Confidentiality (Priority 1 - 10/10):** Medical data is highly private. If leaked, it causes identity theft and violates HIPAA laws, leading to massive fines.
* **Integrity (Priority 2 - 9/10):** If an attacker changes a dosage or allergy record, a doctor might give the wrong treatment, risking the patient's life.
* **Availability (Priority 3 - 8/10):** Patients need access to refills and doctors, but minor app downtime can be managed via phone calls in emergencies.

---

## 2. STRIDE Threat Analysis (Messaging Feature)

### Threat 1: Pretending to be a Doctor (Spoofing)
* **STRIDE Category:** Spoofing
* **Description:** An attacker tricks the system into sending messages under a doctor's name [2].
* **Attack Scenario:** An attacker intercepts an active user session and sends a fake message to a patient saying: "Stop taking your medication immediately."
* **Impact:** Serious patient injury or death, and legal lawsuits against the hospital.
* **Likelihood:** Medium.
* **Mitigation:** The server must automatically pull the sender's identity from secure login tokens (JWTs) instead of trusting the identity text sent by the app.

### Threat 2: Altering Messages in Transit (Tampering)
* **STRIDE Category:** Tampering
* **Description:** An attacker intercepts and changes messages while they travel across the network [2].
* **Attack Scenario:** On a public Wi-Fi network, an attacker intercepts a patient's message asking "Can I take 5mg?" and changes it to "Can I take 50mg?".
* **Impact:** Medication poisoning or overdose.
* **Likelihood:** Medium, if network traffic is unencrypted.
* **Mitigation:** Use strict HTTPS with Certificate Pinning in the mobile apps to block network interception.

### Threat 3: Denying a Message Was Sent (Repudiation)
* **STRIDE Category:** Repudiation
* **Description:** A user or doctor claims they never sent a specific message because there are no solid logs [2].
* **Attack Scenario:** A doctor gives bad medical advice over chat. After an incident, the doctor deletes the message and claims the patient made it up or the app glitched.
* **Impact:** Loss of legal accountability during investigations.
* **Likelihood:** Low-to-Medium.
* **Mitigation:** Keep unchangeable, append-only security logs stored on an isolated server.

### Threat 4: Reading Chats Locally on a Device (Information Disclosure)
* **STRIDE Category:** Information Disclosure
* **Description:** An attacker reads sensitive chat history directly from the phone's local storage [3].
* **Attack Scenario:** An attacker steals an unlocked phone or uses malware to read the unencrypted database cache where the app stores chat history.
* **Impact:** Leak of private medical data (PHI).
* **Likelihood:** Medium.
* **Mitigation:** Store all local data using the phone's native secure storage (iOS Data Protection or Android EncryptedSharedPreferences).

---

## 3. Prioritized Security Controls

1. **Multi-Factor Authentication (MFA):** Blocks unauthorized logins. This is priority 1 because identity is the first line of defense.
2. **Data Encryption (AES-256 & TLS 1.3):** Protects data in transit and at rest. This keeps the platform HIPAA compliant [1].
3. **Role-Based Access Control (RBAC):** Ensures patients can only view their own data and doctors can only see their assigned patients.
4. **Immutable Audit Logs:** Keeps a secure history of who accessed what data to satisfy legal requirements.
5. **Input Validation:** Cleans all text fields to block hackers from executing malicious code injections.

---

## References
* [1] U.S. Department of Health and Human Services (HHS). "Health Insurance Portability and Accountability Act (HIPAA) Security Rule." https://www.hhs.gov/hipaa/
* [2] Microsoft Corporation. "The STRIDE Threat Model." https://learn.microsoft.com/en-us/previous-versions/commerce-server/ee823878(v=cs.20)
* [3] OWASP Foundation. "OWASP Mobile Top 10." https://owasp.org/www-project-mobile-top-10/

