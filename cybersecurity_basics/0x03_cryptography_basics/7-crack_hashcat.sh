#!/bin/bash
hashcat -m 0 "$1" /usr/share/wordlists/rockyou.txt --quiet | cat | hashcat -m 0 "$1" --show | cut -d ':' -f2 > 7-password.txt
