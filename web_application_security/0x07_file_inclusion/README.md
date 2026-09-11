# File Inclusion - web_security_0x07

**Target Machine:** Cyber - WebSec 0x07 (`web0x07.hbtn`)
**Repo path:** `web_application_security/0x07_file_inclusion`

This project covers a series of File Inclusion / Path Traversal challenges built around a common `download_file` endpoint pattern that accepts a `filename` and `path` query parameter and returns the contents of a file from the server's filesystem. Each task incrementally adds a layer of defense, and each layer is bypassed using a different technique.

---

## Task 0 — Path Traversal

**Challenge description:** *"Learn basic path traversal attacks and MD5 hash obfuscation techniques."*
**Endpoint:** `http://web0x07.hbtn/task0/download_file`
**Parameters:** `filename`, `path`
**Flag:** `FLAG_0: 175af81d6cbfdb5408df2c5e99256d47`

### The vulnerability

The endpoint builds a file path on the server from two attacker-controlled inputs — `filename` and `path` — and returns the corresponding file's contents. A normal request looks like:

```
http://web0x07.hbtn/task0/download_file?filename=README.md&path=.
```

Here `path=.` tells the server "look in the current directory" (i.e. the app's default upload/working directory), and `filename` selects the file inside it.

### What we tried first (and why it failed)

The instinctive first move for file inclusion is classic **relative path traversal** — walking up the directory tree with `../` sequences to escape the intended folder:

```
filename=../../../../etc/passwd&path=.
```

This consistently returned 404s, at every depth from 1 to 20+, with both `filename` and `path` carrying the traversal, and even with URL-encoded (`%2e%2e%2f`) and doubly-encoded (`%252e%252e%252f`) variants. A behavioral test confirmed why: uploading a file with a deliberately malicious filename containing `../` caused the server to strip the traversal characters and sanitize the name down to something safe (e.g. `../../../../tmp/pwned.txt` became `tmp_pwned.txt`). This is the signature of a filter like Python's `secure_filename()` (Werkzeug), which strips directory traversal characters before the filename is ever used.

So: **relative traversal via `../` is fully blocked**, on both `filename` and `path`, for both reads and uploads.

### The actual vulnerability

The `path` parameter is never validated to stay **inside** the application's intended base directory. Because it's likely combined with `filename` using something like Python's `os.path.join(path, filename)`, passing an **absolute path** in `path` causes `os.path.join` to discard the base directory entirely — an absolute path always "wins" and becomes the full resolved path, regardless of what came before it.

### The exploit

```
http://web0x07.hbtn/task0/download_file?filename=0-flag.txt&path=/etc
```

No `../`, no encoding, no traversal characters at all — just point `path` directly at the target directory (`/etc`) and `filename` at the real target file (`0-flag.txt`). The filter that blocks `../` never even triggers, because there's nothing traversal-like in the request.

### Takeaway

The developer's mental model was "block traversal *out* of the directory." The actual bug is "never restrict which directory the app reads from *at all*." These are two different problems — sanitizing traversal characters does nothing to stop absolute path injection.

---

## Task 1 — Filter Bypass

**Challenge description:** *"Bypass basic filters using URL encoding and alternative traversal patterns."*
**Endpoint:** `http://web0x07.hbtn/task1/download_file`
**Parameters:** `filename`, `path`
**Flag location:** `/tmp/secure_storage/1-flag.txt`
**Flag:** `FLAG_1: 7b5fabc7a93a26828dee6f6e849cc98a`

### The vulnerability

Task 1's in-app description claims **"a bit more security on the level of download file"** and frames the challenge around bypassing filters and traversal patterns. Despite the framing, this task shares the **exact same root cause as Task 0**: the `path` parameter has no check that the resolved path stays within an allowed base directory.

### The exploit

```
http://web0x07.hbtn/task1/download_file?filename=1-flag.txt&path=/tmp/secure_storage
```

The same absolute-path-injection technique from Task 0 worked immediately, with no modification.

### Why it worked despite "added security"

The endpoint only filters `../` traversal sequences but never checks that the final path stays inside the app's intended directory, so passing an absolute path directly in the `path` parameter bypasses the filter entirely and retrieves the flag. The added filtering almost certainly targets `../`-style traversal patterns specifically — a pattern-matching or character-stripping defense aimed at the "classic" attack. It does nothing to validate that an absolute path passed in `path` is actually within a permitted directory. The task's framing (and its title, "Filter Bypass") suggests the intended solution involves clever encoding or pattern evasion — but the simplest possible technique (skip patterns entirely, just supply an absolute path) already defeats it, because the underlying containment check was never implemented in the first place.

### Takeaway

A filter can be airtight against the specific pattern it's designed to catch, and still be worthless if the actual security boundary (staying inside a base directory) was never enforced independently of that filter.

---

## Task 2 — Encoding Challenges

**Challenge description:** *"Master Base64 encoding and MD5 hash validation bypass techniques."*
**Endpoint:** `http://web0x07.hbtn/task2/download_file`
**Parameters:** `filename`, `path`
**In-app hint:** *"The secret path is: `abc123_secret_path_to_flag`"*
**Flag:** `FLAG_2: 76f1adfcc0caa788a70603fa2c6408a2`

### The vulnerability

This endpoint adds a genuinely different validation layer: the `path` parameter must be **base64-encoded**, and once decoded, it must match a specific expected string exactly. This is discovered empirically:

1. Sending the Task 0/1-style plain absolute path (`path=/etc` style, i.e. plain text of the hinted secret path `abc123_secret_path_to_flag`) returned:
   `Access denied: Invalid encoding. Error: Incorrect padding`
   This is the exact error Python's `base64` module raises when asked to decode a string that isn't valid base64 — a strong signal that the server expects `path` to be base64, not plain text.

2. Base64-encoding the path (`echo -n "/abc123_secret_path_to_flag" | base64`) and retrying returned:
   `Access denied: Invalid path '/abc123_secret_path_to_flag'`
   This confirmed the server *did* successfully decode our base64 string — but then rejected the resulting value because it didn't exactly match what was expected. Note the decoded value still had a leading `/`, which we had added ourselves; the hint text given by the challenge (`abc123_secret_path_to_flag`) had **no leading slash**.

3. Removing the leading slash and re-encoding just the bare hinted string succeeded.

### The exploit

```bash
echo -n "abc123_secret_path_to_flag" | base64
# → YWJjMTIzX3NlY3JldF9wYXRoX3RvX2ZsYWc=
```

```
http://web0x07.hbtn/task2/download_file?filename=2-flag.txt&path=YWJjMTIzX3NlY3JldF9wYXRoX3RvX2ZsYWc=
```

### Takeaway

The endpoint required the `path` parameter to be base64-encoded rather than plain text, and after decoding it, checked that the value exactly matched a hidden secret path (`abc123_secret_path_to_flag`, given in the task's hint) with no leading slash — so base64-encoding that exact string and passing it as `path` granted access to the flag. This isn't really "encoding as a bypass technique" in the offensive sense — it's closer to a locked door where the key (the exact secret path string) was handed to us in the task description. The real skill exercised here was **reading server error messages precisely**: the "incorrect padding" error revealed the expected encoding, and the "invalid path" error (echoing back our decoded value) revealed that an exact-match comparison — not a filesystem check — was happening server-side, and that our value was subtly wrong (extra leading slash).

---

## Task 3 — SSTI (Jinja2)

**Challenge description:** *"Exploit Server-Side Template Injection to access server-side objects."*

Not yet attempted.

---

## Task 4 — LFI with RCE ("Poison the logs")

**Endpoint:** `http://web0x07.hbtn/find_your_shell/find_your_shell.php?filename=...`
**Flag:** `FLAG_4: a98bd1d3f9a0a526b740437c8284d703`

### Task instructions given

1. Accessing `task4_file_hub/shell.php` is necessary to set a required session variable.
2. Some scripts on the machine cannot be executed directly — they can still be triggered indirectly once the correct sequence of files has been accessed.

### The vulnerability

This endpoint follows the same `filename`-driven file-inclusion pattern as the earlier tasks, but adds a **session-gated, multi-step sequence** rather than a single parameter trick:

1. Requesting `task4_file_hub/shell.php` via the endpoint returns:
   `FLAG_SET is now true.`
   This is a **session-based state flag** — visiting this file sets something server-side (a PHP session variable) that unlocks further behavior. This was verified to persist correctly across requests using a `curl` cookie jar (`PHPSESSID`), confirming the state lives in the session and isn't reset between requests.

2. Directly appending a `cmd` parameter to the `shell.php` request (`&cmd=id`) returned no command output — `shell.php` does not process a `cmd` parameter itself. It is purely the "gate" that flips the session flag, not the execution point.

3. Since the file listing/discovery endpoints don't reveal hidden files in `task4_file_hub/`, the remaining files were found via directory fuzzing (`gobuster`/`ffuf` against the `filename` parameter, filtering out the baseline "not found" response size). This revealed a previously unknown file: **`flag.php`**.

4. Fetching `task4_file_hub/flag.php` through the same endpoint, using the session cookie that already had `FLAG_SET` active, returned the flag directly.

### The exploit

```bash
# Step 1: hit shell.php to set the session flag (save cookies)
curl -s -c cookies.txt -b cookies.txt \
  "http://web0x07.hbtn/find_your_shell/find_your_shell.php?filename=task4_file_hub/shell.php"

# Step 2: reuse the session to fetch the real flag file
curl -s -b cookies.txt \
  "http://web0x07.hbtn/find_your_shell/find_your_shell.php?filename=task4_file_hub/flag.php"
```

### Takeaway

This task combined LFI with a **stateful access-control gate**: the flag file wasn't directly discoverable or readable until a specific "unlock" file was visited first in the same session. The task title ("Poison the logs") suggests the *intended* solution path may have involved chaining LFI with log poisoning to achieve PHP code execution (e.g. injecting PHP into a log file via a logged header like User-Agent, then including that log file to execute it) — but in this case, the simpler path of directory-fuzzing for a hidden `flag.php` and reusing the unlocked session was sufficient to retrieve the flag without needing full RCE.

---

## General Patterns Observed Across This Project

1. **Traversal-character filtering ≠ path containment.** Every task that blocked `../` still failed to verify that the *final resolved path* stayed inside an allowed directory. Filtering specific attack patterns is not the same as enforcing the actual security boundary.
2. **Absolute path injection consistently defeats naive filters** that only look for relative traversal sequences (`../`), because `os.path.join()`-style path construction in many languages silently discards prior path components when given an absolute path.
3. **Server error messages are a reconnaissance goldmine.** Both the base64 "incorrect padding" error (Task 2) and the specific response differences between known/unknown files (Task 0/4) revealed internal implementation details that shaped the eventual exploit.
4. **Session state can gate access independently of the file path itself.** Task 4 showed that some endpoints don't just check "is this file allowed" — they check "has the right sequence of prior requests happened in this session," which requires tracking cookies across requests, not just crafting a single clever URL.
5. **Don't over-engineer before testing the simple case.** Several tasks that appeared to require sophisticated encoding or traversal bypasses were solved by the simplest possible technique once the actual validation logic was understood empirically, rather than assumed from the task's framing/title.
