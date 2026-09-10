# Server-Side Request Forgery (SSRF)

## Project: dlh-cyber_security / web_application_security/0x08_ssrf

**Target Application:** ShopAdmin (Exclusive Shop)
**Initial Endpoint:** `http://web0x08.hbtn/`
**Tooling:** Burp Suite Community Edition, Firefox, Kali Linux

This project walks through five progressively hardened stages of an SSRF
vulnerability in a shop application's "Check Reduction" / "Check Discount" /
"Invoice Generation" functionality. Each stage patches the previous
bypass, requiring a new technique to reach the internal admin dashboard.

---

## Task 0: Unlocking security, one exploit at a time!

**Endpoint:** `http://web0x08.hbtn/` (forwarded on port 3000)
**Vulnerable parameter:** `articleApi` (POST body, `/check-reduction`)

### Discovery
Intercepting the "Check Reduction" button on a product page revealed the
baseline (legitimate) parameter value:

```
articleApi=http://internal-api.shop.com:3000/check-reduction
```

The app makes a server-side HTTP request to whatever URL is in `articleApi`
and reflects the response back to the user — classic SSRF.

### Bypass technique
No real filtering was in place yet. Using the URL **userinfo (`@`) trick**,
the whitelisted hostname is placed before `@` (satisfying any naive
substring check) while the actual connection target follows `@`:

```
http://internal-api.shop.com:3000@127.0.0.1:3000/admin/list-of-items
```

This reached the internal Express app's own `/admin/list-of-items` route
(the app SSRFing itself), rendering a normally-inaccessible admin page.

### Flag 0
```
175af81d6cbfdb5408df2c5e99256d47
```

---

## Task 1: Is our security a fortress or a sieve?

**Endpoint:** `http://web0x08.hbtn/app2/` (forwarded on port 3001)
**Vulnerable parameter:** `articleApi`

### Discovery
Same domain reused (`internal-api.shop.com`), now on port 3001. Literal
`127.0.0.1` was blocked this time, but the filter only checked for the
**dotted-decimal string** `127.0.0.1` — not other numeric encodings of the
same address.

### Bypass technique
Decimal representation of `127.0.0.1` (`= 127×256³ + 0×256² + 0×256 + 1`)
combined with the `@` userinfo trick:

```
http://internal-api.shop.com:3001@2130706433:3001/admin/list-of-items
```

### Flag 1
```
7b5fabc7a93a26828dee6f6e849cc98a
```

---

## Task 2: Exploit SSRF to breach our security!

**Endpoint:** `http://web0x08.hbtn/app3/` (forwarded on port 3002)
**Vulnerable parameter:** `articleApi`

### Discovery
A fresh baseline capture showed a **new whitelisted domain**:

```
articleApi=http://discount.newshop.tn:3002/app3/check-reduction
```

This time the anti-SSRF filter properly **resolved DNS and validated the
actual IP** — every loopback encoding tested (decimal, hex, octal,
IPv6 `::1`, IPv4-mapped IPv6, zero-padded octets, `nip.io`/`xip.io`
rebinding domains, userinfo tricks, etc.) was correctly detected and
blocked with `403 Attack is detected. BLOCKING ACCESS`.

### Bypass technique
No bypass was actually needed — the legitimate whitelisted domain, used
directly (no loopback trickery), was already sufficient once the correct
path was found:

```
http://discount.newshop.tn:3002/admin/list-of-items
```

**Lesson:** always re-test the plain/baseline whitelisted request against
new paths before reaching for IP-obfuscation techniques.

### Flag 2
```
76f1adfcc0caa788a70603fa2c6408a2
```

---

## Task 3: New security layers in town!

**Endpoint:** `http://web0x08.hbtn/app4-1/` (forwarded on port 8080)
**Vulnerable parameter:** `articleApi` (POST body, `/app4-1/check-discount`)

### Discovery
Baseline capture:

```
articleApi=http://web0x08.hbtn:8080/app4-1/check-discount
```

This time the **whitelisted domain is the public-facing app itself**
(`web0x08.hbtn`), and direct loopback/IP obfuscation against it was
blocked (`400 Invalid hostname` / `403 Attack is detected`, depending on
encoding). A recon nmap scan of the target confirmed the shared backend
ports (3000–3003) plus 8080/27017.

A new **"Next Product"** feature was found on product pages, implementing
an **open redirect**:

```
GET /app4-1/product/nextProduct?path=/app4-1/product/3
→ 302 Found, Location: /app4-1/product/3
```

### Bypass technique
Classic **SSRF-via-open-redirect** (PortSwigger technique): since the
`nextProduct` endpoint lives on the whitelisted domain, it passes the
filter; the app then follows the redirect to the attacker-controlled
internal target:

```
http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin
```

### Flag 3
```
1ea8f6bbd437fafad6ac708a1719f582
```

---

## Task 4: Unraveling the SSRF Mystery in PDF Generation!

**Endpoint:** `http://web0x08.hbtn/app5/`
**Vulnerable parameter:** `handle` (POST body, invoice "Generate PDF" form)

### Discovery
The invoice generator takes a `handle` value and embeds it — **unescaped**
— into an HTML template that is then rendered server-side into a PDF
(no input sanitization). Baseline:

```
POST /app5/ HTTP/1.1
handle=tomeq&insert=
```

renders as plain text "Customer tomeq" in `output.pdf`.

### Bypass technique
Since the `handle` field is rendered as raw HTML before PDF conversion,
injecting an `<iframe>` tag causes the **PDF rendering engine itself**
(a headless browser process, separate from the main app) to make a
server-side HTTP request to the `src` URL and embed the response visually
in the generated PDF — a direct SSRF-to-screenshot primitive.

The renderer process has no external DNS resolution (`web0x08.hbtn` and
other custom domains failed to resolve from inside it), but it can reach
raw loopback IPs directly on the **default HTTP port (80)**:

```
handle=<iframe src="http://127.0.0.1/admin/list-of-items" width="1200" height="1200"></iframe>&insert=
```

Submitting this form and downloading `output.pdf` displays the internal
admin "list of items" table — including the flag — embedded directly in
the invoice PDF.

### Flag 4
```
(see output.pdf generated from the payload above)
```

---

## Summary of Techniques Used

| Task | Filter Strength | Bypass Technique |
|------|-----------------|-------------------|
| 0 | None | Userinfo (`@`) trick |
| 1 | String-match blacklist | Decimal IP + userinfo trick |
| 2 | Resolved-IP blacklist (robust) | None needed — correct path on legit whitelisted domain |
| 3 | Resolved-IP blacklist (robust) | Open redirect chaining via `nextProduct?path=` |
| 4 | Separate renderer process, no filter | HTML injection (`<iframe>`) into PDF template → SSRF via PDF renderer |

## Key Takeaways
- Always capture and inspect the **baseline/legitimate** request before
  attempting bypasses — the "internal" hostname is usually already
  present in a hidden form field or the app's own request.
- IP-obfuscation bypasses (decimal, hex, octal, IPv6 variants, DNS
  rebinding via `nip.io`/`xip.io`) are effective only against naive
  **string-matching** filters; a filter that resolves DNS and validates
  the actual destination IP defeats all of them.
- **Open redirect** endpoints on a whitelisted domain can be chained to
  reach otherwise-blocked internal targets, provided the SSRF fetcher
  follows redirects.
- Document/PDF generation features that render user input as HTML are a
  distinct and often-overlooked SSRF surface, especially when the
  rendering engine runs as a separate process/container with different
  network visibility than the main application.

