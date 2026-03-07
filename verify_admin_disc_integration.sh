#!/bin/bash

echo "================================================================================"
echo "ADMIN PANEL DISC INTEGRATION - VERIFICATION SCRIPT"
echo "================================================================================"
echo ""

ERRORS=0

# Check file existence
echo "1. Checking file existence..."
echo "--------------------------------------------------------------------------------"

files=(
    "admin_analytics.py"
    "api_admin.py"
    "admin.html"
    "test_admin_analytics.py"
    "ADMIN_DISC_UPDATE.md"
    "ADMIN_CHANGES_SUMMARY.txt"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        ((ERRORS++))
    fi
done

echo ""
echo "2. Checking Python syntax..."
echo "--------------------------------------------------------------------------------"

python -m py_compile admin_analytics.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ admin_analytics.py - No syntax errors"
else
    echo "❌ admin_analytics.py - Syntax errors detected"
    ((ERRORS++))
fi

python -m py_compile api_admin.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ api_admin.py - No syntax errors"
else
    echo "❌ api_admin.py - Syntax errors detected"
    ((ERRORS++))
fi

echo ""
echo "3. Running automated tests..."
echo "--------------------------------------------------------------------------------"

python test_admin_analytics.py > /tmp/test_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
    grep "ALL TESTS PASSED" /tmp/test_output.txt
else
    echo "❌ Tests failed"
    ((ERRORS++))
fi

echo ""
echo "4. Checking required functions in admin.html..."
echo "--------------------------------------------------------------------------------"

functions=(
    "loadDashboard"
    "loadDiscStats"
    "loadUsers"
    "filterUsers"
    "loadAssessments"
    "filterAssessments"
    "loadAnalytics"
)

for func in "${functions[@]}"; do
    if grep -q "function $func" admin.html; then
        echo "✅ Function $func exists"
    else
        echo "❌ Function $func missing"
        ((ERRORS++))
    fi
done

echo ""
echo "5. Checking required HTML elements..."
echo "--------------------------------------------------------------------------------"

elements=(
    "analytics-tab"
    "bigFiveCount"
    "discCount"
    "mostPopular"
    "avgD"
    "avgI"
    "avgS"
    "avgC-disc"
    "discProfiles"
    "userTypeFilter"
    "assessmentTypeFilter"
)

for elem in "${elements[@]}"; do
    if grep -q "id=\"$elem\"" admin.html; then
        echo "✅ Element #$elem exists"
    else
        echo "❌ Element #$elem missing"
        ((ERRORS++))
    fi
done

echo ""
echo "6. Checking API endpoint definitions..."
echo "--------------------------------------------------------------------------------"

endpoints=(
    "/stats/big-five"
    "/stats/disc"
    "/stats/comparison"
    "/stats/time-series"
    "/stats/users/demographics"
    "/stats/conversion-funnel"
    "/analytics/comprehensive"
)

for endpoint in "${endpoints[@]}"; do
    if grep -q "$endpoint" api_admin.py; then
        echo "✅ Endpoint $endpoint defined"
    else
        echo "❌ Endpoint $endpoint missing"
        ((ERRORS++))
    fi
done

echo ""
echo "7. Checking analytics module functions..."
echo "--------------------------------------------------------------------------------"

analytics_functions=(
    "get_big_five_stats"
    "get_disc_stats"
    "get_assessment_comparison"
    "get_time_series_data"
    "get_user_demographics_by_type"
    "get_completion_funnel"
    "generate_comprehensive_report"
)

for func in "${analytics_functions[@]}"; do
    if grep -q "def $func" admin_analytics.py; then
        echo "✅ Function $func exists"
    else
        echo "❌ Function $func missing"
        ((ERRORS++))
    fi
done

echo ""
echo "8. File sizes and line counts..."
echo "--------------------------------------------------------------------------------"

echo "admin_analytics.py: $(wc -l < admin_analytics.py) lines"
echo "api_admin.py: $(wc -l < api_admin.py) lines"
echo "admin.html: $(wc -l < admin.html) lines"
echo "test_admin_analytics.py: $(wc -l < test_admin_analytics.py) lines"

echo ""
echo "================================================================================"

if [ $ERRORS -eq 0 ]; then
    echo "✅ VERIFICATION SUCCESSFUL - All checks passed!"
    echo "================================================================================"
    exit 0
else
    echo "❌ VERIFICATION FAILED - $ERRORS error(s) detected"
    echo "================================================================================"
    exit 1
fi
