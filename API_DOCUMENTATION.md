# 📡 API Documentation - Complete Reference

## Table of Contents
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Big Five Endpoints](#big-five-endpoints)
- [DISC Endpoints](#disc-endpoints)
- [GDPR Endpoints](#gdpr-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)
- [Code Examples](#code-examples)

---

## API Overview

### Base URL

```
Production:  https://your-app.vercel.app
Development: http://localhost:8000
```

### API Version

Current Version: **v1**

All endpoints are prefixed with `/api/v1/`

---

### Content Type

All requests and responses use JSON:

```http
Content-Type: application/json
```

---

### Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Authentication

### Public Endpoints

No authentication required:
- Assessment endpoints (start, submit, get result)
- GDPR endpoints (export, delete)
- Health check

### Admin Endpoints

Require Bearer token authentication:

```http
Authorization: Bearer <ADMIN_API_KEY>
```

**Get Admin API Key:**
Set in environment variables: `ADMIN_API_KEY`

---

## Big Five Endpoints

### 1. Start Big Five Assessment

Start a new Big Five personality assessment using validated IPIP-50 questions.

**Endpoint:**
```http
POST /api/v1/assessment/start
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "assessment_type": "big_five",
  "language": "sv",
  "num_questions": 50
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| user_id | string | Yes | - | Unique user identifier |
| assessment_type | string | Yes | - | Must be "big_five" |
| language | string | No | "sv" | "sv" or "en" |
| num_questions | integer | No | 50 | Number of questions (10-50) |

**Response:** 200 OK
```json
{
  "assessment_id": "assess_user123_20260307100000",
  "assessment_type": "big_five",
  "language": "sv",
  "total_questions": 50,
  "created_at": "2026-03-07T10:00:00Z",
  "questions": [
    {
      "question_id": 1,
      "question_text": "Jag är den som pratar mest på en fest",
      "scale_type": "likert",
      "options": [
        "1 - Stämmer inte alls",
        "2 - Stämmer dåligt",
        "3 - Neutral",
        "4 - Stämmer ganska bra",
        "5 - Stämmer helt"
      ],
      "dimension": "E"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 50
  }'
```

---

### 2. Submit Big Five Answers

Submit completed Big Five assessment answers for analysis.

**Endpoint:**
```http
POST /api/v1/assessment/submit
```

**Request Body:**
```json
{
  "assessment_id": "assess_user123_20260307100000",
  "answers": [
    {
      "question_id": 1,
      "answer": 4
    },
    {
      "question_id": 2,
      "answer": 2
    }
  ]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| assessment_id | string | Yes | Assessment ID from start endpoint |
| answers | array | Yes | Array of answer objects |
| answers[].question_id | integer | Yes | Question ID (1-50) |
| answers[].answer | integer | Yes | Answer value (1-5) |

**Response:** 200 OK
```json
{
  "assessment_id": "assess_user123_20260307100000",
  "user_id": "user_123",
  "assessment_type": "big_five",
  "completed_at": "2026-03-07T10:15:00Z",
  "scores": [
    {
      "dimension": "E",
      "score": 75.5,
      "percentile": 82,
      "interpretation": "Du drar energi från att vara med andra. Du är social, pratsam och trivs naturligt i centrum."
    },
    {
      "dimension": "A",
      "score": 60.0,
      "percentile": 65,
      "interpretation": "Du balanserar samarbete med självhävdelse och navigerar sociala situationer med pragmatism."
    }
  ],
  "summary": "Din personlighet präglas av utåtriktadhet och social kompetens...",
  "detailed_analysis": "Baserat på dina svar visar du...",
  "strengths": [
    "Utmärkt kommunikationsförmåga",
    "Teamorienterad",
    "Anpassningsbar"
  ],
  "development_areas": [
    "Kan behöva mer fokus på detaljer",
    "Planering och struktur"
  ],
  "recommendations": [
    "Utnyttja din sociala förmåga i ledarroller",
    "Arbeta med en mer strukturerad arbetsstil"
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/submit \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "assess_user123_20260307100000",
    "answers": [
      {"question_id": 1, "answer": 4},
      {"question_id": 2, "answer": 2}
    ]
  }'
```

---

### 3. Get Big Five Result

Retrieve a previously completed Big Five assessment result.

**Endpoint:**
```http
GET /api/v1/assessment/result/{assessment_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| assessment_id | string | Yes | Assessment ID |

**Response:** 200 OK
```json
{
  "assessment_id": "assess_user123_20260307100000",
  "user_id": "user_123",
  "assessment_type": "big_five",
  "completed_at": "2026-03-07T10:15:00Z",
  "scores": [...],
  "summary": "...",
  "detailed_analysis": "...",
  "strengths": [...],
  "development_areas": [...],
  "recommendations": [...]
}
```

**cURL Example:**
```bash
curl https://your-app.vercel.app/api/v1/assessment/result/assess_user123_20260307100000
```

---

## DISC Endpoints

### 1. Start DISC Assessment

Start a new DISC behavioral assessment with AI-generated questions.

**Endpoint:**
```http
POST /api/v1/assessment/start
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "assessment_type": "disc",
  "language": "sv",
  "num_questions": 24
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| user_id | string | Yes | - | Unique user identifier |
| assessment_type | string | Yes | - | Must be "disc" |
| language | string | No | "sv" | "sv" or "en" |
| num_questions | integer | No | 24 | Number of questions (12-48) |

**Response:** 200 OK
```json
{
  "assessment_id": "assess_user123_20260307110000",
  "assessment_type": "disc",
  "language": "sv",
  "total_questions": 24,
  "created_at": "2026-03-07T11:00:00Z",
  "questions": [
    {
      "question_id": 1,
      "question_text": "Jag tar gärna ledningen i projekt",
      "scale_type": "likert",
      "options": [
        "1 - Stämmer inte alls",
        "2 - Stämmer dåligt",
        "3 - Neutral",
        "4 - Stämmer ganska bra",
        "5 - Stämmer helt"
      ],
      "dimension": "D"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "assessment_type": "disc",
    "language": "sv",
    "num_questions": 24
  }'
```

---

### 2. Submit DISC Answers

Submit completed DISC assessment answers for behavioral analysis.

**Endpoint:**
```http
POST /api/v1/assessment/submit
```

**Request Body:**
```json
{
  "assessment_id": "assess_user123_20260307110000",
  "answers": [
    {
      "question_id": 1,
      "answer": 5
    },
    {
      "question_id": 2,
      "answer": 3
    }
  ]
}
```

**Response:** 200 OK
```json
{
  "assessment_id": "assess_user123_20260307110000",
  "user_id": "user_123",
  "assessment_type": "disc",
  "completed_at": "2026-03-07T11:15:00Z",
  "scores": [
    {
      "dimension": "D",
      "score": 85.0,
      "percentile": 90,
      "interpretation": "Du är resultatinriktad och tar gärna ledningen. Du fokuserar på att uppnå mål snabbt."
    },
    {
      "dimension": "I",
      "score": 70.0,
      "percentile": 75,
      "interpretation": "Du är utåtriktad och entusiastisk. Du trivs med att prata inför grupper."
    },
    {
      "dimension": "S",
      "score": 30.0,
      "percentile": 25,
      "interpretation": "Du föredrar förändring framför stabilitet och tar initiativ till nya projekt."
    },
    {
      "dimension": "C",
      "score": 45.0,
      "percentile": 50,
      "interpretation": "Du balanserar detaljer med helhetsbilden och är pragmatisk."
    }
  ],
  "summary": "Din DISC-profil visar en dynamisk ledare (hög D, hög I)...",
  "detailed_analysis": "Med höga D- och I-värden är du en driven, social person...",
  "strengths": [
    "Driver projekt framåt",
    "Inspirerar team",
    "Fattar snabba beslut"
  ],
  "development_areas": [
    "Lyssna mer på teamet",
    "Öka tålamod med processer"
  ],
  "recommendations": [
    "Delegera detaljarbete",
    "Para ihop med S-profiler för balans"
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/submit \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "assess_user123_20260307110000",
    "answers": [
      {"question_id": 1, "answer": 5},
      {"question_id": 2, "answer": 3}
    ]
  }'
```

---

### 3. Get DISC Result

Retrieve a previously completed DISC assessment result.

**Endpoint:**
```http
GET /api/v1/assessment/result/{assessment_id}
```

Same as Big Five result endpoint - the response format is identical, just with DISC dimensions (D, I, S, C) instead of Big Five (E, A, C, N, O).

---

### 4. Get Assessment Types

Get information about available assessment types.

**Endpoint:**
```http
GET /api/v1/assessment/types
```

**Response:** 200 OK
```json
{
  "assessment_types": [
    {
      "id": "big_five",
      "name": "Big Five (OCEAN)",
      "description": "Mäter fem huvuddimensioner av personlighet: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism",
      "dimensions": 5,
      "recommended_questions": 50
    },
    {
      "id": "disc",
      "name": "DISC",
      "description": "Mäter beteendeprofil baserat på Dominance, Influence, Steadiness, Conscientiousness",
      "dimensions": 4,
      "recommended_questions": 24
    }
  ]
}
```

**cURL Example:**
```bash
curl https://your-app.vercel.app/api/v1/assessment/types
```

---

## GDPR Endpoints

### 1. Give/Withdraw Consent

Manage user consent for data processing.

**Endpoint:**
```http
POST /api/v1/gdpr/consent
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "consent_type": "data_processing",
  "consent_given": true,
  "purpose": "Personality assessment analysis",
  "legal_basis": "consent"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User ID |
| consent_type | string | Yes | Type: data_processing, storage, ai_analysis |
| consent_given | boolean | Yes | true or false |
| purpose | string | Yes | Purpose of data processing |
| legal_basis | string | Yes | Legal basis: consent, legitimate_interest |

**Response:** 200 OK
```json
{
  "status": "success",
  "consent": {
    "user_id": "user_123",
    "consent_type": "data_processing",
    "consent_given": true,
    "consent_date": "2026-03-07T10:00:00Z",
    "purpose": "Personality assessment analysis",
    "legal_basis": "consent",
    "policy_version": "1.0"
  }
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/gdpr/consent \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "consent_type": "data_processing",
    "consent_given": true,
    "purpose": "Personality assessment analysis",
    "legal_basis": "consent"
  }'
```

---

### 2. Export User Data

Export all user data (Right to Access - GDPR Article 15).

**Endpoint:**
```http
POST /api/v1/gdpr/export
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "email": "user@example.com"
}
```

**Response:** 200 OK
```json
{
  "user_id": "user_123",
  "export_date": "2026-03-07T10:00:00Z",
  "data": {
    "user_info": {
      "user_id": "user_123",
      "created_at": "2026-01-01T00:00:00Z",
      "last_active": "2026-03-07T09:00:00Z",
      "data_retention_days": 365
    },
    "consents": [
      {
        "consent_type": "data_processing",
        "consent_given": true,
        "consent_date": "2026-01-01T00:00:00Z"
      }
    ],
    "assessments": [
      {
        "assessment_id": "assess_user123_20260307100000",
        "assessment_type": "big_five",
        "status": "completed",
        "created_at": "2026-03-07T10:00:00Z",
        "completed_at": "2026-03-07T10:15:00Z",
        "result": {
          "scores": [...],
          "summary": "..."
        }
      },
      {
        "assessment_id": "assess_user123_20260307110000",
        "assessment_type": "disc",
        "status": "completed",
        "created_at": "2026-03-07T11:00:00Z",
        "completed_at": "2026-03-07T11:15:00Z",
        "result": {
          "scores": [...],
          "summary": "..."
        }
      }
    ]
  }
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/gdpr/export \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "email": "user@example.com"
  }'
```

---

### 3. Delete User Data

Request deletion of all user data (Right to Erasure - GDPR Article 17).

**Endpoint:**
```http
POST /api/v1/gdpr/delete
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "email": "user@example.com",
  "reason": "User requested account deletion"
}
```

**Response:** 200 OK
```json
{
  "status": "success",
  "message": "Deletion request received. Verification email sent.",
  "verification_token": "verify_abc123xyz",
  "deletion_request_id": 42
}
```

**Verification Endpoint:**
```http
POST /api/v1/gdpr/delete/verify
```

**Request Body:**
```json
{
  "verification_token": "verify_abc123xyz"
}
```

**Response:** 200 OK
```json
{
  "status": "success",
  "message": "User data successfully deleted",
  "deleted_at": "2026-03-07T10:30:00Z"
}
```

**cURL Example:**
```bash
# Request deletion
curl -X POST https://your-app.vercel.app/api/v1/gdpr/delete \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "email": "user@example.com",
    "reason": "User requested account deletion"
  }'

# Verify deletion
curl -X POST https://your-app.vercel.app/api/v1/gdpr/delete/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verification_token": "verify_abc123xyz"
  }'
```

---

### 4. Get User Consents

Retrieve all consents for a user.

**Endpoint:**
```http
GET /api/v1/gdpr/consent/{user_id}
```

**Response:** 200 OK
```json
{
  "user_id": "user_123",
  "consents": [
    {
      "consent_type": "data_processing",
      "consent_given": true,
      "consent_date": "2026-01-01T00:00:00Z",
      "purpose": "Personality assessment analysis",
      "legal_basis": "consent",
      "policy_version": "1.0"
    },
    {
      "consent_type": "ai_analysis",
      "consent_given": true,
      "consent_date": "2026-01-01T00:00:00Z",
      "purpose": "AI-powered personality insights",
      "legal_basis": "consent",
      "policy_version": "1.0"
    }
  ]
}
```

**cURL Example:**
```bash
curl https://your-app.vercel.app/api/v1/gdpr/consent/user_123
```

---

## Admin Endpoints

### 1. Admin Login

Authenticate as admin to access protected endpoints.

**Endpoint:**
```http
POST /api/v1/admin/login
```

**Request Body:**
```json
{
  "password": "admin_password"
}
```

**Response:** 200 OK
```json
{
  "status": "success",
  "token": "admin_token_abc123",
  "expires_at": "2026-03-08T10:00:00Z"
}
```

**cURL Example:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "password": "your_admin_password"
  }'
```

---

### 2. Get System Stats

Get system-wide statistics (requires admin auth).

**Endpoint:**
```http
GET /api/v1/admin/stats
```

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response:** 200 OK
```json
{
  "total_users": 1234,
  "total_assessments": 2456,
  "assessments_by_type": {
    "big_five": 1500,
    "disc": 956
  },
  "assessments_today": 45,
  "assessments_this_week": 234,
  "assessments_this_month": 890,
  "active_users_today": 23,
  "consent_rate": 98.5,
  "completion_rate": 87.3,
  "average_time_to_complete": {
    "big_five": 1245,
    "disc": 980
  }
}
```

**cURL Example:**
```bash
curl https://your-app.vercel.app/api/v1/admin/stats \
  -H "Authorization: Bearer admin_token_abc123"
```

---

### 3. Get All Assessments

Get list of all assessments with filtering (requires admin auth).

**Endpoint:**
```http
GET /api/v1/admin/assessments
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status: in_progress, completed |
| assessment_type | string | No | Filter by type: big_five, disc |
| limit | integer | No | Limit results (default: 100) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response:** 200 OK
```json
{
  "total": 2456,
  "limit": 100,
  "offset": 0,
  "assessments": [
    {
      "assessment_id": "assess_user123_20260307100000",
      "user_id": "user_123",
      "assessment_type": "big_five",
      "status": "completed",
      "created_at": "2026-03-07T10:00:00Z",
      "completed_at": "2026-03-07T10:15:00Z"
    }
  ]
}
```

**cURL Example:**
```bash
curl "https://your-app.vercel.app/api/v1/admin/assessments?assessment_type=disc&status=completed&limit=50" \
  -H "Authorization: Bearer admin_token_abc123"
```

---

### 4. Get Security Events

Get security events and alerts (requires admin auth).

**Endpoint:**
```http
GET /api/v1/admin/security
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| hours | integer | No | Events from last N hours (default: 24) |
| severity | string | No | Filter by severity: low, medium, high, critical |
| event_type | string | No | Filter by type: rate_limit, brute_force, etc. |

**Response:** 200 OK
```json
{
  "total_events": 156,
  "events": [
    {
      "id": 1,
      "event_type": "rate_limit_exceeded",
      "severity": "medium",
      "client_ip": "203.0.113.45",
      "endpoint": "/api/v1/assessment/start",
      "timestamp": "2026-03-07T09:45:00Z",
      "was_blocked": true,
      "block_duration": 3600
    }
  ],
  "blocked_ips": [
    {
      "ip_address": "203.0.113.45",
      "reason": "rate_limit_exceeded",
      "block_count": 3,
      "unblock_at": "2026-03-07T11:00:00Z"
    }
  ]
}
```

**cURL Example:**
```bash
curl "https://your-app.vercel.app/api/v1/admin/security?hours=24&severity=high" \
  -H "Authorization: Bearer admin_token_abc123"
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

### Error Response Format

```json
{
  "detail": "Detailed error message",
  "error_code": "INVALID_ASSESSMENT_TYPE",
  "status_code": 400
}
```

---

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| INVALID_ASSESSMENT_TYPE | Unknown assessment type | Use "big_five" or "disc" |
| ASSESSMENT_NOT_FOUND | Assessment ID not found | Check assessment_id |
| INCOMPLETE_ANSWERS | Not all questions answered | Submit all required answers |
| INVALID_ANSWER_VALUE | Answer out of range | Use values 1-5 for Likert |
| USER_NOT_FOUND | User ID not found | Check user_id |
| CONSENT_REQUIRED | Consent not given | Request user consent first |
| RATE_LIMIT_EXCEEDED | Too many requests | Wait and retry |
| INVALID_CREDENTIALS | Admin auth failed | Check admin password/token |

---

## Rate Limiting

### Limits by Endpoint

| Endpoint | Limit | Window | Notes |
|----------|-------|--------|-------|
| /assessment/start | 10 req | 1 hour | Per IP |
| /assessment/submit | 20 req | 1 hour | Per IP |
| /assessment/result/* | 100 req | 1 hour | Per IP |
| /gdpr/* | 10 req | 1 hour | Per IP |
| /admin/* | 100 req | 1 hour | Per token |

---

### Rate Limit Headers

Response includes rate limit headers:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1709809200
```

---

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded. Try again in 45 minutes.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "status_code": 429,
  "retry_after": 2700
}
```

---

## Code Examples

### Python (requests)

```python
import requests

API_URL = "https://your-app.vercel.app"

# 1. Start Big Five assessment
response = requests.post(f"{API_URL}/api/v1/assessment/start", json={
    "user_id": "user_123",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 50
})

data = response.json()
assessment_id = data["assessment_id"]
questions = data["questions"]

# 2. Collect answers
answers = []
for question in questions:
    print(f"\n{question['question_text']}")
    for i, option in enumerate(question['options'], 1):
        print(f"{i}. {option}")

    user_answer = int(input("Your answer (1-5): "))

    answers.append({
        "question_id": question["question_id"],
        "answer": user_answer
    })

# 3. Submit answers
response = requests.post(f"{API_URL}/api/v1/assessment/submit", json={
    "assessment_id": assessment_id,
    "answers": answers
})

result = response.json()

# 4. Display results
print("\n=== YOUR RESULTS ===")
print(f"\nSummary: {result['summary']}")

print("\nScores:")
for score in result['scores']:
    print(f"  {score['dimension']}: {score['score']:.1f}/100")
    print(f"  → {score['interpretation']}\n")

print("\nStrengths:")
for strength in result['strengths']:
    print(f"  • {strength}")

print("\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")
```

---

### JavaScript (fetch)

```javascript
const API_URL = "https://your-app.vercel.app";

// 1. Start DISC assessment
async function startDISCAssessment(userId) {
  const response = await fetch(`${API_URL}/api/v1/assessment/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      assessment_type: 'disc',
      language: 'sv',
      num_questions: 24
    })
  });

  const data = await response.json();
  return data;
}

// 2. Submit answers
async function submitAnswers(assessmentId, answers) {
  const response = await fetch(`${API_URL}/api/v1/assessment/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      assessment_id: assessmentId,
      answers: answers
    })
  });

  const result = await response.json();
  return result;
}

// 3. Get result
async function getResult(assessmentId) {
  const response = await fetch(
    `${API_URL}/api/v1/assessment/result/${assessmentId}`
  );

  const result = await response.json();
  return result;
}

// Example usage
(async () => {
  // Start assessment
  const assessment = await startDISCAssessment('user_123');
  console.log('Assessment started:', assessment.assessment_id);

  // Collect answers (example)
  const answers = [
    { question_id: 1, answer: 5 },
    { question_id: 2, answer: 3 },
    // ... more answers
  ];

  // Submit
  const result = await submitAnswers(assessment.assessment_id, answers);
  console.log('Results:', result);
})();
```

---

### TypeScript (axios)

```typescript
import axios from 'axios';

const API_URL = "https://your-app.vercel.app";

interface AssessmentStartRequest {
  user_id: string;
  assessment_type: 'big_five' | 'disc';
  language: 'sv' | 'en';
  num_questions: number;
}

interface AssessmentStartResponse {
  assessment_id: string;
  assessment_type: string;
  questions: Question[];
  total_questions: number;
  created_at: string;
}

interface Question {
  question_id: number;
  question_text: string;
  scale_type: string;
  options: string[];
  dimension: string;
}

interface Answer {
  question_id: number;
  answer: number;
}

interface AssessmentResult {
  assessment_id: string;
  scores: Score[];
  summary: string;
  strengths: string[];
  recommendations: string[];
}

interface Score {
  dimension: string;
  score: number;
  percentile: number;
  interpretation: string;
}

class AssessmentAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async startAssessment(
    request: AssessmentStartRequest
  ): Promise<AssessmentStartResponse> {
    const response = await axios.post(
      `${this.baseURL}/api/v1/assessment/start`,
      request
    );
    return response.data;
  }

  async submitAnswers(
    assessmentId: string,
    answers: Answer[]
  ): Promise<AssessmentResult> {
    const response = await axios.post(
      `${this.baseURL}/api/v1/assessment/submit`,
      {
        assessment_id: assessmentId,
        answers: answers
      }
    );
    return response.data;
  }

  async getResult(assessmentId: string): Promise<AssessmentResult> {
    const response = await axios.get(
      `${this.baseURL}/api/v1/assessment/result/${assessmentId}`
    );
    return response.data;
  }
}

// Usage
const api = new AssessmentAPI(API_URL);

(async () => {
  const assessment = await api.startAssessment({
    user_id: 'user_123',
    assessment_type: 'big_five',
    language: 'sv',
    num_questions: 50
  });

  console.log('Started:', assessment.assessment_id);

  // Collect answers...
  const answers: Answer[] = [
    { question_id: 1, answer: 4 },
    { question_id: 2, answer: 2 }
  ];

  const result = await api.submitAnswers(assessment.assessment_id, answers);
  console.log('Results:', result);
})();
```

---

### cURL Examples

**Start Big Five:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 50
  }'
```

**Start DISC:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "assessment_type": "disc",
    "language": "sv",
    "num_questions": 24
  }'
```

**Submit Answers:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/assessment/submit \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "assess_user123_20260307100000",
    "answers": [
      {"question_id": 1, "answer": 4},
      {"question_id": 2, "answer": 2}
    ]
  }'
```

**Export User Data:**
```bash
curl -X POST https://your-app.vercel.app/api/v1/gdpr/export \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "email": "user@example.com"
  }'
```

**Admin Stats:**
```bash
curl https://your-app.vercel.app/api/v1/admin/stats \
  -H "Authorization: Bearer admin_token_abc123"
```

---

## Webhooks (Future Feature)

*Planned for v2:*

Configure webhooks to receive notifications when assessments are completed:

```json
POST /api/v1/webhooks/register
{
  "url": "https://your-app.com/webhook",
  "events": ["assessment.completed"],
  "secret": "your_webhook_secret"
}
```

---

## API Changelog

### v1.0.0 (2026-03-07)
- Initial release
- Big Five IPIP-50 assessment
- DISC assessment with AI generation
- GDPR compliance endpoints
- Admin dashboard API

---

## Support

**Documentation:** https://docs.persona-assessment.com
**API Status:** https://status.persona-assessment.com
**Email:** support@persona-assessment.com

---

**Last Updated:** March 7, 2026
**API Version:** 1.0.0
**License:** MIT
