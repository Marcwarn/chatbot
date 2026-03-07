# CI/CD Pipeline Guide

## Pipeline Overview

```
Push to Branch
    ↓
Security Scan → Unit Tests → Integration Tests → Linting
    ↓                ↓              ↓              ↓
   Pass            Pass           Pass           Pass
    ↓
Deploy to Staging (if staging/develop branch)
    ↓
Smoke Tests
    ↓
Manual QA on Staging
    ↓
Merge to Main
    ↓
Security Gate → Test Gate
    ↓              ↓
   Pass           Pass
    ↓
Deploy to Production
    ↓
Health Check → Smoke Tests
    ↓              ↓
   Pass           Pass
    ↓
✅ Deployment Complete
```

## Required Secrets

Configure in GitHub Settings → Secrets:

- `VERCEL_TOKEN` - Vercel API token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_STAGING_PROJECT_ID` - Staging project ID
- `VERCEL_PROD_PROJECT_ID` - Production project ID
- `STAGING_ADMIN_HASH` - Staging admin password hash
- `PROD_ADMIN_HASH` - Production admin password hash
- `STAGING_API_KEY` - Staging API key
- `PROD_API_KEY` - Production API key

## Deployment Process

### To Staging:
1. Push to `staging` or `develop` branch
2. CI runs tests automatically
3. If tests pass, auto-deploys to staging
4. Smoke tests run automatically
5. Manual QA if needed

### To Production:
1. Merge `staging` → `main`
2. CI runs full test suite
3. Security scan (strict mode)
4. If all pass, deploys to production
5. Health check + smoke tests
6. Monitor for 10 minutes

## Rollback Procedure

If deployment fails:
```bash
# 1. Identify last good deployment
vercel list

# 2. Rollback (or use Vercel dashboard)
vercel rollback <deployment-url>

# 3. Investigate issue
git log
git diff

# 4. Fix and redeploy
```

## Workflow Files

### `.github/workflows/ci-tests.yml`
Main CI pipeline that runs on all pushes and PRs:
- Security scanning
- Unit tests with coverage
- Integration tests
- Code linting and formatting
- Performance benchmarks

### `.github/workflows/deploy-staging.yml`
Staging deployment pipeline:
- Runs all tests
- Deploys to Vercel staging
- Runs smoke tests
- Notifies on success

### `.github/workflows/deploy-production.yml`
Production deployment pipeline:
- Security gate (strict mode)
- Full test suite with coverage verification
- Deploys to production
- Health checks
- Critical smoke tests
- Automatic rollback on failure

## Test Suites

### Unit Tests
Located in `tests/`:
- `test_api.py` - API endpoint tests
- `test_security.py` - Security tests
- `test_disc.py` - DISC assessment tests
- `test_integration.py` - Integration tests
- `test_performance.py` - Performance tests

### Smoke Tests
`tests/smoke_tests.py` - Post-deployment validation:
- API health check
- Landing page loads
- Assessment pages accessible
- Admin login functional

### Coverage Verification
`tests/verify_coverage.py` - Ensures:
- Minimum 80% overall coverage
- Critical files have adequate coverage
- Coverage reports are generated

### Performance Checks
`tests/check_performance_regression.py` - Monitors:
- API response times
- Database query performance
- Memory usage
- CPU utilization

## Local Testing

Before pushing, run locally:

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test suite
pytest tests/test_security.py -v

# Run performance tests
python tests/test_performance.py --benchmark

# Run smoke tests (requires running server)
python tests/smoke_tests.py --url http://localhost:8000
```

## CI/CD Best Practices

### 1. Branch Strategy
- `main` - Production branch (protected)
- `staging` - Pre-production testing
- `develop` - Development integration
- `feature/*` - Feature branches

### 2. Pull Request Workflow
1. Create feature branch from `develop`
2. Make changes and commit
3. Push and create PR to `develop`
4. CI runs automatically
5. Code review required
6. Merge to `develop` after approval

### 3. Release Process
1. Test thoroughly on `develop`
2. Merge `develop` → `staging`
3. Deploy to staging automatically
4. QA testing on staging
5. Merge `staging` → `main`
6. Deploy to production automatically
7. Monitor production for issues

### 4. Emergency Hotfix
1. Create hotfix branch from `main`
2. Make minimal fix
3. Create PR to `main`
4. Fast-track review
5. Deploy to production
6. Backport to `staging` and `develop`

## Monitoring

### GitHub Actions
- View workflow runs in GitHub Actions tab
- Download artifacts (coverage reports, security scans)
- Monitor build times and success rates

### Vercel Deployments
- Check deployment logs in Vercel dashboard
- Monitor performance metrics
- View deployment history

### Coverage Reports
- Codecov integration for coverage tracking
- HTML coverage reports as artifacts
- Coverage badges in README

## Troubleshooting

### Tests Fail in CI but Pass Locally
- Check environment variables
- Ensure dependencies match `requirements.txt`
- Review CI logs for specific errors

### Deployment Fails
- Check Vercel logs
- Verify all secrets are configured
- Ensure build succeeds locally

### Security Scan Fails
- Review security report artifact
- Fix identified vulnerabilities
- Update dependencies

### Performance Regression
- Review performance metrics
- Identify slow endpoints
- Optimize queries or add caching

## Notifications

Configure notifications in GitHub:
- Settings → Notifications
- Enable for failed builds
- Email or Slack integration

## Security

### Secrets Management
- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly
- Use different secrets for staging/production

### Security Scanning
- Runs on every push
- Strict mode for production
- Reports uploaded as artifacts
- Blocks deployment on critical issues

## Performance

### Build Optimization
- Cache dependencies
- Parallel test execution
- Incremental builds when possible

### Test Optimization
- Run critical tests first
- Skip non-essential tests in smoke testing
- Use test markers for selective runs

## Future Enhancements

- [ ] Add end-to-end tests with Playwright
- [ ] Implement blue-green deployments
- [ ] Add canary releases
- [ ] Integrate load testing
- [ ] Add automated security updates
- [ ] Implement feature flags
- [ ] Add A/B testing support
- [ ] Set up monitoring alerts
