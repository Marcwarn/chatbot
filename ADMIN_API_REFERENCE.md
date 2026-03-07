# Admin API Reference - DISC Integration

Quick reference for all admin endpoints supporting both Big Five and DISC assessments.

## Authentication

All endpoints require admin authentication via Bearer token:

```bash
Authorization: Bearer <admin_token>
```

Get token via login:
```bash
POST /api/admin/login
{
  "password": "your_admin_password"
}
```

---

## Dashboard & Overview

### GET /api/admin/dashboard
Get comprehensive dashboard statistics.

**Response:**
```json
{
  "total_assessments": 100,
  "total_users": 50,
  "total_chat_messages": 200,
  "assessments_last_24h": 5,
  "assessments_last_7d": 30,
  "big_five_count": 60,
  "disc_count": 40,
  "avg_completion_rate": 95.0,
  "top_dimensions": {
    "E": 65.5,
    "A": 70.2,
    "C": 68.8,
    "N": 55.3,
    "O": 72.1
  },
  "api_health": "healthy",
  "most_popular_type": "big_five"
}
```

---

## Assessment Statistics

### GET /api/admin/stats/big-five
Get detailed Big Five analytics.

**Response:**
```json
{
  "total": 60,
  "avg_scores": {
    "E": 65.5,
    "A": 70.2,
    "C": 68.8,
    "N": 55.3,
    "O": 72.1
  },
  "score_distribution": {
    "E": {"high": 30, "average": 25, "low": 5},
    "A": {"high": 35, "average": 20, "low": 5}
  },
  "completion_rate": 95.0
}
```

### GET /api/admin/stats/disc
Get detailed DISC analytics with profile distribution.

**Response:**
```json
{
  "total": 40,
  "avg_scores": {
    "D": 55.0,
    "I": 60.5,
    "S": 50.2,
    "C": 58.8
  },
  "profile_distribution": {
    "D": 12,
    "I": 8,
    "S": 10,
    "C": 6,
    "Di": 4
  },
  "dominant_profiles": [
    {"profile": "D", "count": 12, "percentage": 30.0},
    {"profile": "S", "count": 10, "percentage": 25.0},
    {"profile": "I", "count": 8, "percentage": 20.0}
  ],
  "completion_rate": 95.0
}
```

### GET /api/admin/stats/comparison
Compare Big Five vs DISC assessments.

**Response:**
```json
{
  "total_assessments": 100,
  "big_five": {
    "count": 60,
    "percentage": 60.0
  },
  "disc": {
    "count": 40,
    "percentage": 40.0
  },
  "other": {
    "count": 0,
    "percentage": 0.0
  },
  "most_popular": "big_five"
}
```

---

## Time Series & Trends

### GET /api/admin/stats/time-series?days=30
Get daily assessment breakdown.

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "period_days": 30,
  "data_points": [
    {
      "date": "2026-03-01",
      "big_five": 3,
      "disc": 2,
      "other": 0
    },
    {
      "date": "2026-03-02",
      "big_five": 5,
      "disc": 1,
      "other": 0
    }
  ],
  "total_in_period": 150
}
```

---

## User Management

### GET /api/admin/users?assessment_type={type}
Get list of users with optional filtering.

**Parameters:**
- `assessment_type` (optional): Filter by type ("big_five", "disc")
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "user_id": "user_abc123",
    "assessments_count": 5,
    "big_five_count": 3,
    "disc_count": 2,
    "last_activity": "2026-03-07T10:30:00",
    "last_assessment_type": "disc",
    "consents": {
      "data_processing": true
    },
    "has_chat_profile": true
  }
]
```

### GET /api/admin/users/{user_id}/export?assessment_type={type}
Export user data with optional type filtering.

**Parameters:**
- `assessment_type` (optional): Filter export ("big_five", "disc")

**Response:**
```json
{
  "user_id": "user_abc123",
  "export_date": "2026-03-07T10:30:00",
  "export_filter": "all",
  "profile": {
    "assessments_count": 5,
    "consents": {}
  },
  "assessments": {
    "total": 5,
    "big_five": {
      "count": 3,
      "data": [...]
    },
    "disc": {
      "count": 2,
      "data": [...]
    }
  },
  "chat_profile": null
}
```

### DELETE /api/admin/users/{user_id}
Delete all user data (GDPR compliance).

**Response:**
```json
{
  "message": "User data deleted for user_abc123",
  "deleted": ["user_profile", "assessments", "chat_profile"],
  "timestamp": "2026-03-07T10:30:00"
}
```

---

## Assessment Management

### GET /api/admin/assessments?assessment_type={type}
Get list of assessments with optional filtering.

**Parameters:**
- `assessment_type` (optional): Filter by type ("big_five", "disc")
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "assessment_id": "assess_xyz789",
    "user_id": "user_abc123",
    "assessment_type": "disc",
    "completed_at": "2026-03-07T10:30:00",
    "scores": {
      "D": 75,
      "I": 60,
      "S": 45,
      "C": 55
    },
    "language": "sv"
  }
]
```

---

## User Analytics

### GET /api/admin/stats/users/demographics
Get user behavior patterns by assessment type.

**Response:**
```json
{
  "total_users": 50,
  "preference_distribution": {
    "big_five": 25,
    "disc": 20,
    "both": 5
  },
  "avg_assessments_per_user": 2.5,
  "users_with_both_types": 5
}
```

### GET /api/admin/stats/conversion-funnel
Get conversion rates for assessment types.

**Response:**
```json
{
  "big_five": {
    "started": 65,
    "completed": 60,
    "completion_rate": 92.3
  },
  "disc": {
    "started": 45,
    "completed": 40,
    "completion_rate": 88.9
  }
}
```

---

## Comprehensive Analytics

### GET /api/admin/analytics/comprehensive
Get complete analytics report (all metrics).

**Response:**
```json
{
  "generated_at": "2026-03-07T10:30:00",
  "overview": {
    "total_assessments": 100,
    "big_five": {"count": 60, "percentage": 60.0},
    "disc": {"count": 40, "percentage": 40.0},
    "most_popular": "big_five"
  },
  "big_five": {
    "total": 60,
    "avg_scores": {...}
  },
  "disc": {
    "total": 40,
    "avg_scores": {...},
    "dominant_profiles": [...]
  },
  "trends": {
    "last_24h": {...},
    "last_7d": {...},
    "time_series_30d": {...}
  },
  "users": {
    "total_users": 50,
    "preference_distribution": {...}
  },
  "conversion": {
    "big_five": {...},
    "disc": {...}
  }
}
```

---

## Configuration

### GET /api/admin/config
Get current service configuration.

**Response:**
```json
{
  "api_key_configured": true,
  "chat_enabled": true,
  "ai_reports_enabled": true,
  "gdpr_mode": "strict",
  "max_tokens_chat": 1500,
  "max_tokens_report": 4000
}
```

---

## Health Check

### GET /api/admin/health
Check admin service health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-07T10:30:00",
  "api_configured": true,
  "active_sessions": 3,
  "total_assessments": 100
}
```

---

## Session Management

### POST /api/admin/login
Login to admin panel.

**Request:**
```json
{
  "password": "your_admin_password"
}
```

**Response:**
```json
{
  "token": "abc123xyz789...",
  "expires_at": "2026-03-07T18:30:00",
  "message": "Login successful"
}
```

### POST /api/admin/logout
Logout and invalidate token.

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## DISC Profile Types

The system automatically detects DISC profiles:

**Pure Profiles:**
- `D` - Dominance (Direct, results-oriented)
- `I` - Influence (Enthusiastic, persuasive)
- `S` - Steadiness (Stable, patient)
- `C` - Conscientiousness (Analytical, precise)

**Combination Profiles:**
- `Di` - Dominance + Influence
- `DC` - Dominance + Conscientiousness
- `ID` - Influence + Dominance
- `IS` - Influence + Steadiness
- `SC` - Steadiness + Conscientiousness
- `SI` - Steadiness + Influence

Profile is determined by:
1. If one dimension is 10+ points higher: Pure profile
2. If two dimensions are close: Combination profile

---

## Error Responses

All endpoints return standard error responses:

**401 Unauthorized:**
```json
{
  "detail": "Missing or invalid authorization header"
}
```

**404 Not Found:**
```json
{
  "detail": "User not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

**Current:** No rate limiting (development)

**Recommended for Production:**
- Dashboard: 10 requests/minute
- Analytics: 5 requests/minute
- Export: 2 requests/minute
- Other endpoints: 30 requests/minute

---

## Examples

### Get DISC statistics
```bash
curl -H "Authorization: Bearer your_token" \
  http://localhost:8000/api/admin/stats/disc
```

### Filter users by assessment type
```bash
curl -H "Authorization: Bearer your_token" \
  "http://localhost:8000/api/admin/users?assessment_type=disc"
```

### Get time series for last 7 days
```bash
curl -H "Authorization: Bearer your_token" \
  "http://localhost:8000/api/admin/stats/time-series?days=7"
```

### Export user data (DISC only)
```bash
curl -H "Authorization: Bearer your_token" \
  "http://localhost:8000/api/admin/users/user_123/export?assessment_type=disc"
```

### Get comprehensive analytics report
```bash
curl -H "Authorization: Bearer your_token" \
  http://localhost:8000/api/admin/analytics/comprehensive \
  -o analytics_report.json
```

---

**Version:** 1.0
**Last Updated:** 2026-03-07
**Status:** Production Ready
