# Vercel Deployment Monitoring Setup

## Quick Start

### 1. Get Your Vercel Token

1. Go to https://vercel.com/account/tokens
2. Create a new token with name: "Deployment Monitor"
3. Copy the token (you'll only see it once!)

### 2. Set Environment Variables

```bash
# Required
export VERCEL_TOKEN='your-token-here'

# Optional (for team deployments)
export VERCEL_TEAM_ID='your-team-id'

# Optional (for alerts)
export SLACK_WEBHOOK_URL='your-slack-webhook'
export ALERT_EMAIL='your-email@example.com'
```

### 3. Run the Monitor

```bash
# Simple check
python3 vercel_monitor.py

# Detailed check with log analysis
python3 vercel_monitor.py --detailed

# JSON output for automation
python3 vercel_monitor.py --json

# Or use the automated script
./monitor_deployments.sh
```

---

## Features

### vercel_monitor.py

Python script for comprehensive deployment monitoring:

- **Deployment Tracking**: Monitor recent deployments
- **Issue Detection**: Identify failed deployments and warnings
- **Performance Metrics**: Track build times and success rates
- **Log Analysis**: Parse build logs for common issues
- **Health Reporting**: Generate detailed health reports

### monitor_deployments.sh

Bash automation script with alerting:

- **Automated Monitoring**: Run scheduled checks
- **Alert Integration**: Slack, email notifications
- **Report Archival**: Keep deployment history
- **Status Exit Codes**: Integration with CI/CD

### VERCEL_DEPLOYMENT_GUIDE.md

Complete troubleshooting guide:

- **Issue Identification**: Known problems and solutions
- **Performance Optimization**: Speed up deployments
- **Best Practices**: Configuration recommendations
- **Metrics Tracking**: KPIs to monitor

---

## Monitoring Metrics

### Key Performance Indicators

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Success Rate | 99%+ | <95% |
| Build Time | <5s | >30s |
| Deploy Time | <10s | >60s |
| Cache Hit Rate | >80% | <50% |
| Error Count | 0 | >0 |

### Health Status Levels

- **HEALTHY**: All deployments successful, no warnings
- **WARNING**: Some warnings present, but deployments working
- **DEGRADED**: Failed deployments or critical issues

---

## Integration with CI/CD

### GitHub Actions

```yaml
name: Monitor Deployments

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Run monitor
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: ./monitor_deployments.sh

      - name: Upload report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: deployment-report
          path: deployment-report*.txt
```

### Cron Job

```bash
# Add to crontab (crontab -e)
# Run every hour
0 * * * * cd /path/to/chatbot && ./monitor_deployments.sh >> /var/log/vercel-monitor.log 2>&1
```

---

## Alert Configuration

### Slack Notifications

1. Create a Slack app: https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook URL to channel
4. Set `SLACK_WEBHOOK_URL` environment variable

### Email Alerts

Requires `mailx` or similar:

```bash
# Install mailx (Ubuntu/Debian)
sudo apt-get install mailutils

# Configure
export ALERT_EMAIL='devops@example.com'
```

### Custom Webhooks

Modify `monitor_deployments.sh` to add custom alerting:

```bash
# Example: Send to Discord
if [ ! -z "$DISCORD_WEBHOOK_URL" ]; then
    curl -X POST "$DISCORD_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"content\":\"Deployment alert!\"}"
fi
```

---

## Troubleshooting

### "VERCEL_TOKEN not set" Error

```bash
# Check if token is set
echo $VERCEL_TOKEN

# Set token
export VERCEL_TOKEN='your-token-here'

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export VERCEL_TOKEN="your-token-here"' >> ~/.bashrc
source ~/.bashrc
```

### "No deployments found" Error

1. Verify token has correct permissions
2. Check if team_id is needed
3. Verify API access:

```bash
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
     https://api.vercel.com/v6/deployments
```

### Import Error: requests module

```bash
# Install requests
pip install requests

# Or use requirements.txt
pip install -r requirements.txt
```

### Permission Denied on Scripts

```bash
# Make scripts executable
chmod +x monitor_deployments.sh
chmod +x vercel_monitor.py
```

---

## API Usage Examples

### Python

```python
from vercel_monitor import VercelMonitor
import os

# Initialize monitor
monitor = VercelMonitor(os.getenv('VERCEL_TOKEN'))

# Get recent deployments
deployments = monitor.get_deployments(limit=5)

# Analyze specific deployment
analysis = monitor.analyze_deployment(deployments[0])
print(f"Status: {analysis['state']}")
print(f"Build time: {analysis['build_time_seconds']}s")

# Generate health report
report = monitor.generate_report(detailed=True)
print(f"Health: {report['health_status']}")
print(f"Success rate: {report['summary']['success_rate']}%")
```

### Command Line

```bash
# Get JSON report
python3 vercel_monitor.py --json | jq '.summary'

# Check health status
python3 vercel_monitor.py | grep "Status:"

# Extract warnings
python3 vercel_monitor.py | grep -A 5 "Warnings"

# Monitor continuously
watch -n 300 ./monitor_deployments.sh  # Every 5 minutes
```

---

## Best Practices

### 1. Regular Monitoring

- Schedule automated checks (hourly or daily)
- Review reports weekly
- Track trends over time

### 2. Alert Fatigue Prevention

- Set appropriate thresholds
- Group similar alerts
- Use severity levels (info, warning, critical)

### 3. Metrics Collection

- Archive reports for historical analysis
- Track build time trends
- Monitor cache hit rates
- Measure deployment frequency

### 4. Incident Response

1. Alert triggers
2. Check monitoring report
3. Review deployment logs
4. Apply fixes from VERCEL_DEPLOYMENT_GUIDE.md
5. Verify resolution
6. Document lessons learned

### 5. Security

- Store tokens in environment variables, not code
- Rotate tokens regularly (every 90 days)
- Use read-only tokens when possible
- Limit token scope to necessary permissions

---

## Advanced Features

### Custom Metrics

Extend `vercel_monitor.py` to track custom metrics:

```python
def get_custom_metrics(self, deployment_id: str) -> Dict:
    """Get custom metrics like function duration, memory usage"""
    # Add your custom logic here
    pass
```

### Multi-Environment Monitoring

Monitor production and staging separately:

```bash
# Production
VERCEL_TOKEN=$PROD_TOKEN python3 vercel_monitor.py

# Staging
VERCEL_TOKEN=$STAGING_TOKEN python3 vercel_monitor.py
```

### Integration with Monitoring Tools

- **Datadog**: Send metrics via API
- **New Relic**: Custom events
- **Prometheus**: Export metrics endpoint
- **Grafana**: Visualization dashboards

---

## Resources

- [Vercel API Documentation](https://vercel.com/docs/rest-api)
- [Deployment Events](https://vercel.com/docs/rest-api/endpoints/deployments#list-deployment-events)
- [Build Configuration](https://vercel.com/docs/build-step)
- [Monitoring Best Practices](https://vercel.com/docs/observability)

---

## Support

For issues with the monitoring system:

1. Check logs: `deployment-report.txt`
2. Verify token and permissions
3. Review VERCEL_DEPLOYMENT_GUIDE.md
4. Check Vercel API status: https://vercel-status.com
