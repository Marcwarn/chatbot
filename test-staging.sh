#!/bin/bash
set -e

echo "🧪 Testing STAGING environment..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STAGING_URL="https://persona-assessment-staging.vercel.app"

# Function to print colored output
print_test() {
    echo -e "${YELLOW}▶ Testing: $1${NC}"
}

print_error() {
    echo -e "${RED}  ✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
}

# Track test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_test "$test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        print_success "$test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "$test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "curl is required but not installed"
    exit 1
fi

echo ""
echo "Testing API endpoints..."
echo "---"

# Test 1: Health Check
run_test "Health Check" "curl -f -s ${STAGING_URL}/api/health"

# Test 2: Assessment Endpoint
run_test "Assessment Endpoint" "curl -f -s ${STAGING_URL}/api/assessments"

# Test 3: Admin Page
run_test "Admin Page" "curl -f -s ${STAGING_URL}/admin"

# Test 4: Admin Costs Page
run_test "Admin Costs Page" "curl -f -s ${STAGING_URL}/admin-costs"

# Test 5: DISC Assessment Page
run_test "DISC Assessment Page" "curl -f -s ${STAGING_URL}/disc"

# Test 6: Main Page
run_test "Main Page" "curl -f -s ${STAGING_URL}/"

# Test 7: Demo Page
run_test "Demo Page" "curl -f -s ${STAGING_URL}/demo"

echo ""
echo "Testing API functionality..."
echo "---"

# Test 8: Create Session
run_test "Create Session" "curl -f -s -X POST ${STAGING_URL}/api/session"

# Test 9: CORS Headers
print_test "CORS Headers"
CORS_RESPONSE=$(curl -s -I ${STAGING_URL}/api/health)
if echo "$CORS_RESPONSE" | grep -i "access-control-allow" > /dev/null; then
    print_success "CORS Headers"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "CORS Headers"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test 10: Response Time
print_test "Response Time"
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' ${STAGING_URL}/api/health)
RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d'.' -f1)
if [ $RESPONSE_MS -lt 2000 ]; then
    print_success "Response Time (${RESPONSE_MS}ms)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "Response Time too slow (${RESPONSE_MS}ms)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "Testing Security..."
echo "---"

# Test 11: Security Headers
print_test "Security Headers"
SECURITY_HEADERS=$(curl -s -I ${STAGING_URL}/)
HEADERS_OK=true

if ! echo "$SECURITY_HEADERS" | grep -i "x-content-type-options" > /dev/null; then
    HEADERS_OK=false
fi

if [ "$HEADERS_OK" = true ]; then
    print_success "Security Headers"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "Security Headers missing"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test 12: HTTPS Redirect
print_test "HTTPS Redirect"
if curl -s -I ${STAGING_URL}/ | grep -i "strict-transport-security" > /dev/null; then
    print_success "HTTPS configured"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "HTTPS not fully configured"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "Testing Environment Configuration..."
echo "---"

# Test 13: Environment Detection
print_test "Environment Detection"
ENV_RESPONSE=$(curl -s ${STAGING_URL}/api/health)
if echo "$ENV_RESPONSE" | grep -i "staging" > /dev/null; then
    print_success "Staging environment detected"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "Environment not properly configured"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test 14: Debug Mode
print_test "Debug Mode"
if echo "$ENV_RESPONSE" | grep -i "debug.*true" > /dev/null; then
    print_success "Debug mode enabled (expected for staging)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "Debug mode configuration issue"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Results Summary
echo ""
echo "======================================"
echo "Test Results Summary"
echo "======================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

# Calculate percentage
PASS_PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Pass Rate: ${PASS_PERCENTAGE}%"
echo ""

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Staging environment is ready for testing."
    echo "If everything looks good, you can proceed to production deployment."
    exit 0
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    echo ""
    echo "Please fix the issues before proceeding to production."
    exit 1
fi
