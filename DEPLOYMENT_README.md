# Deployment System Documentation

## Overview

This directory contains a comprehensive staging and production deployment system for Vercel. The system includes automated deployment scripts, environment configuration, testing tools, and monitoring setup.

## Files Structure

```
├── DEPLOYMENT_ENVIRONMENTS.md      # Complete deployment guide
├── DEPLOYMENT_CHECKLIST.md         # Pre/post deployment checklists
├── DEPLOYMENT_QUICK_REFERENCE.md   # Quick command reference
├── DEPLOYMENT_README.md            # This file
├── vercel-production.json          # Production Vercel config
├── vercel-staging.json             # Staging Vercel config
├── .env.production.example         # Production env template
├── .env.staging.example            # Staging env template
├── deploy-production.sh            # Production deploy script
├── deploy-staging.sh               # Staging deploy script
├── test-staging.sh                 # Staging test script
├── environment_config.py           # Environment manager
└── .github/workflows/
    ├── deploy-production.yml       # Production CI/CD
    └── deploy-staging.yml          # Staging CI/CD
```

## Quick Start

### 1. First-Time Setup

#### Set up Vercel Projects

**Option A: Separate Projects (Recommended)**
1. Create two Vercel projects:
   - `persona-assessment` (production)
   - `persona-assessment-staging` (staging)

**Option B: Single Project with Branches**
1. Create one project with branch-based deployments
2. Configure `main` → Production
3. Configure `staging` → Preview

#### Configure Environment Variables

In Vercel dashboard, set these variables for each environment:

**Production:**
- Copy from `.env.production.example`
- Set in Vercel dashboard under Environment Variables
- Select "Production" environment

**Staging:**
- Copy from `.env.staging.example`
- Set in Vercel dashboard under Environment Variables
- Select "Preview" or separate project

#### Set up GitHub Secrets

Add these secrets to your GitHub repository:

```
VERCEL_TOKEN              # Vercel API token
VERCEL_ORG_ID            # Vercel organization ID
VERCEL_STAGING_PROJECT_ID # Staging project ID
VERCEL_PROD_PROJECT_ID   # Production project ID
VERCEL_SCOPE             # Vercel team scope
VERCEL_PROD_SCOPE        # Production team scope (if different)
```

### 2. Deploy to Staging

```bash
# Option 1: Manual deployment
./deploy-staging.sh

# Option 2: Git push (auto-deploys)
git checkout staging
git push origin staging
```

### 3. Test Staging

```bash
./test-staging.sh
```

### 4. Deploy to Production

```bash
# Option 1: Manual deployment
./deploy-production.sh

# Option 2: Git push (auto-deploys)
git checkout main
git merge staging
git push origin main
```

## Environment Configuration

### Environment Detection

The system automatically detects the environment based on the `ENVIRONMENT` variable:

```python
from environment_config import is_production, is_staging, get_config

# Check environment
if is_production():
    # Production-specific code
    pass
elif is_staging():
    # Staging-specific code
    pass

# Get configuration
config = get_config()
print(config.rate_limit_per_minute)  # 30 for prod, 100 for staging
```

### Environment Differences

| Feature | Production | Staging | Development |
|---------|-----------|---------|-------------|
| Debug Mode | `false` | `true` | `true` |
| Rate Limit | 30/min | 100/min | 1000/min |
| Lambda Memory | 1024MB | 512MB | N/A |
| Lambda Timeout | 10s | 30s | N/A |
| Cache TTL | 600s | 300s | 60s |
| Experimental Features | Disabled | Enabled | Enabled |
| Debug Endpoints | Disabled | Enabled | Enabled |

## Deployment Scripts

### deploy-staging.sh

Automated staging deployment with:
- ✅ Git branch check
- ✅ Test suite execution
- ✅ Security scanning
- ✅ Vercel deployment
- ✅ Health checks
- ✅ Smoke tests

```bash
./deploy-staging.sh
```

### deploy-production.sh

Production deployment with strict checks:
- ✅ Branch verification (must be `main`)
- ✅ No uncommitted changes
- ✅ Staging verification
- ✅ Full test suite
- ✅ Strict security scan
- ✅ Database backup
- ✅ Vercel deployment
- ✅ Health checks
- ✅ Smoke tests
- ✅ Git tagging

```bash
./deploy-production.sh
```

### test-staging.sh

Comprehensive staging tests:
- ✅ API endpoint tests
- ✅ Page accessibility tests
- ✅ CORS verification
- ✅ Response time checks
- ✅ Security headers
- ✅ Environment detection
- ✅ Debug mode verification

```bash
./test-staging.sh
```

## GitHub Actions Workflows

### Staging Workflow (.github/workflows/deploy-staging.yml)

**Triggers:**
- Push to `staging` branch
- Push to `develop` branch
- Manual workflow dispatch

**Steps:**
1. Run tests
2. Security scan
3. Deploy to Vercel
4. Health check
5. Smoke tests

### Production Workflow (.github/workflows/deploy-production.yml)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Steps:**
1. Security gate (strict mode)
2. Test gate (full suite + coverage)
3. Deploy to Vercel
4. Health check
5. Smoke tests
6. Deployment status tracking

## Monitoring & Alerts

### Health Checks

```bash
# Production
curl https://persona-assessment.vercel.app/api/health

# Staging
curl https://persona-assessment-staging.vercel.app/api/health
```

### Error Monitoring

- **Sentry:** Configure separate projects for staging/production
- **Vercel Logs:** Access via dashboard or CLI
- **Cost Dashboard:** Available at `/admin-costs`

### Alerts Setup

Configure alerts for:
- Error rate > 1%
- Response time > 2s
- Cost exceeds budget threshold
- Health check failures
- Security vulnerabilities

## Rollback Procedures

### Vercel Rollback

```bash
# Quick rollback to previous deployment
vercel rollback https://persona-assessment.vercel.app
```

### Git Rollback

```bash
# Revert last commit
git revert HEAD
git push origin main

# Deploy specific commit
git checkout <commit-hash>
vercel --prod
```

### Database Rollback

```bash
# Restore from backup
pg_restore -d production_db backup_YYYYMMDD_HHMMSS.sql

# Rollback migration
alembic downgrade -1
```

## Security

### Pre-Deployment Security Checks

The deployment scripts automatically run:
- Security scanner (`security_scanner.py`)
- Dependency vulnerability checks
- Environment variable validation
- Sensitive file detection

### Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use different API keys for each environment
- ✅ Rotate secrets regularly
- ✅ Enable rate limiting
- ✅ Configure CORS properly
- ✅ Use HTTPS only in production
- ✅ Enable security headers

## Cost Management

### Cost Tracking

Monitor costs at: `/admin-costs`

**Features:**
- Real-time API usage tracking
- Daily/weekly/monthly reports
- Budget alerts
- Usage analytics

### Cost Budgets

| Environment | Monthly Budget | Alert Threshold |
|-------------|---------------|-----------------|
| Production | $200 | 90% |
| Staging | $50 | 80% |
| Development | $10 | 50% |

## Performance Optimization

### Production Settings

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

### Caching Strategy

- API responses: 10 minutes
- Static assets: 1 hour
- Database queries: 5 minutes

### Database Optimization

- Connection pooling enabled
- Query optimization
- Index creation for common queries
- Regular VACUUM operations

## Troubleshooting

### Common Issues

#### Deployment Fails
1. Check Vercel dashboard for errors
2. Review GitHub Actions logs
3. Verify environment variables
4. Check build logs

#### Health Check Fails
1. Verify API is responding
2. Check database connectivity
3. Review Sentry errors
4. Check environment configuration

#### High Costs
1. Review cost dashboard
2. Check for API usage spikes
3. Enable caching
4. Optimize expensive operations

### Debug Commands

```bash
# View Vercel logs
vercel logs persona-assessment --follow

# Test local environment
python environment_config.py

# Run security scan
python security_scanner.py --strict

# Check deployment status
vercel ls
```

## Best Practices

### Deployment Workflow

1. **Develop on feature branch**
2. **Merge to staging branch**
3. **Auto-deploy to staging**
4. **Run automated tests**
5. **Manual testing on staging**
6. **Merge to main**
7. **Auto-deploy to production**
8. **Monitor for 24 hours**

### Testing Strategy

- **Unit tests:** Run locally before commit
- **Integration tests:** Run in CI/CD
- **Staging tests:** Automated after deploy
- **Production smoke tests:** After each deploy
- **Manual testing:** Critical user flows

### Monitoring Strategy

- **Immediate (0-5 min):** Health checks
- **Short-term (5-60 min):** Error rates, performance
- **Medium-term (1-24 hours):** Stability, costs
- **Long-term (24+ hours):** Trends, optimizations

## Support

### Documentation

- [DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md) - Complete deployment guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment checklists
- [DEPLOYMENT_QUICK_REFERENCE.md](DEPLOYMENT_QUICK_REFERENCE.md) - Quick commands
- [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) - Production setup
- [SECURITY_SYSTEM_README.md](SECURITY_SYSTEM_README.md) - Security documentation

### External Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Python Vercel Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [GitHub Actions](https://docs.github.com/en/actions)

## Contributing

When adding new features:

1. Update environment configuration if needed
2. Add tests for new functionality
3. Update deployment documentation
4. Test on staging before production
5. Monitor cost impact

## License

[Your License Here]

## Changelog

### 2026-03-07
- Initial deployment system setup
- Added staging and production environments
- Created deployment scripts
- Added GitHub Actions workflows
- Implemented environment configuration
- Added comprehensive documentation
