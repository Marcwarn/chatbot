#!/bin/bash

# Monitor Vercel Deployments
# Automated monitoring script for Vercel deployment health

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_FILE="deployment-report.txt"
JSON_REPORT="deployment-report.json"
ALERT_THRESHOLD=95  # Success rate threshold for alerts

echo -e "${BLUE}🔍 Vercel Deployment Monitor${NC}"
echo "================================"
echo ""

# Check if VERCEL_TOKEN is set
if [ -z "$VERCEL_TOKEN" ]; then
    echo -e "${RED}❌ ERROR: VERCEL_TOKEN environment variable not set${NC}"
    echo ""
    echo "To set up monitoring:"
    echo "1. Get your token from: https://vercel.com/account/tokens"
    echo "2. Export it: export VERCEL_TOKEN='your-token-here'"
    echo "3. Run this script again"
    exit 1
fi

# Check if vercel_monitor.py exists
if [ ! -f "vercel_monitor.py" ]; then
    echo -e "${RED}❌ ERROR: vercel_monitor.py not found${NC}"
    echo "Please ensure the monitoring script is in the current directory."
    exit 1
fi

# Check if requests library is available
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing required dependencies...${NC}"
    pip install requests -q
fi

# Run the monitoring script
echo -e "${BLUE}📊 Fetching deployment data...${NC}"

if python3 vercel_monitor.py > "$REPORT_FILE" 2>&1; then
    MONITOR_EXIT_CODE=0
else
    MONITOR_EXIT_CODE=$?
fi

# Also generate JSON report for programmatic access
python3 vercel_monitor.py --json > "$JSON_REPORT" 2>&1 || true

# Display the report
cat "$REPORT_FILE"

# Parse health status
if grep -q "DEGRADED" "$REPORT_FILE"; then
    echo -e "${RED}⚠️  ALERT: Deployment health degraded!${NC}"
    echo ""

    # Extract key metrics
    if [ -f "$JSON_REPORT" ]; then
        echo "📧 Sending alerts..."

        # Example: Send Slack notification (configure webhook URL)
        if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
            curl -X POST "$SLACK_WEBHOOK_URL" \
                -H 'Content-Type: application/json' \
                -d "{\"text\":\"🚨 Vercel deployment health degraded! Check deployment logs.\"}" \
                2>/dev/null || echo "Failed to send Slack notification"
        fi

        # Example: Send email (requires mailx or similar)
        if command -v mailx &> /dev/null && [ ! -z "$ALERT_EMAIL" ]; then
            echo "Vercel deployment health degraded. See attached report." | \
                mailx -s "Vercel Deployment Alert" -a "$REPORT_FILE" "$ALERT_EMAIL" || \
                echo "Failed to send email notification"
        fi
    fi

elif grep -q "WARNING" "$REPORT_FILE"; then
    echo -e "${YELLOW}⚠️  WARNING: Deployment warnings detected${NC}"
    echo "Review the warnings above and take corrective action."

elif grep -q "HEALTHY" "$REPORT_FILE"; then
    echo -e "${GREEN}✅ All deployments healthy${NC}"

else
    echo -e "${YELLOW}⚠️  Unable to determine deployment status${NC}"
fi

# Check success rate
if [ -f "$JSON_REPORT" ]; then
    SUCCESS_RATE=$(python3 -c "import json; data=json.load(open('$JSON_REPORT')); print(data.get('summary', {}).get('success_rate', 100))" 2>/dev/null || echo "100")

    if (( $(echo "$SUCCESS_RATE < $ALERT_THRESHOLD" | bc -l) )); then
        echo -e "${RED}⚠️  Success rate ($SUCCESS_RATE%) below threshold ($ALERT_THRESHOLD%)${NC}"
    fi
fi

echo ""
echo "================================"
echo -e "${BLUE}📝 Reports saved:${NC}"
echo "   - Text: $REPORT_FILE"
echo "   - JSON: $JSON_REPORT"
echo ""

# Cleanup old reports (keep last 7 days)
find . -name "deployment-report-*.txt" -mtime +7 -delete 2>/dev/null || true
find . -name "deployment-report-*.json" -mtime +7 -delete 2>/dev/null || true

# Archive current reports with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cp "$REPORT_FILE" "deployment-report-$TIMESTAMP.txt" 2>/dev/null || true
cp "$JSON_REPORT" "deployment-report-$TIMESTAMP.json" 2>/dev/null || true

exit $MONITOR_EXIT_CODE
