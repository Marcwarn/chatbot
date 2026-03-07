"""
Admin API - Service Management & Analytics
Provides administrative endpoints for monitoring and managing the service
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os
import hashlib
import secrets

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ── Admin Authentication ─────────────────────────────────────────────────────

# Simple token-based auth (upgrade to JWT in production)
_admin_sessions: Dict[str, dict] = {}  # token -> {created_at, expires_at}

ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    # Default: "admin123" (CHANGE THIS IN PRODUCTION!)
    "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
)

def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify admin authentication token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    if token not in _admin_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    session = _admin_sessions[token]
    if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
        del _admin_sessions[token]
        raise HTTPException(status_code=401, detail="Session expired")

    return session


# ── Models ───────────────────────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    password: str

class AdminLoginResponse(BaseModel):
    token: str
    expires_at: datetime
    message: str

class DashboardStats(BaseModel):
    total_assessments: int
    total_users: int
    total_chat_messages: int
    assessments_last_24h: int
    assessments_last_7d: int
    avg_completion_rate: float
    top_dimensions: Dict[str, float]
    api_health: str

class UserInfo(BaseModel):
    user_id: str
    assessments_count: int
    last_activity: Optional[datetime]
    consents: Dict[str, bool]
    has_chat_profile: bool

class AssessmentInfo(BaseModel):
    assessment_id: str
    user_id: str
    completed_at: datetime
    scores: Dict[str, float]
    language: str

class ServiceConfig(BaseModel):
    api_key_configured: bool
    chat_enabled: bool
    ai_reports_enabled: bool
    gdpr_mode: str
    max_tokens_chat: int
    max_tokens_report: int


# ── In-Memory Analytics (upgrade to DB in production) ────────────────────────

_analytics: Dict[str, Any] = {
    "assessments": [],  # List of assessment records
    "users": {},        # user_id -> user info
    "chat_messages": 0,
    "errors": [],
}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(req: AdminLoginRequest):
    """Admin login - returns auth token"""

    password_hash = hash_password(req.password)

    if password_hash != ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Invalid password")

    # Generate session token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=8)

    _admin_sessions[token] = {
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    return AdminLoginResponse(
        token=token,
        expires_at=expires_at,
        message="Login successful"
    )


@router.post("/logout")
async def admin_logout(session: dict = Depends(verify_admin_token), authorization: str = Header(None)):
    """Logout and invalidate token"""
    token = authorization.replace("Bearer ", "")
    if token in _admin_sessions:
        del _admin_sessions[token]
    return {"message": "Logged out successfully"}


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(session: dict = Depends(verify_admin_token)):
    """Get dashboard statistics"""

    from api_main_gdpr import anthropic_client, _sessions, _user_profiles

    # Calculate stats from in-memory data
    total_assessments = len(_analytics["assessments"])
    total_users = len(_analytics["users"])
    chat_messages = _analytics["chat_messages"]

    # Recent assessments
    now = datetime.utcnow()
    last_24h = sum(1 for a in _analytics["assessments"]
                   if (now - datetime.fromisoformat(a["completed_at"])).total_seconds() < 86400)
    last_7d = sum(1 for a in _analytics["assessments"]
                  if (now - datetime.fromisoformat(a["completed_at"])).total_seconds() < 604800)

    # Average dimension scores
    if _analytics["assessments"]:
        avg_scores = {"E": 0, "A": 0, "C": 0, "N": 0, "O": 0}
        for a in _analytics["assessments"]:
            for dim, score in a["scores"].items():
                if dim in avg_scores:
                    avg_scores[dim] += score
        for dim in avg_scores:
            avg_scores[dim] /= len(_analytics["assessments"])
    else:
        avg_scores = {"E": 50, "A": 50, "C": 50, "N": 50, "O": 50}

    # API health
    api_health = "healthy" if anthropic_client else "api_key_missing"

    return DashboardStats(
        total_assessments=total_assessments,
        total_users=total_users,
        total_chat_messages=chat_messages,
        assessments_last_24h=last_24h,
        assessments_last_7d=last_7d,
        avg_completion_rate=95.0,  # Mock data
        top_dimensions=avg_scores,
        api_health=api_health
    )


@router.get("/users", response_model=List[UserInfo])
async def get_users(
    session: dict = Depends(verify_admin_token),
    limit: int = 100,
    offset: int = 0
):
    """Get list of users"""

    users_list = []
    for user_id, user_data in list(_analytics["users"].items())[offset:offset+limit]:
        users_list.append(UserInfo(
            user_id=user_id,
            assessments_count=user_data.get("assessments_count", 0),
            last_activity=datetime.fromisoformat(user_data["last_activity"]) if user_data.get("last_activity") else None,
            consents=user_data.get("consents", {}),
            has_chat_profile=user_data.get("has_chat_profile", False)
        ))

    return users_list


@router.get("/assessments", response_model=List[AssessmentInfo])
async def get_assessments(
    session: dict = Depends(verify_admin_token),
    limit: int = 50,
    offset: int = 0
):
    """Get list of completed assessments"""

    assessments_list = []
    for a in _analytics["assessments"][offset:offset+limit]:
        assessments_list.append(AssessmentInfo(
            assessment_id=a["assessment_id"],
            user_id=a["user_id"],
            completed_at=datetime.fromisoformat(a["completed_at"]),
            scores=a["scores"],
            language=a.get("language", "sv")
        ))

    return assessments_list


@router.get("/config", response_model=ServiceConfig)
async def get_service_config(session: dict = Depends(verify_admin_token)):
    """Get current service configuration"""

    from api_main_gdpr import anthropic_client

    api_key_configured = anthropic_client is not None

    return ServiceConfig(
        api_key_configured=api_key_configured,
        chat_enabled=api_key_configured,
        ai_reports_enabled=api_key_configured,
        gdpr_mode="strict",
        max_tokens_chat=1500,
        max_tokens_report=4000
    )


@router.delete("/users/{user_id}")
async def delete_user_data(
    user_id: str,
    session: dict = Depends(verify_admin_token)
):
    """Delete all user data (GDPR compliance)"""

    from api_main_gdpr import _user_profiles

    deleted_items = []

    # Delete from analytics
    if user_id in _analytics["users"]:
        del _analytics["users"][user_id]
        deleted_items.append("user_profile")

    # Delete assessments
    _analytics["assessments"] = [
        a for a in _analytics["assessments"]
        if a["user_id"] != user_id
    ]
    deleted_items.append("assessments")

    # Delete from user profiles (in-memory)
    if user_id in _user_profiles:
        del _user_profiles[user_id]
        deleted_items.append("chat_profile")

    return {
        "message": f"User data deleted for {user_id}",
        "deleted": deleted_items,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/users/{user_id}/export")
async def export_user_data(
    user_id: str,
    session: dict = Depends(verify_admin_token)
):
    """Export all user data (GDPR compliance)"""

    from api_main_gdpr import _user_profiles

    user_data = {
        "user_id": user_id,
        "export_date": datetime.utcnow().isoformat(),
        "profile": _analytics["users"].get(user_id, {}),
        "assessments": [
            a for a in _analytics["assessments"]
            if a["user_id"] == user_id
        ],
        "chat_profile": _user_profiles.get(user_id, None)
    }

    return user_data


@router.get("/health")
async def admin_health_check(session: dict = Depends(verify_admin_token)):
    """Check service health"""

    from api_main_gdpr import anthropic_client

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "api_configured": anthropic_client is not None,
        "active_sessions": len(_admin_sessions),
        "total_assessments": len(_analytics["assessments"])
    }


# ── Helper function to track analytics ───────────────────────────────────────

def track_assessment(assessment_id: str, user_id: str, scores: Dict[str, float], language: str = "sv"):
    """Track completed assessment (called from main API)"""
    _analytics["assessments"].append({
        "assessment_id": assessment_id,
        "user_id": user_id,
        "scores": scores,
        "completed_at": datetime.utcnow().isoformat(),
        "language": language
    })

    if user_id not in _analytics["users"]:
        _analytics["users"][user_id] = {
            "assessments_count": 0,
            "consents": {},
            "has_chat_profile": False
        }

    _analytics["users"][user_id]["assessments_count"] += 1
    _analytics["users"][user_id]["last_activity"] = datetime.utcnow().isoformat()


def track_chat_message():
    """Track chat message (called from main API)"""
    _analytics["chat_messages"] += 1


def update_user_consents(user_id: str, consents: Dict[str, bool]):
    """Update user consents (called from main API)"""
    if user_id not in _analytics["users"]:
        _analytics["users"][user_id] = {
            "assessments_count": 0,
            "has_chat_profile": False
        }
    _analytics["users"][user_id]["consents"] = consents
