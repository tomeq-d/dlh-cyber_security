Network Traffic Monitoring & Analysis

# Network Traffic Monitoring & Analysis

This project focuses on analyzing network traffic using tools like **tcpdump**, **tshark**, and **Wireshark**.  
It simulates real-world cybersecurity scenarios such as credential extraction, protocol analysis, and malicious activity detection.

---

## 📌 Tasks Overview

+----+-----------------------------+------------------------------------------------------------+-----------------------------------------+--------------------+------------------------------+
| ID | Task                        | Description                                                | Skills                                  | Tools              | Output                       |
+----+-----------------------------+------------------------------------------------------------+-----------------------------------------+--------------------+------------------------------+
| 0  | Basic Packet Analysis       | Identify protocols, main source IP, and HTTP port          | Protocol analysis, IP/port detection    | tshark, Wireshark  | IP:PORT                      |
| 1  | HTTP Traffic Analysis       | Extract Base64 credentials from HTTP traffic               | HTTP analysis, Base64 decoding          | tshark, strings    | username:password            |
| 2  | DNS Query Analysis          | Find suspicious domain and its resolved IP                 | DNS analysis, network investigation     | tshark             | domain:IP                    |
| 3  | TCP Connection Analysis     | Analyze SYN/FIN packets and determine connection details   | TCP handshake analysis                  | tshark             | JSON                         |
| 4  | Advanced Filtering (FTP)    | Extract FTP password from mixed protocol traffic           | Filtering, credential extraction        | tshark, strings    | password                     |
| 5  | TCP Stream Reconstruction   | Rebuild fragmented TCP stream to recover hidden message    | Stream reconstruction                   | tshark             | full message                 |
| 6  | Malicious Traffic Detection | Detect C2 beaconing and extract exfiltrated data           | Threat detection, pattern analysis      | tshark, strings    | JSON                         |
| 7  | RDP Attack Analysis         | Detect brute-force attack and find successful login        | Attack analysis, authentication tracking| tcpdump            | JSON                         |
+----+-----------------------------+------------------------------------------------------------+-----------------------------------------+--------------------+------------------------------+

---

## 🧠 Key Concepts Learned

- Packet and protocol analysis (TCP, HTTP, DNS, FTP, RDP)
- TCP three-way handshake and connection lifecycle
- Extracting credentials from network traffic
- Base64 decoding and data inspection
- TCP stream reconstruction
- Detecting malicious activity (C2 beaconing, exfiltration)
- Identifying brute-force attacks and authentication patterns

---

## 🛠️ Tools Used

- **tcpdump** → Low-level packet inspection and ASCII analysis  
- **tshark** → Advanced filtering and TCP stream reconstruction  
- **Wireshark** → GUI-based packet analysis  
- **strings** → Extract readable data from PCAP files  

---

## ⚠️ Notes

- Some sensitive data is hidden in **raw TCP payloads**
- Not all traffic is automatically decoded by tools
- TCP streams often require **manual or automated reconstruction**
- Small PCAP files can still contain **complex analysis challenges**

---

## 👤 Author

Tomasz Dembowski  
Cybersecurity Student 🚀
``
