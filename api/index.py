"""
Vercel serverless entry point — minimal standalone implementation.
Handles login and routes directly. Falls back gracefully if main app fails.
"""
import sys, os, json, secrets, hmac
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from mangum import Mangum

# ── Standalone minimal app ────────────────────────────────────────────────────
app = FastAPI(title="Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin sessions (shared with main app if it loads)
_admin_sessions = {}

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")


def verify_password(password: str) -> bool:
    # Plain password check (no C extensions)
    if ADMIN_PASSWORD:
        return hmac.compare_digest(password, ADMIN_PASSWORD)
    # bcrypt fallback
    if ADMIN_PASSWORD_HASH:
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())
        except Exception:
            pass
    return False


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/admin/login")
async def admin_login(req: LoginRequest):
    if req.username != ADMIN_USERNAME or not verify_password(req.password):
        raise HTTPException(status_code=401, detail="Ogiltigt användarnamn eller lösenord")
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=8)
    _admin_sessions[token] = {
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
    }
    # Share sessions with main app if loaded
    try:
        import api_admin
        api_admin._admin_sessions[token] = _admin_sessions[token]
    except Exception:
        pass
    return {"token": token, "expires_at": expires_at.isoformat(), "message": "Login successful"}


@app.get("/api/diagnostic")
async def diagnostic():
    errors = {}
    for mod in ["api_main_gdpr", "api_admin", "api_disc", "api_invites", "database", "monitoring"]:
        try:
            __import__(mod)
            errors[mod] = "OK"
        except Exception as e:
            errors[mod] = str(e)[:200]
    return {"env": {"ADMIN_USERNAME": ADMIN_USERNAME, "has_password": bool(ADMIN_PASSWORD), "has_hash": bool(ADMIN_PASSWORD_HASH)}, "imports": errors}


# ── Try to mount full app routes ──────────────────────────────────────────────
_main_app_loaded = False
try:
    from api_main_gdpr import app as main_app
    # Mount all routes from main app onto our app
    for route in main_app.routes:
        if hasattr(route, "path") and route.path not in [r.path for r in app.routes]:
            app.routes.append(route)
    # Share sessions
    import api_admin as _api_admin_mod
    _api_admin_mod._admin_sessions = _admin_sessions
    _main_app_loaded = True
except Exception as e:
    print(f"Main app load failed: {e}")


handler = Mangum(app, lifespan="off")
