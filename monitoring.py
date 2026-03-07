"""
Monitoring & Security Middleware
Includes Sentry error tracking and rate limiting
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import Request, HTTPException
from typing import Dict
import time
import os


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
