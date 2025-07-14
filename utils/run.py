#!/usr/bin/env python3
import subprocess
import sys
import os
import signal
from pathlib import Path

IMAGE_NAME = "hnp-service"
CONTAINER_ID_FILE = Path("state/.hnp_service_container_id")

def start_service():
    if CONTAINER_ID_FILE.exists():
        print("[INFO] Service already running. Stop it first before starting a new one.")
        sys.exit(1)
    print("[RUN] Starting service...")
    proc = subprocess.run(
        ["docker", "run", "-d", "-p", "8000:8000", IMAGE_NAME],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print("[ERROR] Failed to start Docker container:")
        print(proc.stderr)
        sys.exit(1)
    container_id = proc.stdout.strip()
    CONTAINER_ID_FILE.write_text(container_id)
    print(f"[RUN] Service started with container ID: {container_id}")

def stop_service():
    if not CONTAINER_ID_FILE.exists():
        print("[INFO] No running service found.")
        return
    container_id = CONTAINER_ID_FILE.read_text().strip()
    print(f"[STOP] Stopping service with container ID: {container_id}...")
    proc = subprocess.run(["docker", "stop", container_id], capture_output=True, text=True)
    if proc.returncode != 0:
        print("[ERROR] Failed to stop Docker container:")
        print(proc.stderr)
        sys.exit(1)
    CONTAINER_ID_FILE.unlink()
    print("[STOP] Service stopped successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage Hack and Patch service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    args = parser.parse_args()

    if args.start:
        start_service()
    elif args.stop:
        stop_service()
    else:
        parser.print_help()
