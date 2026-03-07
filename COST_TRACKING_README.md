

# Cost Tracking & Optimization System

Comprehensive cost monitoring and optimization for the personality assessment application.

## Overview

The cost tracking system provides:
- **Real-time cost tracking** for all API calls and services
- **Budget monitoring** with configurable alerts
- **AI-powered optimization** recommendations
- **Advanced analytics** with forecasting and anomaly detection
- **Admin dashboard integration** for visibility

## Architecture

### Core Components

```
cost_tracker.py          # Real-time cost tracking
cost_optimizer.py        # Optimization recommendations
budget_alerts.py         # Budget monitoring & alerts
cost_analytics.py        # Advanced analytics & forecasting
api_admin_costs.py       # Admin API endpoints
database.py              # Cost tracking models (APIUsage, CostBudget, CostAlert)
```

### Data Flow

```
API Call (e.g., Claude)
    ↓
cost_tracker.track_anthropic_call()
    ↓
Store in memory + aggregate metrics
    ↓
budget_monitor.check_budget_status()
    ↓
Send alerts if thresholds exceeded
```

## Setup

### 1. Database Migration

The cost tracking models are already integrated into `database.py`. Run database migration:

```python
from database import db
db.create_tables()
```

### 2. Configure Budget

Set your monthly budget via admin API:

```bash
curl -X POST "https://your-api.com/api/admin/costs/budget/configure" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_budget": 500.00,
    "alert_thresholds": [50, 80, 100]
  }'
```

### 3. Integration

Cost tracking is automatically integrated into:
- **Report generation** (`api_main_gdpr.py`)
- **Chat conversations** (`personality_coach.py`)
- **DISC assessments** (if applicable)

## API Endpoints

### Cost Summary

```http
GET /api/admin/costs/summary
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "today": 12.50,
  "this_week": 87.25,
  "this_month": 342.80,
  "projected_monthly": 450.00,
  "budget": 500.00,
  "budget_status": "yellow",
  "top_cost_drivers": [
    {
      "feature": "Report Generation",
      "cost": 280.40,
      "percentage": 81.8
    }
  ]
}
```

### Cost Breakdown

```http
GET /api/admin/costs/breakdown?period=month
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "period": "month",
  "total_cost": 342.80,
  "by_service": {
    "Anthropic API": 320.50,
    "Database": 15.30,
    "Hosting": 7.00
  },
  "by_feature": {
    "Report Generation": 280.40,
    "Chat": 35.20,
    "Admin Analytics": 12.10
  }
}
```

### Cost Trends

```http
GET /api/admin/costs/trends?days=30
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "date": "2026-03-01",
    "total": 10.50,
    "anthropic": 9.80,
    "database": 0.50,
    "hosting": 0.20
  },
  ...
]
```

### Optimization Suggestions

```http
GET /api/admin/costs/optimizations?days=30
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "category": "caching",
    "priority": "high",
    "title": "Increase Cache Hit Rate",
    "description": "Current cache hit rate is 35%. Increasing to 60% could save $180/month.",
    "current_cost": 320.00,
    "potential_savings": 180.00,
    "implementation_effort": "easy",
    "impact": "Reduces API costs by caching frequently requested reports",
    "action_items": [
      "Increase cache TTL from 1h to 24h",
      "Implement cache warming",
      "Add cache metrics to dashboard"
    ]
  }
]
```

### Budget Status

```http
GET /api/admin/costs/budget/status
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "current_spend": 342.80,
  "budget": 500.00,
  "percentage_used": 68.6,
  "projected_monthly": 456.00,
  "alert_level": "yellow",
  "days_into_month": 15,
  "days_remaining": 16,
  "daily_burn_rate": 22.85,
  "recommended_daily_budget": 9.83
}
```

### Anthropic API Statistics

```http
GET /api/admin/costs/anthropic/stats?days=30
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_calls": 1250,
  "total_cost": 320.50,
  "total_input_tokens": 1500000,
  "total_output_tokens": 850000,
  "avg_tokens_per_call": 1880,
  "avg_cost_per_call": 0.2564,
  "cache_hit_rate": 35.2,
  "cost_by_feature": {
    "report_generation": 280.40,
    "chat": 35.20,
    "admin_analytics": 4.90
  },
  "calls_by_model": {
    "claude-sonnet-4-5-20250929": {
      "count": 1250,
      "cost": 320.50
    }
  }
}
```

### Cost Anomalies

```http
GET /api/admin/costs/analytics/anomalies?days=30&sensitivity=2.0
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "timestamp": "2026-03-05T14:23:00Z",
    "type": "spike",
    "severity": "high",
    "description": "Cost spike detected on 2026-03-05",
    "current_value": 45.80,
    "expected_value": 12.50,
    "deviation_percentage": 266.4,
    "suggested_actions": [
      "Review API calls for this date",
      "Check for unusual user activity",
      "Verify no duplicate report generations"
    ]
  }
]
```

### Cost Forecast

```http
GET /api/admin/costs/analytics/forecast?days_ahead=30&method=linear
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "status": "success",
  "method": "linear",
  "historical_days": 30,
  "forecast_days": 30,
  "current_daily_avg": 11.25,
  "forecasted_daily_avg": 12.10,
  "current_month_cost": 342.80,
  "projected_month_end": 705.80,
  "confidence": "medium",
  "forecast": [
    {
      "date": "2026-03-16",
      "forecasted_cost": 12.05
    },
    ...
  ]
}
```

## Pricing Configuration

Current pricing (as of 2026-03):

### Anthropic API

```python
ANTHROPIC_PRICING = {
    "claude-sonnet-4-5-20250929": {
        "input": 0.003,   # $ per 1K tokens
        "output": 0.015,  # $ per 1K tokens
    },
    "claude-opus-4": {
        "input": 0.015,
        "output": 0.075,
    },
    "claude-haiku-3-5": {
        "input": 0.001,
        "output": 0.005,
    }
}
```

### Database (Vercel Postgres)

```python
DATABASE_PRICING = {
    "storage_per_gb": 0.25,      # $ per GB per month
    "compute_per_hour": 0.01,    # $ per compute hour
    "query_cost": 0.000001,      # $ per query
}
```

### Hosting (Vercel)

```python
HOSTING_PRICING = {
    "bandwidth_per_gb": 0.15,
    "function_exec": 0.00002,
    "function_gb_hour": 0.0000185,
}
```

## Optimization Strategies

### 1. Increase Cache Hit Rate

**Current:** 30-40%
**Target:** 60%+
**Potential Savings:** $180-250/month

**Actions:**
- Increase cache TTL from 1h to 24h
- Implement cache warming for popular assessments
- Use Redis for distributed caching in production

### 2. Optimize Prompts

**Current:** ~2,500 tokens per report
**Target:** 1,500-1,800 tokens
**Potential Savings:** $120-150/month

**Actions:**
- Review and compress system prompts
- Remove redundant instructions
- Use more efficient prompt engineering

### 3. Model Selection

**Current:** Claude Sonnet for all features
**Target:** Use appropriate models per feature
**Potential Savings:** $200-300/month

**Actions:**
- Use Haiku for simple chat responses
- Keep Sonnet for report generation
- Only use Opus if quality requires it

### 4. Streaming Responses

**Cost Impact:** Neutral (improves UX)

**Actions:**
- Implement streaming for chat
- Add loading indicators
- Improve perceived response time

### 5. Batch Processing

**Current:** Real-time processing
**Target:** Queue non-urgent requests
**Potential Savings:** $50-80/month

**Actions:**
- Implement job queue
- Batch similar requests
- Process during off-peak hours

## Budget Alerts

Configure budget alerts to prevent cost overruns:

```python
from budget_alerts import budget_monitor

# Set monthly budget
budget_monitor.set_budget(500.00)

# Configure alert thresholds
budget_monitor.set_alert_thresholds([50, 80, 100])

# Register custom alert callback
def email_alert(alert):
    send_email(
        to="admin@example.com",
        subject=f"Budget Alert - {alert.alert_level.value}",
        body=alert.message
    )

budget_monitor.register_alert_callback(email_alert)
```

### Alert Levels

- **Green:** <50% of budget used
- **Yellow:** 50-80% of budget used
- **Orange:** 80-100% of budget used
- **Red:** >100% or projected to exceed

## Analytics Features

### Cost Per User

```python
from cost_analytics import cost_analytics

metrics = cost_analytics.calculate_cost_per_user(days=30)
print(f"Avg cost per user: ${metrics['avg_cost_per_user']}")
```

### Cost Per Assessment

```python
metrics = cost_analytics.calculate_cost_per_assessment(days=30)
print(f"Avg cost per assessment: ${metrics['avg_cost_per_assessment']}")
```

### ROI Analysis

```python
roi = cost_analytics.calculate_roi(revenue_per_assessment=2.00)
print(f"ROI: {roi['roi_percentage']}%")
print(f"Profit per assessment: ${roi['profit_per_assessment']}")
```

### Anomaly Detection

```python
anomalies = cost_analytics.identify_cost_anomalies(days=30, sensitivity=2.0)
for anomaly in anomalies:
    print(f"{anomaly.type}: {anomaly.description}")
```

### Cost Forecasting

```python
forecast = cost_analytics.forecast_costs(days_ahead=30, method="linear")
print(f"Projected month-end: ${forecast['projected_month_end']}")
```

## Testing

Run the comprehensive test suite:

```bash
pytest test_cost_tracking.py -v
```

**Test Coverage:**
- ✅ Cost calculation accuracy
- ✅ Cache hit rate tracking
- ✅ Budget alert thresholds
- ✅ Anomaly detection
- ✅ Forecasting algorithms
- ✅ ROI calculations
- ✅ Export/import functionality

## Monitoring Dashboard

The cost tracking system integrates with the admin dashboard at `/admin.html`:

**Cost Overview Section:**
- Real-time cost metrics
- Budget progress bar
- Cost trends chart (Chart.js)
- Top cost drivers (pie chart)
- Optimization suggestions

**Access:**
1. Navigate to `/admin.html`
2. Login with admin credentials
3. Select "Cost Monitoring" tab

## Production Deployment

### Environment Variables

```bash
# Set budget (optional, can be configured via API)
MONTHLY_BUDGET=500.00

# Alert email (optional)
BUDGET_ALERT_EMAIL=admin@example.com
```

### Persistence

For production, consider persisting cost data:

```python
# Export data periodically
data = cost_tracker.export_data()
save_to_database(data)  # Your persistence logic

# Import on startup
saved_data = load_from_database()
cost_tracker.import_data(saved_data)
```

### Scheduled Jobs

Set up cron jobs for:

1. **Daily budget check:**
   ```bash
   0 9 * * * curl https://your-api.com/api/admin/costs/budget/status
   ```

2. **Weekly optimization report:**
   ```bash
   0 9 * * 1 curl https://your-api.com/api/admin/costs/optimizations
   ```

3. **Monthly cost export:**
   ```bash
   0 0 1 * * curl https://your-api.com/api/admin/costs/export
   ```

## Troubleshooting

### Issue: Costs not being tracked

**Check:**
1. Verify `cost_tracker` is imported in API files
2. Check that `track_anthropic_call()` is called after API responses
3. Verify API response includes `usage` object

### Issue: Budget alerts not triggering

**Check:**
1. Verify budget is configured: `budget_monitor.check_budget_status()`
2. Check alert thresholds are set
3. Verify alert callbacks are registered
4. Check alert cooldown period (6 hours default)

### Issue: Inaccurate cost calculations

**Check:**
1. Verify pricing constants in `cost_tracker.py` are current
2. Check token counts from API responses
3. Verify cache hit detection logic

## Future Enhancements

- [ ] Database persistence for cost history
- [ ] Slack/email alert integration
- [ ] Multi-currency support
- [ ] Custom cost allocation tags
- [ ] Advanced ML-based forecasting
- [ ] Cost allocation by user/team
- [ ] Automated optimization actions
- [ ] Integration with billing systems

## Support

For questions or issues:
- Check this README
- Review test suite for examples
- Check API documentation: `/docs`
- Contact: admin@example.com

---

**Last Updated:** 2026-03-07
**Version:** 1.0.0
**License:** MIT
