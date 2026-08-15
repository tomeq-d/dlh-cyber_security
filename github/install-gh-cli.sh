#!/bin/bash
# install-gh-cli.sh
# Installs GitHub CLI (gh) on Debian/Kali when it's not available via the
# default apt repos. Safe to re-run - each step checks before acting.

set -e

echo "== Checking if gh is already installed =="
if command -v gh &> /dev/null; then
    echo "gh is already installed: $(gh --version | head -n1)"
    exit 0
fi

echo "== Trying simple apt install first =="
if sudo apt install gh -y; then
    echo "Installed via apt directly."
    gh --version
    exit 0
fi

echo "== Falling back to official GitHub CLI apt repo =="

echo "-- Ensuring wget is present --"
type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)

echo "-- Adding GitHub CLI signing key --"
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
  sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg

echo "-- Adding GitHub CLI apt source --"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
  sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

echo "-- Refreshing package list for the new GitHub CLI source only --"
sudo apt update -o Dir::Etc::sourcelist="sources.list.d/github-cli.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"
echo "-- Installing gh --"
sudo apt install gh -y

echo "== Done =="
gh --version
