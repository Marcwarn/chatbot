"""
Monitoring & Security Middleware
Includes Sentry error tracking, rate limiting, and attack detection
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import Request, HTTPException
from typing import Dict, List, Optional, Set
import time
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum


# ── Sentry Setup ─────────────────────────────────────────────────────────────

def init_sentry():
    """Initialize Sentry error tracking"""
    sentry_dsn = os.getenv("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
            ],
            # Performance monitoring
            traces_sample_rate=0.1,  # 10% of transactions

            # Error filtering
            before_send=before_send_filter,

            # Environment
            environment=os.getenv("ENVIRONMENT", "production"),

            # Release tracking
            release=os.getenv("VERCEL_GIT_COMMIT_SHA", "local"),
        )
        print("✅ Sentry monitoring initialized")
    else:
        print("ℹ️  Sentry DSN not configured - monitoring disabled")


def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    # Don't send 404s
    if event.get("exception"):
        exc_type = event["exception"]["values"][0].get("type", "")
        if "404" in exc_type:
            return None

    # Don't send auth failures (too noisy)
    if "Unauthorized" in str(event):
        return None

    return event


# ── Rate Limiting ────────────────────────────────────────────────────────────

class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis-based rate limiting
    """

    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.limits = {
            "/api/admin/login": {"calls": 5, "period": 300},  # 5 attempts per 5 min
            "/api/v1/chat": {"calls": 20, "period": 60},      # 20 msgs per minute
            "/api/v1/assessment/start": {"calls": 10, "period": 3600},  # 10 assessments per hour
            "default": {"calls": 100, "period": 60}           # 100 requests per minute
        }

    def _clean_old_requests(self, key: str, period: int):
        """Remove requests older than the period"""
        if key not in self.requests:
            return

        now = time.time()
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if now - timestamp < period
        ]

    def is_allowed(self, client_ip: str, endpoint: str) -> bool:
        """Check if request is allowed"""
        # Find matching limit
        limit_config = self.limits.get(endpoint, self.limits["default"])

        key = f"{client_ip}:{endpoint}"
        now = time.time()

        # Clean old requests
        self._clean_old_requests(key, limit_config["period"])

        # Initialize if new key
        if key not in self.requests:
            self.requests[key] = []

        # Check if limit exceeded
        if len(self.requests[key]) >= limit_config["calls"]:
            return False

        # Record request
        self.requests[key].append(now)
        return True

    def get_remaining(self, client_ip: str, endpoint: str) -> int:
        """Get remaining requests"""
        limit_config = self.limits.get(endpoint, self.limits["default"])
        key = f"{client_ip}:{endpoint}"

        self._clean_old_requests(key, limit_config["period"])

        if key not in self.requests:
            return limit_config["calls"]

        return max(0, limit_config["calls"] - len(self.requests[key]))


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path

    # Check rate limit
    if not rate_limiter.is_allowed(client_ip, endpoint):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )

    # Add rate limit headers
    response = await call_next(request)
    remaining = rate_limiter.get_remaining(client_ip, endpoint)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response


# ── Security Event Types ─────────────────────────────────────────────────────

class SecurityEventType(str, Enum):
    """Types of security events to track"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    DOS_ATTEMPT = "dos_attempt"
    DATA_EXFILTRATION = "data_exfiltration"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    SCANNER_DETECTED = "scanner_detected"
    HONEYPOT_TRIGGERED = "honeypot_triggered"


# ── Attack Detection ─────────────────────────────────────────────────────────

class AttackDetector:
    """
    Real-time attack detection system
    Detects common attack patterns and suspicious behavior
    """

    def __init__(self):
        # Track failed login attempts
        self.failed_logins: Dict[str, List[float]] = defaultdict(list)

        # Track request patterns for DoS detection
        self.request_patterns: Dict[str, List[float]] = defaultdict(list)

        # Track data export volumes
        self.export_volumes: Dict[str, List[int]] = defaultdict(list)

        # Blocked IPs (temporary)
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_timestamp

        # SQL injection patterns
        self.sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b\s+\d+\s*=\s*\d+)",
            r"(\band\b\s+\d+\s*=\s*\d+)",
            r"(;.*drop\b)",
            r"(;.*delete\b)",
            r"(;.*insert\b)",
            r"(;.*update\b)",
            r"('.*--)",
            r"('.*\bor\b.*')",
            r"(\bexec\b.*\()",
            r"(\bexecute\b.*\()",
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",  # onclick, onerror, etc.
            r"<iframe[^>]*>",
            r"<embed[^>]*>",
            r"<object[^>]*>",
            r"eval\s*\(",
            r"document\.cookie",
            r"document\.write",
        ]

        # Scanner user agents
        self.scanner_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "nessus",
            "burp", "zap", "acunetix", "appscan", "metasploit"
        ]

    def detect_brute_force(self, client_ip: str, endpoint: str, success: bool = False) -> bool:
        """
        Detect brute force login attempts
        Returns True if attack detected
        """
        if not endpoint.endswith("/login"):
            return False

        now = time.time()
        key = f"{client_ip}:{endpoint}"

        # Clean old attempts (5 minute window)
        self.failed_logins[key] = [
            t for t in self.failed_logins[key]
            if now - t < 300
        ]

        if not success:
            self.failed_logins[key].append(now)

        # Threshold: 5 failed attempts in 5 minutes
        if len(self.failed_logins[key]) >= 5:
            return True

        return False

    def detect_sql_injection(self, input_data: str) -> Optional[str]:
        """
        Detect SQL injection attempts in input
        Returns matched pattern if found
        """
        input_lower = input_data.lower()

        for pattern in self.sql_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return pattern

        return None

    def detect_xss(self, input_data: str) -> Optional[str]:
        """
        Detect XSS attempts in input
        Returns matched pattern if found
        """
        for pattern in self.xss_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                return pattern

        return None

    def detect_dos(self, client_ip: str, endpoint: str) -> bool:
        """
        Detect DoS/DDoS attempts
        Returns True if suspicious rate detected
        """
        now = time.time()
        key = f"{client_ip}:{endpoint}"

        # Clean old requests (1 minute window)
        self.request_patterns[key] = [
            t for t in self.request_patterns[key]
            if now - t < 60
        ]

        self.request_patterns[key].append(now)

        # Threshold: 50 requests per minute (aggressive)
        if len(self.request_patterns[key]) >= 50:
            return True

        # Also check burst patterns: 20 requests in 5 seconds
        recent = [t for t in self.request_patterns[key] if now - t < 5]
        if len(recent) >= 20:
            return True

        return False

    def detect_data_exfiltration(self, client_ip: str, data_size: int) -> bool:
        """
        Detect mass data exports (potential exfiltration)
        Returns True if suspicious export pattern detected
        """
        now = time.time()

        # Clean old exports (1 hour window)
        old_exports = self.export_volumes[client_ip]
        self.export_volumes[client_ip] = [
            size for size in old_exports
        ][-10:]  # Keep last 10 exports

        self.export_volumes[client_ip].append(data_size)

        # Threshold: More than 3 large exports (>100KB) in short time
        large_exports = [s for s in self.export_volumes[client_ip] if s > 100000]
        if len(large_exports) >= 3:
            return True

        return False

    def detect_scanner(self, user_agent: str) -> bool:
        """
        Detect automated security scanners
        Returns True if scanner detected
        """
        ua_lower = user_agent.lower()
        return any(scanner in ua_lower for scanner in self.scanner_agents)

    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if client_ip in self.blocked_ips:
            if time.time() < self.blocked_ips[client_ip]:
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[client_ip]
        return False

    def block_ip(self, client_ip: str, duration_seconds: int = 3600):
        """Temporarily block an IP (default 1 hour)"""
        self.blocked_ips[client_ip] = time.time() + duration_seconds

    def get_blocked_ips(self) -> List[Dict]:
        """Get list of currently blocked IPs"""
        now = time.time()
        return [
            {
                "ip": ip,
                "unblock_at": datetime.fromtimestamp(timestamp).isoformat(),
                "remaining_seconds": int(timestamp - now)
            }
            for ip, timestamp in self.blocked_ips.items()
            if timestamp > now
        ]


# Global attack detector instance
attack_detector = AttackDetector()


# ── Security Event Storage ───────────────────────────────────────────────────

class SecurityEventStore:
    """
    In-memory storage for security events
    For production, use Redis or database
    """

    def __init__(self, max_events: int = 1000):
        self.events: List[Dict] = []
        self.max_events = max_events

    def add_event(self, event_type: SecurityEventType, client_ip: str,
                  endpoint: str, details: Dict = None):
        """Add security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "client_ip": client_ip,
            "endpoint": endpoint,
            "details": details or {}
        }

        self.events.insert(0, event)  # Most recent first

        # Keep only recent events
        if len(self.events) > self.max_events:
            self.events = self.events[:self.max_events]

        # Also send to Sentry with high priority
        if sentry_sdk:
            sentry_sdk.capture_message(
                f"Security Event: {event_type.value}",
                level="warning",
                extras=event
            )

    def get_recent_events(self, limit: int = 100,
                         event_type: Optional[SecurityEventType] = None) -> List[Dict]:
        """Get recent security events"""
        events = self.events

        if event_type:
            events = [e for e in events if e["event_type"] == event_type.value]

        return events[:limit]

    def get_events_by_ip(self, client_ip: str, limit: int = 50) -> List[Dict]:
        """Get events for specific IP"""
        return [e for e in self.events if e["client_ip"] == client_ip][:limit]

    def get_event_counts(self, hours: int = 24) -> Dict[str, int]:
        """Get event counts by type for last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [
            e for e in self.events
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        counts = defaultdict(int)
        for event in recent:
            counts[event["event_type"]] += 1

        return dict(counts)


# Global security event store
security_events = SecurityEventStore()


# ── Analytics Tracking ───────────────────────────────────────────────────────

def track_api_call(endpoint: str, user_id: str = None, duration_ms: float = 0):
    """Track API call for analytics"""
    # This can be extended to send to analytics service
    # For now, just log to Sentry breadcrumb
    if sentry_sdk:
        sentry_sdk.add_breadcrumb(
            category="api",
            message=f"API call: {endpoint}",
            level="info",
            data={
                "endpoint": endpoint,
                "user_id": user_id,
                "duration_ms": duration_ms
            }
        )
