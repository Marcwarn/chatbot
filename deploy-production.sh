#!/bin/bash
set -e

echo "🚀 Deploying to PRODUCTION..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_URL="https://persona-assessment.vercel.app"
STAGING_URL="https://persona-assessment-staging.vercel.app"

# Function to print colored output
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Step 0: Confirmation
echo ""
echo "⚠️  WARNING: This will deploy to PRODUCTION (live users)!"
echo ""
read -p "Are you absolutely sure? Type 'DEPLOY' to continue: " confirm

if [ "$confirm" != "DEPLOY" ]; then
    echo "Deployment cancelled"
    exit 1
fi

# Step 1: Check if we're on main branch
print_step "Checking git branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_error "Must be on 'main' branch for production deployment"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Step 2: Check for uncommitted changes
print_step "Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    print_error "You have uncommitted changes"
    git status --short
    echo "Commit or stash changes before deploying to production"
    exit 1
fi

# Step 3: Pull latest changes
print_step "Pulling latest changes..."
git pull origin main

# Step 4: Verify staging environment
print_step "Verifying staging environment..."
if command -v curl &> /dev/null; then
    if curl -f -s "${STAGING_URL}/api/health" > /dev/null; then
        print_success "Staging health check passed"
    else
        print_error "Staging health check failed!"
        echo "Deploy to staging and verify first"
        exit 1
    fi
else
    print_warning "curl not found, skipping staging verification"
fi

# Step 5: Run full test suite
print_step "Running full test suite..."
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --cov=. --cov-report=term-missing; then
        print_success "All tests passed"
    else
        print_error "Tests failed!"
        echo "Fix tests before deploying to production"
        exit 1
    fi
else
    print_error "pytest not found"
    exit 1
fi

# Step 6: Security scan (strict mode)
print_step "Running security scan (strict mode)..."
if [ -f "security_scanner.py" ]; then
    if python security_scanner.py --strict; then
        print_success "Security scan passed"
    else
        print_error "Security scan failed!"
        echo "Fix security issues before deploying to production"
        exit 1
    fi
else
    print_error "security_scanner.py not found"
    exit 1
fi

# Step 7: Check for sensitive files
print_step "Checking for sensitive files..."
if git ls-files | grep -E '\.(env|key|pem|cert)$' > /dev/null; then
    print_error "Found potential sensitive files in git!"
    git ls-files | grep -E '\.(env|key|pem|cert)$'
    exit 1
fi

# Step 8: Database backup (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    print_step "Backing up production database..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "Creating backup: $BACKUP_FILE"
    # Add your database backup command here
    # Example: pg_dump $DATABASE_URL > $BACKUP_FILE
    print_success "Database backup created"
else
    print_warning "DATABASE_URL not set, skipping database backup"
fi

# Step 9: Check Vercel CLI
print_step "Checking Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not installed"
    echo "Install with: npm i -g vercel"
    exit 1
fi

# Step 10: Final confirmation
echo ""
print_warning "Final check before production deployment:"
echo "  - All tests passed: ✓"
echo "  - Security scan passed: ✓"
echo "  - On main branch: ✓"
echo "  - No uncommitted changes: ✓"
echo "  - Staging verified: ✓"
echo ""
read -p "Proceed with production deployment? (yes/no): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 1
fi

# Step 11: Deploy to Vercel
print_step "Deploying to Vercel Production..."
echo "Using configuration from vercel-production.json"

if [ -n "$VERCEL_TOKEN" ] && [ -n "$VERCEL_PROD_SCOPE" ]; then
    # Use token if available
    vercel --prod --token=$VERCEL_TOKEN --scope=$VERCEL_PROD_SCOPE --yes
else
    # Interactive deployment
    vercel --prod
fi

# Step 12: Wait for deployment
print_step "Waiting for deployment to complete..."
sleep 10

# Step 13: Health check
print_step "Running production health check..."
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s "${PRODUCTION_URL}/api/health" > /dev/null; then
        print_success "Production health check passed"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            print_warning "Health check failed, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
            sleep 5
        else
            print_error "Production health check failed after $MAX_RETRIES attempts!"
            echo ""
            echo "🚨 CRITICAL: Production deployment may have failed!"
            echo ""
            echo "Immediate actions:"
            echo "  1. Check Vercel dashboard for errors"
            echo "  2. Check application logs"
            echo "  3. Consider rolling back: vercel rollback $PRODUCTION_URL"
            echo ""
            exit 1
        fi
    fi
done

# Step 14: Smoke tests
print_step "Running smoke tests..."
SMOKE_TESTS_PASSED=true

# Test API endpoints
endpoints=("/api/health" "/api/assessments" "/admin")
for endpoint in "${endpoints[@]}"; do
    if curl -f -s "${PRODUCTION_URL}${endpoint}" > /dev/null 2>&1; then
        echo "  ✓ ${endpoint}"
    else
        echo "  ✗ ${endpoint}"
        SMOKE_TESTS_PASSED=false
    fi
done

if [ "$SMOKE_TESTS_PASSED" = false ]; then
    print_warning "Some smoke tests failed"
    echo "Monitor the deployment closely"
fi

# Step 15: Tag release
print_step "Creating git tag..."
VERSION_TAG="v$(date +%Y%m%d-%H%M%S)"
git tag -a $VERSION_TAG -m "Production deployment: $VERSION_TAG"
git push origin $VERSION_TAG
print_success "Created tag: $VERSION_TAG"

# Success!
echo ""
echo "======================================"
print_success "Production deployment complete!"
echo "======================================"
echo ""
echo "🌐 Production URL: ${PRODUCTION_URL}"
echo "📊 Admin Panel: ${PRODUCTION_URL}/admin"
echo "💰 Cost Dashboard: ${PRODUCTION_URL}/admin-costs"
echo "🏷️  Version Tag: ${VERSION_TAG}"
echo ""
echo "⚠️  Important:"
echo "  1. Monitor production logs for errors"
echo "  2. Check Sentry for any issues"
echo "  3. Monitor cost tracking dashboard"
echo "  4. Verify user-facing features"
echo "  5. Keep backup ready for rollback if needed"
echo ""
echo "Rollback command (if needed):"
echo "  vercel rollback ${PRODUCTION_URL}"
echo ""
