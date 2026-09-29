# Linux Privilege Escalation

**Cybersecurity Academy — `privilege_escalation_security_shells/0x01_linux_privesc`**

This project is a set of three hacking challenges. In each one we start as an ordinary, low-power user on a Linux machine and have to find a way to become **root** — the all-powerful administrator account. Once we are root, we can read a secret file, `/root/flag.txt`, that ordinary users are forbidden from opening. The secret inside is called a **flag**, and submitting it proves we solved the challenge.

This README explains every challenge from the ground up, in plain language, so that someone with little or no computer background can follow along.

---

## Table of contents

1. [Background: what does "privilege escalation" mean?](#background)
2. [How we connect to the machines](#connecting)
3. [Task 0 — Escalation through a `sudo` command (`choom`)](#task-0)
4. [Task 1 — Escalation through a misconfigured scheduled job (`cron` + `tar`)](#task-1)
5. [Task 2 — Escalation through a vulnerable custom program (SUID binary)](#task-2)
6. [Summary of results](#results)
7. [Glossary](#glossary)

---

<a name="background"></a>
## 1. Background: what does "privilege escalation" mean?

On any computer there are different levels of power:

- **Ordinary users** can do everyday things (read their own files, run normal programs) but are blocked from touching the important, protected parts of the system.
- **Root** (also called the *administrator* or *superuser*) can do **anything** — read every file, change any setting, install or delete anything.

Think of a large office building. An ordinary user has a key to their own office. Root has the master key that opens every door in the building.

**Privilege escalation** is the art of starting with the small key and finding a trick, a mistake, or a badly-locked door that lets you get hold of the master key. Attackers do this to take over systems; security professionals learn to do it so they can find and fix these weaknesses before criminals do.

In every task below, the machine has been deliberately set up with one such mistake. Our job is to find it and use it.

**The flag:** the goal is always to read `/root/flag.txt`. The file contains text like:

```
CTF{privilege_escalation_via_sudo_choom_579eea17d42c385d4be6a0750c6b5562}
```

The part we actually submit is only the long code in the middle — the **hash** (here `579eea17...`). A hash is just a unique fingerprint made of letters and numbers.

---

<a name="connecting"></a>
## 2. How we connect to the machines

Each challenge runs on a fresh, separate practice machine (a "container") that the school spins up on demand. Each one is given its own network address (an **IP address**, like a street address for a computer).

We connect using **SSH** (Secure Shell) — a tool that gives us a remote command line on the target machine over an encrypted connection. The command looks like this (replace the address with the one the container shows):

```
ssh user@CONTAINER_IP
```

When asked for a password, we type:

```
user
```

After that we have a text-based control panel (a **terminal**) on the remote machine, logged in as the low-power account named `user`.

---

<a name="task-0"></a>
## 3. Task 0 — Flag File Privilege Escalation (`sudo` + `choom`)

### The concept

Linux has a command called **`sudo`** ("**s**uper**u**ser **do**"). It lets an ordinary user run *specific* commands with root's power, usually after typing a password. It exists so that, for example, a user can be trusted to restart the printer service without being handed the master key to the whole building.

The danger: an administrator decides *which* commands you may run through `sudo`. If they pick the wrong command — one that can be tricked into doing more than intended — you can abuse it to become full root.

### Step 1 — See what `sudo` lets us do

The command `sudo -l` lists exactly which commands our user is allowed to run as root:

```
sudo -l
```

The machine answered:

```
User user may run the following commands:
    (ALL) NOPASSWD: /usr/bin/choom
```

Translated into plain English: *"You are allowed to run the program `/usr/bin/choom` as root, and you don't even need to type a password."* (`NOPASSWD` means no password required.)

### Step 2 — Why `choom` is the weak link

`choom` is a small, legitimate system tool. Its real job is boring: it adjusts how likely a program is to be shut down when the computer runs low on memory. But — and this is the whole trick — to do that job, **`choom` launches another program for you.** You tell it *which* program to launch.

So if root launches `choom`, and `choom` then launches a command *of our choosing*, that command also runs with root's power. We simply ask it to launch a shell (a command line) for us.

This kind of "a trusted tool can be talked into running our command" trick is so common that there is a public catalogue of them called **GTFOBins**. `choom` is one of the entries.

### The exploit

```
sudo choom -n 0 /bin/bash
```

What each piece means:
- `sudo` — run the following with root's power (allowed, as we saw).
- `choom` — the tool we're permitted to run.
- `-n 0` — a harmless required setting (it just gives `choom` a valid number to work with).
- `/bin/bash` — **the program we secretly want `choom` to launch for us: a new command line.**

Because `choom` was started as root, the new command line it opens is also **running as root**.

### Confirming and grabbing the flag

Check who we are now:

```
id
```

It showed `uid=0(root)` — `uid=0` is the identity number of root. We made it.

Read the secret:

```
cat /root/flag.txt
```

**Why it worked:** the administrator trusted us with a command (`choom`) that is capable of launching *any* other program. Trusting someone with that is the same as trusting them with everything, because they can simply launch a root shell.

**Flag:** `fe90cae5428da629bd59e540e5d129bb`

---

<a name="task-1"></a>
## 4. Task 1 — Privilege Escalation through Cron Job Misconfiguration

### The concept

Linux can run tasks automatically on a schedule — for example, "make a backup every night at 2 a.m." The system that does this is called **cron**, and each scheduled task is a **cron job**. Many cron jobs run as **root**, because backups and maintenance need full access.

The danger: if a root-scheduled job runs a program or handles files that an *ordinary user is allowed to tamper with*, then the user can quietly influence what root does — and make root do something helpful to the attacker instead.

### Step 1 — Find the scheduled jobs

Cron jobs are listed in special files. We read them:

```
cat /etc/crontab
```

```
cat /etc/cron.d/*
```

Among the normal entries, one stood out:

```
* * * * * root (cd /home/user/dropbox; /usr/bin/tar -czf /tmp/dropbox_backup.tar.gz *) 2>&1
```

Reading it in plain English:
- `* * * * *` — **run this every single minute.**
- `root` — run it **as root** (full power).
- `cd /home/user/dropbox` — go into the folder `/home/user/dropbox`. **This folder belongs to us — we can put whatever files we like inside it.**
- `tar -czf ... *` — bundle up **all files** (`*`) in that folder into a backup archive.

So every minute, root walks into *our* folder and runs `tar` on *our* files. That is the opening.

### Step 2 — The trick: "wildcard injection" with `tar`

The key is the little star, `*`. In Linux, before a command runs, the system replaces `*` with **the list of filenames in the folder**. So `tar ... *` really becomes `tar ... file1 file2 file3 ...`.

Here's the clever part: the `tar` program treats some words on its command line as **filenames**, but other words as **instructions** (options), depending on how they are spelled. Options start with dashes, like `--checkpoint`.

`tar` happens to have an option that means *"run this command for me"*:

- `--checkpoint=1` — tells `tar` to pause after processing a file.
- `--checkpoint-action=exec=...` — tells `tar` **"when you pause, run this command."**

Now — what if we create **files whose names are actually those options?** When root's cron job runs `tar ... *`, the star expands to include our sneakily-named files, and `tar` mistakes their *names* for *instructions*. It ends up running our command — as root.

This is called **wildcard injection**: we inject options into a command by disguising them as filenames.

### The exploit, step by step

**a) Prepare the payload.** We write a tiny script that, when run as root, makes us a permanent "root launcher." We put it in our folder:

```
echo 'cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash' > /home/user/dropbox/exploit.sh
```

What this script does when root runs it:
- `cp /bin/bash /tmp/rootbash` — make a **copy** of the command-line program `bash`, calling the copy `rootbash`.
- `chmod 4755 /tmp/rootbash` — set a special flag (called **SUID**, explained fully in Task 2) that means *"whoever runs this copy runs it with the power of its owner."* Since root creates it, its owner is root — so anyone who runs `rootbash` gets root power.

**b) Create the two option-named files.** Their names *are* the `tar` instructions:

```
cd /home/user/dropbox
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh exploit.sh'
```

- `touch` normally just creates empty files.
- The `--` tells `touch`: *"everything after this is a filename, not an option for you"* — otherwise `touch` itself would get confused by the dashes.
- So we end up with two empty files literally named `--checkpoint=1` and `--checkpoint-action=exec=sh exploit.sh`, sitting next to `exploit.sh`.

**c) Wait one minute.** The cron job fires, root runs `tar ... *`, the star expands to include our option-named files, `tar` obeys them, and executes `sh exploit.sh` **as root**. That creates our root-powered `rootbash`.

Check that it appeared:

```
ls -la /tmp/rootbash
```

We saw `-rwsr-xr-x ... root root ... /tmp/rootbash`. The `s` in that permission string is the magic SUID flag, and the owner is `root`. 

**d) Use it.** Launch our root copy:

```
/tmp/rootbash -p
```

The `-p` is important: without it, `bash` politely drops the borrowed power on startup. `-p` tells it to **keep** the root power.

```
id
```

Now `id` reported root. Read the flag:

```
cat /root/flag.txt
```

**Why it worked:** a maintenance job running as root reached into a folder that we control, and used a wildcard (`*`) that let our filenames become commands. By planting files whose *names* were secret instructions to `tar`, we made root run our script. That script left behind a root-powered shell we could use any time.

**Flag:** `5222ec05a56d45b4050dcbb152b40154`

---

<a name="task-2"></a>
## 5. Task 2 — SUID Binaries and Privilege Escalation Challenge

This one required reverse-engineering a custom program. It was the hardest, so we go slowly.

### The concept: SUID programs

Normally, a program runs with **your** power. But some programs *need* extra power to do their job — for example, the `passwd` program that changes your password must edit a protected system file.

Linux solves this with the **SUID flag** ("Set User ID"). When a program has the SUID flag, it runs with the power of its **owner**, not the person who launched it. If the owner is root, then **any** user who runs that program temporarily borrows root's power *for the duration of that program*.

This is safe **only if the program is careful** and never lets the user do anything root shouldn't. If a SUID-root program has a bug or a hidden weakness, that bug runs with root's power — and we can exploit it.

### Step 1 — Find the SUID programs

We ask Linux to list every program carrying the SUID flag:

```
find / -perm -4000 -type f 2>/dev/null
```

(`-perm -4000` means "has the SUID flag"; `2>/dev/null` just hides harmless error messages.)

Most results were normal, expected system tools (`sudo`, `passwd`, `mount`, …). But one did not belong:

```
/home/user/service
```

A **custom program**, sitting in our home folder, owned by root, carrying the SUID flag. That is our target.

### Step 2 — Understand what the program does

Run it with no input:

```
/home/user/service
```

It replied `Usage: /home/user/service <input>` — so it expects us to give it some text.

We can't read the program's source code, but we can peek at the readable text baked inside it:

```
strings /home/user/service
```

Interesting words appeared, including:
- `strcpy` — a function that **copies text without checking how long it is** (this is a classic source of bugs).
- `strcmp` — a function that **compares two pieces of text** to see if they match.
- `setuid`, `setgid` — functions that **claim root's identity**.
- `system` and `/bin/bash` — the program can **launch a command line**.

Putting it together, the program's hidden logic looked like:

> *Copy the user's input into a box. Compare something against a secret password. If it matches, become root and open a command line.*

So there is a hidden "become root" reward inside — we just need to trigger it.

### Step 3 — Read the program's instructions (disassembly)

To see the exact logic, we translated the program back into readable machine instructions:

```
objdump -d -M intel /home/user/service | grep -A130 '<main>:'
```

This revealed the important details:

1. The program copies our input into a storage box (a **buffer**) using `strcpy` — **with no length check.** If we type more than fits, the extra spills out and overwrites neighbouring things. This overflow is a well-known vulnerability called a **buffer overflow**.

2. Just next to that box sits a small variable that the program fills with the text `"11111111"`.

3. The program then compares that variable against the fixed text `"22222222"` — and **only if they are equal** does it become root and open a shell.

Notice the built-in joke: it compares `"11111111"` to `"22222222"`. **Those are never equal**, so under normal use the "become root" reward can *never* trigger. It's locked by design. Our job is to unlock it.

### Step 4 — First idea, and the obstacle

Our first plan was the classic buffer-overflow move: type so much input that the overflow reaches all the way to the program's hidden "return address" (the note telling the program where to go next when it finishes) and reroute it straight to the "become root" code.

We measured exactly how much padding was needed (**120 characters**) to reach that return address. Control confirmed — but then we hit a wall:

- The "become root" code lives at a memory location whose address is `0x401348`. Written out in full, that address **contains several zero bytes**.
- Our only way in is `strcpy`, which copies text and **stops dead at the first zero**. It's physically impossible to feed an address containing zeros through it in the middle of our input.
- We also checked whether the machine's memory layout was predictable (a protection called **ASLR** — Address Space Layout Randomization — that shuffles memory addresses on every run to foil attackers). It was switched **on** (`/proc/sys/kernel/randomize_va_space` = `2`), so addresses change every single run and can't be hard-coded.

Between the zero-byte problem and randomized addresses, the "reroute the return address" approach was a dead end. So we stepped back and looked for a simpler door.

### Step 5 — The winning idea: overwrite the password *variable*

Here is the elegant solution. Remember:
- Our input is copied into a box using an overflow-prone `strcpy`.
- **Right next to that box** sits the variable holding `"11111111"`, which the program will soon compare against `"22222222"`.
- The copy happens **before** the comparison.

So we don't need to touch the return address at all. We just make our input **long enough to spill over into that neighbouring variable**, and fill the spill-over with exactly `"22222222"`. Then when the program does its comparison, the variable it reads is no longer `"11111111"` — **it's the `"22222222"` we planted.** The two match, the check passes, and the program itself happily becomes root and hands us a shell.

No zero-bytes needed. No guessing randomized addresses. We simply overwrite the answer key so our (rigged) test passes.

**The measurement:** from the disassembly, the input box starts `0x70` (112) bytes before a reference point, and the password variable sits `0x21` (33) bytes before it. The gap between them is `112 − 33 = 79` bytes. So: **79 characters of filler, then `"22222222"`.**

### The exploit

```
/home/user/service $(python3 -c 'print("A"*79 + "2"*8)')
```

In plain English, this feeds the program:
- 79 harmless `A` characters (filler, just to reach the right spot), then
- `22222222` (eight 2's), which lands **exactly on top of the password variable**.

When the program compares, it now finds `"22222222"` == `"22222222"` — a match! It runs its hidden reward: `setuid(0)` and `setgid(0)` (claim root's identity), then `system("/bin/bash")` (open a command line). Because it claimed root's identity *first*, the command line it opens is a **root** command line.

Confirm and read the flag:

```
id
```

```
cat /root/flag.txt
```

`id` reported root, and the flag came out.

**Why it worked:** the program trusted that the variable next to our input box would always stay `"11111111"`. But because it copied our input carelessly (no length check), we were able to reach past our box and rewrite that variable to `"22222222"` — the exact value that unlocks the built-in "become root" reward. We didn't break the lock; we changed the combination to one we knew.

**Flag:** `3950b859bbb8b8d014c84b9bdc514bf1`

---

<a name="results"></a>
## 6. Summary of results

| Task | Weakness exploited | Core technique | Flag |
|------|--------------------|----------------|------|
| 0 | A `sudo`-allowed command (`choom`) that can launch any program | Abusing a trusted tool to launch a root shell (GTFOBins-style) | `fe90cae5428da629bd59e540e5d129bb` |
| 1 | A root cron job running `tar *` in a folder we control | Wildcard injection: filenames disguised as `tar` options run our command as root | `5222ec05a56d45b4050dcbb152b40154` |
| 2 | A SUID-root program that copies input without a length check | Buffer overflow used to overwrite a comparison variable and unlock the program's hidden "become root" code | `3950b859bbb8b8d014c84b9bdc514bf1` |

**The common lesson:** in all three cases, root was undone not by "breaking in through the front door," but by a small piece of *misplaced trust* — trusting a user with a too-powerful command, trusting a user's folder in a root task, or trusting that a value in memory couldn't be changed. Privilege escalation is almost always about finding that one misplaced trust.

---

<a name="glossary"></a>
## 7. Glossary

- **Root / superuser:** the all-powerful administrator account. Its identity number is `uid=0`.
- **User / ordinary user:** a limited account that can only touch its own things.
- **Flag:** the secret string proving a challenge was solved; hidden in `/root/flag.txt`.
- **SSH:** a tool for getting a secure remote command line on another machine.
- **Terminal / shell:** the text-based control panel where we type commands (e.g. `bash`).
- **`sudo`:** lets a user run *specific* commands with root's power.
- **GTFOBins:** a public catalogue of ordinary tools that can be abused to gain extra power.
- **cron / cron job:** the system that runs tasks automatically on a schedule; a scheduled task.
- **Wildcard (`*`):** a symbol Linux replaces with "all the filenames here" before running a command.
- **Wildcard injection:** creating files whose *names* are secret command options, so a program is tricked into obeying them.
- **SUID flag:** a setting that makes a program run with the power of its *owner* instead of the person launching it. Shown as an `s` in a file's permissions (e.g. `-rwsr-xr-x`).
- **Buffer:** a fixed-size box in memory that holds data (like our input text).
- **Buffer overflow:** typing more data than the box can hold, so the extra spills over and overwrites neighbouring memory. A classic security bug.
- **`strcpy`:** a copy function that doesn't check length (a common cause of buffer overflows) and stops at the first zero byte.
- **`strcmp`:** a function that checks whether two pieces of text are identical.
- **Return address:** a stored note telling a program where to continue when a piece of it finishes. A prime target in advanced overflows.
- **ASLR (Address Space Layout Randomization):** a defence that shuffles memory addresses on every run so attackers can't hard-code them.
- **Hash:** a fixed-length fingerprint made of letters and numbers; here, the part of the flag we submit.

