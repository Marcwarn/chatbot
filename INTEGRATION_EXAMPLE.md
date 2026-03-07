# Security Monitoring Integration Examples

Quick copy-paste examples for integrating security monitoring into your existing API.

## 1. Add to Main API File (`api_main_gdpr.py`)

### Import Security Modules

Add these imports at the top of your file:

```python
# Security monitoring imports
from api_security import router as security_router
from monitoring import comprehensive_security_middleware, init_sentry
from security_integration import (
    LoginMonitor,
    validate_input_security,
    inspect_request_security,
    DataExportMonitor
)
```

### Initialize Sentry (Already Done)

The monitoring system is already initialized in your code:
```python
init_sentry()  # Already present in api_main_gdpr.py
```

### Add Security Router

Add after your other routers:

```python
# Add security monitoring router
app.include_router(security_router)
```

### Add Security Middleware

Add after other middleware:

```python
# Add comprehensive security middleware
app.middleware("http")(comprehensive_security_middleware)
```

## 2. Protect Login Endpoint (`api_admin.py`)

Update your login endpoint to monitor for brute force:

```python
from security_integration import LoginMonitor

@router.post("/login")
async def admin_login(req: LoginRequest, request: Request):
    """Admin login with brute force protection"""

    client_ip = request.client.host if request.client else "unknown"

    # Verify password
    success = verify_password(req.password, ADMIN_PASSWORD_HASH)

    # Log login attempt (auto-detects brute force)
    await LoginMonitor.log_login_attempt(
        client_ip=client_ip,
        endpoint="/api/admin/login",
        success=success,
        username="admin"  # or req.username if you have one
    )

    if not success:
        raise HTTPException(status_code=401, detail="Invalid password")

    # Generate session token
    session_token = secrets.token_urlsafe(32)
    # ... rest of your login logic
```

## 3. Protect Chat Endpoint

Add input validation to detect SQL injection and XSS:

```python
from security_integration import validate_input_security

@app.post("/api/v1/chat", response_model=ChatResponse)
async def personality_coach_chat(req: ChatRequest, request: Request):
    """Chat with security input validation"""

    client_ip = request.client.host if request.client else "unknown"

    # Validate input for attacks (SQL injection, XSS, etc.)
    await validate_input_security(
        input_data=req.message,
        client_ip=client_ip,
        endpoint="/api/v1/chat"
    )

    # ... rest of your chat logic
```

## 4. Monitor GDPR Data Exports

Add to your GDPR export endpoint:

```python
from security_integration import DataExportMonitor
import json

@router.post("/export", response_model=DataExportResponse)
async def export_user_data(request: DataExportRequest, req: Request):
    """GDPR export with exfiltration monitoring"""

    client_ip = req.client.host if req.client else "unknown"

    # ... your export logic
    user_data = get_user_data(request.user_id)

    # Monitor for mass data exfiltration
    data_size = len(json.dumps(user_data))
    await DataExportMonitor.log_export(
        client_ip=client_ip,
        endpoint="/api/v1/gdpr/export",
        data_size=data_size,
        export_type="gdpr_export"
    )

    return DataExportResponse(data=user_data, ...)
```

## 5. Add Assessment Input Validation

Protect assessment endpoints:

```python
from security_integration import validate_input_security

@app.post("/api/v1/assessment/start", response_model=AssessmentStartResponse)
async def start_assessment(req: StartAssessmentRequest, request: Request):
    """Start assessment with input validation"""

    client_ip = request.client.host if request.client else "unknown"

    # Validate user_id if provided
    if req.user_id:
        await validate_input_security(
            input_data=req.user_id,
            client_ip=client_ip,
            endpoint="/api/v1/assessment/start"
        )

    # Validate email if provided
    if req.email:
        await validate_input_security(
            input_data=req.email,
            client_ip=client_ip,
            endpoint="/api/v1/assessment/start"
        )

    # ... rest of your assessment logic
```

## 6. Complete api_main_gdpr.py Integration

Here's the complete set of changes for `api_main_gdpr.py`:

```python
# Add these imports
from api_security import router as security_router
from monitoring import comprehensive_security_middleware
from security_integration import (
    LoginMonitor,
    validate_input_security,
    DataExportMonitor
)

# After other routers
app.include_router(security_router)

# After other middleware
app.middleware("http")(comprehensive_security_middleware)

# In your chat endpoint
@app.post("/api/v1/chat", response_model=ChatResponse)
async def personality_coach_chat(req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    # Add input validation
    await validate_input_security(
        input_data=req.message,
        client_ip=client_ip,
        endpoint="/api/v1/chat"
    )

    # Rest of existing code...
    if not anthropic_client:
        raise HTTPException(...)

    # ... etc
```

## 7. Complete api_admin.py Integration

Add to `api_admin.py`:

```python
# Add import
from security_integration import LoginMonitor

# Update login endpoint
@router.post("/login")
async def admin_login(req: LoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    # Existing password verification
    if not verify_password(req.password, ADMIN_PASSWORD_HASH):
        # Log failed attempt
        await LoginMonitor.log_login_attempt(
            client_ip=client_ip,
            endpoint="/api/admin/login",
            success=False,
            username="admin"
        )
        raise HTTPException(status_code=401, detail="Invalid password")

    # Log successful attempt
    await LoginMonitor.log_login_attempt(
        client_ip=client_ip,
        endpoint="/api/admin/login",
        success=True,
        username="admin"
    )

    # Rest of existing code...
```

## 8. Test Your Integration

### Test Attack Detection

```bash
# Test SQL injection detection
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "SELECT * FROM users--", "conversation_history": []}'

# Expected: 400 Bad Request - Invalid input detected

# Test brute force (run multiple times)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/admin/login \
    -H "Content-Type: application/json" \
    -d '{"password": "wrongpassword"}'
  sleep 1
done

# Expected: 403 Forbidden after 5 attempts
```

### Test Dashboard

```bash
# Access dashboard
open http://localhost:8000/api/admin/security/dashboard

# Get metrics
curl http://localhost:8000/api/admin/security/metrics

# Get security score
curl http://localhost:8000/api/admin/security/score
```

### Test Alerts

```bash
# Send test alert
curl -X POST http://localhost:8000/api/admin/security/test-alert

# Check Slack/Email for notification
```

## 9. Environment Variables

Make sure your `.env` file has:

```bash
# Required
ADMIN_PASSWORD_HASH=<bcrypt-hash>
ANTHROPIC_API_KEY=<your-key>

# Security Monitoring (Optional)
SENTRY_DSN=<your-sentry-dsn>
SLACK_WEBHOOK_URL=<your-slack-webhook>
SMTP_HOST=smtp.gmail.com
SMTP_USER=<your-email>
SMTP_PASSWORD=<your-app-password>
ALERT_TO_EMAILS=admin@example.com

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 10. Verify Everything Works

### Checklist

- [ ] Run setup script: `python setup_security_monitoring.py`
- [ ] Configure .env with at least ADMIN_PASSWORD_HASH
- [ ] Add security router to main API
- [ ] Add security middleware to main API
- [ ] Update login endpoint with LoginMonitor
- [ ] Add input validation to chat endpoint
- [ ] Test SQL injection detection
- [ ] Test brute force protection
- [ ] Access security dashboard
- [ ] Send test alert
- [ ] Review security metrics

### Quick Test Command

```bash
# Start server
uvicorn api_main_gdpr:app --reload

# In another terminal, run tests
./test_security.sh  # (create this script with the test commands above)
```

## 11. Monitor in Production

Once deployed:

1. **Daily**: Check security dashboard
2. **Weekly**: Review weekly security report
3. **Monthly**: Analyze attack patterns
4. **Always**: Respond to critical alerts

### Access Production Dashboard

```
https://yourdomain.com/api/admin/security/dashboard
```

### Get Weekly Report

```bash
curl https://yourdomain.com/api/admin/security/report/weekly
```

## 🎉 You're Done!

Your application now has:
- ✅ Real-time attack detection
- ✅ Auto-blocking malicious IPs
- ✅ Multi-channel alerting
- ✅ Security analytics dashboard
- ✅ Comprehensive monitoring

**Security is now visible and actionable!** 🛡️
