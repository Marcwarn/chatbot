# LESSONS LEARNED - Security Vulnerability Prevention Guide

**Created:** 2026-03-07
**Purpose:** Document every security vulnerability found in this codebase and establish "Never Do This Again" rules

---

## 🔴 CRITICAL VULNERABILITIES - NEVER REPEAT THESE

### 1. WEAK PASSWORD HASHING - SHA-256 Without Salt

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

**Why It's Dangerous:**
- SHA-256 is a fast hashing algorithm designed for data integrity, NOT passwords
- Without salt, identical passwords produce identical hashes
- Attackers can use rainbow tables to crack millions of passwords instantly
- Vulnerable to GPU-accelerated brute force attacks (billions of hashes per second)

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (adaptive cost factor)"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password using timing-safe comparison"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

**Why bcrypt is correct:**
- Built-in salt (random per password)
- Adaptive cost factor (can increase difficulty over time)
- Slow by design (prevents brute force)
- Industry standard for password storage

**Rule:** ALWAYS use bcrypt, argon2, or scrypt for password hashing. NEVER use SHA-256, MD5, or SHA-1.

---

### 2. HARDCODED CREDENTIALS IN SOURCE CODE

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # Default: "admin123"
)

# In GDPR endpoint:
ADMIN_KEY = "CHANGE_ME_IN_PRODUCTION"
```

**Why It's Dangerous:**
- Source code is often public (GitHub, internal repos)
- Default credentials are the #1 target for attackers
- "CHANGE_ME" strings are grep-able by attackers
- Violates principle of least privilege

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
import os
import sys

# Require environment variables, no defaults for secrets
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
if not ADMIN_PASSWORD_HASH:
    raise ValueError("ADMIN_PASSWORD_HASH environment variable must be set")

ADMIN_KEY = os.getenv("ADMIN_API_KEY")
if not ADMIN_KEY:
    raise ValueError("ADMIN_API_KEY environment variable must be set")

# For development, use .env files (NEVER commit .env to git)
```

**Rule:**
- NEVER hardcode passwords, API keys, or secrets
- NEVER use defaults for production credentials
- ALWAYS fail fast if required secrets are missing
- ALWAYS use .env files locally (add .env to .gitignore)
- ALWAYS use secret management (AWS Secrets Manager, Vault, etc.) in production

---

### 3. TIMING ATTACKS IN PASSWORD VERIFICATION

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
if password_hash != ADMIN_PASSWORD_HASH:
    raise HTTPException(status_code=401, detail="Invalid password")
```

**Why It's Dangerous:**
- Python's `!=` operator uses early exit optimization
- Comparison stops at first non-matching character
- Attacker can measure response time to infer password length and characters
- Allows password recovery through timing analysis

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
import secrets

# For string comparison
if not secrets.compare_digest(password_hash, ADMIN_PASSWORD_HASH):
    raise HTTPException(status_code=401, detail="Invalid password")

# For bcrypt (built-in timing safety)
if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
    raise HTTPException(status_code=401, detail="Invalid password")
```

**Why secrets.compare_digest is correct:**
- Constant-time comparison (always checks all bytes)
- Prevents timing-based side-channel attacks
- Required for any security-sensitive string comparison

**Rule:** ALWAYS use `secrets.compare_digest()` for comparing passwords, tokens, API keys, or any security-critical strings. NEVER use `==` or `!=` for security comparisons.

---

### 4. CORS WILDCARD - Allows All Origins

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ANY website to make requests
    allow_credentials=True,  # With credentials! Critical vulnerability
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why It's Dangerous:**
- `allow_origins=["*"]` with `allow_credentials=True` is a critical CSRF vulnerability
- Malicious websites can steal user sessions and make authenticated requests
- Bypasses Same-Origin Policy (browser's main security mechanism)
- Can lead to complete account takeover

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
import os

# Define allowed origins explicitly
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    # For development only
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Explicit whitelist
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
)
```

**Rule:**
- NEVER use `allow_origins=["*"]` with credentials
- ALWAYS use explicit origin whitelist
- ALWAYS use environment variables for configuration
- For public APIs without credentials, `["*"]` is OK but disable credentials

---

### 5. NO INPUT VALIDATION - Path Traversal & Injection Risk

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
@router.delete("/users/{user_id}")
async def delete_user(user_id: str):  # No validation!
    # user_id could be: "../admin", "'; DROP TABLE users--", etc.
    pass
```

**Why It's Dangerous:**
- Unvalidated input can contain path traversal attacks (../, ..\..\)
- SQL injection if used in queries
- Command injection if used in shell commands
- NoSQL injection if used in MongoDB queries

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
from pydantic import Field, validator
from typing import Annotated
from fastapi import Path
import re

# Option 1: Pydantic validation
class UserRequest(BaseModel):
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{1,128}$')

# Option 2: FastAPI Path validation
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: Annotated[str, Path(pattern=r'^[a-zA-Z0-9_-]{1,128}$')]
):
    pass

# Option 3: Custom validator function
def validate_user_id(user_id: str) -> str:
    """Validate user ID format"""
    if not re.match(r'^[a-zA-Z0-9_-]{1,128}$', user_id):
        raise ValueError("Invalid user_id format")
    return user_id
```

**Validation Rules by Input Type:**
- **User IDs:** `^[a-zA-Z0-9_-]{1,128}$` (alphanumeric, underscore, hyphen only)
- **Email:** Use `pydantic.EmailStr` (built-in validation)
- **URLs:** Use `pydantic.HttpUrl` (built-in validation)
- **Filenames:** `^[a-zA-Z0-9_.-]{1,255}$` (no path separators)
- **Phone numbers:** `^\+?[1-9]\d{1,14}$` (E.164 format)

**Rule:**
- ALWAYS validate ALL user input with regex patterns
- ALWAYS use whitelists (allowed characters) not blacklists
- ALWAYS set maximum lengths
- ALWAYS use Pydantic validators for complex validation

---

### 6. IN-MEMORY SESSION STORAGE - DoS & Data Loss Risk

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
_admin_sessions: Dict[str, dict] = {}  # In-memory dictionary

def verify_admin_token(token: str):
    if token not in _admin_sessions:  # Sessions lost on restart!
        raise HTTPException(401)
```

**Why It's Dangerous:**
- Memory exhaustion DoS attack (attacker creates unlimited sessions)
- All sessions lost on server restart
- No session sharing across multiple servers
- No automatic cleanup of expired sessions

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS - Use Redis
import redis
import json

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6000)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def create_session(user_id: str, expires_in: int = 3600) -> str:
    """Create session in Redis with automatic expiration"""
    token = secrets.token_urlsafe(32)
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    redis_client.setex(
        f"session:{token}",
        expires_in,
        json.dumps(session_data)
    )
    return token

def verify_session(token: str) -> dict:
    """Verify session from Redis"""
    data = redis_client.get(f"session:{token}")
    if not data:
        raise HTTPException(401, "Invalid or expired session")
    return json.loads(data)
```

**Rule:**
- NEVER store sessions in memory for production
- ALWAYS use Redis or database for session storage
- ALWAYS set automatic expiration (TTL)
- ALWAYS implement session cleanup

---

### 7. WEAK RATE LIMITING - Brute Force Risk

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
self.limits = {
    "/api/admin/login": {"calls": 5, "period": 300},  # 5 attempts per 5 min - too generous!
}
```

**Why It's Dangerous:**
- 5 attempts per 5 minutes = 1,440 attempts per day
- Allows brute force attacks on weak passwords
- No account lockout mechanism
- No progressive delays

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
# Strict rate limiting for authentication
RATE_LIMITS = {
    "/api/admin/login": {
        "calls": 3,          # Only 3 attempts
        "period": 900,       # Per 15 minutes
        "lockout": True,     # Enable account lockout
        "lockout_duration": 3600  # 1 hour lockout after 3 failed attempts
    }
}

class RateLimiter:
    def check_and_increment(self, key: str) -> bool:
        attempts = self.get_attempts(key)

        # Check if locked out
        if self.is_locked_out(key):
            raise HTTPException(429, "Account locked due to too many failed attempts")

        # Check rate limit
        if attempts >= limit:
            self.lockout(key, duration)
            raise HTTPException(429, "Too many attempts")

        self.increment(key)
        return True
```

**Rate Limiting Best Practices:**
- Login endpoints: 3 attempts per 15 minutes + account lockout
- API endpoints: 100 requests per minute
- GDPR data export: 3 requests per hour
- Password reset: 3 requests per hour
- Use progressive delays (exponential backoff)

**Rule:** ALWAYS implement strict rate limiting on authentication endpoints. ALWAYS use account lockout after failed attempts.

---

### 8. NO AUTHENTICATION ON GDPR ENDPOINTS

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
@router.post("/api/v1/gdpr/export")
async def export_user_data(user_id: str):  # NO AUTHENTICATION!
    # Anyone can export anyone's data!
    return user_data
```

**Why It's Dangerous:**
- Allows mass data exfiltration by attackers
- GDPR violation (unauthorized data access)
- Privacy breach (personal data exposed)
- No audit trail of who accessed data

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
@router.post("/api/v1/gdpr/export")
async def export_user_data(
    user_id: str,
    session: dict = Depends(verify_admin_token)  # Require admin auth
):
    # Log access for audit
    audit_log.record(
        action="data_export",
        user_id=user_id,
        admin_id=session["admin_id"],
        ip_address=request.client.host
    )

    return user_data
```

**Rule:**
- ALWAYS require authentication for GDPR endpoints
- ALWAYS require admin privileges for bulk operations
- ALWAYS log all data access for audit trails
- ALWAYS implement multi-factor confirmation for deletion

---

### 9. SENSITIVE DATA EXPOSED IN API RESPONSES

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
@router.get("/users/{user_id}/export")
async def export_user_data(user_id: str):
    return {
        "user_id": user_id,
        "profile": user_profile,  # Contains sensitive data
        "assessments": all_assessments,  # Full history
        "chat_profile": chat_data  # Private conversations
    }
```

**Why It's Dangerous:**
- Exposes full chat history (private conversations)
- No data redaction for sensitive information
- No field-level access control
- Could expose PII (Personally Identifiable Information)

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
def redact_sensitive_data(data: dict) -> dict:
    """Redact sensitive fields from data"""
    sensitive_fields = ["password", "api_key", "token", "ssn", "credit_card"]

    redacted = data.copy()
    for key in redacted:
        if key in sensitive_fields:
            redacted[key] = "[REDACTED]"
        elif isinstance(redacted[key], dict):
            redacted[key] = redact_sensitive_data(redacted[key])

    return redacted

@router.get("/users/{user_id}/export")
async def export_user_data(
    user_id: str,
    session: dict = Depends(verify_admin_token)
):
    user_data = get_user_data(user_id)
    redacted_data = redact_sensitive_data(user_data)

    # Audit log
    audit_log.record("data_export", user_id, session["admin_id"])

    return redacted_data
```

**Rule:**
- ALWAYS redact sensitive data in API responses
- ALWAYS use field-level access control
- ALWAYS log data exports
- ALWAYS minimize data exposure (principle of least privilege)

---

## 🟠 HIGH PRIORITY VULNERABILITIES

### 10. RATE LIMITER IP SPOOFING - X-Forwarded-For Bypass

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
client_ip = request.client.host  # Can be spoofed behind proxy
```

**Why It's Dangerous:**
- Attackers can spoof X-Forwarded-For header
- Bypasses rate limiting completely
- Allows distributed attacks from single source

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
def get_real_client_ip(request: Request) -> str:
    """Get real client IP considering proxy headers"""

    # If behind trusted proxy (e.g., Vercel, CloudFlare)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (client IP)
        return forwarded_for.split(",")[0].strip()

    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

# Better: Use trusted proxy configuration
TRUSTED_PROXIES = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
```

**Rule:** ALWAYS use proper proxy header handling when behind reverse proxy. ALWAYS configure trusted proxy IPs.

---

### 11. NO SESSION CLEANUP - Memory Leak Risk

**What We Did Wrong:**
```python
# ❌ NEVER DO THIS
_admin_sessions[token] = {
    "created_at": datetime.utcnow().isoformat(),
    "expires_at": expires_at.isoformat(),
}
# No cleanup of expired sessions!
```

**Why It's Dangerous:**
- Memory grows indefinitely
- Eventual out-of-memory crash
- DoS vulnerability

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
import asyncio
from datetime import datetime, timedelta

async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    while True:
        try:
            now = datetime.utcnow()
            expired_keys = [
                token for token, session in _admin_sessions.items()
                if datetime.fromisoformat(session["expires_at"]) < now
            ]

            for token in expired_keys:
                del _admin_sessions[token]

            if expired_keys:
                print(f"Cleaned up {len(expired_keys)} expired sessions")

        except Exception as e:
            print(f"Session cleanup error: {e}")

        await asyncio.sleep(300)  # Run every 5 minutes

# Start on app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_sessions())
```

**Rule:** ALWAYS implement automatic cleanup of expired data. ALWAYS use background tasks for maintenance.

---

### 12. SQL INJECTION RISK (Future-proofing)

**What We Did Wrong (potential):**
```python
# ❌ NEVER DO THIS
query = f"SELECT * FROM users WHERE user_id = '{user_id}'"  # String interpolation
cursor.execute(query)
```

**Why It's Dangerous:**
- Allows SQL injection attacks
- Can read entire database
- Can delete or modify data
- Can execute system commands

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS - Use parameterized queries
# With SQLAlchemy ORM (preferred)
user = session.query(User).filter(User.id == user_id).first()

# With raw SQL (if needed)
cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

# NEVER concatenate user input into SQL
```

**Rule:** ALWAYS use parameterized queries. NEVER concatenate user input into SQL. ALWAYS use ORM when possible.

---

## 🟡 MEDIUM PRIORITY ISSUES

### 13. NO HTTPS ENFORCEMENT

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Rule:** ALWAYS enforce HTTPS in production. NEVER transmit credentials over HTTP.

---

### 14. NO CSRF PROTECTION

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/admin/login")
async def login(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf()
```

**Rule:** ALWAYS implement CSRF protection for state-changing operations.

---

### 15. MISSING SECURITY HEADERS

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

**Rule:** ALWAYS add security headers. Use CSP to prevent XSS.

---

### 16. NO REQUEST SIZE LIMITS

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
app.add_middleware(RequestSizeLimitMiddleware, max_size=10_000_000)  # 10MB limit
```

**Rule:** ALWAYS set request size limits to prevent DoS attacks.

---

### 17. INSUFFICIENT AUDIT LOGGING

**The CORRECT Pattern:**
```python
# ✅ ALWAYS DO THIS
def audit_log(action: str, user_id: str, resource: str, ip: str):
    """Log all security-relevant events"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "ip_address": ip,
    }
    # Store in database, send to SIEM
    db.audit_logs.insert(log_entry)
```

**Rule:** ALWAYS log authentication, authorization, and data access events.

---

## 📋 CODING GUIDELINES - MANDATORY CHECKLIST

### Before Writing Any Authentication Code:
- [ ] Use bcrypt for password hashing
- [ ] Use secrets.compare_digest for comparisons
- [ ] Implement strict rate limiting (3 attempts/15 min)
- [ ] Add account lockout mechanism
- [ ] Log all authentication attempts
- [ ] Never hardcode credentials
- [ ] Require environment variables for secrets

### Before Writing Any API Endpoint:
- [ ] Validate ALL input with regex patterns
- [ ] Set maximum length limits
- [ ] Add authentication if needed
- [ ] Add authorization checks
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Return minimal data (no sensitive fields)

### Before Deploying to Production:
- [ ] All environment variables set (no defaults)
- [ ] CORS configured with explicit origins
- [ ] HTTPS enforced
- [ ] Security headers added
- [ ] Rate limiting configured
- [ ] Session storage uses Redis (not in-memory)
- [ ] All secrets rotated
- [ ] Audit logging enabled
- [ ] Error tracking configured (Sentry)

### Before Handling User Data:
- [ ] GDPR consent obtained
- [ ] Data minimization applied
- [ ] Retention policy defined
- [ ] Encryption at rest enabled
- [ ] Access logging enabled
- [ ] Export functionality tested
- [ ] Deletion functionality tested

---

## 🎯 SECURITY PRINCIPLES - ALWAYS FOLLOW

1. **Defense in Depth**: Multiple layers of security (authentication + authorization + rate limiting + validation)

2. **Principle of Least Privilege**: Give minimal access needed, nothing more

3. **Fail Securely**: On error, deny access (don't default to allowing)

4. **Never Trust User Input**: Validate, sanitize, and escape everything

5. **Secure by Default**: Require opt-in for permissive settings, never opt-out

6. **Explicit is Better Than Implicit**: Whitelist allowed values, don't blacklist dangerous ones

7. **Assume Breach**: Log everything, monitor for anomalies, have incident response plan

---

## 📚 REQUIRED READING

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 🔄 REVIEW SCHEDULE

This document must be reviewed and updated:
- After every security incident
- After every penetration test
- Quarterly (minimum)
- When new team members join
- Before major releases

**Last Updated:** 2026-03-07
**Next Review:** 2026-06-07
