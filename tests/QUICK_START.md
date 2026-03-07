# Quick Start - Security Test Suite

## Installation

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-timeout
pip install bcrypt psutil  # For security and performance tests

# Install application dependencies
pip install -r requirements.txt
```

## Run All Tests

```bash
# Basic run
pytest

# With coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing
```

## Run Specific Test Suites

```bash
# Security tests only (all 22 vulnerabilities)
pytest tests/test_security.py -v

# Integration tests (end-to-end flows)
pytest tests/test_integration.py -v

# Performance tests (load testing, memory leaks)
pytest tests/test_performance.py -v
```

## Run Tests by Severity

```bash
# Critical vulnerabilities (9 tests)
pytest tests/test_security.py -v -k "critical"

# High severity (5 tests)
pytest tests/test_security.py -v -k "high"

# Medium severity (8 tests)
pytest tests/test_security.py -v -k "medium"
```

## Run Specific Vulnerability Tests

```bash
# Password hashing vulnerability
pytest tests/test_security.py::test_weak_password_hashing_sha256 -v

# CORS wildcard vulnerability
pytest tests/test_security.py::test_cors_wildcard_allows_all_origins -v

# SQL injection
pytest tests/test_security.py::test_user_id_sql_injection -v

# Rate limiting
pytest tests/test_security.py::test_rate_limit_blocks_brute_force -v
```

## Quick Commands

```bash
# Run fast tests only (skip slow performance tests)
pytest -v -k "not slow"

# Run with minimal output
pytest -q

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run tests that failed in last run, then all others
pytest --ff

# Run tests in parallel (faster)
pytest -n auto  # Requires: pip install pytest-xdist
```

## Coverage Commands

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Show missing lines in terminal
pytest --cov=. --cov-report=term-missing

# Fail if coverage < 70%
pytest --cov=. --cov-fail-under=70
```

## Environment Variables

```bash
# Set admin password for tests (optional, has default)
export ADMIN_PASSWORD_HASH="your-bcrypt-hash-here"

# Set API key for AI tests (most tests use mocks)
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Verify Test Suite

```bash
# List all tests
pytest --collect-only

# Count tests
pytest --collect-only -q | tail -1

# Expected: 60+ tests total
# - 22+ security tests (all vulnerabilities)
# - 12+ integration tests
# - 15+ performance tests
```

## CI/CD Integration

Tests run automatically on GitHub Actions:

- Every pull request
- Every push to main/develop
- Daily at 2 AM UTC
- Manual trigger

## Common Issues

**"No module named 'anthropic'"**
```bash
pip install anthropic
```

**"ModuleNotFoundError: No module named 'psutil'"**
```bash
pip install psutil
```

**Tests hang/timeout**
```bash
pytest --timeout=60  # Set timeout to 60 seconds
```

## Test Results Interpretation

### Passing Tests ✅

```
test_weak_password_hashing_sha256 PASSED
```
= Vulnerability is properly tested, fix verification in place

### Failing Tests ❌

```
test_weak_password_hashing_sha256 FAILED
AssertionError: Hashes should match (proving vulnerability)
```
= Read test docstring for EXPLOIT SCENARIO and FIX instructions

### Skipped Tests ⊘

```
test_https_enforcement SKIPPED (MEDIUM RISK: No HSTS header)
```
= Feature not yet implemented, listed as known issue

## Next Steps

1. **Run all tests**: `pytest -v`
2. **Check coverage**: `pytest --cov=. --cov-report=html`
3. **Review failures**: Read test docstrings for fix instructions
4. **Fix vulnerabilities**: Follow FIX guidance in test documentation
5. **Re-run**: Verify fixes with `pytest --lf`

## Full Documentation

See `tests/README_TESTS.md` for complete documentation.

## Support

- Test docstrings include EXPLOIT SCENARIO
- GitHub Actions logs show CI failures
- Coverage reports in `htmlcov/index.html`
