"""
Hack With India @ MCET Campus - Server & Prototype Tunnel Runner
Launches the FastAPI application and optionally exposes a live public prototype URL
using an instant secure SSH tunnel (Pinggy / Localhost.run) or pyngrok.
"""
import sys
import os
import time
import subprocess
import threading
import re

# Set UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure current directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from main import app

PORT = 8000
HOST = "0.0.0.0"

def start_tunnel(port):
    """
    Spawns an instant public HTTPS tunnel for presentations.
    Supports localhost.run and pinggy with IPv4 loopback mapping.
    """
    print(f"\n[+] Spawning public HTTPS presentation tunnel for 127.0.0.1:{port}...")
    try:
        # Using localhost.run with explicit 127.0.0.1 to avoid IPv6 resolution issues
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            f"-R", f"80:127.0.0.1:{port}",
            "nokey@localhost.run"
        ]
        proc = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )

        tunnel_url = None
        for line in proc.stdout:
            if not tunnel_url:
                match = re.search(r'https://[a-zA-Z0-9-]+\.lhr\.life', line)
                if match:
                    tunnel_url = match.group(0)
                    print("\n" + "="*70)
                    print(">> LIVE PROTOTYPE URL FOR PRESENTATION:")
                    print(f">> {tunnel_url}")
                    print("="*70)
                    print("Share this link with your team, mentors, and presentation audience!\n")
                    
                    with open(os.path.join(BASE_DIR, "prototype_url.txt"), "w", encoding="utf-8") as f:
                        f.write(tunnel_url)
        proc.wait()
    except Exception as e:
        print(f"[!] Tunnel notice: {e}")
        print(f"You can also run manually in PowerShell:")
        print(f"ssh -R 80:127.0.0.1:{port} nokey@localhost.run")

def run():
    print("="*70)
    print(">> HACK WITH INDIA @ MCET CAMPUS - VIBECODING HUB <<")
    print(f"Local Server: http://127.0.0.1:{PORT}")
    print("="*70)

    # Launch tunnel in background thread if requested
    if "--tunnel" in sys.argv or "-t" in sys.argv:
        t = threading.Thread(target=start_tunnel, args=(PORT,), daemon=True)
        t.start()

    uvicorn.run("main:app", host=HOST, port=PORT, reload=False, log_level="info")

if __name__ == "__main__":
    run()
