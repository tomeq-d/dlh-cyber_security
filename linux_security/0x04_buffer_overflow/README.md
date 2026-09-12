# Buffer Overflow

Linux Security — 0x04_buffer_overflow
## Description

This project explores buffer overflow vulnerabilities from both a
practical and theoretical angle: hands-on manipulation of a running
process's heap memory, and a written report covering how buffer
overflows work, their history, and how to defend against them.

## Tasks

| # | Task | File |
|---|------|------|
| 0 | **Hack the VM** — locate a running process's heap via `/proc/[pid]/maps` and overwrite an ASCII string directly in `/proc/[pid]/mem` | `read_write_heap.py` |
| 1 | **Buffer Overflow Attack Report** — a blog-post style report covering what buffer overflows are, how they occur, a worked example, historical incidents, and mitigation techniques | `buffer_overflow_report.md` |

## Task 0: `read_write_heap.py`

Finds a string in the heap of a running process and replaces it in place.

```bash
sudo python3 read_write_heap.py <pid> <search_string> <replace_string>
```

- `pid` — PID of the target process
- `search_string` / `replace_string` — ASCII strings; the replacement is
  padded with null bytes if shorter than the original, and rejected if
  longer
- Reads `/proc/[pid]/maps` to locate the `[heap]` region, then reads and
  writes directly through `/proc/[pid]/mem`
- Requires root (accessing another process's memory needs elevated
  privileges)
- Exits with status `1` and a message on usage errors, an unreadable
  process, or a string that isn't found

**Example:**

```bash
$ ./main &
$ ps aux | grep ./main
$ sudo python3 read_write_heap.py <pid> Holberton maroua
```

## Task 1: Buffer Overflow Attack Report

A written report (`buffer_overflow_report.md`) covering:

- What buffer overflows are and their impact on security
- How stack and heap overflows occur at the memory level
- A simplified exploitation example
- Historical incidents: the Morris Worm, Code Red / SQL Slammer, Heartbleed
- Mitigation techniques: secure coding, stack canaries, ASLR, NX/DEP,
  static/dynamic analysis, and fuzzing

Published version: Google Doc / Medium post (see submission links).

## Requirements

- Python 3
- Linux (relies on `/proc/[pid]/maps` and `/proc/[pid]/mem`)
- Root privileges to run `read_write_heap.py` against another process

## Author

Tomasz — Cybersecurity Academy
