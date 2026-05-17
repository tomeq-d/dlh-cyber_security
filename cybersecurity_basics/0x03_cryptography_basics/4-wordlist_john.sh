#!/bin/bash
john --wordlist=usr/share/wordlist/rockyou.txt "$1" | john --show "$1" | awk -F: '{print $2}' > 4-password.txt

