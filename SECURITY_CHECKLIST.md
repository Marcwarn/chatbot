# SECURITY CHECKLIST

**Purpose:** Mandatory checklist for developers before committing, deploying, or handling user data.

---

## 📝 BEFORE COMMITTING CODE

### Authentication & Authorization
- [ ] **No hardcoded passwords, API keys, or tokens** in code
- [ ] All secrets loaded from environment variables
- [ ] Passwords hashed with bcrypt (NEVER SHA-256, MD5, or SHA-1)
- [ ] Password verification uses `secrets.compare_digest()` or bcrypt
- [ ] Authentication endpoints have rate limiting (≤3 attempts per 15 min)
- [ ] Failed login attempts are logged
- [ ] Session tokens are cryptographically random (`secrets.token_urlsafe`)
- [ ] Session expiration is implemented (max 8 hours, recommended 1 hour)

### Input Validation
- [ ] **ALL user input validated** with regex patterns
- [ ] User IDs validated: `^[a-zA-Z0-9_-]{1,128}$`
- [ ] Email addresses validated with `pydantic.EmailStr`
- [ ] Maximum length limits set on all string inputs
- [ ] No direct string concatenation with user input
- [ ] Pydantic models use `Field()` with validators
- [ ] Path parameters use FastAPI `Path()` with patterns

### CORS & Security Headers
- [ ] `allow_origins` is NOT `["*"]` (must be explicit whitelist)
- [ ] If `allow_credentials=True`, origins MUST be specific domains
- [ ] CORS origins loaded from environment variable
- [ ] Security headers middleware added (CSP, X-Frame-Options, etc.)
- [ ] HTTPS redirect enabled for production

### Rate Limiting
- [ ] Rate limiting middleware enabled
- [ ] Login endpoints: 3 attempts per 15 minutes
- [ ] API endpoints: 100 requests per minute
- [ ] GDPR export: 3 requests per hour
- [ ] Account lockout after failed attempts

### SQL & Injection Prevention
- [ ] Using ORM (SQLAlchemy) for all database queries
- [ ] If raw SQL needed, using parameterized queries only
- [ ] NO f-string or string concatenation in SQL
- [ ] NO user input in shell commands (`subprocess`, `os.system`)

### Session Management
- [ ] Sessions stored in Redis (NOT in-memory for production)
- [ ] Session cleanup task implemented
- [ ] Session expiration enforced server-side
- [ ] Session tokens invalidated on logout

### Audit Logging
- [ ] Authentication attempts logged (success and failure)
- [ ] Data access logged (exports, deletions)
- [ ] Admin actions logged
- [ ] IP address captured in audit logs

### GDPR Compliance
- [ ] Explicit consent required before data processing
- [ ] User can export their data
- [ ] User can delete their data
- [ ] Data retention policy implemented
- [ ] Audit logs for data access

### Code Quality
- [ ] No commented-out code with TODOs like "CHANGE_ME"
- [ ] No debug print statements with sensitive data
- [ ] Error messages don't leak sensitive information
- [ ] Stack traces disabled in production

---

## 🚀 BEFORE DEPLOYING TO PRODUCTION

### Environment Configuration
- [ ] **ALL environment variables set** (no fallback defaults for secrets)
- [ ] `ADMIN_PASSWORD_HASH` set (NOT using default)
- [ ] `ADMIN_API_KEY` set (NOT "CHANGE_ME_IN_PRODUCTION")
- [ ] `ANTHROPIC_API_KEY` set (if using AI features)
- [ ] `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` set
- [ ] `SENTRY_DSN` set for error tracking
- [ ] `ALLOWED_ORIGINS` set with specific domains
- [ ] `ENVIRONMENT=production` set

### Database & Storage
- [ ] Database migrations applied
- [ ] Database backups enabled
- [ ] Redis persistence enabled
- [ ] Encryption at rest enabled
- [ ] Database credentials rotated

### Security Settings
- [ ] HTTPS enforced (HTTP → HTTPS redirect)
- [ ] CORS configured with specific origins (NO wildcards)
- [ ] Rate limiting enabled and tested
- [ ] Security headers verified (use securityheaders.com)
- [ ] Session storage is Redis (NOT in-memory)
- [ ] CSRF protection enabled for state-changing operations

### Monitoring & Logging
- [ ] Sentry error tracking enabled
- [ ] Audit logging to database/SIEM enabled
- [ ] Rate limit violations logged
- [ ] Authentication failures logged
- [ ] Uptime monitoring configured
- [ ] Performance monitoring enabled

### Testing
- [ ] Security tests passing (`pytest tests/test_security.py`)
- [ ] Rate limiting tested
- [ ] Authentication tested
- [ ] GDPR endpoints tested
- [ ] Load testing completed
- [ ] Penetration testing completed (if major release)

### Documentation
- [ ] API documentation updated
- [ ] Environment variables documented
- [ ] Deployment runbook updated
- [ ] Incident response plan reviewed

### Dependencies
- [ ] All dependencies updated to latest secure versions
- [ ] No known vulnerabilities in dependencies (`pip audit`)
- [ ] Dependency lock file committed (`requirements.txt` or `poetry.lock`)

---

## 🔌 BEFORE ADDING NEW ENDPOINTS

### Design
- [ ] Endpoint follows RESTful principles
- [ ] Minimum data exposed (principle of least privilege)
- [ ] Authentication required if handling sensitive data
- [ ] Authorization checks implemented (user can only access their data)

### Input Validation
- [ ] All path parameters validated with regex
- [ ] All query parameters validated
- [ ] Request body validated with Pydantic models
- [ ] File uploads have size limits
- [ ] File uploads have type validation

### Security
- [ ] Rate limiting configured for this endpoint
- [ ] Input sanitization applied
- [ ] Output encoding applied (prevent XSS)
- [ ] CSRF protection if state-changing (POST/PUT/DELETE)
- [ ] SQL injection prevention (using ORM)

### GDPR Compliance
- [ ] Data minimization (only collect necessary data)
- [ ] Purpose of data collection documented
- [ ] Consent obtained if collecting personal data
- [ ] Retention period defined
- [ ] Data can be exported
- [ ] Data can be deleted

### Testing
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Security tests written (injection, XSS, etc.)
- [ ] Edge cases tested (empty input, max length, etc.)
- [ ] Error handling tested

### Documentation
- [ ] OpenAPI/Swagger docs auto-generated
- [ ] Request/response examples provided
- [ ] Error codes documented
- [ ] Authentication requirements documented

---

## 👤 BEFORE HANDLING USER DATA

### Collection
- [ ] **Explicit consent obtained** via checkbox (not pre-checked)
- [ ] Purpose of data collection explained
- [ ] Legal basis documented (consent, legitimate interest, contract)
- [ ] Data minimization applied (only collect what's needed)
- [ ] Retention period defined and communicated

### Storage
- [ ] Sensitive data encrypted at rest
- [ ] Database credentials secured
- [ ] Access controls implemented (role-based)
- [ ] Audit logging enabled for data access
- [ ] Regular backups enabled

### Processing
- [ ] Data anonymized/pseudonymized when possible
- [ ] Processing purpose documented
- [ ] Third-party processors have DPA (Data Processing Agreement)
- [ ] Data transfers comply with GDPR (if EU data)

### Access
- [ ] Authentication required to access data
- [ ] Authorization checks (users can only access own data)
- [ ] Audit log of who accessed what data
- [ ] Admin access requires MFA (multi-factor authentication)

### Export (Right to Access)
- [ ] User can request data export
- [ ] Export in machine-readable format (JSON)
- [ ] Export includes all user data
- [ ] Export rate-limited (prevent abuse)
- [ ] Export logged for audit

### Deletion (Right to Erasure)
- [ ] User can request data deletion
- [ ] Deletion removes all user data
- [ ] Deletion is permanent (not soft delete for GDPR)
- [ ] Deletion logged for audit
- [ ] Confirmation required before deletion
- [ ] Admin approval required for mass deletions

### Breach Response
- [ ] Data breach detection in place
- [ ] Incident response plan documented
- [ ] Notification procedure defined (72 hours for GDPR)
- [ ] Contact information for DPO (Data Protection Officer) or legal

---

## 🔒 SECURITY CODE REVIEW CHECKLIST

Use this checklist when reviewing pull requests:

### General
- [ ] No secrets in code (API keys, passwords, tokens)
- [ ] No commented-out code with TODOs
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include sensitive data

### Authentication & Authorization
- [ ] Authentication required for protected endpoints
- [ ] Authorization checks for user-specific data
- [ ] Password hashing uses bcrypt
- [ ] Timing-safe comparison for secrets
- [ ] Rate limiting on auth endpoints

### Input Validation
- [ ] All user input validated
- [ ] Regex patterns are whitelist-based
- [ ] Maximum lengths enforced
- [ ] Pydantic models used for request validation

### Database
- [ ] Using ORM (SQLAlchemy)
- [ ] No raw SQL with string concatenation
- [ ] Transactions used where needed
- [ ] Proper error handling

### API Security
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Request size limits set
- [ ] Security headers added

### Testing
- [ ] Tests include security scenarios
- [ ] Edge cases covered
- [ ] Error handling tested

---

## 🚨 INCIDENT RESPONSE CHECKLIST

If a security vulnerability is discovered:

### Immediate (Within 1 hour)
- [ ] Assess severity (Critical, High, Medium, Low)
- [ ] Contain the breach (disable affected endpoint if needed)
- [ ] Notify security team/lead developer
- [ ] Create incident ticket

### Short-term (Within 24 hours)
- [ ] Develop fix
- [ ] Test fix thoroughly
- [ ] Deploy fix to production
- [ ] Verify fix is working
- [ ] Document the incident

### Medium-term (Within 72 hours)
- [ ] Assess impact (which users affected)
- [ ] Notify affected users if data breach
- [ ] Notify authorities if required (GDPR: 72 hours)
- [ ] Update LESSONS_LEARNED.md
- [ ] Add pre-commit hook to prevent recurrence

### Long-term (Within 1 week)
- [ ] Post-mortem meeting
- [ ] Update security training
- [ ] Review similar code for same vulnerability
- [ ] Implement automated detection
- [ ] Update security checklist

---

## 📊 SECURITY METRICS TO TRACK

Monitor these metrics regularly:

### Authentication
- Failed login attempts per hour
- Account lockouts per day
- Average session duration
- Suspicious login patterns

### Rate Limiting
- Rate limit violations per endpoint
- Blocked IPs count
- Automated scanner detections

### Data Access
- GDPR export requests per day
- GDPR deletion requests per day
- Admin data access events
- Unusual data access patterns

### Errors
- Authentication errors
- Authorization errors
- Validation errors
- Server errors (500s)

---

## 🎓 SECURITY TRAINING REQUIREMENTS

All developers must:
- [ ] Read LESSONS_LEARNED.md
- [ ] Complete OWASP Top 10 training
- [ ] Review this checklist before every commit
- [ ] Attend quarterly security review meetings
- [ ] Report any security concerns immediately

---

## 📞 WHO TO CONTACT

- **Security Issues:** [Security Team Email/Slack]
- **GDPR Questions:** [DPO/Legal Team]
- **Incident Response:** [On-call Rotation]
- **Code Review:** [Lead Developer]

---

## ✅ QUICK PRE-COMMIT CHECKLIST

Run through this before every commit:

1. [ ] No secrets in code
2. [ ] All input validated
3. [ ] CORS not set to wildcard
4. [ ] Using bcrypt for passwords
5. [ ] Rate limiting on new endpoints
6. [ ] Tests passing
7. [ ] No debugging code

**If you can't check all boxes, DO NOT COMMIT.**

---

**Last Updated:** 2026-03-07
**Version:** 1.0
