#!/bin/bash
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt "$1" | grep '(?)' | awk '{print $1}' > 5-password.txt
