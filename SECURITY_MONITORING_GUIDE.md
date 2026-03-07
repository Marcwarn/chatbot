# Security Monitoring & Alerting System

Complete real-time security monitoring and threat detection system for your application.

## 🛡️ Features

### Attack Detection
- **Brute Force Detection**: Monitors failed login attempts and auto-blocks aggressive attackers
- **SQL Injection Detection**: Pattern matching for SQL injection attempts
- **XSS Detection**: Identifies cross-site scripting attempts in user inputs
- **DoS Detection**: Rate-based detection for denial-of-service attacks
- **Data Exfiltration Detection**: Monitors mass data exports
- **Scanner Detection**: Identifies automated security scanners
- **Honeypot Traps**: Detects bots accessing non-existent endpoints

### Alerting System
- **Slack Notifications**: Real-time alerts to Slack channels
- **Email Alerts**: Email notifications for critical events
- **Sentry Integration**: Critical events sent to Sentry
- **Incident Reports**: Auto-generated detailed incident reports
- **Severity Levels**: Low, Medium, High, Critical

### Auto-blocking
- **Temporary IP Blocks**: Automatic temporary blocking based on threat severity
- **Permanent Blocks**: Option for permanent IP blocks
- **Configurable Durations**: Customizable block durations per attack type
- **Auto-unblock**: Expired blocks automatically removed

### Monitoring Dashboard
- **Real-time Security Events Feed**: Live stream of security events
- **Failed Login Chart**: Visualize brute force patterns
- **Rate Limit Violations Chart**: Track DoS attempts
- **Security Score**: Overall security health score (0-100)
- **Blocked IPs List**: Currently blocked IP addresses
- **Auto-refresh**: Real-time updates every 5 seconds

### Analytics & Reporting
- **Security Score**: 0-100 grade with trend analysis
- **Attack Pattern Analysis**: Detect coordinated and distributed attacks
- **Weekly Reports**: Comprehensive weekly security summaries
- **Metrics Export**: JSON export for external analytics
- **Trend Analysis**: Compare current vs. previous periods

## 📁 File Structure

```
/home/user/chatbot/
├── monitoring.py                    # Core attack detection & rate limiting
├── alerts.py                        # Multi-channel alerting system
├── metrics.py                       # Security analytics & reporting
├── api_security.py                  # Security API endpoints
├── security_integration.py          # Integration helpers
├── security_dashboard.html          # Real-time monitoring dashboard
├── database.py                      # Enhanced with security models
└── SECURITY_MONITORING_GUIDE.md     # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

Already included in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Dependencies:
- `sentry-sdk[fastapi]` - Error tracking & alerts
- `httpx` - Async HTTP client for webhooks
- `bcrypt` - Secure password hashing

### 2. Configure Environment Variables

Create/update `.env` file:

```bash
# Sentry (Optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production

# Slack Alerts (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Alerts (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM_EMAIL=security@yourdomain.com
ALERT_TO_EMAILS=admin@yourdomain.com,security@yourdomain.com

# Admin API (Required)
ADMIN_PASSWORD_HASH=<bcrypt-hash-of-your-password>
```

### 3. Update Main API File

Add to `api_main_gdpr.py`:

```python
from api_security import router as security_router
from monitoring import comprehensive_security_middleware

# Add security router
app.include_router(security_router)

# Add comprehensive security middleware
app.middleware("http")(comprehensive_security_middleware)
```

### 4. Initialize Database

Run database migrations to create security tables:

```bash
python -c "from database import db; db.create_tables()"
```

This creates:
- `security_events` - Log all security events
- `blocked_ips` - Track blocked IP addresses
- `security_metrics` - Aggregated metrics
- `incident_reports` - Major incident reports

### 5. Access Security Dashboard

Navigate to:
```
http://localhost:8000/api/admin/security/dashboard
```

## 🎯 Usage Examples

### Integrate Login Monitoring

```python
from security_integration import LoginMonitor

@app.post("/api/admin/login")
async def admin_login(request: Request, credentials: LoginRequest):
    client_ip = request.client.host

    # Verify credentials
    success = verify_credentials(credentials)

    # Log login attempt (detects brute force)
    await LoginMonitor.log_login_attempt(
        client_ip=client_ip,
        endpoint="/api/admin/login",
        success=success,
        username=credentials.username
    )

    if not success:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"token": generate_token()}
```

### Validate User Input

```python
from security_integration import validate_input_security

@app.post("/api/v1/chat")
async def chat(request: Request, message: str):
    client_ip = request.client.host

    # Validate input for SQL injection, XSS, etc.
    await validate_input_security(
        input_data=message,
        client_ip=client_ip,
        endpoint="/api/v1/chat"
    )

    # Process message
    return {"response": process_chat(message)}
```

### Monitor Data Exports

```python
from security_integration import DataExportMonitor

@app.post("/api/v1/gdpr/export")
async def export_data(request: Request, user_id: str):
    client_ip = request.client.host

    # Generate export
    data = generate_export(user_id)
    data_size = len(json.dumps(data))

    # Monitor for mass exfiltration
    await DataExportMonitor.log_export(
        client_ip=client_ip,
        endpoint="/api/v1/gdpr/export",
        data_size=data_size,
        export_type="gdpr_export"
    )

    return data
```

### Request Inspection

```python
from security_integration import inspect_request_security

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Comprehensive security inspection
    await inspect_request_security(request)

    response = await call_next(request)
    return response
```

## 📊 API Endpoints

### Get Security Metrics
```
GET /api/admin/security/metrics?hours=24
```
Returns comprehensive security metrics for dashboard.

### Get Security Events
```
GET /api/admin/security/events?hours=24&event_type=brute_force&limit=100
```
Retrieve recent security events with filtering.

### Get Blocked IPs
```
GET /api/admin/security/blocked-ips
```
List all currently blocked IP addresses.

### Block IP (Manual)
```
POST /api/admin/security/block-ip
{
  "ip_address": "192.168.1.100",
  "reason": "Manual block - suspicious activity",
  "duration_seconds": 3600,
  "is_permanent": false
}
```

### Unblock IP
```
POST /api/admin/security/unblock-ip
{
  "ip_address": "192.168.1.100"
}
```

### Get Security Score
```
GET /api/admin/security/score?hours=24
```
Returns security score (0-100) with grade and trend.

### Get Attack Patterns
```
GET /api/admin/security/patterns?hours=24
```
Analyze and return detected attack patterns.

### Generate Weekly Report
```
GET /api/admin/security/report/weekly
```
Generate comprehensive weekly security report.

### Export Metrics (JSON)
```
GET /api/admin/security/export/json?hours=24
```
Export security metrics in JSON format.

### Test Alerts
```
POST /api/admin/security/test-alert
```
Send test alert to verify notification channels.

## 🔔 Alert Configuration

### Slack Setup

1. Create a Slack webhook:
   - Go to https://api.slack.com/apps
   - Create new app → Incoming Webhooks
   - Add to workspace and copy webhook URL

2. Add to `.env`:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

### Email Setup

For Gmail:
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

### Sentry Setup

1. Create Sentry project: https://sentry.io
2. Copy DSN
3. Add to `.env`:
   ```
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

## 📈 Security Score

The security score (0-100) is calculated based on:

- **SQL Injection**: -10 points per attempt
- **XSS Attempt**: -8 points per attempt
- **Brute Force**: -5 points per attempt
- **Data Exfiltration**: -15 points per attempt (critical)
- **DoS Attempt**: -3 points per attempt
- **Scanner Detection**: -2 points per detection
- **Honeypot Triggered**: -4 points per trigger

**Grades:**
- A+ (95-100): Excellent security
- A (90-94): Very good
- B+ (85-89): Good
- B (80-84): Acceptable
- C+ (75-79): Needs improvement
- C (70-74): Concerning
- D (60-69): Poor
- F (0-59): Critical issues

## 🎨 Customization

### Adjust Block Durations

Edit `alerts.py`:

```python
self.block_rules = {
    "brute_force": {"duration": 7200, "threshold": 3},  # 2 hours after 3 attempts
    "sql_injection": {"duration": 172800, "threshold": 1},  # 48 hours
    # ... customize as needed
}
```

### Adjust Rate Limits

Edit `monitoring.py`:

```python
self.limits = {
    "/api/admin/login": {"calls": 3, "period": 300},  # 3 per 5 min
    "/api/v1/chat": {"calls": 30, "period": 60},      # 30 per minute
    # ... customize as needed
}
```

### Add Custom Attack Patterns

Edit `monitoring.py`:

```python
# Add to SQL patterns
self.sql_patterns.append(r"your_custom_pattern")

# Add to XSS patterns
self.xss_patterns.append(r"your_custom_pattern")
```

## 🧪 Testing

### Test Attack Detection

```bash
# Test SQL injection detection
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello; DROP TABLE users--"}'

# Test brute force (run multiple times)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/admin/login \
    -H "Content-Type: application/json" \
    -d '{"password": "wrong"}'
done

# Test honeypot
curl http://localhost:8000/wp-admin
```

### Test Alerts

```bash
curl -X POST http://localhost:8000/api/admin/security/test-alert
```

Check Slack/email for test alert.

## 📝 Incident Reports

Incident reports are auto-generated for critical events and saved to:
```
security_reports/incident_<type>_<ip>_<timestamp>.txt
```

Weekly reports saved to:
```
security_reports/weekly_report_<timestamp>.txt
```

## 🔒 Best Practices

1. **Enable All Alert Channels**: Configure Slack, email, and Sentry
2. **Review Dashboard Daily**: Check for patterns and trends
3. **Read Weekly Reports**: Review comprehensive weekly summaries
4. **Adjust Thresholds**: Tune based on your traffic patterns
5. **Whitelist IPs**: Add trusted IPs to bypass checks
6. **Monitor False Positives**: Review blocked IPs regularly
7. **Keep Logs**: Security events are kept for 30 days

## 🚨 Emergency Response

If under active attack:

1. **Check Dashboard**: Identify attack type and source
2. **Block Attackers**: Use manual block for immediate response
3. **Review Patterns**: Use pattern analysis endpoint
4. **Scale Protection**: Adjust rate limits temporarily
5. **Enable WAF**: Consider Cloudflare or AWS WAF
6. **Contact Authorities**: For serious attacks

## 📞 Support

For issues or questions:
- Check logs in `security_reports/`
- Review Sentry for errors
- Test individual components
- Verify environment variables

## 🎉 What You Get

✅ Real-time attack detection and blocking
✅ Multi-channel alerting (Slack/Email/Sentry)
✅ Beautiful security dashboard
✅ Comprehensive analytics and reporting
✅ Auto-generated incident reports
✅ Security score tracking
✅ Pattern analysis for sophisticated attacks
✅ Database persistence for all events
✅ Weekly security summaries
✅ JSON export for external tools

**Your security is now visible and actionable!** 🛡️
