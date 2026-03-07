import sys, os, json, secrets, hmac
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_sessions = {}
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

def check_password(pw: str) -> bool:
    if ADMIN_PASSWORD:
        return hmac.compare_digest(pw, ADMIN_PASSWORD)
    if ADMIN_PASSWORD_HASH:
        try:
            import bcrypt
            return bcrypt.checkpw(pw.encode(), ADMIN_PASSWORD_HASH.encode())
        except Exception:
            pass
    return False

class LoginReq(BaseModel):
    username: str
    password: str

@app.post("/api/admin/login")
async def login(req: LoginReq):
    if req.username != ADMIN_USERNAME or not check_password(req.password):
        raise HTTPException(401, "Ogiltigt användarnamn eller lösenord")
    token = secrets.token_urlsafe(32)
    exp = datetime.utcnow() + timedelta(hours=8)
    _sessions[token] = {"expires_at": exp.isoformat()}
    return {"token": token, "expires_at": exp.isoformat(), "message": "Login successful"}

@app.get("/api/ping")
async def ping():
    return {"ok": True, "user": ADMIN_USERNAME, "has_pw": bool(ADMIN_PASSWORD), "has_hash": bool(ADMIN_PASSWORD_HASH)}

