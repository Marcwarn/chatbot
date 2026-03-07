# Deployment Quick Reference

## Quick Commands

### Deploy to Staging
```bash
./deploy-staging.sh
```

### Deploy to Production
```bash
./deploy-production.sh
```

### Test Staging
```bash
./test-staging.sh
```

### Check Deployment Status
```bash
vercel ls
```

### View Logs
```bash
# Staging
vercel logs persona-assessment-staging

# Production
vercel logs persona-assessment
```

### Rollback Production
```bash
vercel rollback https://persona-assessment.vercel.app
```

## Environment URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| Production | https://persona-assessment.vercel.app | Live users |
| Staging | https://persona-assessment-staging.vercel.app | Testing |
| Development | http://localhost:8000 | Local dev |

## Key Configuration Files

| File | Purpose |
|------|---------|
| `vercel-production.json` | Production Vercel config |
| `vercel-staging.json` | Staging Vercel config |
| `.env.production.example` | Production env template |
| `.env.staging.example` | Staging env template |
| `deploy-production.sh` | Production deploy script |
| `deploy-staging.sh` | Staging deploy script |
| `test-staging.sh` | Staging test script |

## Environment Variables

### Required (All Environments)
- `ENVIRONMENT` - Environment name (production/staging/development)
- `ANTHROPIC_API_KEY` - Claude API key
- `ADMIN_PASSWORD_HASH` - Admin password hash
- `DATABASE_URL` - Database connection string

### Production-Specific
- `DEBUG=false`
- `ALLOWED_ORIGINS=https://persona-assessment.vercel.app`
- `RATE_LIMIT_PER_MINUTE=30`

### Staging-Specific
- `DEBUG=true`
- `ALLOWED_ORIGINS=https://persona-assessment-staging.vercel.app`
- `RATE_LIMIT_PER_MINUTE=100`

## Deployment Workflow

### Standard Flow
```
1. develop → staging branch
2. Deploy to staging (auto or ./deploy-staging.sh)
3. Test on staging (./test-staging.sh)
4. staging → main branch
5. Deploy to production (auto or ./deploy-production.sh)
6. Monitor production
```

### Emergency Hotfix
```
1. Create hotfix branch from main
2. Apply fix
3. Test locally
4. Deploy to staging first
5. If urgent, deploy directly to production
6. Monitor closely
```

## Pre-Deployment Checklist (Minimal)

### Staging
- [ ] Tests pass locally
- [ ] No sensitive data in code
- [ ] Environment variables configured

### Production
- [ ] Staging deployment successful
- [ ] All tests pass
- [ ] Security scan passes
- [ ] Database backup created
- [ ] Team notified

## Post-Deployment Verification

### Immediate (< 5 min)
```bash
# Check health
curl https://persona-assessment.vercel.app/api/health

# Check main page
curl -I https://persona-assessment.vercel.app/
```

### Verify Features
- [ ] Main page loads
- [ ] Admin panel accessible
- [ ] Assessment submission works
- [ ] No errors in Sentry

## Troubleshooting

### Deployment Failed
1. Check Vercel dashboard
2. Review GitHub Actions logs
3. Check build logs: `vercel logs`
4. Verify environment variables

### Health Check Fails
1. Check API logs
2. Verify database connection
3. Check environment variables
4. Review Sentry errors

### Slow Performance
1. Check Lambda memory (should be 1024MB for prod)
2. Check database queries
3. Review response times in logs
4. Check cache configuration

## Monitoring Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Vercel | vercel.com/dashboard | Deployments |
| Admin Panel | /admin | Application admin |
| Cost Tracking | /admin-costs | API cost monitoring |
| Sentry | sentry.io | Error tracking |

## Emergency Contacts

### Immediate Actions for Issues
1. Check health endpoint
2. Review error logs in Sentry
3. Check Vercel dashboard
4. If critical: Rollback immediately

### Rollback Commands
```bash
# Vercel rollback
vercel rollback https://persona-assessment.vercel.app

# Git revert
git revert HEAD
git push origin main
```

## Common Issues

### Issue: Environment variable not working
**Solution:**
- Check Vercel environment variables dashboard
- Redeploy after changing variables
- Verify variable name matches code

### Issue: Database connection fails
**Solution:**
- Verify DATABASE_URL is set
- Check database is accessible from Vercel
- Verify connection string format

### Issue: CORS errors
**Solution:**
- Check ALLOWED_ORIGINS in environment
- Verify domain matches exactly
- Check Vercel headers configuration

### Issue: High API costs
**Solution:**
- Check cost dashboard at /admin-costs
- Review API usage patterns
- Enable caching if not already
- Check for infinite loops

## Best Practices

1. **Always deploy to staging first**
2. **Test thoroughly before production**
3. **Deploy during low-traffic hours**
4. **Monitor for 24 hours after deployment**
5. **Keep rollback plan ready**
6. **Document all changes**
7. **Communicate with team**

## Git Workflow

### Create Staging Branch (First Time)
```bash
git checkout -b staging
git push -u origin staging
```

### Deploy to Staging
```bash
git checkout staging
git merge develop  # or make changes directly
git push origin staging
# Auto-deploys via GitHub Actions
```

### Deploy to Production
```bash
git checkout main
git merge staging
git push origin main
# Auto-deploys via GitHub Actions
```

## Vercel CLI Setup

### Install
```bash
npm i -g vercel
```

### Login
```bash
vercel login
```

### Link Project
```bash
vercel link
```

### Set Environment Variable
```bash
vercel env add ANTHROPIC_API_KEY production
```

## Security Reminders

- ✅ Never commit `.env` files
- ✅ Rotate API keys regularly
- ✅ Use different keys for staging/production
- ✅ Enable rate limiting
- ✅ Monitor for suspicious activity
- ✅ Keep dependencies updated
- ✅ Run security scans before production deploy

## Performance Optimization

### Production Settings
- Lambda Memory: 1024MB
- Lambda Timeout: 10s
- Cache TTL: 600s
- Enable compression
- Optimize database queries

### Staging Settings
- Lambda Memory: 512MB
- Lambda Timeout: 30s
- Cache TTL: 300s
- Debug logging enabled

## Cost Management

### Monitor Costs
- Check `/admin-costs` dashboard daily
- Set up cost alerts in Vercel
- Review API usage patterns
- Optimize expensive operations

### Cost Budgets
- Production: $200/month
- Staging: $50/month
- Development: $10/month

## Support Resources

### Documentation
- [DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md) - Full guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Complete checklist
- [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) - Production setup
- [SECURITY_SYSTEM_README.md](SECURITY_SYSTEM_README.md) - Security

### External Resources
- [Vercel Docs](https://vercel.com/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Python Vercel Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)

## Version History

Track deployments with git tags:
```bash
# List recent deployments
git tag -l "v*" | tail -10

# View tag details
git show v20260307-120000
```
