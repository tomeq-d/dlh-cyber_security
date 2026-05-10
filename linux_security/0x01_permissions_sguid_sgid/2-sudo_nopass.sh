#!/bin/bash
# Allows user to execute sudo without entering password
echo "$1 ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
