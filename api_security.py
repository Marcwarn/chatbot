"""
Security API Endpoints
Provides access to security dashboard, metrics, and monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from monitoring import (
    security_events,
    attack_detector,
    SecurityEventType
)
from metrics import (
    score_calculator,
    pattern_analyzer,
    report_generator,
    metrics_tracker,
    metrics_exporter
)
from alerts import alert_manager
from database import db


# ── Router Setup ─────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/admin/security", tags=["security"])


# ── Pydantic Models ──────────────────────────────────────────────────────────

class SecurityMetricsResponse(BaseModel):
    """Response model for security metrics"""
    failed_logins: int
    rate_violations: int
    sql_injections: int
    xss_attempts: int
    active_threats: int
    blocked_ips_count: int
    security_score: dict
    login_timeline: dict
    rate_timeline: dict
    recent_events: List[dict]
    blocked_ips: List[dict]


class BlockIPRequest(BaseModel):
    """Request to block an IP"""
    ip_address: str
    reason: str
    duration_seconds: int = 3600
    is_permanent: bool = False


class UnblockIPRequest(BaseModel):
    """Request to unblock an IP"""
    ip_address: str


# ── Authentication Helper ────────────────────────────────────────────────────

async def verify_admin_access(request: Request):
    """Verify admin access for security endpoints"""
    # You can integrate with your existing admin authentication
    # For now, this is a placeholder
    # In production, check for valid admin session/token
    pass


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/metrics", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    hours: int = 24,
    admin: dict = Depends(verify_admin_access)
):
    """
    Get comprehensive security metrics for dashboard
    """
    try:
        # Get events from in-memory store
        events = security_events.get_recent_events(limit=1000)

        # Count events by type
        event_counts = security_events.get_event_counts(hours=hours)

        # Get security score
        score_data = score_calculator.calculate_score(events, hours=hours)

        # Get timelines
        login_timeline = metrics_tracker.get_timeline(
            "failed_login",
            hours=hours,
            interval_minutes=60
        )

        rate_timeline = metrics_tracker.get_timeline(
            "rate_violation",
            hours=hours,
            interval_minutes=60
        )

        # Get blocked IPs
        blocked_ips = attack_detector.get_blocked_ips()

        # Calculate active threats (recent high-severity events)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        active_threats = len([
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
            and e["event_type"] in ["sql_injection", "xss_attempt", "data_exfiltration"]
        ])

        return SecurityMetricsResponse(
            failed_logins=event_counts.get("brute_force", 0),
            rate_violations=event_counts.get("dos_attempt", 0),
            sql_injections=event_counts.get("sql_injection", 0),
            xss_attempts=event_counts.get("xss_attempt", 0),
            active_threats=active_threats,
            blocked_ips_count=len(blocked_ips),
            security_score=score_data,
            login_timeline=login_timeline,
            rate_timeline=rate_timeline,
            recent_events=events[:50],
            blocked_ips=blocked_ips
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/events")
async def get_security_events(
    hours: int = 24,
    event_type: Optional[str] = None,
    limit: int = 100,
    admin: dict = Depends(verify_admin_access)
):
    """
    Get recent security events with optional filtering
    """
    try:
        events = security_events.get_recent_events(limit=limit, event_type=event_type)
        return {"events": events, "total": len(events)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")


@router.get("/blocked-ips")
async def get_blocked_ips(admin: dict = Depends(verify_admin_access)):
    """
    Get list of currently blocked IPs
    """
    try:
        blocked_ips = attack_detector.get_blocked_ips()
        return {"blocked_ips": blocked_ips, "total": len(blocked_ips)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blocked IPs: {str(e)}")


@router.post("/block-ip")
async def block_ip(
    request: BlockIPRequest,
    admin: dict = Depends(verify_admin_access)
):
    """
    Manually block an IP address
    """
    try:
        attack_detector.block_ip(
            request.ip_address,
            duration_seconds=request.duration_seconds
        )

        # Also save to database
        db.block_ip(
            ip_address=request.ip_address,
            reason=request.reason,
            duration_seconds=request.duration_seconds,
            is_permanent=request.is_permanent
        )

        # Send alert
        await alert_manager.send_security_alert(
            event_type="manual_block",
            client_ip=request.ip_address,
            endpoint="N/A",
            details={"reason": request.reason, "admin_action": True},
            auto_blocked=False
        )

        return {
            "success": True,
            "message": f"IP {request.ip_address} has been blocked",
            "duration": request.duration_seconds
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block IP: {str(e)}")


@router.post("/unblock-ip")
async def unblock_ip(
    request: UnblockIPRequest,
    admin: dict = Depends(verify_admin_access)
):
    """
    Manually unblock an IP address
    """
    try:
        # Remove from in-memory block list
        if request.ip_address in attack_detector.blocked_ips:
            del attack_detector.blocked_ips[request.ip_address]

        return {
            "success": True,
            "message": f"IP {request.ip_address} has been unblocked"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unblock IP: {str(e)}")


@router.get("/score")
async def get_security_score(
    hours: int = 24,
    admin: dict = Depends(verify_admin_access)
):
    """
    Get current security score
    """
    try:
        events = security_events.get_recent_events(limit=1000)
        score_data = score_calculator.calculate_score(events, hours=hours)

        return score_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


@router.get("/patterns")
async def get_attack_patterns(
    hours: int = 24,
    admin: dict = Depends(verify_admin_access)
):
    """
    Analyze and return detected attack patterns
    """
    try:
        events = security_events.get_recent_events(limit=1000)
        patterns = pattern_analyzer.analyze_patterns(events, hours=hours)

        return patterns

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze patterns: {str(e)}")


@router.get("/report/weekly")
async def get_weekly_report(admin: dict = Depends(verify_admin_access)):
    """
    Generate and return weekly security report
    """
    try:
        events = security_events.get_recent_events(limit=10000)
        report = report_generator.generate_report(events)

        # Save report to file
        report_path = report_generator.save_report(report)

        return {
            "report": report,
            "saved_to": report_path,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/export/json")
async def export_metrics_json(
    hours: int = 24,
    admin: dict = Depends(verify_admin_access)
):
    """
    Export security metrics as JSON
    """
    try:
        events = security_events.get_recent_events(limit=1000)
        score_data = score_calculator.calculate_score(events, hours=hours)
        patterns = pattern_analyzer.analyze_patterns(events, hours=hours)

        json_data = metrics_exporter.export_to_json(
            events=events,
            score_data=score_data,
            patterns=patterns
        )

        return {
            "data": json_data,
            "exported_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {str(e)}")


@router.post("/test-alert")
async def test_security_alert(admin: dict = Depends(verify_admin_access)):
    """
    Send a test security alert to verify notification channels
    """
    try:
        await alert_manager.send_security_alert(
            event_type="test",
            client_ip="127.0.0.1",
            endpoint="/api/test",
            details={"message": "This is a test alert"},
            auto_blocked=False
        )

        return {
            "success": True,
            "message": "Test alert sent successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test alert: {str(e)}")


@router.get("/dashboard")
async def serve_security_dashboard():
    """
    Serve the security dashboard HTML
    """
    from fastapi.responses import FileResponse
    return FileResponse("security_dashboard.html")
