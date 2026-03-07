# Git Hooks - Security Validation

This directory contains automated security checks that run at different stages of the Git workflow.

## Installation

To enable these hooks, run:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/*
```

Or run the setup script:

```bash
./setup-hooks.sh
```

## Hooks Overview

### 1. `pre-commit` - Code Security Validation

**When it runs:** Before every commit (after `git commit`)

**What it checks:**
- ❌ **Hardcoded secrets** (passwords, API keys, tokens)
- ❌ **Weak password hashing** (SHA-256, MD5, SHA-1 instead of bcrypt)
- ❌ **CORS wildcard** configuration (`allow_origins=["*"]`)
- ❌ **Timing attack vulnerabilities** (using `==` instead of `secrets.compare_digest`)
- ❌ **SQL injection patterns** (f-strings in SQL, string concatenation)
- ⚠️  **Missing input validation** (path parameters without Field/Path validators)
- ⚠️  **Missing authentication** (DELETE/PUT endpoints without Depends)

**Blocks commit if:** Critical vulnerabilities found (❌)

**Example output:**
```
🔒 Running security pre-commit checks...
🔑 [1/7] Checking for hardcoded secrets...
❌ CRITICAL: Potential hardcoded secret found in api_admin.py
   Pattern: password\s*=\s*['"][^'"]+['"]

❌ COMMIT BLOCKED: 1 critical security issue(s) found
```

### 2. `commit-msg` - Commit Message Quality

**When it runs:** After entering commit message

**What it checks:**
- Security-related commits have detailed messages (≥50 characters)
- Commit messages aren't too vague ("fix", "update")
- WIP/TODO/FIXME warnings

**Blocks commit if:** Message is too vague

**Example:**
```
❌ COMMIT BLOCKED: Commit message too vague
   'fix' is not descriptive enough

   Use format: 'Fix: <what was fixed>'
   Example: 'Fix: Remove hardcoded admin password'
```

### 3. `pre-push` - Final Production Checks

**When it runs:** Before pushing to remote (after `git push`)

**What it checks:**
- ❌ `.env` files staged for commit
- ⚠️  Large files (>1MB) that might contain sensitive data
- ⚠️  Dependency vulnerabilities (using `pip-audit`)
- ⚠️  Security test coverage
- 🔐 Git secrets scan (if `git-secrets` installed)

**Blocks push if:** Critical issues found

## Bypassing Hooks (Emergency Only)

**⚠️ WARNING:** Only bypass hooks in emergencies!

```bash
# Skip pre-commit hook (NOT RECOMMENDED)
git commit --no-verify

# Skip pre-push hook (NOT RECOMMENDED)
git push --no-verify
```

**Never bypass hooks for:**
- Production deployments
- Security-related code
- GDPR-related changes
- Authentication/authorization changes

## Hook Customization

### Adding New Checks

Edit the relevant hook file and add your check in a new section:

```bash
# =============================================================================
# CHECK X: Your New Check
# =============================================================================
echo "🔍 [X/Y] Checking for your new security pattern..."

for file in $STAGED_PY_FILES; do
    if grep -inE "your-pattern" "$file"; then
        echo -e "${RED}❌ CRITICAL: Your security issue in $file${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done
```

### Adjusting Severity

- **Critical (❌):** Increments `ERRORS` (blocks commit/push)
- **Warning (⚠️):** Increments `WARNINGS` (allows commit/push with warning)

## Troubleshooting

### Hooks not running

```bash
# Check hooks path
git config core.hooksPath

# Should output: .githooks

# If not set:
git config core.hooksPath .githooks
```

### Permission denied

```bash
# Make hooks executable
chmod +x .githooks/*
```

### False positives

If a hook incorrectly flags code:

1. **Check if it's actually a vulnerability** (consult LESSONS_LEARNED.md)
2. If false positive, add exception comment:
   ```python
   # ❌ NEVER DO THIS (example for documentation)
   password = "example"
   ```
3. Update hook pattern to exclude documentation/examples

### Hook performance issues

If hooks are slow:

1. **pre-commit:** Only scans staged files (fast)
2. **pre-push:** Runs full security scan (slower, but important)

To skip expensive checks during development:
```bash
# Disable pre-push temporarily (re-enable before production push!)
git config core.hooksPath ""

# Re-enable
git config core.hooksPath .githooks
```

## Integration with CI/CD

These same checks should run in CI/CD pipeline:

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run security checks
        run: |
          .githooks/pre-commit
          .githooks/pre-push
```

## Additional Tools

Enhance security with these tools:

### 1. git-secrets (AWS)
Prevents committing AWS credentials

```bash
# macOS
brew install git-secrets

# Ubuntu/Debian
git clone https://github.com/awslabs/git-secrets
cd git-secrets
sudo make install

# Setup
git secrets --register-aws
git secrets --install
```

### 2. pip-audit
Scans Python dependencies for vulnerabilities

```bash
pip install pip-audit

# Run manually
pip-audit --requirement requirements.txt

# Auto-fix
pip-audit --requirement requirements.txt --fix
```

### 3. bandit
Python security linter

```bash
pip install bandit

# Scan all Python files
bandit -r .

# Integrate with pre-commit
bandit -r $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
```

### 4. Safety
Checks dependencies against vulnerability database

```bash
pip install safety

# Check installed packages
safety check

# Check requirements.txt
safety check -r requirements.txt
```

## Maintenance

### Monthly Tasks
- [ ] Review and update hook patterns
- [ ] Test hooks with known vulnerable code
- [ ] Update LESSONS_LEARNED.md with new vulnerabilities

### After Security Incidents
- [ ] Add detection pattern to relevant hook
- [ ] Test that hook catches the vulnerability
- [ ] Document in LESSONS_LEARNED.md

## Support

- **Questions:** See SECURITY_CHECKLIST.md
- **New vulnerability patterns:** Update LESSONS_LEARNED.md first
- **Hook failures:** Review output and fix code (don't bypass!)

## Version History

- **v1.0** (2026-03-07): Initial release
  - Pre-commit: 7 security checks
  - Commit-msg: Message quality validation
  - Pre-push: 5 production checks

---

**Remember:** Hooks are your last line of defense before code enters the codebase. Never bypass them without understanding the risk.
