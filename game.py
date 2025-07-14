#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path("state/.hnp_config")
GLOBAL_STATE_FILE = Path("state/hnp_global.json")
DEFAULT_DEV_TIME = 300
FLAG_FORMAT = "HNP{"

BUILD_SCRIPT = [sys.executable, "utils/build.py"]
RUN_SCRIPT = [sys.executable, "utils/run.py"]

def now():
    return datetime.now(timezone.utc).isoformat()

def read_json(path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def build_docker_image():
    print("[BUILD] Checking/building Docker image...")
    result = subprocess.run(BUILD_SCRIPT)
    if result.returncode != 0:
        print("[ERROR] Failed to build Docker image. Aborting.")
        sys.exit(1)

def start_service():
    print("[RUN] Starting service...")
    result = subprocess.run(RUN_SCRIPT + ["--start"])
    if result.returncode != 0:
        print("[ERROR] Failed to start service.")
        sys.exit(1)

def stop_service():
    print("[RUN] Stopping service...")
    result = subprocess.run(RUN_SCRIPT + ["--stop"])
    if result.returncode != 0:
        print("[ERROR] Failed to stop service.")
        sys.exit(1)

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

def setup_only():
    if CONFIG_FILE.exists():
        print("[INFO] .hnp_config already exists.")
        return
    init_config()

def start_challenge(test_mode=False):
    if test_mode:
        print("[TEST] Running service without saving state.")
        start_service()
        return

    build_docker_image()
    start_service()

    config = read_json(CONFIG_FILE)
    config["hack_start"] = now()
    write_json(CONFIG_FILE, config)
    print("[START] Hack time started at", config["hack_start"])

def submit_flag(submitted_flag):
    config = read_json(CONFIG_FILE)
    global_data = read_json(GLOBAL_STATE_FILE)
    username = config.get("username")

    if not username:
        print("[ERROR] Username not found in config. Run --start first.")
        return

    if not submitted_flag.startswith(FLAG_FORMAT):
        print("[ERROR] Invalid flag format.")
        return

    if not config.get("hack_start"):
        print("[ERROR] Hack start time not found. Run --start first.")
        return

    start = datetime.fromisoformat(config["hack_start"])
    end = datetime.now(timezone.utc)
    hack_time = int((end - start).total_seconds())

    print(f"[INFO] Hack duration: {hack_time} seconds")

    opponent = None
    for user in global_data.get("players", {}):
        if user != username:
            opponent = user
            break

    if not opponent:
        print("[ERROR] No opponent found in global state.")
        return

    global_data["players"][opponent]["dev_time"] = global_data["players"][opponent].get("dev_time", 0) + hack_time
    write_json(GLOBAL_STATE_FILE, global_data)
    print(f"[SUCCESS] Flag accepted. {opponent}'s dev time increased by {hack_time}s.")
    print(f"[NEXT] Run: python game.py --patch")

def patch():
    config = read_json(CONFIG_FILE)
    username = config.get("username")
    if not username:
        print("[ERROR] Username not found in config. Run --start first.")
        return

    branch_name = f"patch-{username}-{int(time.time())}"
    print(f"[GIT] Creating branch {branch_name}...")
    result = subprocess.run(["git", "checkout", "-b", branch_name])
    if result.returncode != 0:
        print("[ERROR] Failed to create git branch. Make sure you are in a git repo.")
        return

    config["patch_start"] = now()
    config["current_branch"] = branch_name
    write_json(CONFIG_FILE, config)
    print(f"[PATCH] Branch {branch_name} created and dev timer started.")

def end_patch(new_flag):
    config = read_json(CONFIG_FILE)
    global_data = read_json(GLOBAL_STATE_FILE)
    username = config.get("username")

    if not username:
        print("[ERROR] Username not found in config. Run --start first.")
        return

    if not config.get("patch_start"):
        print("[ERROR] Patch start time not found. Run --patch first.")
        return

    start = datetime.fromisoformat(config["patch_start"])
    end = datetime.now(timezone.utc)
    patch_time = int((end - start).total_seconds())
    allowed_time = global_data.get("players", {}).get(username, {}).get("dev_time", DEFAULT_DEV_TIME)

    print(f"[END] Allowed dev time: {allowed_time}s")
    print(f"[END] Actual dev time: {patch_time}s")

    if patch_time > allowed_time:
        decision = input("You exceeded dev time. Proceed with push? (y/N): ").strip().lower()
        if decision != 'y':
            print("[RESET] Resetting branch to origin/main...")
            subprocess.run(["git", "reset", "--hard", "origin/main"])
            return

    print("[GIT] Merging branch and pushing changes...")
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["git", "merge", config["current_branch"]])
    subprocess.run(["git", "push", "origin", "main"])

    global_data["players"][username]["last_flag"] = new_flag
    global_data["players"][username]["dev_time"] = 0
    global_data["players"][username]["last_round"] = now()
    write_json(GLOBAL_STATE_FILE, global_data)

    print(f"[PUSHED] Changes merged to main with new flag: {new_flag}")

def main():
    parser = argparse.ArgumentParser(description="Hack and Patch Game")
    parser.add_argument("--start", action="store_true", help="Start the challenge")
    parser.add_argument("--submit", type=str, help="Submit a flag")
    parser.add_argument("--patch", action="store_true", help="Begin patching")
    parser.add_argument("--end", type=str, help="End patch and provide new flag")
    parser.add_argument("--test", action="store_true", help="Run service in test mode")
    parser.add_argument("--stop", action="store_true", help="Stop the running service")
    parser.add_argument("--setup", action="store_true", help="Initialize user without starting")

    args = parser.parse_args()

    if args.setup:
        setup_only()
    elif args.test:
        start_challenge(test_mode=True)
    elif args.start:
        init_config()
        start_challenge()
    elif args.submit:
        submit_flag(args.submit)
    elif args.patch:
        patch()
    elif args.end:
        end_patch(args.end)
    elif args.stop:
        stop_service()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()