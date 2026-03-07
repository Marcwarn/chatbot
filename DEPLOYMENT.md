# 🚀 Deployment Guide - Production Deployment

## Table of Contents
- [Overview](#overview)
- [Vercel Deployment](#vercel-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Testing Checklist](#testing-checklist)
- [Security Checklist](#security-checklist)
- [Monitoring Setup](#monitoring-setup)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the Persona Assessment Platform to **Vercel** with PostgreSQL database.

### Prerequisites

✅ **Required:**
- Vercel account (free tier works)
- GitHub account
- Anthropic API key (Claude AI)
- Domain name (optional)

✅ **Recommended:**
- Sentry account (error monitoring)
- Vercel Pro (for production apps)
- PostgreSQL database (Vercel Postgres or external)

---

## Vercel Deployment

### Step 1: Prepare Repository

**1.1 Ensure vercel.json is configured:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "big-five-demo.html",
      "use": "@vercel/static"
    },
    {
      "src": "admin.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/admin",
      "dest": "/admin.html"
    },
    {
      "src": "/",
      "dest": "/big-five-demo.html"
    }
  ]
}
```

**1.2 Check requirements.txt:**

```txt
fastapi==0.104.1
uvicorn==0.24.0
anthropic==0.7.7
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
mangum==0.17.0
bcrypt==4.1.1
sentry-sdk==1.38.0
```

---

### Step 2: Deploy to Vercel

**2.1 Install Vercel CLI:**

```bash
npm install -g vercel
```

**2.2 Login to Vercel:**

```bash
vercel login
```

**2.3 Deploy from CLI:**

```bash
# Link project (first time)
vercel

# Deploy to production
vercel --prod
```

**OR Deploy via GitHub:**

1. Push code to GitHub
2. Go to https://vercel.com/new
3. Import your GitHub repository
4. Configure environment variables (see next section)
5. Click "Deploy"

---

### Step 3: Configure Project Settings

**In Vercel Dashboard:**

1. Go to **Settings** → **General**
2. Set **Framework Preset:** Other
3. Set **Build Command:** (leave empty)
4. Set **Output Directory:** (leave empty)
5. Set **Install Command:** `pip install -r requirements.txt`

---

## Environment Variables

### Required Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

#### 1. ANTHROPIC_API_KEY
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx
```

**Where to get:**
1. Go to https://console.anthropic.com/
2. Create account / Login
3. Go to API Keys
4. Create new key
5. Copy and paste

**Cost:** Pay-as-you-go (approx $0.01 per assessment)

---

#### 2. ADMIN_PASSWORD_HASH
```bash
ADMIN_PASSWORD_HASH=240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
```

**Generate hash:**

```python
import hashlib

password = "your_secure_password_here"
hash = hashlib.sha256(password.encode()).hexdigest()
print(hash)
```

Or use online tool: https://emn178.github.io/online-tools/sha256.html

**Security:** Use a strong password (16+ characters, mixed case, numbers, symbols)

---

#### 3. ADMIN_API_KEY
```bash
ADMIN_API_KEY=admin_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Generate secure key:**

```python
import secrets
print(f"admin_{secrets.token_urlsafe(32)}")
```

Or use: `openssl rand -base64 32`

---

#### 4. ALLOWED_ORIGINS
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com
```

**Format:** Comma-separated list of allowed domains

**Examples:**
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
ALLOWED_ORIGINS=https://persona-app.vercel.app,https://app.persona.com

# Multiple domains
ALLOWED_ORIGINS=https://app.persona.com,https://beta.persona.com,https://admin.persona.com
```

**Security:** Never use wildcard `*` in production!

---

#### 5. DATABASE_URL
```bash
DATABASE_URL=postgres://user:password@host:5432/dbname
```

**Vercel Postgres:**

1. Go to Vercel Dashboard → Storage
2. Create Postgres Database
3. Copy `POSTGRES_URL` from .env tab
4. Paste as `DATABASE_URL`

**External PostgreSQL:**

Format: `postgresql://user:password@host:port/database`

Example:
```bash
DATABASE_URL=postgresql://dbuser:securepass@db.example.com:5432/persona_db
```

**Important:**
- Vercel uses `postgres://` prefix
- SQLAlchemy needs `postgresql://` prefix
- The code auto-converts this (see database.py)

---

### Optional Variables

#### 6. SENTRY_DSN (Recommended)
```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

**Setup:**
1. Create account at https://sentry.io
2. Create new Python project
3. Copy DSN from Settings
4. Add to Vercel environment variables

**Benefit:** Automatic error tracking and alerting

---

#### 7. ENVIRONMENT
```bash
ENVIRONMENT=production
```

**Values:** `development`, `staging`, `production`

**Effect:**
- Controls logging verbosity
- Enables/disables debug features
- Affects error messages

---

### Setting Environment Variables in Vercel

**Via Dashboard:**

1. Go to Project → Settings → Environment Variables
2. Click "Add New"
3. Enter Name and Value
4. Select environments: Production, Preview, Development
5. Click "Save"

**Via CLI:**

```bash
# Set single variable
vercel env add ANTHROPIC_API_KEY

# Set from file
vercel env pull .env.production
```

---

## Database Setup

### Option 1: Vercel Postgres (Recommended)

**Pros:**
- Fully managed
- Automatic backups
- Low latency (same region as app)
- Free tier available

**Setup:**

1. **Create Database:**
   - Go to Vercel Dashboard → Storage
   - Click "Create Database"
   - Select "Postgres"
   - Choose region (same as your app)
   - Click "Create"

2. **Get Connection String:**
   - Click on your database
   - Go to ".env.local" tab
   - Copy `POSTGRES_URL`

3. **Add to Project:**
   - Go to Project → Settings → Environment Variables
   - Add `DATABASE_URL` with the connection string
   - Select "Production" environment
   - Save

4. **Initialize Schema:**

```bash
# SSH into Vercel function
vercel env pull .env.production
python database.py
```

Or run migration endpoint:
```bash
curl -X POST https://your-app.vercel.app/api/v1/admin/migrate \
  -H "Authorization: Bearer $ADMIN_API_KEY"
```

---

### Option 2: External PostgreSQL

**Providers:**
- **Supabase** (Free tier, 500MB)
- **Railway** (Free tier, 1GB)
- **Neon** (Free tier, 3GB)
- **AWS RDS** (Paid, highly scalable)

**Setup Example (Supabase):**

1. **Create Database:**
   - Go to https://supabase.com
   - Create new project
   - Wait for database provisioning

2. **Get Connection String:**
   - Go to Project Settings → Database
   - Copy "Connection string" (URI format)
   - Replace `[YOUR-PASSWORD]` with your password

3. **Add to Vercel:**
   - Format: `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`
   - Add as `DATABASE_URL` environment variable

4. **Initialize Schema:**
   - Run `database.py` locally with connection string
   - Or use migration endpoint

---

### Database Migration

**Run migrations on first deployment:**

```python
# database.py (run once)
from database import db

db.create_tables()
print("✅ Tables created!")
```

**Or via API endpoint (if implemented):**

```bash
curl -X POST https://your-app.vercel.app/api/v1/admin/migrate \
  -H "Authorization: Bearer $ADMIN_API_KEY"
```

---

### Database Backup

**Vercel Postgres:**
- Automatic daily backups (Pro plan)
- Point-in-time recovery (last 7 days)

**Manual backup:**

```bash
# Export data
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore data
psql $DATABASE_URL < backup_20240307.sql
```

**Automated backups (cron):**

```bash
# Add to crontab
0 2 * * * pg_dump $DATABASE_URL > /backups/persona_$(date +\%Y\%m\%d).sql
```

---

## Testing Checklist

### Pre-Deployment Tests

Run these tests **before** deploying to production:

**✅ 1. Local Testing:**

```bash
# Start local server
uvicorn api_main_gdpr:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/assessment/types

# Run test suite
pytest tests/
```

---

**✅ 2. Environment Variables:**

```bash
# Check all required vars are set
vercel env ls

# Verify values (don't print secrets!)
echo "Checking DATABASE_URL..." && [[ -n "$DATABASE_URL" ]] && echo "✓ Set"
echo "Checking ANTHROPIC_API_KEY..." && [[ -n "$ANTHROPIC_API_KEY" ]] && echo "✓ Set"
echo "Checking ADMIN_API_KEY..." && [[ -n "$ADMIN_API_KEY" ]] && echo "✓ Set"
```

---

**✅ 3. Database Connection:**

```python
# Test database connectivity
from database import db

try:
    session = db.get_session()
    session.execute("SELECT 1")
    print("✅ Database connected")
except Exception as e:
    print(f"❌ Database error: {e}")
```

---

**✅ 4. AI API Test:**

```python
# Test Anthropic API
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

try:
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("✅ Anthropic API working")
except Exception as e:
    print(f"❌ Anthropic API error: {e}")
```

---

### Post-Deployment Tests

After deploying to Vercel:

**✅ 1. Health Check:**

```bash
curl https://your-app.vercel.app/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

---

**✅ 2. API Endpoints:**

```bash
# Test assessment types
curl https://your-app.vercel.app/api/v1/assessment/types

# Test Big Five start
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 10
  }'

# Test DISC start
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "assessment_type": "disc",
    "language": "sv",
    "num_questions": 12
  }'
```

---

**✅ 3. CORS Test:**

```javascript
// Run in browser console on your frontend domain
fetch('https://your-app.vercel.app/api/v1/assessment/types')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);

// Should succeed if ALLOWED_ORIGINS is configured correctly
```

---

**✅ 4. Admin Access:**

```bash
# Test admin login
curl -X POST https://your-app.vercel.app/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your_admin_password"}'

# Test admin stats
curl https://your-app.vercel.app/api/v1/admin/stats \
  -H "Authorization: Bearer $ADMIN_API_KEY"
```

---

**✅ 5. GDPR Endpoints:**

```bash
# Test consent
curl -X POST https://your-app.vercel.app/api/v1/gdpr/consent \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "consent_type": "data_processing",
    "consent_given": true,
    "purpose": "Testing",
    "legal_basis": "consent"
  }'
```

---

**✅ 6. Load Testing:**

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 https://your-app.vercel.app/health

# Expected: All requests succeed, <1s response time
```

---

## Security Checklist

### Pre-Production Security Review

**✅ 1. Environment Variables:**
- [ ] No secrets in code (use environment variables)
- [ ] No hardcoded API keys
- [ ] No default passwords
- [ ] Strong admin password (16+ chars)
- [ ] Secure ADMIN_API_KEY (32+ chars random)

---

**✅ 2. CORS Configuration:**
- [ ] `ALLOWED_ORIGINS` set to specific domains
- [ ] No wildcard `*` in production
- [ ] HTTPS-only origins
- [ ] Test CORS from browser

---

**✅ 3. Database Security:**
- [ ] Strong database password
- [ ] SSL/TLS enabled for database connections
- [ ] Database not publicly accessible
- [ ] Connection string stored securely
- [ ] Regular backups enabled

---

**✅ 4. API Security:**
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection (output sanitization)
- [ ] CSRF protection (for state-changing operations)

---

**✅ 5. Authentication:**
- [ ] Admin endpoints require authentication
- [ ] Passwords hashed with bcrypt
- [ ] No password in logs or error messages
- [ ] Session timeout configured

---

**✅ 6. GDPR Compliance:**
- [ ] Privacy policy published
- [ ] Consent management working
- [ ] Data export working
- [ ] Data deletion working
- [ ] Audit logging enabled
- [ ] Data retention policies set

---

**✅ 7. Monitoring:**
- [ ] Sentry error tracking configured
- [ ] Security events logged
- [ ] Failed login attempts tracked
- [ ] Rate limit violations logged

---

**✅ 8. HTTPS:**
- [ ] All traffic over HTTPS
- [ ] HTTP redirects to HTTPS
- [ ] HSTS headers enabled
- [ ] Valid SSL certificate

---

### Security Scanning

**Run automated security scan:**

```bash
# Install safety
pip install safety

# Check for vulnerable dependencies
safety check -r requirements.txt

# Expected: No known security vulnerabilities
```

**Run code security scan:**

```bash
# Install bandit
pip install bandit

# Scan Python code
bandit -r . -ll

# Fix any HIGH or MEDIUM severity issues
```

---

## Monitoring Setup

### 1. Sentry Error Monitoring

**Setup:**

```python
# monitoring.py (already included)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        environment=os.getenv("ENVIRONMENT", "production")
    )
```

**Verify:**
1. Deploy with `SENTRY_DSN` set
2. Trigger an error (e.g., call non-existent endpoint)
3. Check Sentry dashboard for error

---

### 2. Vercel Analytics

**Enable:**
1. Go to Project → Analytics
2. Enable Web Analytics
3. Add Vercel Analytics script to frontend

**Metrics:**
- Page views
- Unique visitors
- Core Web Vitals
- API response times

---

### 3. Database Monitoring

**Vercel Postgres:**
- Built-in metrics dashboard
- CPU, Memory, Connections
- Query performance

**External DB:**
- Use provider's monitoring (Supabase, Railway, etc.)
- Or set up custom monitoring with Prometheus

---

### 4. Custom Alerts

**Set up alerts for:**

```python
# Example: Alert on high error rate
from monitoring import alert_high_error_rate

# In your error handler
if error_rate > 0.1:  # 10% errors
    alert_high_error_rate(
        error_rate=error_rate,
        time_window="5min"
    )
```

**Alert channels:**
- Email (Sentry)
- Slack (Sentry webhook)
- PagerDuty (for critical issues)

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error

**Problem:** Python module not installed

**Solution:**
```bash
# Add missing module to requirements.txt
echo "module-name==version" >> requirements.txt

# Redeploy
vercel --prod
```

---

#### 2. Database Connection Fails

**Problem:** Can't connect to database

**Debug:**
```python
import os
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:30]}...")

# Check if URL starts with postgresql:// not postgres://
url = os.getenv('DATABASE_URL')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
    print(f"Converted to: {url[:30]}...")
```

**Solutions:**
- Verify `DATABASE_URL` is set in Vercel
- Check database is accessible (not IP restricted)
- Verify credentials are correct

---

#### 3. CORS Errors

**Problem:** Frontend can't call API

**Symptoms:**
```
Access to fetch at 'https://api...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Solution:**
```bash
# Verify ALLOWED_ORIGINS includes your frontend domain
vercel env ls | grep ALLOWED_ORIGINS

# Add frontend domain
vercel env add ALLOWED_ORIGINS
# Enter: https://your-frontend.vercel.app,https://app.yourdomain.com
```

---

#### 4. AI Analysis Fails

**Problem:** Claude API returns error

**Debug:**
```python
import os
from anthropic import Anthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API key set: {bool(api_key)}")
print(f"API key starts with: {api_key[:10] if api_key else 'NONE'}...")

client = Anthropic(api_key=api_key)
# Try a test call
```

**Solutions:**
- Verify API key is valid
- Check Anthropic account has credits
- Check rate limits not exceeded

---

#### 5. Admin Login Fails

**Problem:** Can't login to admin panel

**Debug:**
```python
import hashlib

password = "your_password"
hash = hashlib.sha256(password.encode()).hexdigest()
print(f"Hash: {hash}")

# Compare with ADMIN_PASSWORD_HASH in Vercel
```

**Solutions:**
- Verify password hash is correct
- Regenerate hash if needed
- Check ADMIN_PASSWORD_HASH is set in Vercel

---

#### 6. Slow Response Times

**Problem:** API takes too long to respond

**Debug:**
```bash
# Time API call
time curl https://your-app.vercel.app/api/v1/assessment/start \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","assessment_type":"big_five","language":"sv"}'
```

**Solutions:**
- Check database query performance
- Add database indexes
- Enable Redis caching
- Optimize AI prompts (reduce max_tokens)
- Consider upgrading Vercel plan (Pro has better performance)

---

### Logs & Debugging

**View Vercel logs:**

```bash
# Real-time logs
vercel logs --follow

# Last 100 logs
vercel logs

# Filter by function
vercel logs api/index.py
```

**Check Sentry for errors:**
1. Go to https://sentry.io
2. Select your project
3. View recent errors
4. Click error for stack trace

---

## Performance Optimization

### 1. Enable Caching

**Add Redis caching:**

```python
# Install redis
pip install redis

# Add to requirements.txt
redis==5.0.1

# Configure in code (caching.py)
import redis
import os

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379")
)
```

---

### 2. Database Optimization

**Add indexes:**

```sql
-- Add index on assessment_id for faster lookups
CREATE INDEX idx_assessment_id ON assessments(id);
CREATE INDEX idx_user_id ON assessments(user_id);
CREATE INDEX idx_assessment_type ON assessments(assessment_type);
```

**Connection pooling:**

```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Connections to keep open
    max_overflow=40,     # Extra connections when needed
    pool_pre_ping=True   # Check connection health
)
```

---

### 3. CDN for Static Assets

**Vercel automatically CDNs:**
- HTML files
- CSS files
- JavaScript files
- Images

**No configuration needed!**

---

## Rollback Plan

**If deployment fails:**

```bash
# Rollback to previous deployment
vercel rollback
```

**Or via dashboard:**
1. Go to Deployments
2. Find previous working deployment
3. Click "⋮" → "Promote to Production"

---

## Production Launch Checklist

**Final checks before going live:**

- [ ] All environment variables set
- [ ] Database initialized with schema
- [ ] CORS configured for frontend domain
- [ ] Admin password changed from default
- [ ] Sentry error tracking working
- [ ] All tests passing
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] GDPR endpoints tested
- [ ] Backup system configured
- [ ] Monitoring alerts set up
- [ ] Documentation updated
- [ ] Team trained on admin panel
- [ ] Support email configured
- [ ] Privacy policy published
- [ ] Terms of service published

---

**🎉 Congratulations! Your app is production-ready!**

---

**Last Updated:** March 7, 2026
**Version:** 1.0.0
**Maintainer:** Persona Platform Team
