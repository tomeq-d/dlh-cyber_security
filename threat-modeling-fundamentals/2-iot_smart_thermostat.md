# Threat Modeling: IoT Smart Thermostat

## 1. IoT-Specific Threats

1. **Physical Debug Port Exploitation:** Attackers plug directly into diagnostic pins (UART/JTAG) on the circuit board to get root command access [1].
2. **Firmware Extraction:** Desoldering the memory chip to copy the software and find hidden passwords or security flaws [1].
3. **Local Radio Protocol Attacks:** Exploiting weak local connections like Zigbee or Bluetooth to hijack the thermostat without using the internet [2].
4. **Hardware Cloning:** Copying a real device's secret keys to make a fake device that sends bad data to the cloud network [2].
5. **Insecure Local Fallback:** Exploiting local control systems that keep working when internet is down but lack proper login checks.

---

## 2. Physical Access Attack Chain

```
[Open Enclosure] ──► [Connect to Board Pins] ──► [Extract Keys] ──► [Control Local Network]
```

* **Attack Scenario:** An attacker takes the thermostat off the wall, opens the case, and connects a small device to the diagnostic pins [1]. They reboot it into a root shell, extract the Wi-Fi password and cloud connection certificates, and then use the thermostat as a gateway to hack other devices on the home network.
* **Impact:**
  * **Safety:** Turning off heat in winter to freeze and burst pipes.
  * **Privacy:** Tracking energy usage to know when the home is empty.
  * **Infrastructure:** Turning thousands of thermostats into a botnet to attack websites.

---

## 3. Secure Over-The-Air (OTA) Updates

1. **Cryptographic Code Signing:** All firmware must be signed with a private key kept offline by the company. The thermostat checks this signature using an embedded public key before installing it [3].
2. **Hardware Secure Boot:** A chip-level check ensures the device only runs trusted, unmodified software from the moment it powers on [3].
3. **Mutual TLS (mTLS):** Both the device and the update server must verify each other's certificates before any files are sent.
4. **Anti-Rollback Protection:** Use built-in hardware counters to block attackers from installing older, insecure versions of the software.
5. **A/B Partitioning:** Write updates to a secondary memory partition. If the update fails or crashes, the device automatically reverts to the working software on the primary partition.

---

## References
* [1] OWASP Foundation. "OWASP Internet of Things (IoT) Top 10." https://owasp.org/www-project-internet-of-things/
* [2] NIST. "NIST IR 8259: Foundational Cybersecurity Activities for IoT Device Manufacturers." https://csrc.nist.gov/
* [3] ENISA. "Guidelines for Securing the Internet of Things." https://www.enisa.europa.eu/

