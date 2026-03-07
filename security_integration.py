"""
Security Integration Module
Integrates all security components with existing API endpoints
"""

from fastapi import Request, HTTPException
from typing import Optional
import asyncio

from monitoring import (
    attack_detector,
    security_events,
    SecurityEventType,
    honeypot_detector,
    RequestFingerprint,
    detect_command_injection,
    detect_path_traversal
)
from alerts import alert_manager, auto_block_manager
from database import db
from metrics import metrics_tracker


# ── Input Validation & Attack Detection ──────────────────────────────────────

class SecurityInputValidator:
    """
    Comprehensive input validation and attack detection
    """

    @staticmethod
    def validate_and_detect(
        input_data: str,
        client_ip: str,
        endpoint: str
    ) -> Optional[dict]:
        """
        Validate input and detect attacks
        Returns dict with attack details if detected, None otherwise
        """

        # Check for SQL injection
        sql_pattern = attack_detector.detect_sql_injection(input_data)
        if sql_pattern:
            return {
                "attack_type": SecurityEventType.SQL_INJECTION,
                "severity": "critical",
                "pattern": sql_pattern,
                "description": "SQL injection attempt detected"
            }

        # Check for XSS
        xss_pattern = attack_detector.detect_xss(input_data)
        if xss_pattern:
            return {
                "attack_type": SecurityEventType.XSS_ATTEMPT,
                "severity": "high",
                "pattern": xss_pattern,
                "description": "XSS attempt detected"
            }

        # Check for command injection
        cmd_pattern = detect_command_injection(input_data)
        if cmd_pattern:
            return {
                "attack_type": SecurityEventType.SUSPICIOUS_PATTERN,
                "severity": "high",
                "pattern": cmd_pattern,
                "description": "Command injection attempt detected"
            }

        return None


# ── Request Inspector ────────────────────────────────────────────────────────

class RequestInspector:
    """
    Inspect requests for security threats
    """

    @staticmethod
    async def inspect_request(request: Request) -> Optional[dict]:
        """
        Comprehensive request inspection
        Returns threat details if detected
        """
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        user_agent = request.headers.get("user-agent", "")

        threats = []

        # 1. Check if IP is blocked
        if attack_detector.is_ip_blocked(client_ip):
            return {
                "blocked": True,
                "reason": "IP is temporarily blocked",
                "threat_level": "critical"
            }

        # 2. Check honeypot endpoints
        if honeypot_detector.check_endpoint(endpoint):
            honeypot_detector.record_trigger(client_ip)

            # Log event
            security_events.add_event(
                SecurityEventType.HONEYPOT_TRIGGERED,
                client_ip,
                endpoint,
                {"user_agent": user_agent}
            )

            # Auto-block
            attack_detector.block_ip(client_ip, duration_seconds=7200)

            # Send alert
            asyncio.create_task(
                alert_manager.send_security_alert(
                    event_type="honeypot_triggered",
                    client_ip=client_ip,
                    endpoint=endpoint,
                    details={"user_agent": user_agent},
                    auto_blocked=True
                )
            )

            return {
                "blocked": True,
                "reason": "Honeypot triggered",
                "threat_level": "high"
            }

        # 3. Check for scanners
        if attack_detector.detect_scanner(user_agent):
            security_events.add_event(
                SecurityEventType.SCANNER_DETECTED,
                client_ip,
                endpoint,
                {"user_agent": user_agent}
            )

            # Auto-block
            attack_detector.block_ip(client_ip, duration_seconds=3600)

            # Send alert
            asyncio.create_task(
                alert_manager.send_security_alert(
                    event_type="scanner_detected",
                    client_ip=client_ip,
                    endpoint=endpoint,
                    details={"user_agent": user_agent},
                    auto_blocked=True
                )
            )

            return {
                "blocked": True,
                "reason": "Security scanner detected",
                "threat_level": "medium"
            }

        # 4. Check DoS patterns
        if attack_detector.detect_dos(client_ip, endpoint):
            security_events.add_event(
                SecurityEventType.DOS_ATTEMPT,
                client_ip,
                endpoint,
                {"user_agent": user_agent}
            )

            # Record metric
            metrics_tracker.record_metric("rate_violation", 1, {"ip": client_ip})

            # Auto-block for aggressive DoS
            attack_detector.block_ip(client_ip, duration_seconds=1800)

            # Send alert
            asyncio.create_task(
                alert_manager.send_security_alert(
                    event_type="dos_attempt",
                    client_ip=client_ip,
                    endpoint=endpoint,
                    details={"user_agent": user_agent},
                    auto_blocked=True
                )
            )

            return {
                "blocked": True,
                "reason": "DoS attempt detected",
                "threat_level": "medium"
            }

        # 5. Check suspicious user agent
        fingerprint_check = RequestFingerprint.is_suspicious(user_agent)
        if fingerprint_check["is_suspicious"]:
            security_events.add_event(
                SecurityEventType.SUSPICIOUS_PATTERN,
                client_ip,
                endpoint,
                {
                    "reasons": fingerprint_check["reasons"],
                    "user_agent": user_agent
                }
            )

        # 6. Check path traversal in URL
        path_attack = detect_path_traversal(str(request.url))
        if path_attack:
            security_events.add_event(
                SecurityEventType.SUSPICIOUS_PATTERN,
                client_ip,
                endpoint,
                {"attack_type": "path_traversal", "pattern": path_attack}
            )

            return {
                "blocked": True,
                "reason": "Path traversal attempt detected",
                "threat_level": "high"
            }

        return None


# ── Login Monitor ────────────────────────────────────────────────────────────

class LoginMonitor:
    """
    Monitor login attempts for brute force attacks
    """

    @staticmethod
    async def log_login_attempt(
        client_ip: str,
        endpoint: str,
        success: bool,
        username: Optional[str] = None
    ):
        """
        Log login attempt and detect brute force
        """

        # Detect brute force
        if attack_detector.detect_brute_force(client_ip, endpoint, success):
            # Log event
            security_events.add_event(
                SecurityEventType.BRUTE_FORCE,
                client_ip,
                endpoint,
                {
                    "username": username,
                    "success": success,
                    "attempts": len(attack_detector.failed_logins.get(f"{client_ip}:{endpoint}", []))
                }
            )

            # Record metric
            metrics_tracker.record_metric("failed_login", 1, {"ip": client_ip})

            # Check if should auto-block
            block_decision = auto_block_manager.should_block(
                "brute_force",
                event_count=len(attack_detector.failed_logins.get(f"{client_ip}:{endpoint}", []))
            )

            if block_decision["should_block"]:
                # Auto-block
                attack_detector.block_ip(client_ip, duration_seconds=block_decision["duration"])

                # Save to database
                db.block_ip(
                    ip_address=client_ip,
                    reason=block_decision["reason"],
                    duration_seconds=block_decision["duration"]
                )

                # Send alert
                await alert_manager.send_security_alert(
                    event_type="brute_force",
                    client_ip=client_ip,
                    endpoint=endpoint,
                    details={
                        "username": username,
                        "attempts": len(attack_detector.failed_logins.get(f"{client_ip}:{endpoint}", []))
                    },
                    auto_blocked=True
                )

        if not success:
            # Record failed login metric
            metrics_tracker.record_metric("failed_login", 1, {"ip": client_ip})


# ── Data Export Monitor ──────────────────────────────────────────────────────

class DataExportMonitor:
    """
    Monitor data exports for potential exfiltration
    """

    @staticmethod
    async def log_export(
        client_ip: str,
        endpoint: str,
        data_size: int,
        export_type: str
    ):
        """
        Log data export and detect mass exfiltration
        """

        # Detect data exfiltration
        if attack_detector.detect_data_exfiltration(client_ip, data_size):
            # Log event
            security_events.add_event(
                SecurityEventType.DATA_EXFILTRATION,
                client_ip,
                endpoint,
                {
                    "data_size": data_size,
                    "export_type": export_type,
                    "total_exports": len(attack_detector.export_volumes[client_ip])
                }
            )

            # Send critical alert
            await alert_manager.send_security_alert(
                event_type="data_exfiltration",
                client_ip=client_ip,
                endpoint=endpoint,
                details={
                    "data_size": data_size,
                    "export_type": export_type
                },
                auto_blocked=False
            )


# ── Helper Functions ─────────────────────────────────────────────────────────

async def validate_input_security(
    input_data: str,
    client_ip: str,
    endpoint: str
) -> None:
    """
    Validate input for security threats
    Raises HTTPException if threat detected
    """
    validator = SecurityInputValidator()
    attack = validator.validate_and_detect(input_data, client_ip, endpoint)

    if attack:
        # Log event
        security_events.add_event(
            attack["attack_type"],
            client_ip,
            endpoint,
            {
                "pattern": attack["pattern"],
                "description": attack["description"]
            }
        )

        # Check if should auto-block
        block_decision = auto_block_manager.should_block(
            attack["attack_type"].value,
            event_count=1
        )

        if block_decision["should_block"]:
            # Auto-block
            attack_detector.block_ip(client_ip, duration_seconds=block_decision["duration"])

            # Save to database
            db.block_ip(
                ip_address=client_ip,
                reason=block_decision["reason"],
                duration_seconds=block_decision["duration"]
            )

            # Send alert
            await alert_manager.send_security_alert(
                event_type=attack["attack_type"].value,
                client_ip=client_ip,
                endpoint=endpoint,
                details=attack,
                auto_blocked=True
            )

        # Block the request
        raise HTTPException(
            status_code=400,
            detail="Invalid input detected"
        )


async def inspect_request_security(request: Request) -> None:
    """
    Inspect request for security threats
    Raises HTTPException if threat detected
    """
    inspector = RequestInspector()
    threat = await inspector.inspect_request(request)

    if threat and threat.get("blocked"):
        raise HTTPException(
            status_code=403,
            detail=threat.get("reason", "Access forbidden")
        )


# ── Export all helpers ───────────────────────────────────────────────────────

__all__ = [
    "SecurityInputValidator",
    "RequestInspector",
    "LoginMonitor",
    "DataExportMonitor",
    "validate_input_security",
    "inspect_request_security"
]
