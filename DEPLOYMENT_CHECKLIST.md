# Deployment Checklist

## Pre-Deployment Checklist

### Staging Deployment

- [ ] **Code Review**
  - [ ] All code changes reviewed
  - [ ] No sensitive data in code
  - [ ] No debug code or console logs
  - [ ] Documentation updated

- [ ] **Testing**
  - [ ] All unit tests pass locally
  - [ ] Integration tests pass
  - [ ] Security scan passes
  - [ ] Performance tests acceptable

- [ ] **Environment Configuration**
  - [ ] `.env.staging.example` reviewed
  - [ ] Staging environment variables set in Vercel
  - [ ] Database URL configured
  - [ ] API keys configured
  - [ ] CORS origins configured

- [ ] **Database**
  - [ ] Database migrations ready
  - [ ] Migration tested locally
  - [ ] Rollback plan prepared

- [ ] **Security**
  - [ ] No `.env` files committed
  - [ ] Security scanner passes
  - [ ] Dependencies up to date
  - [ ] No known vulnerabilities

- [ ] **Deployment Files**
  - [ ] `vercel-staging.json` configured
  - [ ] GitHub workflow tested
  - [ ] Deployment script tested

### Production Deployment

- [ ] **Staging Verification**
  - [ ] Staging deployment successful
  - [ ] All staging tests pass
  - [ ] Manual testing on staging complete
  - [ ] Performance acceptable on staging
  - [ ] Cost tracking working on staging

- [ ] **Code Quality**
  - [ ] Code freeze in effect
  - [ ] All tests pass (100% critical paths)
  - [ ] Security scan passes (strict mode)
  - [ ] Code coverage > 80%
  - [ ] No TODO or FIXME in critical code

- [ ] **Environment Configuration**
  - [ ] `.env.production.example` reviewed
  - [ ] Production environment variables set in Vercel
  - [ ] Database URL configured (production)
  - [ ] API keys configured (production)
  - [ ] CORS origins restricted to production domain
  - [ ] Rate limits configured appropriately

- [ ] **Database**
  - [ ] Production database backup created
  - [ ] Migration tested on staging
  - [ ] Rollback script ready
  - [ ] Data integrity verified

- [ ] **Security**
  - [ ] Security headers configured
  - [ ] HTTPS enforced
  - [ ] Secrets rotated (if needed)
  - [ ] Admin credentials secure
  - [ ] Rate limiting enabled
  - [ ] CSRF protection enabled

- [ ] **Monitoring**
  - [ ] Sentry configured for production
  - [ ] Error tracking working
  - [ ] Cost alerts configured
  - [ ] Performance monitoring ready
  - [ ] Uptime monitoring configured

- [ ] **Performance**
  - [ ] Lambda memory optimized (1024MB)
  - [ ] Lambda timeout set (10s)
  - [ ] Caching configured
  - [ ] Assets optimized
  - [ ] Database queries optimized

- [ ] **Deployment Files**
  - [ ] `vercel-production.json` configured
  - [ ] GitHub workflow tested
  - [ ] Deployment script tested
  - [ ] Rollback procedure documented

- [ ] **Communication**
  - [ ] Team notified of deployment
  - [ ] Deployment window scheduled
  - [ ] Rollback plan communicated

## During Deployment

- [ ] **Staging Deployment**
  - [ ] Run deployment script: `./deploy-staging.sh`
  - [ ] Monitor deployment in Vercel dashboard
  - [ ] Wait for deployment to complete
  - [ ] Check deployment logs for errors

- [ ] **Staging Verification**
  - [ ] Run test suite: `./test-staging.sh`
  - [ ] Manual smoke tests
  - [ ] Check all critical features
  - [ ] Verify database migrations
  - [ ] Check error monitoring

- [ ] **Production Deployment**
  - [ ] Final confirmation obtained
  - [ ] Run deployment script: `./deploy-production.sh`
  - [ ] Monitor deployment in Vercel dashboard
  - [ ] Wait for deployment to complete
  - [ ] Check deployment logs for errors

- [ ] **Production Verification**
  - [ ] Health check passes
  - [ ] Smoke tests pass
  - [ ] Critical features verified
  - [ ] Database connectivity confirmed
  - [ ] Error monitoring active

## Post-Deployment Checklist

### Immediate Verification (0-5 minutes)

- [ ] **Health Checks**
  - [ ] API health endpoint responding
  - [ ] Main application accessible
  - [ ] Admin panel accessible
  - [ ] No 500 errors in logs

- [ ] **Core Functionality**
  - [ ] Create session works
  - [ ] Assessment submission works
  - [ ] Report generation works
  - [ ] Admin authentication works

- [ ] **Monitoring**
  - [ ] Sentry receiving events
  - [ ] No critical errors in Sentry
  - [ ] Response times normal
  - [ ] Database connections healthy

### Short-Term Monitoring (5-60 minutes)

- [ ] **Performance**
  - [ ] Response times < 2s
  - [ ] No timeout errors
  - [ ] Database queries performant
  - [ ] Cache hit rate acceptable

- [ ] **Errors**
  - [ ] No increase in error rate
  - [ ] No new error types
  - [ ] All errors being caught
  - [ ] Error messages user-friendly

- [ ] **User Experience**
  - [ ] Pages loading correctly
  - [ ] Forms submitting properly
  - [ ] Navigation working
  - [ ] No broken links

- [ ] **Cost Tracking**
  - [ ] API usage being tracked
  - [ ] Costs within expected range
  - [ ] No unusual spikes
  - [ ] Alerts working properly

### Medium-Term Monitoring (1-24 hours)

- [ ] **Stability**
  - [ ] No crashes or restarts
  - [ ] Memory usage stable
  - [ ] No connection pool issues
  - [ ] No rate limit issues

- [ ] **Business Metrics**
  - [ ] User activity normal
  - [ ] Completion rates normal
  - [ ] No unusual patterns
  - [ ] Analytics working

- [ ] **Integration**
  - [ ] External services working
  - [ ] API integrations functioning
  - [ ] Email notifications sending
  - [ ] Webhooks firing

- [ ] **Security**
  - [ ] No suspicious activity
  - [ ] Authentication working
  - [ ] Authorization enforced
  - [ ] No security alerts

### Long-Term Monitoring (24+ hours)

- [ ] **Performance Trends**
  - [ ] Response times stable
  - [ ] Error rates normal
  - [ ] Resource usage predictable
  - [ ] No degradation over time

- [ ] **Cost Analysis**
  - [ ] Daily costs within budget
  - [ ] API usage as expected
  - [ ] No cost anomalies
  - [ ] Optimization opportunities identified

- [ ] **User Feedback**
  - [ ] No major complaints
  - [ ] Feature usage as expected
  - [ ] User satisfaction maintained
  - [ ] Support tickets normal

## Rollback Checklist

### When to Rollback

Rollback immediately if:
- [ ] Health checks failing
- [ ] Critical features broken
- [ ] Database integrity compromised
- [ ] Security vulnerability exposed
- [ ] Error rate > 5%
- [ ] User-facing errors occurring

### Rollback Procedure

- [ ] **Immediate Actions**
  - [ ] Stop new deployments
  - [ ] Notify team of rollback
  - [ ] Document reason for rollback

- [ ] **Vercel Rollback**
  - [ ] Run: `vercel rollback https://persona-assessment.vercel.app`
  - [ ] Verify rollback successful
  - [ ] Test rolled-back version

- [ ] **Database Rollback** (if needed)
  - [ ] Stop application traffic
  - [ ] Restore database backup
  - [ ] Verify data integrity
  - [ ] Rollback migrations

- [ ] **Verification**
  - [ ] Health checks passing
  - [ ] Critical features working
  - [ ] No errors in logs
  - [ ] Users can access application

- [ ] **Post-Rollback**
  - [ ] Investigate root cause
  - [ ] Document incident
  - [ ] Plan fix and redeployment
  - [ ] Update team

## Environment-Specific Notes

### Staging Environment

**Purpose:** Testing changes before production

**Guidelines:**
- Can be deployed frequently
- Used for testing new features
- Debug mode enabled
- Relaxed rate limits
- Can reset data if needed

**Deployment Frequency:** As needed (multiple times per day)

### Production Environment

**Purpose:** Live user-facing application

**Guidelines:**
- Deploy only after staging verification
- Strict security and performance requirements
- Comprehensive testing required
- Rollback plan mandatory
- User data protection critical

**Deployment Frequency:** Scheduled (after thorough testing)

## Deployment Windows

### Recommended Deployment Times

**Staging:**
- Anytime during business hours
- Avoid end of day Friday

**Production:**
- Tuesday-Thursday, 10am-2pm (low traffic)
- Avoid Mondays (post-weekend issues)
- Avoid Fridays (weekend support unavailable)
- Avoid holidays and weekends

### Emergency Deployments

For critical security fixes or major bugs:
- Can deploy outside normal windows
- Requires extra caution
- Full team notification
- Enhanced monitoring

## Success Criteria

### Staging Deployment Success

- [ ] All tests pass
- [ ] No deployment errors
- [ ] Health checks pass
- [ ] Manual testing successful

### Production Deployment Success

- [ ] Zero downtime deployment
- [ ] All health checks pass
- [ ] Error rate < 0.1%
- [ ] Response times < 2s
- [ ] No user complaints
- [ ] All critical features working
- [ ] 24-hour stability confirmed

## Contact Information

**Deployment Issues:**
- Check Vercel dashboard
- Review GitHub Actions logs
- Check Sentry for errors
- Review deployment logs

**Emergency Contacts:**
- DevOps Team: [contact info]
- Security Team: [contact info]
- On-call Engineer: [contact info]

## Documentation

**Related Docs:**
- [DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [SECURITY_SYSTEM_README.md](SECURITY_SYSTEM_README.md)
- [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
