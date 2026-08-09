# What is the Shell? — Solutions

## Task 0 — `1-flag.txt`

**The problem:** We need to read `/home/user/flag`, but we're not allowed to
type the word "flag" as-is, and lots of commands/characters are blocked.

**What's still allowed:** `cat` is fine to use. Spaces are fine. The wildcard
characters `?` and `*` are fine too — they weren't on the blacklist.

**Solution:**
```sh
cat /home/user/fl?g
```

**How it works, in plain terms:**
The `?` character means "match any single character here" — it's a wildcard,
like when you search for `photo?.jpg` and it matches `photo1.jpg`,
`photo2.jpg`, etc. Before `cat` even runs, the shell itself looks at
`/home/user/fl?g`, checks what files exist in that folder, and swaps in
whatever matches — in this case, `flag`. So what you *typed* is `fl?g`, but
what `cat` actually *receives and opens* is `flag`. The blacklist filter only
checks the text you typed, and `fl?g` isn't the word "flag", so it slips
through.

**Other ways to do the same trick:**
```sh
cat /home/user/fl*g      # * matches "zero or more characters" instead of just one
cat /home/user/*ag       # matches anything ending in "ag"
more /home/user/fl?g     # 'more' is not blacklisted, works the same way
less /home/user/fl?g     # same idea, different viewer program
head /home/user/fl?g     # prints the first lines of the file, also works
```

---

## Task 1 — `2-flag.txt`

**The problem:** Same idea, but now it's harder. Wildcards (`?`, `*`) are
blocked this time, AND — this is the tricky part — **the space bar itself is
blocked**. Normally you'd type `cat` then a space then the filename, but you
can't type that space at all.

**Solution:**
```sh
cat${IFS}/home/user/flag
```

**How it works, in plain terms:**
`IFS` stands for "Internal Field Separator." It's a built-in variable that
every bash shell already has, and by default its value is... a blank space
character. When you write `${IFS}`, you're not typing a space — you're
typing the *name* of a variable that *contains* a space. The shell reads
`${IFS}`, looks up what's stored in it, and replaces it with an actual space
before running the command. So the text you typed has zero literal spaces in
it (just letters, `$`, `{`, `}`), which sails past the filter — but by the
time `cat` actually runs, it sees `cat /home/user/flag` with a real space in
between, exactly as if you'd typed it normally.

Think of it like writing a secret note that says "insert space here" instead
of an actual space — the reader (the shell) knows to substitute it in before
acting on the note.

**Other ways to do the same trick:**
```sh
cat</home/user/flag
```
The `<` symbol means "take input from this file." It doesn't need a space
before the filename to work — `cat<file` and `cat < file` behave the same
way in bash. So this dodges the space rule entirely by not needing a space
in the first place.

```sh
cat$IFS$9/home/user/flag
```
Same `${IFS}` trick as above, but `$9` is added in the middle. `$9` normally
refers to a script's 9th argument — since there isn't one, it just expands to
nothing. People add it as a decoy in case a filter is specifically looking
for the exact text `${IFS}` and blocking that string — breaking it up with
`$9` avoids that exact match while still working the same way.

**Note:** the `${IFS}` solution is the cleanest and most reliable of the
three — try that first.

---

## The big idea tying both tasks together
In both cases, the trick is the same: **the shell processes and expands
certain symbols (wildcards, variables) before running the actual command**.
A blacklist filter only sees the raw text you type — it has no idea what
that text turns into after the shell works its magic. So instead of typing
the blocked word or character directly, you type something that *looks*
harmless but *becomes* the blocked thing at the last second, after the
filter has already let it through.

