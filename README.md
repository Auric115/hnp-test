# Hack and Patch

**Hack and Patch** is a CTF-inspired game where you and a friend take turns hacking and patching a live web app. Your opponent's hack time becomes your time limit for patching to create a fun Purple-teaming and DevSecOps exercise enabled through Git and Docker. 

### Commands

All interactions with the game are done through:

```bash
python game.py
```

* `--start` – Begin the hacking session (saves your name if it's the first time)
* `--test` – Launch the app without saving anything, useful for devs
* `--submit HNP{flag}` – Submit the flag you found to end your hack
* `--patch` – Start patching session and switch to a new git branch
* `--end HNP{new_flag}` – Finish patching and either push or reset based on time

## How to Start Playing

1. Make sure you have the latest Python 3, Git, and Docker installed and a UNIX-like environment like a Linux VM, macOS, WSL or Git Bash
2. Fork this repository into your own GitHub account.
3. Invite your opponent's GitHub account to the fork as a collaborator.
4. Run `python game.py --start` and submit the flag.

## Rules of the Game
**No Hacking the Infrastructure.** 'game.py' cannot be altered without the agreement of both opponents and the gitignore should only be added to, not deleted.

**Black Box Hacking.** While hacking you are not allowed to look at the source code. We pretend these are running in production, therefore you would only have access to localhost or similar endpoints.