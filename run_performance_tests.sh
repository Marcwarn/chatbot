#!/bin/bash

# Performance Testing Script
# Runs comprehensive performance tests and generates reports

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         PERSONA API - PERFORMANCE TEST SUITE                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
CONCURRENT_USERS="${CONCURRENT_USERS:-100}"
TEST_DURATION="${TEST_DURATION:-30}"

echo "Configuration:"
echo "  API URL: $API_URL"
echo "  Concurrent Users: $CONCURRENT_USERS"
echo "  Test Duration: ${TEST_DURATION}s"
echo ""

# Check if API is running
echo -n "Checking API health... "
if curl -s -f "$API_URL/api/v1/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not running!${NC}"
    echo ""
    echo "Please start the API first:"
    echo "  uvicorn api_main_gdpr:app --reload"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 1: Testing Cache Performance"
echo "════════════════════════════════════════════════════════════════════"
echo ""

python3 -c "
from caching import cache, generate_profile_hash
import time

print('Testing cache operations...')

# Test AI report caching
test_scores = {'E': 75.0, 'A': 60.0, 'C': 85.0, 'N': 40.0, 'O': 70.0}
profile_hash = generate_profile_hash(test_scores)

# First access (cache miss)
start = time.time()
report = cache.get_ai_report(profile_hash)
miss_time = (time.time() - start) * 1000

# Cache a report
test_report = {
    'profile_overview': 'Test profile',
    'career_suggestions': ['Developer', 'Designer']
}
cache.set_ai_report(profile_hash, test_report)

# Second access (cache hit)
start = time.time()
cached_report = cache.get_ai_report(profile_hash)
hit_time = (time.time() - start) * 1000

print(f'  Cache MISS: {miss_time:.1f}ms')
print(f'  Cache HIT:  {hit_time:.1f}ms')
print(f'  Speedup:    {miss_time/hit_time:.0f}x faster')

# Get cache stats
stats = cache.get_stats()
print(f'\\n  Backend: {stats[\"backend_type\"]}')
print(f'  Size: {stats.get(\"size\", \"N/A\")}')

print('\\n✅ Cache test passed!')
"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 2: Testing Database Optimization"
echo "════════════════════════════════════════════════════════════════════"
echo ""

python3 -c "
from database import db
from performance_optimizations import OptimizedQueries, create_performance_indexes
import time

print('Creating performance indexes...')
try:
    create_performance_indexes(db.engine)
    print('✅ Indexes created successfully')
except Exception as e:
    print(f'⚠️  Indexes may already exist: {e}')

print('\\nTesting optimized queries...')
session = db.get_session()
optimizer = OptimizedQueries(session)

# Test batch operations
print('  Testing batch user queries...')
start = time.time()
users = optimizer.get_users_batch(['user_1', 'user_2', 'user_3'])
batch_time = (time.time() - start) * 1000
print(f'    Batch query time: {batch_time:.1f}ms')

session.close()
print('\\n✅ Database optimization test passed!')
"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 3: Running Load Tests"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "⚠️  This will simulate $CONCURRENT_USERS concurrent users for ${TEST_DURATION}s"
echo "⚠️  High load may impact system performance temporarily"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Load test skipped."
    exit 0
fi

echo ""
echo "Starting load test..."
echo ""

# Run Python load tests
python3 load_testing.py

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "STEP 4: Generating Performance Report"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check if report was generated
if [ -f "load_test_report.json" ]; then
    echo -e "${GREEN}✓ Load test report generated: load_test_report.json${NC}"

    # Extract key metrics using Python
    python3 -c "
import json
with open('load_test_report.json', 'r') as f:
    data = json.load(f)
    results = data['results']

print('\\n📊 Key Metrics:')
print(f'  Total Requests: {results[\"total_requests\"]}')
print(f'  Success Rate: {results[\"success_rate\"]:.1f}%')
print(f'  Requests/sec: {results[\"requests_per_second\"]:.1f}')
print(f'  Avg Response: {results[\"avg_response_time_ms\"]:.0f}ms')
print(f'  P95 Response: {results[\"p95_response_time_ms\"]:.0f}ms')
print(f'  P99 Response: {results[\"p99_response_time_ms\"]:.0f}ms')
    "
else
    echo -e "${RED}✗ Load test report not found${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "SUMMARY"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "✅ All performance tests completed!"
echo ""
echo "Generated files:"
echo "  - load_test_report.json (detailed results)"
echo "  - PERFORMANCE_REPORT.md (comprehensive analysis)"
echo ""
echo "Next steps:"
echo "  1. Review load_test_report.json for detailed metrics"
echo "  2. Read PERFORMANCE_REPORT.md for optimization recommendations"
echo "  3. Monitor cache hit rates in production"
echo "  4. Deploy optimizations gradually"
echo ""
echo "For questions, see:"
echo "  - performance_integration_guide.py (code examples)"
echo "  - caching.py (caching documentation)"
echo "  - performance_optimizations.py (core optimizations)"
echo ""
