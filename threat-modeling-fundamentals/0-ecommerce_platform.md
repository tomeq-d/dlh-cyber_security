# Threat Modeling: E-commerce Platform

## 1. STRIDE Threat Analysis (Checkout Process)

### Threat 1: Changing the Price in the Browser
* **STRIDE Category:** Tampering
* **Description:** An attacker changes the price of an item in their browser before the request goes to the server [1].
* **Attack Scenario:** A user adds a $1,000 laptop to their cart. Right before clicking "Pay," they use a web proxy tool to intercept the network request and change `"price": 1000.00` to `"price": 1.00`. The server blindly charges them $1.00 and ships the laptop.
* **Impact:** Direct financial loss and broken inventory numbers.
* **Likelihood:** High, because web intercept tools are free and easy to use.
* **Mitigation:** Never trust prices sent by the client browser. The frontend should only send the `product_id` and `quantity`. The Node.js backend must look up the official price from the PostgreSQL database to calculate the total before charging via Stripe.

### Threat 2: Stealing Credit Card Data over Public Wi-Fi
* **STRIDE Category:** Information Disclosure
* **Description:** An attacker intercepts network traffic to steal sensitive customer payment details [2].
* **Attack Scenario:** A customer checks out while connected to an unsecured coffee shop Wi-Fi network. Because the site does not enforce encryption, an attacker on the same network captures the raw data packets and reads the credit card numbers.
* **Impact:** Stolen customer data, legal penalties, and violation of PCI-DSS compliance.
* **Likelihood:** Medium, requiring the attacker to be on the same network or path.
* **Mitigation:** Enforce strict HTTPS everywhere using an HSTS policy. Use the official Stripe SDK (Stripe Elements) in the React frontend so card data goes directly to Stripe's secure servers and never touches your backend.

### Threat 3: Stealing Sessions to Make Unapproved Purchases
* **STRIDE Category:** Elevation of Privilege
* **Description:** An attacker steals a user's logged-in session token to access their private checkout profile [1].
* **Attack Scenario:** The app stores login tokens (JWTs) in unsecure browser local storage. An attacker exploits a basic script flaw (XSS) on the site, steals a user's token, puts it into their own browser, and buys items using the victim's saved shipping profile.
* **Impact:** Fraudulent purchases and compromised user profiles.
* **Likelihood:** Medium, depending on whether the site has script injection flaws.
* **Mitigation:** Store login tokens strictly in `HttpOnly`, `Secure`, and `SameSite=Strict` cookies so JavaScript scripts cannot steal them. Force users to re-enter their card CVV code right before confirming an order.

---

## 2. Trust Boundaries Analysis

A trust boundary is any point where data moves from a place we don't control (untrusted) to a place we do control (trusted) [3].

### The 3 Core Trust Boundaries
1. **User Browser ↔ Public Internet:** Data leaves the user's personal device and enters the public web. We cannot trust anything happening inside the user's browser environment.
2. **Public Internet ↔ Node.js API Backend:** Data crosses our cloud network perimeter. We must validate and clean every piece of data entering here.
3. **Node.js Backend ↔ PostgreSQL Database:** Data moves internally within our private network. The database trusts the backend to feed it safe, sanitized queries.

### Simplified System & Boundary Diagram

```
[ UNTRUSTED USER ZONE ]           ||       [ TRUSTED INTERNAL ZONE ]
                                  ||
 +-------------------------+      ||      +-------------------------+
 |     React Frontend      |      ||      |   Node.js API Backend   |
 |  (User's Web Browser)   |      ||      |  (Verifies & Checks)    |
 +-------------------------+      ||      +-------------------------+
              │                   ||                   │
              │ (HTTPS Requests)  ||                   ├─(SQL)─► [PostgreSQL]
              ▼                   ||                   │
   ============================   ||                   └─(API)─► [Stripe Pay]
   |    TRUST BOUNDARY 1 & 2  |===||
   |  (Internet Outer Edge)   |   ||
   ============================   ||
```

---

## 3. DREAD Risk Assessment: SQL Injection in Product Search

This rates the danger of an attacker typing malicious SQL commands into the public product search bar [1].

### The DREAD Formula
$$\text{Risk Score} = \frac{\text{Damage} + \text{Reproducibility} + \text{Exploitability} + \text{Affected Users} + \text{Discoverability}}{5}$$

### Factor Scoring & Reasoning

* **Damage (D): 9 / 10**
  * *Reasoning:* A successful attack allows someone to bypass login gates or steal the entire user database. (Stripe data is safe, but usernames and histories are leaked).
* **Reproducibility (R): 10 / 10**
  * *Reasoning:* If a search field is broken, the exploit will work perfectly every single time until the code is fixed.
* **Exploitability (E): 8 / 10**
  * *Reasoning:* The search bar is completely public. Free automated hacker tools can find and abuse this flaw within minutes.
* **Affected Users (A): 10 / 10**
  * *Reasoning:* A broken database allows an attacker to steal information belonging to **all** registered users on the site.
* **Discoverability (D): 9 / 10**
  * *Reasoning:* Search boxes are the very first place an attacker looks at and tests when checking a website for security holes.

### Risk Score Calculation

$$\text{Risk Score} = \frac{9 + 10 + 8 + 10 + 9}{5} = \frac{46}{5} = 9.2$$

* **Overall Risk Rating:** **Critical (9.2 / 10)**

---

## References
* [1] OWASP Foundation. "OWASP Top 10:2021 - The Critical Web Application Security Risks." https://owasp.org/www-project-top-ten/
* [2] PCI Security Standards Council. "Payment Card Industry (PCI) Data Security Standard (DSS) v4.0." https://www.pcisecuritystandards.org/
* [3] Microsoft Corporation. "The STRIDE Threat Model." https://learn.microsoft.com/en-us/previous-versions/commerce-server/ee823878(v=cs.20)

