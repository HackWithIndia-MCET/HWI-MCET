import sys
import os
import importlib.util

# Add project root directory to sys.path so modules resolve cleanly on Vercel
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Safety fallback: resolve admin_auth regardless of filename spacing
if "admin_auth" not in sys.modules:
    for filename in ("admin_auth.py", "admin auth.py"):
        candidate = os.path.join(ROOT_DIR, filename)
        if os.path.exists(candidate):
            try:
                spec = importlib.util.spec_from_file_location("admin_auth", candidate)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules["admin_auth"] = mod
                    spec.loader.exec_module(mod)
                    break
            except Exception:
                pass

from main import app as fastapi_app

# ASGI Path Normalizer: Translates Vercel's rewritten /api/index.py path to the actual requested route
async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path")
        if matched_path:
            scope["path"] = matched_path.decode("latin1")
        elif scope["path"] in ("/api/index.py", "/api/index", "/api", "/api/"):
            scope["path"] = "/"

    await fastapi_app(scope, receive, send)

handler = app
