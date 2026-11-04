"""
Auto-reconnecting persistent tunnel runner for presentation
"""
import subprocess
import time
import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "prototype_url.txt")

def run_tunnel():
    print("[*] Starting persistent tunnel service for 127.0.0.1:8000...")
    while True:
        try:
            cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "ServerAliveInterval=15",
                "-o", "ServerAliveCountMax=3",
                "-o", "ExitOnForwardFailure=yes",
                "-R", "80:127.0.0.1:8000",
                "nokey@localhost.run"
            ]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )

            current_url = None
            for line in proc.stdout:
                match = re.search(r'https://[a-zA-Z0-9-]+\.lhr\.life', line)
                if match:
                    current_url = match.group(0)
                    print(f"\n[+] LIVE PROTOTYPE URL: {current_url}\n")
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(current_url)

            proc.wait()
            print("[!] Tunnel disconnected. Reconnecting in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"[!] Tunnel error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_tunnel()
