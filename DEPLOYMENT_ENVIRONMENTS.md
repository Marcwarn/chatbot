# Deployment Environments

## Overview

We use two Vercel environments:
- **Production**: persona-assessment.vercel.app (live users)
- **Staging**: persona-assessment-staging.vercel.app (testing)

## Environment Variables

### Production (.env.production)
```bash
# Database
DATABASE_URL=postgresql://prod-db-url

# API Keys
ANTHROPIC_API_KEY=sk-ant-prod-xxx
ADMIN_PASSWORD_HASH=<prod-bcrypt-hash>
ADMIN_API_KEY=<prod-secure-key>

# URLs
ALLOWED_ORIGINS=https://persona-assessment.vercel.app
NEXT_PUBLIC_API_URL=https://persona-assessment.vercel.app/api

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/prod
SENTRY_ENVIRONMENT=production

# Features
ENVIRONMENT=production
DEBUG=false
```

### Staging (.env.staging)
```bash
# Database (separate staging database)
DATABASE_URL=postgresql://staging-db-url

# API Keys (can use same or separate)
ANTHROPIC_API_KEY=sk-ant-staging-xxx
ADMIN_PASSWORD_HASH=<staging-bcrypt-hash>
ADMIN_API_KEY=<staging-secure-key>

# URLs
ALLOWED_ORIGINS=https://persona-assessment-staging.vercel.app
NEXT_PUBLIC_API_URL=https://persona-assessment-staging.vercel.app/api

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/staging
SENTRY_ENVIRONMENT=staging

# Features
ENVIRONMENT=staging
DEBUG=true
```

## Vercel Setup

### 1. Create Two Projects

**Option A: Separate Projects (Recommended)**
- persona-assessment (production)
- persona-assessment-staging (staging)

**Option B: Same Project, Different Branches**
- main branch → Production
- staging branch → Staging Preview

### 2. Configure vercel.json

For production, use `vercel-production.json`:
```json
{
  "version": 2,
  "name": "persona-assessment",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "ENVIRONMENT": "production",
    "DEBUG": "false"
  },
  "functions": {
    "api/index.py": {
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

For staging, use `vercel-staging.json`:
```json
{
  "version": 2,
  "name": "persona-assessment-staging",
  "env": {
    "ENVIRONMENT": "staging",
    "DEBUG": "true"
  }
}
```

### 3. GitHub Integration

#### Staging Deployment Workflow
```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches:
      - staging
      - develop

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel Staging
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          scope: ${{ secrets.VERCEL_SCOPE }}
```

#### Production Deployment Workflow
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run Tests
        run: pytest tests/ -v --cov=.

      - name: Security Scan
        run: python security_scanner.py --json > scan-results.json

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel Production
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROD_PROJECT_ID }}
          vercel-args: '--prod'
```

## Deployment Workflow

### Staging Deployment:
```bash
# 1. Create staging branch (if not exists)
git checkout -b staging

# 2. Make changes
git add .
git commit -m "Feature: Add new assessment"

# 3. Push to staging
git push origin staging

# 4. Vercel auto-deploys to staging URL
# Visit: https://persona-assessment-staging.vercel.app

# 5. Test thoroughly
./test-staging.sh

# 6. If tests pass, merge to main
git checkout main
git merge staging
git push origin main

# 7. Vercel auto-deploys to production
```

### Production Deployment:
```bash
# Option 1: Merge from staging
git checkout main
git merge staging
git push origin main

# Option 2: Direct production deploy (use with caution)
./deploy-production.sh
```

### Database Migrations:

```bash
# Staging database
DATABASE_URL=<staging-url> alembic upgrade head

# Test migration on staging
# Verify data integrity

# Production database (after staging verification)
DATABASE_URL=<production-url> alembic upgrade head
```

## Environment Detection

```python
# config.py
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
IS_STAGING = ENVIRONMENT == "staging"
IS_DEVELOPMENT = ENVIRONMENT == "development"

# Use in code
if IS_PRODUCTION:
    # Production-only features
    # Stricter rate limits
    # Full monitoring
    pass
elif IS_STAGING:
    # Staging-only features
    # Debug tools enabled
    # Relaxed rate limits
    pass
else:
    # Development
    # Full debug output
    pass
```

## Testing Checklist

### Before Deploying to Production:
- [ ] All tests pass on staging
- [ ] Security scan passes
- [ ] Manual testing completed
- [ ] Database migration tested
- [ ] Performance benchmarks acceptable
- [ ] Error monitoring configured
- [ ] Rollback plan ready
- [ ] API keys rotated (if needed)
- [ ] CORS origins configured
- [ ] Rate limits configured

## Monitoring

### Staging Monitoring:
- Sentry errors (staging environment)
- Cost tracking (separate from production)
- Test user data (can be reset)
- Debug logs enabled
- Relaxed rate limits

### Production Monitoring:
- Sentry errors (production environment)
- Real user data (protected)
- Uptime monitoring
- Performance metrics
- Cost alerts
- Security alerts

## Cost Management

### Staging Environment:
- Use lower-tier database (if separate)
- Can use shared API keys (but monitor usage)
- Disable expensive features if needed
- Set lower rate limits
- Use smaller Lambda functions

### Production Environment:
- Full-tier database
- Dedicated API keys
- All features enabled
- Production rate limits
- Optimized Lambda configuration

## Rollback Procedures

### If Production Deploy Fails:

1. **Immediate Rollback**:
   ```bash
   vercel rollback https://persona-assessment.vercel.app
   ```

2. **Git Revert**:
   ```bash
   git revert HEAD
   git push origin main
   ```

3. **Manual Deployment**:
   ```bash
   git checkout <previous-commit>
   vercel --prod
   ```

### Database Rollback:
```bash
# Restore from backup
pg_restore -d production_db backup.sql

# Or rollback migration
alembic downgrade -1
```

## Security Considerations

### Environment Variables:
- Never commit `.env` files
- Use Vercel's environment variable UI
- Rotate API keys regularly
- Use different keys for staging/production

### Secrets Management:
- Store secrets in Vercel dashboard
- Use different secrets for each environment
- Enable Vercel's secret scanning
- Audit access to secrets regularly

### CORS Configuration:
```bash
# Staging - Allow staging domain
ALLOWED_ORIGINS=https://persona-assessment-staging.vercel.app

# Production - Allow production domain only
ALLOWED_ORIGINS=https://persona-assessment.vercel.app
```

## Performance Optimization

### Production Configuration:
```json
{
  "functions": {
    "api/index.py": {
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

### Staging Configuration:
```json
{
  "functions": {
    "api/index.py": {
      "memory": 512,
      "maxDuration": 30
    }
  }
}
```

## Useful Commands

### Deploy to Staging:
```bash
./deploy-staging.sh
```

### Deploy to Production:
```bash
./deploy-production.sh
```

### Check Deployment Status:
```bash
vercel ls
```

### View Logs:
```bash
# Staging
vercel logs persona-assessment-staging

# Production
vercel logs persona-assessment
```

### Environment Variables:
```bash
# List environment variables
vercel env ls

# Add environment variable
vercel env add ANTHROPIC_API_KEY production

# Remove environment variable
vercel env rm ANTHROPIC_API_KEY production
```

## Troubleshooting

### Deployment Fails:
1. Check build logs: `vercel logs`
2. Verify environment variables
3. Check Python dependencies in requirements.txt
4. Verify API routes configuration

### Database Connection Issues:
1. Verify DATABASE_URL in environment
2. Check database credentials
3. Verify network access (Vercel IPs)
4. Check connection pool limits

### API Errors:
1. Check Sentry for error details
2. Review application logs
3. Verify API key validity
4. Check rate limits

## Best Practices

1. **Always deploy to staging first**
2. **Test thoroughly on staging**
3. **Use feature flags for risky changes**
4. **Monitor production closely after deployment**
5. **Keep staging environment similar to production**
6. **Document all deployment steps**
7. **Maintain rollback procedures**
8. **Regular security audits**
9. **Cost monitoring and alerts**
10. **Regular backups**

## Support

For deployment issues:
- Check Vercel dashboard
- Review deployment logs
- Check GitHub Actions
- Contact team lead
