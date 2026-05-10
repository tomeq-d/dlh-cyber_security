#!/bin/bash
# Create new user with password passed as arguments
useradd "$1"; echo "$1:$2" | chpasswd
