# 🛡️ Security Monitoring & Alerting System

## Overview

A complete, production-ready security monitoring and alerting system that provides real-time attack detection, automatic IP blocking, multi-channel alerts, and comprehensive analytics.

## ✨ What You Get

### Core Features
- ✅ **Real-time Attack Detection** - SQL injection, XSS, brute force, DoS, data exfiltration
- ✅ **Auto-blocking System** - Intelligent IP blocking with configurable rules
- ✅ **Multi-channel Alerts** - Slack, Email, and Sentry notifications
- ✅ **Security Dashboard** - Beautiful real-time monitoring interface
- ✅ **Analytics & Reporting** - Security scores, pattern analysis, weekly reports
- ✅ **Database Persistence** - All events stored for analysis
- ✅ **Easy Integration** - Simple helpers for existing endpoints

## 📁 Files Created

### Core Modules
- `monitoring.py` (Enhanced) - Attack detection & rate limiting
- `alerts.py` (NEW) - Multi-channel alerting system
- `metrics.py` (NEW) - Security analytics & reporting
- `api_security.py` (NEW) - Security API endpoints
- `security_integration.py` (NEW) - Integration helpers
- `security_dashboard.html` (NEW) - Real-time monitoring dashboard
- `database.py` (Enhanced) - Security event models

### Documentation
- `SECURITY_MONITORING_GUIDE.md` - Complete feature documentation
- `SECURITY_SYSTEM_SUMMARY.md` - Detailed technical summary
- `INTEGRATION_EXAMPLE.md` - Copy-paste integration examples
- `setup_security_monitoring.py` - Automated setup wizard

## 🚀 Quick Start (5 minutes)

### 1. Run Setup Script
```bash
python setup_security_monitoring.py
```

This will:
- ✅ Check all required files
- ✅ Verify dependencies
- ✅ Initialize database tables
- ✅ Validate configuration
- ✅ Create reports directory

### 2. Configure Environment Variables

Minimum required in `.env`:
```bash
ADMIN_PASSWORD_HASH=<your-bcrypt-hash>
```

Recommended for full features:
```bash
# Sentry (error tracking)
SENTRY_DSN=https://...@sentry.io/...

# Slack (alerts)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Email (alerts)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
ALERT_TO_EMAILS=admin@example.com
```

### 3. Integrate with Your API

Add to `api_main_gdpr.py`:
```python
from api_security import router as security_router
from monitoring import comprehensive_security_middleware

# Add router
app.include_router(security_router)

# Add middleware
app.middleware("http")(comprehensive_security_middleware)
```

### 4. Start & Access Dashboard
```bash
# Start server
uvicorn api_main_gdpr:app --reload

# Access dashboard
http://localhost:8000/api/admin/security/dashboard
```

## 📊 Key Features Explained

### Attack Detection

**Detects 8+ Attack Types:**
1. **Brute Force** - Failed login monitoring (5 attempts/5min)
2. **SQL Injection** - 11 attack patterns detected
3. **XSS** - 9 attack patterns detected
4. **DoS/DDoS** - Rate-based detection (50 req/min)
5. **Data Exfiltration** - Mass export detection
6. **Scanner Detection** - 10+ security scanners identified
7. **Honeypot Triggers** - Bot detection via fake endpoints
8. **Path Traversal** - Directory traversal attempts

### Auto-blocking Rules

| Attack Type | Block Duration | Threshold |
|------------|----------------|-----------|
| Brute Force | 1 hour | 5 attempts |
| SQL Injection | 24 hours | 1 attempt |
| XSS | 24 hours | 1 attempt |
| DoS | 30 minutes | Detection |
| Scanner | 2 hours | Detection |
| Honeypot | 2 hours | Trigger |

### Alert Channels

**Severity-based routing:**
- **Critical** → Slack + Email + Sentry + Incident Report
- **High** → Slack + Email + Sentry
- **Medium** → Slack + Sentry
- **Low** → Sentry only

### Security Dashboard

Real-time visualization of:
- Failed login attempts (chart)
- Rate limit violations (chart)
- Recent security events (live feed)
- Blocked IPs (with countdown)
- Security score (0-100)
- Active threats counter

Auto-refreshes every 5 seconds!

### Analytics

**Security Score (0-100)**
- Calculated from recent attack events
- Letter grades (A+ to F)
- Trend analysis (improving/stable/degrading)

**Attack Pattern Analysis**
- Coordinated attacks (multiple types from same IP)
- Distributed attacks (same type from multiple IPs)
- Reconnaissance detection (scanner → attack)
- Persistent attackers (long-duration)

**Weekly Reports**
- Comprehensive security summaries
- Attack statistics
- Most targeted endpoints
- Top attacking IPs
- Recommendations

## 🎯 Common Integrations

### Protect Login Endpoint
```python
from security_integration import LoginMonitor

@app.post("/api/admin/login")
async def login(request: Request, credentials: LoginRequest):
    client_ip = request.client.host
    success = verify_credentials(credentials)

    # Log attempt (auto-detects brute force)
    await LoginMonitor.log_login_attempt(
        client_ip=client_ip,
        endpoint="/api/admin/login",
        success=success,
        username=credentials.username
    )

    if not success:
        raise HTTPException(401)

    return {"token": generate_token()}
```

### Validate User Input
```python
from security_integration import validate_input_security

@app.post("/api/v1/chat")
async def chat(request: Request, message: str):
    # Detect SQL injection, XSS, etc.
    await validate_input_security(
        input_data=message,
        client_ip=request.client.host,
        endpoint="/api/v1/chat"
    )

    return {"response": process_message(message)}
```

### Monitor Data Exports
```python
from security_integration import DataExportMonitor

@app.post("/api/gdpr/export")
async def export(request: Request, user_id: str):
    data = generate_export(user_id)

    # Monitor for mass exfiltration
    await DataExportMonitor.log_export(
        client_ip=request.client.host,
        endpoint="/api/gdpr/export",
        data_size=len(json.dumps(data)),
        export_type="gdpr_export"
    )

    return data
```

## 📡 API Endpoints

```bash
# Dashboard & Metrics
GET  /api/admin/security/dashboard          # HTML dashboard
GET  /api/admin/security/metrics            # All metrics for dashboard
GET  /api/admin/security/score              # Security score (0-100)

# Events & Monitoring
GET  /api/admin/security/events             # Recent security events
GET  /api/admin/security/patterns           # Attack pattern analysis
GET  /api/admin/security/blocked-ips        # Currently blocked IPs

# Actions
POST /api/admin/security/block-ip           # Block IP manually
POST /api/admin/security/unblock-ip         # Unblock IP
POST /api/admin/security/test-alert         # Test alert system

# Reports & Export
GET  /api/admin/security/report/weekly      # Generate weekly report
GET  /api/admin/security/export/json        # Export metrics as JSON
```

## 🧪 Testing

### Test Attack Detection
```bash
# SQL injection
curl -X POST http://localhost:8000/api/v1/chat \
  -d '{"message": "SELECT * FROM users--"}'
# Expected: 400 Bad Request

# Brute force (run 6 times)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/admin/login \
    -d '{"password": "wrong"}'
done
# Expected: 403 Forbidden after 5th attempt

# Honeypot
curl http://localhost:8000/wp-admin
# Expected: 404 + IP blocked

# Test alerts
curl -X POST http://localhost:8000/api/admin/security/test-alert
# Expected: Alert sent to Slack/Email
```

## 📈 Production Deployment

### Pre-deployment Checklist
- [ ] Configure all environment variables
- [ ] Set up Slack webhook
- [ ] Configure SMTP for emails
- [ ] Add Sentry DSN
- [ ] Set ALLOWED_ORIGINS (not wildcard!)
- [ ] Run database migrations
- [ ] Test all alert channels
- [ ] Review and adjust rate limits
- [ ] Test dashboard access
- [ ] Set up monitoring alerts

### Post-deployment
- Monitor security dashboard daily
- Review weekly reports
- Adjust thresholds based on traffic
- Whitelist legitimate IPs if needed
- Keep alert channels active
- Respond to critical alerts

## 🔧 Customization

### Adjust Block Durations
Edit `alerts.py`:
```python
self.block_rules = {
    "brute_force": {"duration": 7200, "threshold": 3},  # 2 hours
    # ...
}
```

### Change Rate Limits
Edit `monitoring.py`:
```python
self.limits = {
    "/api/admin/login": {"calls": 3, "period": 300},  # 3/5min
    # ...
}
```

### Modify Security Scores
Edit `metrics.py`:
```python
self.weights = {
    "sql_injection": -15,  # More severe
    # ...
}
```

## 📚 Documentation

- **This File** - Quick overview and getting started
- **SECURITY_MONITORING_GUIDE.md** - Complete feature documentation
- **SECURITY_SYSTEM_SUMMARY.md** - Detailed technical summary
- **INTEGRATION_EXAMPLE.md** - Copy-paste integration code
- **SECURITY_QUICK_REFERENCE.md** - Best practices quick reference

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard 404 | Add `app.include_router(security_router)` |
| Not blocking | Add middleware: `app.middleware("http")(...)` |
| No alerts | Check .env for webhook/SMTP settings |
| Database errors | Run `db.create_tables()` |
| Import errors | `pip install -r requirements.txt` |

## 🎉 Success Metrics

You're fully protected when:
- ✅ Dashboard shows real-time events
- ✅ Alerts sent to Slack/Email
- ✅ IPs auto-blocked after attacks
- ✅ Security score calculated
- ✅ Weekly reports generated
- ✅ All tests passing

## 📞 Support

- Check `security_reports/` for logs
- Review Sentry for errors
- Test individual endpoints
- Verify environment variables
- Read full documentation

## 🚀 Next Steps

1. **Run Setup**: `python setup_security_monitoring.py`
2. **Configure .env**: Add at least ADMIN_PASSWORD_HASH
3. **Integrate**: Add router and middleware to main API
4. **Test**: Run attack detection tests
5. **Monitor**: Check dashboard daily
6. **Review**: Read weekly reports

---

**Your application now has enterprise-grade security monitoring!** 🛡️

For detailed documentation, see:
- Setup Guide: `SECURITY_MONITORING_GUIDE.md`
- Integration Examples: `INTEGRATION_EXAMPLE.md`
- Technical Details: `SECURITY_SYSTEM_SUMMARY.md`

**Questions?** Check the documentation or test individual components.

**Everything working?** Congratulations - your security is now visible and actionable! 🎊
