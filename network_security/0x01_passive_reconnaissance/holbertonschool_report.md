# Passive Reconnaissance Report: holbertonschool.com

## 1. Introduction

This report presents passive reconnaissance findings for the domain **holbertonschool.com** using Shodan. The objective is to gather information about infrastructure, IP ranges, and technologies used.

---

## 2. IP Addresses and Ranges

### Identified IPs:
- 35.180.27.154
- 52.47.143.83

### Hosting Provider:
- Amazon Web Services (AWS)
- Region: eu-west-3 (Paris)

### IP Ranges:
- 35.180.0.0/16
- 52.47.0.0/16

---

## 3. Subdomains

Discovered subdomains:
- holbertonschool.com
- yriry2.holbertonschool.com

---

## 4. Technologies and Frameworks

Based on Shodan analysis:

### Web Server:
- nginx (versions 1.18.0 and 1.21.6)

### Operating System:
- Ubuntu Linux

### SSL / Security:
- Let's Encrypt SSL certificate
- Supports TLSv1.2 and TLSv1.3

---

## 5. Services

Observed open services:
- HTTP (port 80)
- HTTPS (port 443)

Responses indicate:
- 301 redirects (likely enforcing domain routing)
- 200 OK responses on active subdomains

---

## 6. Observations

- Infrastructure hosted on AWS cloud
- Use of nginx suggests a lightweight and efficient server setup
- HTTPS is properly configured using Let's Encrypt
- Minimal exposed surface, indicating good security practices

---

## 7. Conclusion

Holbertonschool.com uses AWS cloud infrastructure with nginx web servers and modern SSL security. The attack surface is limited and appears well-managed.

---

## 8. Tools Used

- Shodan (https://www.shodan.io)
