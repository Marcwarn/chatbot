#!/bin/bash
set -e

echo "🚀 Deploying to STAGING..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
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

# Step 1: Check if we're on the right branch
print_step "Checking git branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "staging" ] && [ "$CURRENT_BRANCH" != "develop" ]; then
    print_warning "Current branch is '$CURRENT_BRANCH'. Recommended: 'staging' or 'develop'"
    read -p "Continue anyway? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 1
    fi
fi

# Step 2: Check for uncommitted changes
print_step "Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes"
    git status --short
    read -p "Continue with uncommitted changes? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 1
    fi
fi

# Step 3: Run tests
print_step "Running test suite..."
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short; then
        print_success "All tests passed"
    else
        print_error "Tests failed!"
        read -p "Deploy anyway? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            exit 1
        fi
    fi
else
    print_warning "pytest not found, skipping tests"
fi

# Step 4: Security scan
print_step "Running security scan..."
if [ -f "security_scanner.py" ]; then
    if python security_scanner.py --json > scan-results.json 2>&1; then
        print_success "Security scan passed"
    else
        print_warning "Security scan found issues (check scan-results.json)"
        read -p "Continue anyway? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            exit 1
        fi
    fi
else
    print_warning "security_scanner.py not found, skipping security scan"
fi

# Step 5: Check Vercel CLI
print_step "Checking Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not installed"
    echo "Install with: npm i -g vercel"
    exit 1
fi

# Step 6: Deploy to Vercel
print_step "Deploying to Vercel Staging..."
echo "Using configuration from vercel-staging.json"

if [ -n "$VERCEL_TOKEN" ]; then
    # Use token if available
    vercel --prod --token=$VERCEL_TOKEN --yes
else
    # Interactive deployment
    vercel --prod
fi

# Step 7: Wait for deployment
print_step "Waiting for deployment to complete..."
sleep 5

# Step 8: Health check
print_step "Running health check..."
if command -v curl &> /dev/null; then
    if curl -f -s "${STAGING_URL}/api/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed!"
        echo "Please check the deployment manually"
        exit 1
    fi
else
    print_warning "curl not found, skipping health check"
fi

# Step 9: Run smoke tests (if available)
if [ -f "test_staging.sh" ]; then
    print_step "Running smoke tests..."
    if bash test_staging.sh; then
        print_success "Smoke tests passed"
    else
        print_warning "Smoke tests failed"
    fi
fi

# Success!
echo ""
echo "======================================"
print_success "Staging deployment complete!"
echo "======================================"
echo ""
echo "🌐 Staging URL: ${STAGING_URL}"
echo "📊 Admin Panel: ${STAGING_URL}/admin"
echo "💰 Cost Dashboard: ${STAGING_URL}/admin-costs"
echo ""
echo "Next steps:"
echo "  1. Test the staging environment thoroughly"
echo "  2. Verify all features work correctly"
echo "  3. Check cost tracking and monitoring"
echo "  4. If everything looks good, deploy to production"
echo ""
