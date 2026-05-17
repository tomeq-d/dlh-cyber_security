#!/bin/bash
john --format=raw-sha256 --wordlist=/usr/share/wordlists/rockyou.txt "$1" | grep '(?)' | awk '{print $1}' > 6-password.txt
