# Security Quick Reference Card

**Print this out and keep it at your desk!**

---

## 🚫 NEVER DO THIS

```python
# ❌ Hardcoded secrets
password = "admin123"
API_KEY = "sk-1234567890abcdef"

# ❌ Weak password hashing
hashlib.sha256(password.encode()).hexdigest()

# ❌ CORS wildcard
allow_origins=["*"]

# ❌ Timing attack
if password_hash == stored_hash:

# ❌ SQL injection
execute(f"SELECT * FROM users WHERE id = {user_id}")

# ❌ No input validation
async def delete_user(user_id: str):

# ❌ String comparison for secrets
if token == stored_token:
```

---

## ✅ ALWAYS DO THIS

```python
# ✅ Use environment variables
password_hash = os.getenv("ADMIN_PASSWORD_HASH")
if not password_hash:
    raise ValueError("ADMIN_PASSWORD_HASH must be set")

# ✅ Use bcrypt for passwords
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
is_valid = bcrypt.checkpw(password.encode(), hashed)

# ✅ Explicit CORS origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
allow_origins=ALLOWED_ORIGINS

# ✅ Timing-safe comparison
import secrets
if secrets.compare_digest(password_hash, stored_hash):

# ✅ Parameterized queries / ORM
session.query(User).filter(User.id == user_id).first()

# ✅ Input validation
from pydantic import Field
user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{1,128}$')

# ✅ Timing-safe comparison
if secrets.compare_digest(token, stored_token):
```

---

## 🔒 Before Every Commit

- [ ] No hardcoded secrets
- [ ] All input validated
- [ ] Using bcrypt for passwords
- [ ] CORS not set to wildcard
- [ ] Using secrets.compare_digest()
- [ ] Tests passing

---

## 🚀 Before Every Deploy

- [ ] All environment variables set
- [ ] HTTPS enforced
- [ ] Rate limiting enabled
- [ ] Session storage is Redis
- [ ] Security headers configured
- [ ] Audit logging enabled

---

## 📋 Common Patterns

### Authentication Endpoint
```python
@router.post("/login")
async def login(req: LoginRequest):
    # ✅ Rate limiting (3/15min)
    # ✅ bcrypt verification
    if not bcrypt.checkpw(req.password.encode(), stored_hash.encode()):
        # ✅ Audit log
        audit_log.record("failed_login", req.username)
        raise HTTPException(401, "Invalid credentials")

    # ✅ Secure session token
    token = secrets.token_urlsafe(32)
    # ✅ Store in Redis with expiration
    redis_client.setex(f"session:{token}", 3600, user_id)

    return {"token": token}
```

### Protected Endpoint
```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str = Path(..., regex=r'^[a-zA-Z0-9_-]{1,128}$'),
    session: dict = Depends(verify_admin_token)
):
    # ✅ Input validated
    # ✅ Authentication required
    # ✅ Audit logging
    audit_log.record("user_deletion", user_id, session["admin_id"])

    # ✅ Use ORM
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()

    return {"message": "User deleted"}
```

### GDPR Endpoint
```python
@router.post("/gdpr/export")
async def export_data(
    user_id: str = Path(..., regex=r'^[a-zA-Z0-9_-]{1,128}$'),
    session: dict = Depends(verify_admin_token)
):
    # ✅ Admin authentication
    # ✅ Rate limiting (3/hour)
    # ✅ Audit logging
    audit_log.record("data_export", user_id, session["admin_id"])

    # ✅ Data minimization
    data = get_user_data(user_id)

    # ✅ Redact sensitive fields
    redacted = redact_sensitive_data(data)

    return redacted
```

---

## 🔍 Security Validation Commands

```bash
# Run security scanner
python security_scanner.py

# Check dependencies
pip-audit --requirement requirements.txt

# Test hooks
git commit -m "Test"  # Should run pre-commit checks

# Check for secrets
git secrets --scan -r

# Run security tests
pytest tests/test_security.py
```

---

## 📚 Quick Links

- **Detailed Guide:** LESSONS_LEARNED.md
- **Full Checklist:** SECURITY_CHECKLIST.md
- **System Docs:** SECURITY_SYSTEM_README.md
- **Audit Report:** SECURITY_AUDIT_REPORT.md

---

## 🆘 Emergency Contacts

- **Security Team:** [Email/Slack]
- **DPO/Legal:** [Email]
- **On-call:** [Phone/Pager]

---

## 🎯 Security Principles

1. **Defense in Depth** - Multiple layers of security
2. **Least Privilege** - Minimum access needed
3. **Fail Securely** - Deny by default
4. **Never Trust Input** - Validate everything
5. **Secure by Default** - Require opt-in for permissive settings
6. **Explicit > Implicit** - Whitelist, don't blacklist
7. **Assume Breach** - Log everything, monitor for anomalies

---

## 📊 Common Regex Patterns

```python
# User ID
r'^[a-zA-Z0-9_-]{1,128}$'

# Email (use pydantic.EmailStr instead)
r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# UUID v4
r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'

# Alphanumeric only
r'^[a-zA-Z0-9]+$'

# Safe filename
r'^[a-zA-Z0-9_.-]{1,255}$'

# Phone (E.164)
r'^\+?[1-9]\d{1,14}$'
```

---

## ⚡ Quick Fixes

| Problem | Fix |
|---------|-----|
| Hardcoded password | `password = os.getenv("PASSWORD")` |
| SHA-256 password | `bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())` |
| CORS wildcard | `allow_origins=["https://yourdomain.com"]` |
| No input validation | `user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{1,128}$')` |
| Timing attack | `secrets.compare_digest(hash1, hash2)` |
| SQL injection | Use ORM or parameterized queries |
| No authentication | Add `session: dict = Depends(verify_token)` |
| No rate limiting | Add rate limiting middleware |

---

## 🔢 Security Limits

| Item | Limit | Reason |
|------|-------|--------|
| Login attempts | 3 per 15 min | Prevent brute force |
| API requests | 100 per min | Prevent DoS |
| GDPR export | 3 per hour | Prevent abuse |
| Session duration | 1-8 hours | Balance UX vs security |
| Password length | 12+ chars | Crypto strength |
| Token entropy | 32+ bytes | Prevent guessing |
| Request size | 10MB max | Prevent DoS |

---

**Keep this card visible while coding!**

Last Updated: 2026-03-07
