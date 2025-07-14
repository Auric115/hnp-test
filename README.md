# Hack and Patch

**Hack and Patch** is a CTF-inspired game where you and a friend take turns hacking and patching a live web app. Your opponent's hack time becomes your time limit for patching, creating a fun Purple-teaming and DevSecOps exercise enabled through Git and Docker.

## Game Commands

Run all game logic via:

```bash
python game.py
```

### Available Options

* `--setup` – Initialize yourself as a user without starting the service
* `--start` – Begin your hacking session (also runs setup if not already done)
* `--test` – Launch the app without recording any game state (for development/testing)
* `--submit HNP{flag}` – Submit a flag to end your hack session and update your opponent’s patch time
* `--patch` – Start your patch session and check out a new Git branch
* `--end HNP{new_flag}` – Finish patching with your new flag; will merge and push if valid
* `--stop` – Stop the Dockerized service manually if needed

## How to Start Playing

1. Make sure you have the latest versions of **Python 3**, **Git**, and **Docker** installed.

2. Use a UNIX-like environment: Linux, macOS, WSL, or Git Bash.

3. Fork this repository to your GitHub account.

4. Invite your opponent's GitHub account as a collaborator.

5. Run:

   ```bash
   python game.py --setup
   python game.py --start
   ```

6. When done hacking, run:

   ```bash
   python game.py --submit HNP{captured_flag}
   ```

7. Your opponent will then patch using:

   ```bash
   python game.py --patch
   ...
   python game.py --end HNP{new_flag}
   ```

## Game Rules

* **No Hacking the Infrastructure** – `game.py` must not be altered without mutual agreement. `.gitignore` should only ever be appended to, never trimmed.
* **Black Box Hacking** – You must not inspect the source code while hacking. You may only interact with the running service (usually via `localhost:8000`).
    - After hacking however, you have unlimited time to inspect the source code. Your time starts when you run --patch to make your first change. Do not prepare a file and copy paste it or things of that nature to try to circumvent the system. This is not permitted.

```
