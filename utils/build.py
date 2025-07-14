import subprocess
import sys

def build():
    print("[BUILD] Building Docker image...")
    proc = subprocess.run(["docker", "build", "-t", "hnp-service", "."], capture_output=True, text=True)
    if proc.returncode != 0:
        print("[ERROR] Docker build failed:")
        print(proc.stderr)
        sys.exit(1)
    print("[BUILD] Docker image 'hnp-service' built successfully.")

if __name__ == "__main__":
    build()
