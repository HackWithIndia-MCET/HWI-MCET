"""
Unified Server & Cloudflare Edge Tunnel Runner with Active Watchdog
Automatically starts FastAPI on port 8000 and establishes a persistent Cloudflare Tunnel.
"""
import subprocess
import threading
import time
import re
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

CLOUDFLARED_BIN = r"C:\Users\saad uddin\.gemini\antigravity\scratch\cloudflared.exe"
URL_FILE = os.path.join(BASE_DIR, "prototype_url.txt")

import uvicorn
from main import app

current_public_url = None

def tunnel_watchdog():
    global current_public_url
    consecutive_failures = 0
    # Allow initial DNS propagation
    time.sleep(60)
    while True:
        time.sleep(45)  # Check every 45 seconds
        if not current_public_url:
            continue
        try:
            req = urllib.request.Request(current_public_url, headers={"User-Agent": "TunnelWatchdog/2.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
        except Exception as e:
            consecutive_failures += 1
            print(f"[Watchdog] Tunnel check ping note: {e} ({consecutive_failures}/5)", flush=True)

        if consecutive_failures >= 5:
            print("[Watchdog] Persistent tunnel drop confirmed (5 consecutive failed probes). Reconnecting Cloudflare...", flush=True)
            os.system("taskkill /F /IM cloudflared.exe /T >nul 2>&1")
            consecutive_failures = 0
            time.sleep(60)  # Grace period after restart


def start_cloudflare_tunnel():
    global current_public_url
    time.sleep(2)  # Give uvicorn a moment to bind
    print("\n[*] Starting Cloudflare Edge Tunnel...", flush=True)
    
    # Start watchdog thread
    w_thread = threading.Thread(target=tunnel_watchdog, daemon=True)
    w_thread.start()

    while True:
        try:
            cmd = [
                CLOUDFLARED_BIN,
                "tunnel",
                "--url", "http://127.0.0.1:8000",
                "--no-autoupdate"
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

            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                match = re.search(r'https://([a-zA-Z0-9-]+)\.trycloudflare\.com', line)
                if match and match.group(1).lower() != "api":
                    current_public_url = match.group(0)
                    print("\n" + "="*70, flush=True)
                    print(">> YOUR LIVE CLOUDFLARE PUBLIC PROTOTYPE URL:", flush=True)
                    print(f">> {current_public_url}", flush=True)
                    print("="*70 + "\n", flush=True)
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(current_public_url)

            proc.wait()
            print("[!] Cloudflared tunnel process closed. Spawning fresh tunnel in 2s...", flush=True)
            time.sleep(2)
        except Exception as e:
            print(f"[!] Tunnel exception: {e}. Retrying in 3s...", flush=True)
            time.sleep(3)

if __name__ == "__main__":
    # Start Cloudflare in a background daemon thread
    t = threading.Thread(target=start_cloudflare_tunnel, daemon=True)
    t.start()

    # Run Uvicorn on 0.0.0.0:8000
    print("[*] Starting Uvicorn on http://0.0.0.0:8000...", flush=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
