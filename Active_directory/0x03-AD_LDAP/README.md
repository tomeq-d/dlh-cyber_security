# Active Directory — LDAP Project: Enumeration Command Writeup

Target: Windows Server 2019 Domain Controller (`DC01.PENTESTLAB.local`) — IP redacted, see note below
Directory: `Active_directory/0x03-AD_LDAP`

> **Note on the target IP:** the Domain Controller's address is omitted
> from this write-up and replaced with `<DC_IP>` in every command. This
> lab environment sits on a private/internal network, but since this
> README is committed to a public repository, publishing the live IP
> alongside a documented, working attack chain (anonymous LDAP dump,
> credential recovery, etc.) is unnecessary exposure. Substitute your own
> assigned target IP when running these commands.

## Result: all five flags confirmed correct

A single broad, anonymous `ldapsearch` query against the `LDAP-Project`
OU returned every flag needed for Tasks 0–4 in one pass, and each was
verified correct by the checker. Earlier projects in this lab planted
decoy flags in similarly "obvious" spots (including, notably, the exact
same hash seen here for Diana Reeves, which *was* a decoy in a different
project — see caveat below) — but for **this specific project**, that
pattern doesn't hold: every value recovered this way was genuine, despite
each task's description implying a different, more specific tool was
required to find it.

**Takeaway:** this lab reuses the same underlying AD objects and
sometimes the same literal flag values across separate, unrelated
projects. The same string can be the *correct* answer in one project and
a *decoy* in another — the project context matters, not just the string
format. Always confirm against the checker, but don't assume a value is
wrong just because it resembles a decoy seen elsewhere.

---

## The command

```bash
ldapsearch -x -H ldap://<DC_IP> -b "OU=LDAP-Project,DC=PENTESTLAB,DC=local" -s sub "(objectClass=user)" "*" "+"
```

### Flag-by-flag breakdown

| Flag | Meaning |
|---|---|
| `-x` | Use **simple authentication** instead of SASL. On its own this does *not* mean anonymous — it just means "send a plain bind request." Since no `-D` (bind DN) or `-w` (password) was supplied, the bind defaults to an **anonymous** simple bind: no identity, no credentials. Whether an anonymous bind is permitted at all — and how much data it can see — is controlled by the Domain Controller's LDAP anonymous-access policy (most modern DCs restrict this heavily by default; this lab has clearly loosened it for teaching purposes, matching Task 0's premise exactly). |
| `-H ldap://<DC_IP>` | The LDAP **server URI** to connect to: protocol (`ldap://`, unencrypted — as opposed to `ldaps://` on port 636) plus the target host/IP. Defaults to port 389 for `ldap://`. |
| `-b "OU=LDAP-Project,DC=PENTESTLAB,DC=local"` | The **search base** — the distinguished name (DN) of the directory node the search starts from. Only this object and (depending on scope) what's beneath it will be considered. Here it's scoped to the `LDAP-Project` organizational unit, not the whole domain. |
| `-s sub` | The **search scope**. `sub` (subtree) searches the base object itself and everything below it, recursively. The other options are `base` (only the exact object named in `-b`) and `one` (only immediate children, not deeper). |
| `"(objectClass=user)"` | The **search filter**, written in LDAP filter syntax (RFC 4515). This one matches only objects whose `objectClass` attribute includes `user` — i.e., real Active Directory user accounts (people and service accounts), excluding groups, OUs, computers, etc. |
| `"*"` | Requests all **standard** (user) attributes — every attribute normally returned by a default query. |
| `"+"` | Requests all **operational** attributes — metadata attributes that AD does not return by default even when `*` is requested (e.g. `whenCreated`, `uSNChanged`, `dSCorePropagationData`). Combining `"*" "+"` is how you get the fullest possible attribute dump from a single query — still subject to whatever access control (ACLs) the querying identity — here, anonymous — is permitted to see. |

**In plain terms:** *"Anonymously connect to the DC, and for every user
object under the `LDAP-Project` OU (and its sub-containers), return every
attribute — standard and operational — that an anonymous bind is allowed
to read."*

This single query satisfies the anonymous-access premise stated in
Task 0's description ("some Domain Controllers allow partial LDAP
queries without authentication"), and it happens to also surface the
attributes the other four tasks describe — even though each task's
narrative frames a different discovery tool (CrackMapExec, BloodHound,
rpcclient, a targeted `userAccountControl` filter) as the "intended"
path to the same data.

---

## Recovered flags

Nine user objects were returned from three sub-containers under
`OU=LDAP-Project`: `OU=Users` and `OU=Service-Accounts`.

### Task 0 — Diana Reeves (`dreeves`), `info` attribute
```
description: Temp password: Reeves@Temp2024
info: FLAG0{921d2a56bd128240587aa7abbcad0a37fb8e5c6e091fa763754f27648fbe}
```
**Flag:** `FLAG0{921d2a56bd128240587aa7abbcad0a37fb8e5c6e091fa763754f27648fbe}`
— confirmed correct for this project. (Note: the identical hash string
appeared as a decoy in a separate, earlier project in this lab — same
value, different context, different correct/incorrect status.)

### Task 1 — Nathan Cross (`ncross`), `comment` attribute
```
comment: FLAG1{4f3c8b2e1a97d560ec342f8b1094a3d27c6e5f08b23aa914867d390c21e}
```
**Flag:** `FLAG1{4f3c8b2e1a97d560ec342f8b1094a3d27c6e5f08b23aa914867d390c21e}`

### Task 2 — Olivia Stone (`ostone`), `wWWHomePage` attribute
```
wWWHomePage: FLAG2{b7e4190dc3a825f671308ecd5b2f93a40d71c6e982fb047153e8a26490d}
```
**Flag:** `FLAG2{b7e4190dc3a825f671308ecd5b2f93a40d71c6e982fb047153e8a26490d}`

### Task 3 — Victor Hayes (`vhayes`), `scriptPath` attribute
```
scriptPath: FLAG3{3e6d07c2f9b4a158d023e7c80469ba512f93d6e2c47b081a953f10827e5}
```
**Flag:** `FLAG3{3e6d07c2f9b4a158d023e7c80469ba512f93d6e2c47b081a953f10827e5}`

### Task 4 — Ryan Foster (`rfoster`), `employeeNumber` attribute
```
info: svc credential: User@2024!
employeeNumber: FLAG4{4S_R3P_R04ST1NG_M4ST3R_F5}
servicePrincipalName: MSSQLSvc/app-dev.pentestlab.local:1433
userAccountControl: 4260352
```
**Flag:** `FLAG4{4S_R3P_R04ST1NG_M4ST3R_F5}`

`userAccountControl: 4260352` includes the `DONT_REQ_PREAUTH` bit
(`4194304`), confirming Ryan Foster is genuinely the AS-REP-Roastable
account Task 4 describes — the `employeeNumber` attribute served as the
"extended attribute" the task hinted at.

### No flags found on:
- Marcus Webb (`mwebb`) — member of `Lab-ReadOnly`, `Machine-Abuse`,
  `LDAP-Lab-Users`; no flag-shaped attribute
- SQL Service (`svc_mssql`), PKI Service (`svc_pki`), Relay Service
  (`svc_relay`) — service accounts, no flag-shaped attributes present

---

## Key lesson

Unlike the two previous projects in this lab — where a broad, single
`ldapsearch` dump reliably surfaced *decoy* flags planted specifically to
punish this shortcut — this project's design places the genuine answers
in the same easy-to-reach attributes. The lesson isn't "always trust the
first dump" or "always distrust it," but: **verify every recovered value
against the checker before treating it as final**, regardless of which
project or how plausible the result looks. The same underlying AD
objects and even identical flag strings are reused across this lab's
different projects with different correct/incorrect status each time.
