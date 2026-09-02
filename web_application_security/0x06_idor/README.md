# 0x06 — Insecure Direct Object Reference (IDOR)

## Project Overview

This project explores Insecure Direct Object Reference (IDOR) vulnerabilities within a simulated banking application called **CyberBank**. The target environment is `http://web0x06.hbtn` and all tasks are performed against the Cyber WebSec 0x06 target.

## General Requirements

- Allowed editors: `vi`, `vim`, `emacs`
- All scripts tested on Kali Linux
- All scripts must be exactly one line long (`wc -l file` must print `1`)
- All files must end with a new line
- A `README.md` file at the root of the project folder is mandatory

## Vulnerability Assessment Report

A full professional vulnerability report covering all findings from this project is available here:

**[CyberBank Vulnerability Assessment Report — Google Docs](https://docs.google.com/document/d/1Avuot3N68qzOZrBQAysToiv39lL-P8bM/edit?usp=sharing&ouid=112557182350692958991&rtpof=true&sd=true)**

---

## Tasks

### Task 0 — Uncovering User IDs

**File:** `0-flag.txt`

**Description:**
The first step in IDOR exploitation is discovering other users' IDs. By exploring the CyberBank API and observing network requests, user identifiers are exposed through endpoints that lack proper authorization checks.

**Target Endpoint:** `http://web0x06.hbtn/dashboard`

**Steps:**
1. Log into CyberBank and open DevTools → Network tab
2. Observe the `GET /api/customer/info/me` request — this returns your own customer profile including your `id` field
3. Visit `GET /api/customer/contacts/me` to retrieve the contact list — each entry includes other users' `id` fields
4. Access another user's profile by substituting their `id` in `GET /api/customer/info/<customer_id>`
5. The response includes a `flag_0` field

---

### Task 1 — Enumerating Account Numbers for Balance Disclosure

**File:** `1-flag.txt`

**Description:**
Using the user IDs discovered in Task 0, enumerate account numbers and access account balances belonging to other users.

**Target Endpoint:** `http://web0x06.hbtn/dashboard`

**Steps:**
1. From the target user's customer profile, extract the `accounts_id` array
2. Access `GET /api/accounts/info/<account_id>` using a victim's account ID
3. The response returns balance, routing info, and a `flag_1` field

---

### Task 2 — Manipulating Wire Transfers to Inflate Account Balance

**File:** `2-flag.txt`

**Description:**
Exploit a business logic flaw in the wire transfer endpoint to artificially inflate your account balance beyond $10,000. The server does not validate that transfer amounts are positive, allowing negative-amount transfers that increase the sender's balance.

**Target Endpoint:** `http://web0x06.hbtn/dashboard`

**Steps:**
1. Capture the `POST /api/accounts/transfer_to/<account_id>` request format using DevTools
2. Replay the request via the browser console with a large negative `amount` value
3. The source account balance increases instead of decreasing
4. Once `total_balance` exceeds $10,000, `GET /api/customer/info/me` returns a `flag_2` field

---

### Task 3 — Bypassing 3D Secure Verification for Unauthorized Payment

**File:** `3-flag.txt`

**Description:**
Execute a payment charged to another user's card by bypassing 3D Secure (OTP) verification. The confirmation endpoint does not validate that the submitted OTP belongs to the same card or transaction being confirmed.

**Target Endpoints:** `http://web0x06.hbtn/upgrade` · `http://web0x06.hbtn/confirmation`

**Steps:**
1. Obtain a victim's full card details (PAN, CVV, expiry) via IDOR on `GET /api/cards/info/<card_id>`
2. Initiate a payment with the victim's card: `POST /api/cards/init_payment` → receive victim's `transaction_id`
3. Initiate a separate payment with your own card via the `/upgrade` UI → receive your own OTP from `GET /api/cards/3dsecure/<your_card_id>`
4. Confirm the victim's transaction using your own valid OTP: `POST /api/cards/confirm_payment/<victim_transaction_id>`
5. The server confirms the payment without validating OTP ownership — `flag_3` is returned in the response

---

### Task 4 — Comprehensive Vulnerability Report

**Directory:** `web_application_security/0x06_idor`

**Description:**
Compile all findings into a professional vulnerability report suitable for presentation to a financial institution. The report covers all discovered vulnerabilities with descriptions, impact assessments, reproduction steps, and remediation recommendations.

**Report:** [Google Docs — CyberBank Vulnerability Assessment Report](https://docs.google.com/document/d/1Avuot3N68qzOZrBQAysToiv39lL-P8bM/edit?usp=sharing&ouid=112557182350692958991&rtpof=true&sd=true)

---

## Repository Structure

```
web_application_security/0x06_idor/
├── README.md       — This file
├── Solution.md     — Step-by-step walkthrough of all flag recoveries
├── 0-flag.txt      — Flag for Task 0: User ID enumeration
├── 1-flag.txt      — Flag for Task 1: Account balance disclosure
├── 2-flag.txt      — Flag for Task 2: Wire transfer manipulation
└── 3-flag.txt      — Flag for Task 3: 3D Secure bypass
```

## Author

Tomasz Musk — Holberton School Cybersecurity Academy
