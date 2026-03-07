# Comprehensive Security Test Suite

## Overview

This test suite provides **100% coverage of all 22 vulnerabilities** identified in the security audit report. Tests are organized into three main categories:

1. **Security Tests** (`test_security.py`) - All vulnerability exploits and fixes
2. **Integration Tests** (`test_integration.py`) - End-to-end workflow testing
3. **Performance Tests** (`test_performance.py`) - Load testing, memory leaks, DoS protection

## Test Structure

### Security Tests (test_security.py)

Tests all 22 vulnerabilities from `SECURITY_AUDIT_REPORT.md`:

#### CRITICAL Vulnerabilities (9 tests)

1. **Weak Password Hashing** - SHA-256 without salt vulnerable to rainbow tables
2. **Hardcoded Default Password** - "admin123" visible in source code
3. **Insecure Session Storage** - In-memory storage causing DoS vulnerability
4. **CORS Wildcard** - `allow_origins=["*"]` enables CSRF attacks
5. **Hardcoded GDPR Admin Key** - "CHANGE_ME_IN_PRODUCTION" in source
6. **Weak Rate Limiting** - 5 attempts/5min allows brute force
7. **Timing Attack** - Password comparison leaks information
8. **No Input Validation** - user_id allows SQL injection, path traversal
9. **Sensitive Data Exposure** - Full chat history, API keys in responses

#### HIGH Vulnerabilities (5 tests)

10. **Rate Limiter IP Spoofing** - X-Forwarded-For can be faked
11. **No Session Cleanup** - Expired sessions cause memory leak
12. **Missing GDPR Auth** - Export/delete endpoints lack authentication
13. **Immediate User Deletion** - No confirmation required
14. **SQL Injection Risk** - Dynamic queries vulnerable

#### MEDIUM Vulnerabilities (8 tests)

15. **No HTTPS Enforcement** - Missing HSTS header
16. **No CSRF Protection** - State-changing operations unprotected
17. **Missing Security Headers** - No CSP, X-Frame-Options, etc.
18. **No Request Size Limits** - DoS via large payloads
19. **Insufficient Audit Logging** - Admin actions not logged
20. **Email Hash Collision** - SHA-256 collisions possible
21. **No API Versioning** - Breaking changes affect old clients
22. **Dependency Vulnerabilities** - Outdated packages with CVEs

### Integration Tests (test_integration.py)

End-to-end user flows:

- **Assessment Flow** - Start → Answer → Results
- **Chat Flow** - Profile integration, multi-turn conversations
- **GDPR Compliance** - Consent, export, deletion
- **Admin Operations** - Login, dashboard, user management
- **Error Handling** - Invalid inputs, edge cases

### Performance Tests (test_performance.py)

Load testing and DoS protection:

- **Load Testing** - Concurrent users, high throughput
- **Memory Leak Detection** - Session storage, profile caching
- **Rate Limiting Effectiveness** - Brute force protection
- **Response Time Benchmarks** - Performance baselines
- **Resource Exhaustion** - Large payloads, nested objects

## Running Tests

### Run All Security Tests

```bash
pytest tests/test_security.py -v
```

### Run Specific Vulnerability Category

```bash
# Critical vulnerabilities only
pytest tests/test_security.py -v -k "critical"

# High severity
pytest tests/test_security.py -v -k "high"

# Medium severity
pytest tests/test_security.py -v -k "medium"
```

### Run Integration Tests

```bash
pytest tests/test_integration.py -v
```

### Run Performance Tests

```bash
# All performance tests
pytest tests/test_performance.py -v

# Skip slow tests
pytest tests/test_performance.py -v -k "not slow"
```

### Run All Tests with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
```

### Run Specific Test by Name

```bash
# Test weak password hashing
pytest tests/test_security.py::test_weak_password_hashing_sha256 -v

# Test CORS wildcard
pytest tests/test_security.py::test_cors_wildcard_allows_all_origins -v

# Test complete assessment flow
pytest tests/test_integration.py::test_complete_assessment_flow -v
```

## Test Fixtures

Located in `conftest.py`:

### Authentication Fixtures

- `admin_password` - Default admin password for testing
- `admin_token` - Valid admin authentication token
- `expired_admin_token` - Expired token for timeout testing

### Test Client Fixtures

- `client` - Standard FastAPI test client
- `client_no_rate_limit` - Client with rate limiting disabled

### Mock API Fixtures

- `mock_anthropic_api` - Mocked AI responses (no actual API calls)
- `mock_anthropic_api_error` - Mocked API errors

### Security Testing Utilities

- `malicious_payloads` - SQL injection, XSS, path traversal payloads
- `timing_attack_detector` - Detects timing vulnerabilities
- `security_scanner` - XSS detection, sensitive data scanning
- `rate_limit_tester` - Rate limiting effectiveness testing
- `memory_monitor` - Memory leak detection

### Test Data

- `test_user_id` - Unique user ID for each test
- `complete_assessment_data` - Valid 50-question assessment
- `mock_big_five_scores` - Realistic personality scores

## GitHub Actions Integration

Tests run automatically on:

- **Every Pull Request** to `main` or `develop`
- **Every Push** to `main` or `develop`
- **Daily Schedule** at 2 AM UTC
- **Manual Trigger** via GitHub Actions UI

### Workflow: `.github/workflows/security-tests.yml`

The workflow:

1. Runs on Python 3.10 and 3.11
2. Executes all test suites
3. Generates coverage reports
4. Runs dependency vulnerability scans (pip-audit, safety)
5. **Fails PR if any security test fails**
6. Uploads coverage to Codecov
7. Requires 70% code coverage minimum

### Required Secrets

Configure in GitHub repository settings:

- `ANTHROPIC_API_KEY` - API key for AI features (optional for most tests)
- `ADMIN_PASSWORD_HASH` - Production admin password hash

## Test Documentation Format

Each test includes:

1. **Clear descriptive name** - What vulnerability it tests
2. **Docstring with EXPLOIT SCENARIO** - How attacker would exploit
3. **LOCATION reference** - Where in code vulnerability exists
4. **FIX description** - How to fix the vulnerability
5. **Assertion messages** - Why test failed, what to do

Example:

```python
def test_weak_password_hashing_sha256(client):
    """
    VULNERABILITY: SHA-256 without salt - susceptible to rainbow table attacks

    EXPLOIT SCENARIO:
    If database is breached, attacker can use rainbow tables to reverse
    SHA-256 hashes of common passwords. Without salt, identical passwords
    produce identical hashes.

    LOCATION: api_admin.py:27-29
    FIX: Use bcrypt with per-password salt
    """
    # Test implementation
```

## Coverage Requirements

- **Overall Coverage**: 70% minimum
- **Security-Critical Code**: 90%+ recommended
- **All 22 Vulnerabilities**: 100% tested

## Continuous Improvement

### Adding New Tests

1. Add test to appropriate file:
   - `test_security.py` - For new vulnerabilities
   - `test_integration.py` - For new workflows
   - `test_performance.py` - For new performance checks

2. Follow naming convention: `test_<vulnerability>_<scenario>`

3. Include complete docstring with EXPLOIT SCENARIO

4. Add assertions with descriptive messages

5. Update this README if adding new category

### Test Markers

Use pytest markers for categorization:

```python
@pytest.mark.critical
def test_critical_vulnerability():
    pass

@pytest.mark.slow
def test_long_running_operation():
    pass
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'anthropic'**
```bash
pip install anthropic
```

**ModuleNotFoundError: No module named 'psutil'**
```bash
pip install psutil
```

**Tests fail due to missing API key**

Most tests use `mock_anthropic_api` fixture. If test requires real API:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Rate limit tests interfering with each other**

Fixtures `cleanup_sessions` and `reset_rate_limiters` run automatically.
If issues persist, run tests sequentially:
```bash
pytest tests/test_security.py -v --forked
```

**Memory monitor tests failing**

Requires `psutil`:
```bash
pip install psutil
```

## Security Test Metrics

- **Total Tests**: 60+
- **Vulnerabilities Covered**: 22/22 (100%)
- **CRITICAL Coverage**: 9/9 (100%)
- **HIGH Coverage**: 5/5 (100%)
- **MEDIUM Coverage**: 8/8 (100%)
- **Integration Flows**: 12+
- **Performance Tests**: 15+

## References

- **Security Audit**: `SECURITY_AUDIT_REPORT.md`
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **GDPR Compliance**: Articles 6, 7, 15, 17
- **CWE Database**: https://cwe.mitre.org/

## Support

For questions or issues with tests:

1. Check test docstrings for EXPLOIT SCENARIO
2. Review `SECURITY_AUDIT_REPORT.md`
3. Run with `-v` flag for verbose output
4. Check GitHub Actions logs for CI failures

---

**Last Updated**: 2026-03-07
**Test Suite Version**: 1.0
**Coverage Target**: 70% (minimum), 90% (recommended)
