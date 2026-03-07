# Cost Tracking System - Quick Start Guide

Get started with the cost tracking and optimization system in 5 minutes.

## ⚡ Quick Setup

### 1. Verify Installation (30 seconds)

Run the verification script:
```bash
python verify_cost_system.py
```

You should see:
```
✅ Cost tracking system is operational!
📊 Current Metrics: ...
💡 Optimization Potential: ...
```

### 2. Configure Budget (1 minute)

Set your monthly budget via API:

```bash
# Replace YOUR_ADMIN_TOKEN with your actual admin token
curl -X POST "http://localhost:8000/api/admin/costs/budget/configure" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_budget": 500.00,
    "alert_thresholds": [50, 80, 100]
  }'
```

Or use Python:
```python
from budget_alerts import budget_monitor

# Set monthly budget
budget_monitor.set_budget(500.00)

# Configure alerts at 50%, 80%, 100%
budget_monitor.set_alert_thresholds([50, 80, 100])
```

### 3. Check Current Status (30 seconds)

Get cost summary:
```bash
curl "http://localhost:8000/api/admin/costs/summary" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Response:
```json
{
  "today": 12.50,
  "this_week": 87.25,
  "this_month": 342.80,
  "projected_monthly": 450.00,
  "budget": 500.00,
  "budget_status": "yellow",
  "top_cost_drivers": [...]
}
```

## 📊 Essential Endpoints

### Check Budget Status
```bash
GET /api/admin/costs/budget/status
```

### Get Cost Trends (30 days)
```bash
GET /api/admin/costs/trends?days=30
```

### Get Optimization Suggestions
```bash
GET /api/admin/costs/optimizations?days=30
```

### Get Anthropic API Stats
```bash
GET /api/admin/costs/anthropic/stats?days=30
```

## 🎯 Common Tasks

### Task 1: Check Daily Costs

```python
from cost_tracker import cost_tracker

daily = cost_tracker.get_daily_costs()
print(f"Today: ${daily['total']:.2f}")
print(f"  Anthropic: ${daily['anthropic']:.2f}")
print(f"  Database:  ${daily['database']:.2f}")
```

### Task 2: Get Optimization Ideas

```python
from cost_optimizer import cost_optimizer

optimizations = cost_optimizer.suggest_optimizations(days=30)

for opt in optimizations[:3]:  # Top 3
    print(f"{opt.title}")
    print(f"  Savings: ${opt.potential_savings:.2f}/month")
    print(f"  Actions: {opt.action_items[0]}")
```

### Task 3: Monitor Budget

```python
from budget_alerts import budget_monitor

status = budget_monitor.check_budget_status()

print(f"Budget: ${status.budget:.2f}")
print(f"Spent:  ${status.current_spend:.2f} ({status.percentage_used:.1f}%)")
print(f"Status: {status.alert_level.value}")
print(f"Daily burn: ${status.daily_burn_rate:.2f}")
```

### Task 4: Analyze Costs

```python
from cost_analytics import cost_analytics

# Cost per assessment
metrics = cost_analytics.calculate_cost_per_assessment(days=30)
print(f"Avg cost: ${metrics['avg_cost_per_assessment']:.4f}/assessment")

# ROI (if you have revenue)
roi = cost_analytics.calculate_roi(revenue_per_assessment=2.00)
print(f"ROI: {roi['roi_percentage']:.1f}%")
print(f"Profit/assessment: ${roi['profit_per_assessment']:.4f}")
```

## 🚨 Budget Alerts

### Setup Email Alerts

```python
from budget_alerts import budget_monitor
import smtplib
from email.message import EmailMessage

def send_email_alert(alert):
    """Send email when budget alert triggered"""
    msg = EmailMessage()
    msg['Subject'] = f'Budget Alert - {alert.alert_level.value.upper()}'
    msg['From'] = 'noreply@yourapp.com'
    msg['To'] = 'admin@yourapp.com'
    msg.set_content(alert.message)

    # Send email (configure your SMTP settings)
    # with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    #     smtp.send_message(msg)

    print(f"📧 Alert email sent: {alert.message}")

# Register callback
budget_monitor.register_alert_callback(send_email_alert)

# Test alert
budget_monitor.send_alert_if_needed(force=True)
```

### Setup Slack Alerts

```python
import requests

def send_slack_alert(alert):
    """Send Slack notification"""
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"

    color = {
        "green": "good",
        "yellow": "warning",
        "orange": "warning",
        "red": "danger"
    }[alert.alert_level.value]

    payload = {
        "attachments": [{
            "color": color,
            "title": f"💰 Budget Alert - {alert.alert_level.value.upper()}",
            "text": alert.message,
            "fields": [
                {"title": "Current Spend", "value": f"${alert.current_spend:.2f}", "short": True},
                {"title": "Budget", "value": f"${alert.budget:.2f}", "short": True}
            ]
        }]
    }

    requests.post(webhook_url, json=payload)

budget_monitor.register_alert_callback(send_slack_alert)
```

## 📈 Dashboard Integration

Access the admin dashboard:

1. Navigate to: `http://localhost:8000/admin.html`
2. Login with admin credentials
3. Click "Cost Monitoring" tab

You'll see:
- Real-time cost metrics
- Budget progress bar
- Cost trends chart
- Top cost drivers
- Optimization suggestions

## 🔍 Monitoring Best Practices

### Daily (2 minutes)
```bash
# Check today's costs
curl http://localhost:8000/api/admin/costs/summary | jq '.today'

# Check budget status
curl http://localhost:8000/api/admin/costs/budget/status | jq '.alert_level'
```

### Weekly (5 minutes)
```bash
# Review cost trends
curl http://localhost:8000/api/admin/costs/trends?days=7

# Check optimization suggestions
curl http://localhost:8000/api/admin/costs/optimizations?days=7

# Review Anthropic stats
curl http://localhost:8000/api/admin/costs/anthropic/stats?days=7
```

### Monthly (15 minutes)
```bash
# Generate comprehensive report
curl http://localhost:8000/api/admin/costs/analytics/comprehensive?days=30

# Check anomalies
curl http://localhost:8000/api/admin/costs/analytics/anomalies?days=30

# Review forecast
curl http://localhost:8000/api/admin/costs/analytics/forecast?days_ahead=30
```

## 🎓 Pro Tips

### Tip 1: Set Realistic Budget
```python
# Start conservative, adjust based on usage
budget_monitor.set_budget(500.00)  # Month 1
# budget_monitor.set_budget(400.00)  # Month 2 (after optimization)
```

### Tip 2: Monitor Cache Hit Rate
```python
stats = cost_tracker.get_anthropic_stats(7)
if stats['cache_hit_rate'] < 50:
    print("⚠️  Cache hit rate low - review caching strategy")
```

### Tip 3: Track Cost Per Assessment
```python
metrics = cost_analytics.calculate_cost_per_assessment(30)
target = 0.10  # $0.10 per assessment

if metrics['avg_cost_per_assessment'] > target:
    print(f"⚠️  Above target: ${metrics['avg_cost_per_assessment']:.4f} vs ${target:.4f}")
```

### Tip 4: Export Data for Analysis
```python
# Export to JSON
data = cost_tracker.export_data()
with open('cost_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Import later
with open('cost_data.json', 'r') as f:
    data = json.load(f)
cost_tracker.import_data(data)
```

## 🐛 Troubleshooting

### Problem: No costs being tracked

**Solution:**
```python
# Check if tracking is working
from cost_tracker import cost_tracker

# Manually track a test call
cost = cost_tracker.track_anthropic_call(
    model="claude-sonnet-4-5-20250929",
    input_tokens=100,
    output_tokens=50,
    purpose="report_generation"
)

print(f"Test cost: ${cost:.4f}")
```

### Problem: Budget alerts not triggering

**Solution:**
```python
from budget_alerts import budget_monitor

# Verify budget is set
status = budget_monitor.check_budget_status()
print(f"Budget: ${status.budget}")

if status.budget == 0:
    budget_monitor.set_budget(500.00)

# Force alert check
alert = budget_monitor.send_alert_if_needed(force=True)
if alert:
    print(f"Alert triggered: {alert.message}")
```

### Problem: Inaccurate cost calculations

**Solution:**
```python
# Verify pricing is current
from cost_tracker import CostTracker

tracker = CostTracker()
print("Anthropic pricing:")
print(tracker.ANTHROPIC_PRICING)

# Update if needed (in cost_tracker.py)
```

## 📚 Next Steps

1. **Read full documentation:** `COST_TRACKING_README.md`
2. **Review complete summary:** `COST_SYSTEM_SUMMARY.md`
3. **Run verification:** `python verify_cost_system.py`
4. **Run tests:** `pytest test_cost_tracking.py -v`
5. **Explore API:** Visit `/docs` endpoint

## 🆘 Support

- **Documentation:** `COST_TRACKING_README.md`
- **Summary:** `COST_SYSTEM_SUMMARY.md`
- **Tests:** `test_cost_tracking.py`
- **Verification:** `verify_cost_system.py`
- **API Docs:** http://localhost:8000/docs

---

**Ready to start?** Run `python verify_cost_system.py` to verify everything is working! ✅
