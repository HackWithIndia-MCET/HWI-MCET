"""
Cloudflare Tunnel Runner for 48hr+ persistent live prototype URL
"""
import subprocess
import time
import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "prototype_url.txt")
CLOUDFLARED_BIN = r"C:\Users\saad uddin\.gemini\antigravity\scratch\cloudflared.exe"

def run_cf_tunnel():
    print("[*] Launching Cloudflare 48hr+ Tunnel for http://127.0.0.1:8000...")
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

            current_url = None
            for line in proc.stdout:
                # Cloudflare prints the tunnel URL in stderr/stdout
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    current_url = match.group(0)
                    print("\n" + "="*70)
                    print(">> CLOUDFLARE 48-HOUR+ LIVE PROTOTYPE URL:")
                    print(f">> {current_url}")
                    print("="*70 + "\n")
                    sys.stdout.flush()
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(current_url)

            proc.wait()
            print("[!] Tunnel process exited. Reconnecting in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"[!] Tunnel error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_cf_tunnel()
