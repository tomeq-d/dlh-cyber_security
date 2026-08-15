# install-gh-cli.sh

Installs GitHub CLI (`gh`) on Debian/Kali via apt, falling back to the official GitHub repo if it's not available by default.

## Usage

```bash
chmod +x install-gh-cli.sh
./install-gh-cli.sh
```

## What it does

1. Checks if `gh` is already installed — exits immediately if so.
2. Tries a plain `sudo apt install gh` first, in case Kali's default repos already carry it.
3. If that fails, adds GitHub's official CLI apt repository (signing key + source list) and installs from there.
4. Only refreshes package metadata for the newly-added GitHub CLI source — does not run a full `apt update` against all repos, so it won't touch or report on unrelated pending system upgrades.

Safe to re-run at any time.
