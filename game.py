#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CONFIG_FILE = Path(".hnp_config")
GLOBAL_STATE_FILE = Path("hnp_global.json")
DEFAULT_DEV_TIME = 300  # seconds (5 minutes)
FLAG_FORMAT = "HNP{"

# -------------------- UTILS --------------------
def now():
    return datetime.utcnow().isoformat()

def read_json(path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# -------------------- CONFIG INIT --------------------
def init_config():
    if CONFIG_FILE.exists():
        print("[INFO] .hnp_config already exists.")
        return

    username = input("Enter your username: ").strip()
    data = {
        "username": username,
        "hack_start": None,
        "patch_start": None,
        "current_branch": None
    }
    write_json(CONFIG_FILE, data)
    print(f"[INIT] Welcome, {username}! .hnp_config created.")

    # Initialize or update global file
    global_data = read_json(GLOBAL_STATE_FILE)
    if "players" not in global_data:
        global_data["players"] = {}

    if username not in global_data["players"]:
        global_data["players"][username] = {
            "dev_time": 0,
            "last_flag": "",
            "last_round": now()
        }
        write_json(GLOBAL_STATE_FILE, global_data)
        print("[INIT] Global player state initialized.")

# -------------------- HACK START --------------------
def start_challenge():
    config = read_json(CONFIG_FILE)
    config["hack_start"] = now()
    write_json(CONFIG_FILE, config)
    print("[START] Hack time started at", config["hack_start"])
    subprocess.run(["./run.sh"])

# -------------------- SUBMIT FLAG --------------------
def submit_flag(submitted_flag):
    config = read_json(CONFIG_FILE)
    global_data = read_json(GLOBAL_STATE_FILE)
    username = config["username"]

    if not submitted_flag.startswith(FLAG_FORMAT):
        print("[ERROR] Invalid flag format.")
        return

    start = datetime.fromisoformat(config["hack_start"])
    end = datetime.utcnow()
    hack_time = int((end - start).total_seconds())

    print(f"[INFO] Hack duration: {hack_time} seconds")

    # Find opponent (the other user who last pushed)
    opponent = None
    for user in global_data["players"]:
        if user != username:
            opponent = user
            break

    if not opponent:
        print("[ERROR] No opponent found in global state.")
        return

    # Assume success for now
    global_data["players"][opponent]["dev_time"] += hack_time
    write_json(GLOBAL_STATE_FILE, global_data)
    print(f"[SUCCESS] Flag accepted. {opponent}'s dev time increased by {hack_time}s.")
    print(f"[NEXT] Run: python game.py --patch")

# -------------------- PATCH BRANCH --------------------
def patch():
    config = read_json(CONFIG_FILE)
    branch_name = f"patch-{config['username']}-{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", branch_name])
    config["patch_start"] = now()
    config["current_branch"] = branch_name
    write_json(CONFIG_FILE, config)
    print(f"[PATCH] Branch {branch_name} created and dev timer started.")

# -------------------- END PATCH --------------------
def end_patch(new_flag):
    config = read_json(CONFIG_FILE)
    global_data = read_json(GLOBAL_STATE_FILE)
    username = config["username"]

    start = datetime.fromisoformat(config["patch_start"])
    end = datetime.utcnow()
    patch_time = int((end - start).total_seconds())
    allowed_time = global_data["players"][username].get("dev_time", DEFAULT_DEV_TIME)

    print(f"[END] Allowed dev time: {allowed_time}s")
    print(f"[END] Actual dev time: {patch_time}s")

    if patch_time > allowed_time:
        decision = input("You exceeded dev time. Proceed with push? (y/N): ").strip().lower()
        if decision != 'y':
            print("[RESET] Resetting branch to origin/main...")
            subprocess.run(["git", "reset", "--hard", "origin/main"])
            return

    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["git", "merge", config["current_branch"]])
    subprocess.run(["git", "push", "origin", "main"])

    # Update global state
    global_data["players"][username]["last_flag"] = new_flag
    global_data["players"][username]["dev_time"] = 0
    global_data["players"][username]["last_round"] = now()
    write_json(GLOBAL_STATE_FILE, global_data)

    print(f"[PUSHED] Changes merged to main with new flag: {new_flag}")

# -------------------- MAIN ENTRY --------------------
def main():
    parser = argparse.ArgumentParser(description="Hack and Patch Game")
    parser.add_argument("--start", action="store_true", help="Start the challenge")
    parser.add_argument("--submit", type=str, help="Submit a flag")
    parser.add_argument("--patch", action="store_true", help="Begin patching")
    parser.add_argument("--end", type=str, help="End patch and provide new flag")

    args = parser.parse_args()

    if args.start:
        init_config()
        start_challenge()
    elif args.submit:
        submit_flag(args.submit)
    elif args.patch:
        patch()
    elif args.end:
        end_patch(args.end)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()