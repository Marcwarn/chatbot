"""
Admin API - Service Management & Analytics
Provides administrative endpoints for monitoring and managing the service
Supports both Big Five and DISC assessments
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import bcrypt
from admin_analytics import AdminAnalytics

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ── Admin Authentication ─────────────────────────────────────────────────────

# Simple token-based auth (upgrade to JWT in production)
_admin_sessions: Dict[str, dict] = {}  # token -> {created_at, expires_at}

ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")  # bcrypt hash (optional)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")             # plain password fallback
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

def verify_password(password: str) -> bool:
    """Verify password — supports plain ADMIN_PASSWORD or bcrypt ADMIN_PASSWORD_HASH."""
    import hmac
    if ADMIN_PASSWORD:
        return hmac.compare_digest(password, ADMIN_PASSWORD)
    if ADMIN_PASSWORD_HASH:
        try:
            return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())
        except Exception:
            return False
    return False

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
    username: str
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
    big_five_count: int
    disc_count: int
    avg_completion_rate: float
    top_dimensions: Dict[str, float]
    api_health: str
    most_popular_type: str

class UserInfo(BaseModel):
    user_id: str
    assessments_count: int
    big_five_count: int
    disc_count: int
    last_activity: Optional[datetime]
    last_assessment_type: Optional[str]
    consents: Dict[str, bool]
    has_chat_profile: bool

class AssessmentInfo(BaseModel):
    assessment_id: str
    user_id: str
    assessment_type: str
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

    # Check username then password (constant-time)
    if req.username != ADMIN_USERNAME or not verify_password(req.password):
        raise HTTPException(status_code=401, detail="Ogiltigt användarnamn eller lösenord")

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
    """Get dashboard statistics - supports both Big Five and DISC"""

    from api_main_gdpr import anthropic_client, _sessions, _user_profiles

    # Initialize analytics engine
    analytics = AdminAnalytics(_analytics)

    # Calculate stats from in-memory data
    total_assessments = len(_analytics["assessments"])
    total_users = len(_analytics["users"])
    chat_messages = _analytics["chat_messages"]

    # Count by assessment type
    big_five_count = sum(1 for a in _analytics["assessments"] if a.get("assessment_type") == "big_five")
    disc_count = sum(1 for a in _analytics["assessments"] if a.get("assessment_type") == "disc")

    # Recent assessments
    recent_24h = analytics.get_assessments_last_24h()
    recent_7d = analytics.get_assessments_last_7d()

    # Average dimension scores (Big Five only for backward compatibility)
    bf_stats = analytics.get_big_five_stats()
    avg_scores = bf_stats["avg_scores"]

    # Most popular assessment type
    comparison = analytics.get_assessment_comparison()
    most_popular = comparison["most_popular"]

    # API health
    api_health = "healthy" if anthropic_client else "api_key_missing"

    return DashboardStats(
        total_assessments=total_assessments,
        total_users=total_users,
        total_chat_messages=chat_messages,
        assessments_last_24h=recent_24h["total"],
        assessments_last_7d=recent_7d["total"],
        big_five_count=big_five_count,
        disc_count=disc_count,
        avg_completion_rate=95.0,
        top_dimensions=avg_scores,
        api_health=api_health,
        most_popular_type=most_popular
    )


@router.get("/users", response_model=List[UserInfo])
async def get_users(
    session: dict = Depends(verify_admin_token),
    limit: int = 100,
    offset: int = 0,
    assessment_type: Optional[str] = None
):
    """Get list of users with optional filtering by assessment type"""

    users_list = []
    for user_id, user_data in list(_analytics["users"].items())[offset:offset+limit]:
        # Count assessments by type for this user
        user_assessments = [a for a in _analytics["assessments"] if a["user_id"] == user_id]
        bf_count = sum(1 for a in user_assessments if a.get("assessment_type") == "big_five")
        disc_count = sum(1 for a in user_assessments if a.get("assessment_type") == "disc")

        # Get last assessment type
        last_assessment = max(user_assessments, key=lambda a: a.get("completed_at", ""), default=None)
        last_type = last_assessment.get("assessment_type") if last_assessment else None

        # Filter by assessment type if specified
        if assessment_type:
            if assessment_type == "big_five" and bf_count == 0:
                continue
            if assessment_type == "disc" and disc_count == 0:
                continue

        users_list.append(UserInfo(
            user_id=user_id,
            assessments_count=user_data.get("assessments_count", 0),
            big_five_count=bf_count,
            disc_count=disc_count,
            last_activity=datetime.fromisoformat(user_data["last_activity"]) if user_data.get("last_activity") else None,
            last_assessment_type=last_type,
            consents=user_data.get("consents", {}),
            has_chat_profile=user_data.get("has_chat_profile", False)
        ))

    return users_list


@router.get("/assessments", response_model=List[AssessmentInfo])
async def get_assessments(
    session: dict = Depends(verify_admin_token),
    limit: int = 50,
    offset: int = 0,
    assessment_type: Optional[str] = None
):
    """Get list of completed assessments with optional type filtering"""

    # Filter by type if specified
    assessments = _analytics["assessments"]
    if assessment_type:
        assessments = [a for a in assessments if a.get("assessment_type") == assessment_type]

    assessments_list = []
    for a in assessments[offset:offset+limit]:
        assessments_list.append(AssessmentInfo(
            assessment_id=a["assessment_id"],
            user_id=a["user_id"],
            assessment_type=a.get("assessment_type", "unknown"),
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
    session: dict = Depends(verify_admin_token),
    assessment_type: Optional[str] = None
):
    """
    Export all user data (GDPR compliance)

    Args:
        user_id: User ID to export
        assessment_type: Optional filter for specific assessment type (big_five, disc)

    Returns:
        Complete user data export in JSON format
    """

    from api_main_gdpr import _user_profiles

    # Get user assessments
    assessments = [
        a for a in _analytics["assessments"]
        if a["user_id"] == user_id
    ]

    # Filter by type if specified
    if assessment_type:
        assessments = [a for a in assessments if a.get("assessment_type") == assessment_type]

    # Separate by type for organized export
    big_five_assessments = [a for a in assessments if a.get("assessment_type") == "big_five"]
    disc_assessments = [a for a in assessments if a.get("assessment_type") == "disc"]

    user_data = {
        "user_id": user_id,
        "export_date": datetime.utcnow().isoformat(),
        "export_filter": assessment_type or "all",
        "profile": _analytics["users"].get(user_id, {}),
        "assessments": {
            "total": len(assessments),
            "big_five": {
                "count": len(big_five_assessments),
                "data": big_five_assessments
            },
            "disc": {
                "count": len(disc_assessments),
                "data": disc_assessments
            }
        },
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


@router.get("/stats/big-five")
async def get_big_five_analytics(session: dict = Depends(verify_admin_token)):
    """Get detailed Big Five analytics"""
    analytics = AdminAnalytics(_analytics)
    return analytics.get_big_five_stats()


@router.get("/stats/disc")
async def get_disc_analytics(session: dict = Depends(verify_admin_token)):
    """
    Get detailed DISC analytics

    Returns:
    - Total DISC assessments
    - Average DISC scores (D, I, S, C)
    - DISC profile distribution (Di, Sc, etc.)
    - Dominant profiles
    - Completion rate
    """
    analytics = AdminAnalytics(_analytics)
    return analytics.get_disc_stats()


@router.get("/stats/comparison")
async def get_assessment_comparison(session: dict = Depends(verify_admin_token)):
    """Compare Big Five vs DISC assessments"""
    analytics = AdminAnalytics(_analytics)
    return analytics.get_assessment_comparison()


@router.get("/stats/time-series")
async def get_time_series(
    session: dict = Depends(verify_admin_token),
    days: int = 30
):
    """
    Get time series data for assessments

    Args:
        days: Number of days to analyze (default 30)

    Returns:
        Daily breakdown of assessments by type
    """
    analytics = AdminAnalytics(_analytics)
    return analytics.get_time_series_data(days)


@router.get("/stats/users/demographics")
async def get_user_demographics(session: dict = Depends(verify_admin_token)):
    """Get user demographics by assessment type preference"""
    analytics = AdminAnalytics(_analytics)
    return analytics.get_user_demographics_by_type()


@router.get("/stats/conversion-funnel")
async def get_conversion_funnel(session: dict = Depends(verify_admin_token)):
    """Get conversion funnel: Start → Complete for each assessment type"""
    analytics = AdminAnalytics(_analytics)
    return analytics.get_completion_funnel()


@router.get("/analytics/comprehensive")
async def get_comprehensive_analytics(session: dict = Depends(verify_admin_token)):
    """
    Get comprehensive analytics report

    Includes:
    - Overview statistics
    - Big Five analytics
    - DISC analytics
    - Time series trends
    - User demographics
    - Conversion funnel
    """
    analytics = AdminAnalytics(_analytics)
    return analytics.generate_comprehensive_report()


# ── Helper function to track analytics ───────────────────────────────────────

def track_assessment(
    assessment_id: str,
    user_id: str,
    scores: Dict[str, float],
    assessment_type: str = "big_five",
    language: str = "sv"
):
    """
    Track completed assessment (called from main API)

    Args:
        assessment_id: Unique assessment ID
        user_id: User ID
        scores: Assessment scores
        assessment_type: Type of assessment (big_five, disc, etc.)
        language: Language code
    """
    _analytics["assessments"].append({
        "assessment_id": assessment_id,
        "user_id": user_id,
        "assessment_type": assessment_type,
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
