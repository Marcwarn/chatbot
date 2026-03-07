"""
Invite System API - Bjud in deltagare till DISC-test
Admin skapar inbjudningslänkar, deltagare genomför test,
admin kan välja att dela resultaten med deltagaren.
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import secrets
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/disc/invite", tags=["invites"])

# ─── In-memory store ─────────────────────────────────────────────────────────
# Persists under Lambda-warm-period. För produktion: byt till PostgreSQL.
_invites: Dict[str, dict] = {}


# ─── Auth ────────────────────────────────────────────────────────────────────

def verify_admin(authorization: Optional[str] = Header(None)) -> dict:
    """Återanvänd admin-sessioner från api_admin.py"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Admin-auktorisering krävs")
    token = authorization.replace("Bearer ", "")
    try:
        from api_admin import _admin_sessions
        if token not in _admin_sessions:
            raise HTTPException(status_code=401, detail="Ogiltig eller utgången session")
        session = _admin_sessions[token]
        if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Session har gått ut")
        return session
    except ImportError:
        raise HTTPException(status_code=503, detail="Admin-modul ej tillgänglig")


# ─── Models ──────────────────────────────────────────────────────────────────

class CreateInviteRequest(BaseModel):
    participant_name: str
    participant_email: Optional[str] = None
    group_name: Optional[str] = None
    notes: Optional[str] = None
    expires_days: int = 30

class UpdateInviteRequest(BaseModel):
    allow_participant_view: Optional[bool] = None
    notes: Optional[str] = None
    group_name: Optional[str] = None

class CompleteInviteRequest(BaseModel):
    disc_scores: Dict[str, float]
    profile_code: str
    report: Dict[str, Any]


# ─── Admin Endpoints ─────────────────────────────────────────────────────────

@router.post("")
async def create_invite(req: CreateInviteRequest, admin=Depends(verify_admin)):
    """Admin: Skapa en ny inbjudningslänk för en deltagare"""
    token = secrets.token_urlsafe(32)
    invite = {
        "token": token,
        "participant_name": req.participant_name,
        "participant_email": req.participant_email,
        "group_name": req.group_name or "",
        "notes": req.notes or "",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=req.expires_days)).isoformat(),
        "completed_at": None,
        "disc_scores": None,
        "profile_code": None,
        "report": None,
        "allow_participant_view": False,
        "status": "pending"  # pending | completed | expired
    }
    _invites[token] = invite
    return {"token": token, "invite": invite}


@router.get("/admin/list")
async def list_invites(admin=Depends(verify_admin)):
    """Admin: Lista alla inbjudningar med status och resultat"""
    invites = list(_invites.values())
    # Markera utgångna
    now = datetime.utcnow()
    for inv in invites:
        if inv["status"] == "pending" and datetime.fromisoformat(inv["expires_at"]) < now:
            inv["status"] = "expired"
    # Sortera: senaste först
    invites.sort(key=lambda x: x["created_at"], reverse=True)
    return {"invites": invites, "total": len(invites)}


@router.get("/admin/{token}")
async def get_invite_admin(token: str, admin=Depends(verify_admin)):
    """Admin: Hämta fullständig data för en inbjudan inkl. rapport"""
    invite = _invites.get(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte")
    return invite


@router.patch("/{token}")
async def update_invite(token: str, req: UpdateInviteRequest, admin=Depends(verify_admin)):
    """Admin: Uppdatera inbjudan (dela resultat, anteckningar, grupp)"""
    invite = _invites.get(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte")
    if req.allow_participant_view is not None:
        invite["allow_participant_view"] = req.allow_participant_view
    if req.notes is not None:
        invite["notes"] = req.notes
    if req.group_name is not None:
        invite["group_name"] = req.group_name
    return {"message": "Inbjudan uppdaterad", "invite": invite}


@router.delete("/{token}")
async def delete_invite(token: str, admin=Depends(verify_admin)):
    """Admin: Radera en inbjudan och dess data"""
    if token not in _invites:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte")
    del _invites[token]
    return {"message": "Inbjudan raderad"}


# ─── Participant Endpoints ────────────────────────────────────────────────────

@router.get("/{token}")
async def get_invite(token: str):
    """Deltagare: Hämta inbjudningsstatus (öppen för alla med token)"""
    invite = _invites.get(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte eller har gått ut")

    now = datetime.utcnow()
    if datetime.fromisoformat(invite["expires_at"]) < now and invite["status"] == "pending":
        raise HTTPException(status_code=410, detail="Inbjudan har gått ut")

    # Begränsad info till deltagaren
    return {
        "token": token,
        "participant_name": invite["participant_name"],
        "group_name": invite["group_name"],
        "status": invite["status"],
        "allow_participant_view": invite["allow_participant_view"],
        "completed_at": invite["completed_at"],
    }


@router.post("/{token}/complete")
async def complete_invite(token: str, req: CompleteInviteRequest):
    """Deltagare: Spara genomfört DISC-test till inbjudan"""
    invite = _invites.get(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte")
    if invite["status"] == "completed":
        # Tillåt uppdatering om de av misstag gör om testet
        pass
    if datetime.fromisoformat(invite["expires_at"]) < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Inbjudan har gått ut")

    invite["disc_scores"] = req.disc_scores
    invite["profile_code"] = req.profile_code
    invite["report"] = req.report
    invite["completed_at"] = datetime.utcnow().isoformat()
    invite["status"] = "completed"

    return {"message": "Test genomfört och sparat", "status": "completed"}


@router.get("/{token}/report")
async def get_invite_report(token: str):
    """Deltagare: Hämta DISC-rapport (endast om admin har delat den)"""
    invite = _invites.get(token)
    if not invite:
        raise HTTPException(status_code=404, detail="Inbjudan hittades inte")
    if invite["status"] != "completed":
        raise HTTPException(status_code=400, detail="Testet är inte genomfört än")
    if not invite["allow_participant_view"]:
        raise HTTPException(
            status_code=403,
            detail="Resultaten har inte delats av din administratör än"
        )

    return {
        "participant_name": invite["participant_name"],
        "completed_at": invite["completed_at"],
        "disc_scores": invite["disc_scores"],
        "profile_code": invite["profile_code"],
        "report": invite["report"]
    }
