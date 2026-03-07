# 🏗️ System Architecture - Dual-Assessment Platform

## Table of Contents
- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Database Schema](#database-schema)
- [API Routing](#api-routing)
- [Shared Infrastructure](#shared-infrastructure)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Scalability Considerations](#scalability-considerations)

---

## Overview

The Persona Assessment Platform is a **dual-assessment system** supporting both **Big Five** and **DISC** personality assessments through a unified API and database infrastructure.

### Key Design Principles

1. **Unified Schema**: Single database schema supports both assessment types
2. **Shared Services**: Common authentication, GDPR, and security layers
3. **Modular Design**: Easy to add new assessment types
4. **GDPR-First**: Privacy and compliance built into architecture
5. **Serverless-Ready**: Designed for Vercel/AWS Lambda deployment

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Web Browser]
        B[Mobile App]
        C[Lovable UI]
    end

    subgraph "API Gateway"
        D[Vercel Edge Network]
        E[CORS Middleware]
        F[Rate Limiter]
    end

    subgraph "Application Layer"
        G[FastAPI App]
        H[Assessment Router]
        I[GDPR Router]
        J[Admin Router]
    end

    subgraph "Business Logic"
        K[Big Five Service]
        L[DISC Service]
        M[AI Analysis Service]
        N[Score Calculator]
    end

    subgraph "Data Layer"
        O[(PostgreSQL DB)]
        P[Redis Cache]
        Q[File Storage]
    end

    subgraph "External Services"
        R[Claude AI API]
        S[Sentry Monitoring]
        T[Email Service]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    G --> J
    H --> K
    H --> L
    K --> M
    L --> M
    M --> R
    K --> N
    L --> N
    H --> O
    I --> O
    J --> O
    G --> P
    G --> S
```

---

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ UserConsent : has
    User ||--o{ Assessment : owns
    User ||--o{ AuditLog : generates
    Assessment ||--o{ AssessmentQuestion : contains
    Assessment ||--o{ AssessmentAnswer : has
    Assessment ||--|| AssessmentResult : produces

    User {
        string id PK
        string email_hash
        datetime created_at
        datetime last_active
        int data_retention_days
        datetime delete_after
        boolean is_active
    }

    UserConsent {
        int id PK
        string user_id FK
        string consent_type
        boolean consent_given
        datetime consent_date
        datetime consent_withdrawn_date
        string purpose
        string legal_basis
        string policy_version
    }

    Assessment {
        string id PK
        string user_id FK
        enum assessment_type
        string language
        string status
        datetime created_at
        datetime completed_at
        boolean is_anonymized
    }

    AssessmentQuestion {
        int id PK
        string assessment_id FK
        int question_id
        text question_text
        string scale_type
        json options
        string dimension
    }

    AssessmentAnswer {
        int id PK
        string assessment_id FK
        int question_id
        string answer_value
        datetime answered_at
    }

    AssessmentResult {
        int id PK
        string assessment_id FK
        json scores
        text summary
        text detailed_analysis
        json strengths
        json development_areas
        json recommendations
        datetime created_at
    }

    AuditLog {
        int id PK
        string user_id FK
        string action
        string resource_type
        string resource_id
        json details
        string ip_address
        datetime timestamp
    }
```

---

### Assessment Type Enum

```python
class AssessmentType(enum.Enum):
    """Assessment type enumeration"""
    BIG_FIVE = "big_five"
    DISC = "disc"
```

This single enum field allows the same schema to support multiple assessment types.

---

### Key Tables

#### 1. Users Table
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,              -- Pseudonymous ID (e.g., "user_abc123")
    email_hash VARCHAR UNIQUE,           -- SHA-256 hash of email
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    data_retention_days INT DEFAULT 365,
    delete_after TIMESTAMP               -- Auto-delete date
);
```

**GDPR Features:**
- Pseudonymous IDs (not real names)
- Email stored as hash only
- Automatic deletion scheduling
- Audit trail support

---

#### 2. Assessments Table
```sql
CREATE TABLE assessments (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    assessment_type VARCHAR NOT NULL,    -- 'big_five' or 'disc'
    language VARCHAR DEFAULT 'sv',
    status VARCHAR DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    is_anonymized BOOLEAN DEFAULT FALSE
);
```

**Key Points:**
- `assessment_type` field enables dual-assessment support
- CASCADE delete ensures GDPR compliance
- `is_anonymized` flag for data protection

---

#### 3. Assessment Results Table
```sql
CREATE TABLE assessment_results (
    id SERIAL PRIMARY KEY,
    assessment_id VARCHAR UNIQUE REFERENCES assessments(id) ON DELETE CASCADE,
    scores JSON NOT NULL,                -- Flexible format for Big Five or DISC
    summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    strengths JSON NOT NULL,
    development_areas JSON NOT NULL,
    recommendations JSON NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**JSON Structure for Big Five:**
```json
{
  "scores": [
    {"dimension": "E", "score": 75.5, "percentile": 82, "interpretation": "..."},
    {"dimension": "A", "score": 60.0, "percentile": 65, "interpretation": "..."}
  ]
}
```

**JSON Structure for DISC:**
```json
{
  "scores": [
    {"dimension": "D", "score": 85.0, "percentile": 90, "interpretation": "..."},
    {"dimension": "I", "score": 70.0, "percentile": 75, "interpretation": "..."}
  ]
}
```

---

#### 4. Security Tables

```sql
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    client_ip VARCHAR NOT NULL,
    endpoint VARCHAR NOT NULL,
    user_id VARCHAR,
    user_agent VARCHAR,
    details JSON,
    timestamp TIMESTAMP DEFAULT NOW(),
    was_blocked BOOLEAN DEFAULT FALSE,
    block_duration INT
);

CREATE TABLE blocked_ips (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR UNIQUE NOT NULL,
    reason VARCHAR NOT NULL,
    block_count INT DEFAULT 1,
    first_blocked_at TIMESTAMP DEFAULT NOW(),
    last_blocked_at TIMESTAMP DEFAULT NOW(),
    unblock_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_permanent BOOLEAN DEFAULT FALSE
);
```

---

## API Routing

### Vercel Routing Configuration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

---

### FastAPI Router Structure

```python
# api_main_gdpr.py (main app)
app = FastAPI(
    title="Persona – Big Five Assessment API",
    version="3.0.0"
)

# Include sub-routers
app.include_router(gdpr_router)    # GDPR endpoints
app.include_router(admin_router)   # Admin endpoints

# Assessment endpoints (support both Big Five and DISC)
@app.post("/api/v1/assessment/start")
@app.post("/api/v1/assessment/submit")
@app.get("/api/v1/assessment/result/{assessment_id}")
```

---

### Endpoint Map

```mermaid
graph LR
    A[/ Root] --> B[Assessment Endpoints]
    A --> C[GDPR Endpoints]
    A --> D[Admin Endpoints]
    A --> E[Security Endpoints]

    B --> B1[POST /api/v1/assessment/start]
    B --> B2[POST /api/v1/assessment/submit]
    B --> B3[GET /api/v1/assessment/result/:id]
    B --> B4[GET /api/v1/assessment/types]

    C --> C1[POST /api/v1/gdpr/consent]
    C --> C2[POST /api/v1/gdpr/export]
    C --> C3[POST /api/v1/gdpr/delete]
    C --> C4[GET /api/v1/gdpr/consent/:user_id]

    D --> D1[GET /api/v1/admin/stats]
    D --> D2[GET /api/v1/admin/assessments]
    D --> D3[POST /api/v1/admin/login]
    D --> D4[GET /api/v1/admin/security]
```

---

### Assessment Type Routing Logic

The API uses a **single set of endpoints** for both Big Five and DISC, differentiated by the `assessment_type` parameter:

```python
@app.post("/api/v1/assessment/start")
async def start_assessment(request: StartAssessmentRequest):
    """
    Handles both Big Five and DISC assessments
    Routes to appropriate service based on assessment_type
    """
    if request.assessment_type == "big_five":
        questions = get_big_five_questions(request.language)
    elif request.assessment_type == "disc":
        questions = generate_disc_questions_with_ai(
            num_questions=request.num_questions,
            language=request.language
        )
    else:
        raise HTTPException(400, "Invalid assessment type")

    # Store in unified schema
    assessment = create_assessment(
        user_id=request.user_id,
        assessment_type=request.assessment_type,
        questions=questions
    )

    return assessment
```

---

## Shared Infrastructure

### 1. Authentication & Authorization

```python
# api_admin.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import os

security = HTTPBearer()

def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify admin API token"""
    token = credentials.credentials
    expected = os.getenv("ADMIN_API_KEY")

    if not token or token != expected:
        raise HTTPException(403, "Invalid admin credentials")

    return True
```

**Used by:** Admin endpoints (both Big Five and DISC management)

---

### 2. GDPR Compliance Layer

```python
# api_gdpr.py
router = APIRouter(prefix="/api/v1/gdpr", tags=["GDPR"])

@router.post("/export")
async def export_user_data(request: ExportRequest):
    """
    Export all user data (works for both assessment types)
    """
    user = get_user(request.user_id)

    # Export includes both Big Five and DISC assessments
    data = {
        "user_info": user.to_dict(),
        "consents": [c.to_dict() for c in user.consents],
        "assessments": [a.to_dict() for a in user.assessments]  # All types
    }

    return data
```

**Features:**
- Right to Access (export)
- Right to Erasure (delete)
- Consent Management
- Audit Logging

**Works for:** Both Big Five and DISC assessments transparently

---

### 3. AI Analysis Service

```python
# Shared AI service for both assessment types
from anthropic import Anthropic

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_assessment(
    assessment_type: str,
    questions: List,
    answers: List,
    language: str
) -> AssessmentResult:
    """
    Universal AI analysis function
    Routes to appropriate prompt based on assessment_type
    """
    if assessment_type == "big_five":
        system_prompt = BIG_FIVE_SYSTEM_PROMPT
    elif assessment_type == "disc":
        system_prompt = DISC_SYSTEM_PROMPT
    else:
        raise ValueError(f"Unknown assessment type: {assessment_type}")

    # Call Claude AI
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": build_analysis_prompt(answers)}]
    )

    return parse_ai_response(message.content[0].text)
```

---

### 4. Caching Layer

```python
# caching.py
from functools import lru_cache
import redis
import os

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def cache_assessment_result(assessment_id: str, result: dict):
    """Cache result for fast retrieval"""
    redis_client.setex(
        f"assessment:{assessment_id}",
        3600,  # 1 hour TTL
        json.dumps(result)
    )

def get_cached_result(assessment_id: str) -> Optional[dict]:
    """Retrieve cached result"""
    cached = redis_client.get(f"assessment:{assessment_id}")
    return json.loads(cached) if cached else None
```

**Benefits:**
- Faster repeated result retrieval
- Reduced database load
- Better user experience

---

### 5. Security Middleware

```python
# monitoring.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting for all endpoints
    Protects both Big Five and DISC APIs
    """
    client_ip = request.client.host

    # Check if IP is blocked
    if db.is_ip_blocked(client_ip):
        raise HTTPException(429, "Too many requests - IP blocked")

    # Check rate limit
    if is_rate_limited(client_ip, request.url.path):
        db.log_security_event(
            event_type="rate_limit_exceeded",
            severity="medium",
            client_ip=client_ip,
            endpoint=request.url.path
        )
        raise HTTPException(429, "Rate limit exceeded")

    response = await call_next(request)
    return response
```

---

## Security Architecture

### Defense in Depth Strategy

```mermaid
graph TB
    A[Internet] --> B[Vercel Edge Network]
    B --> C[DDoS Protection]
    C --> D[Rate Limiting]
    D --> E[IP Blocking]
    E --> F[Input Validation]
    F --> G[SQL Injection Prevention]
    G --> H[XSS Protection]
    H --> I[Authentication]
    I --> J[Authorization]
    J --> K[Audit Logging]
    K --> L[Database]
```

---

### Security Layers

#### Layer 1: Network Security
- **Vercel Edge Network**: DDoS protection, SSL/TLS
- **CORS**: Explicit origin whitelist
- **HTTPS Only**: All traffic encrypted

#### Layer 2: Application Security
- **Rate Limiting**: Per-IP, per-endpoint limits
- **IP Blocking**: Automatic blocking of attackers
- **Input Validation**: Pydantic models validate all inputs

#### Layer 3: Data Security
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Prevention**: Output sanitization
- **Parameterized Queries**: No raw SQL

#### Layer 4: Authentication & Authorization
- **API Keys**: For admin access
- **Token-based Auth**: Bearer tokens
- **Password Hashing**: bcrypt for admin passwords

#### Layer 5: Monitoring & Audit
- **Sentry**: Error tracking
- **Audit Logs**: All data operations logged
- **Security Events**: Attack tracking

---

### Security Configuration

```python
# Environment Variables (Security)
ADMIN_PASSWORD_HASH=<bcrypt_hash>
ADMIN_API_KEY=<secure_random_token>
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
SENTRY_DSN=<sentry_url>
DATABASE_URL=<postgresql_url>
ANTHROPIC_API_KEY=<claude_api_key>
```

---

## Deployment Architecture

### Vercel Serverless Deployment

```mermaid
graph TB
    subgraph "Vercel Edge Network"
        A[Edge Function 1]
        B[Edge Function 2]
        C[Edge Function N]
    end

    subgraph "Application Layer"
        D[FastAPI Handler]
        E[Mangum Adapter]
    end

    subgraph "Data Layer"
        F[(Vercel Postgres)]
        G[Vercel Blob Storage]
    end

    subgraph "External Services"
        H[Anthropic Claude AI]
        I[Sentry Monitoring]
    end

    Internet --> A
    Internet --> B
    Internet --> C
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    E --> G
    D --> H
    D --> I
```

---

### Serverless Function Entry Point

```python
# api/index.py
from mangum import Mangum
from api_main_gdpr import app

# Wrap FastAPI app for AWS Lambda / Vercel
handler = Mangum(app, lifespan="off")
```

**Key Points:**
- Each request runs in isolated function
- Stateless design (no in-memory state)
- Database handles all persistence
- Cold start optimization needed

---

### Environment-Specific Configuration

#### Development
```bash
DATABASE_URL=sqlite:///./assessment_gdpr.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
ENVIRONMENT=development
```

#### Production (Vercel)
```bash
DATABASE_URL=postgres://user:pass@db.vercel.com/prod
ALLOWED_ORIGINS=https://app.persona.com
ENVIRONMENT=production
SENTRY_DSN=https://...@sentry.io/...
```

---

## Scalability Considerations

### Current Architecture Limits

| Component | Current Limit | Bottleneck |
|-----------|---------------|------------|
| Vercel Functions | 10s timeout | Long AI analysis |
| Database Connections | 100 concurrent | Connection pool |
| Claude AI API | 50 req/min | API quota |
| Redis Cache | 512MB | Memory |

---

### Scaling Strategies

#### 1. Horizontal Scaling (Vercel)
- **Auto-scaling**: Vercel automatically scales edge functions
- **No configuration**: Zero-config horizontal scaling
- **Cost**: Pay per execution

#### 2. Database Scaling
```python
# Connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True  # Check connections before use
)
```

#### 3. Caching Strategy
```python
# Cache common queries
@lru_cache(maxsize=1000)
def get_assessment_types():
    """Cached assessment types"""
    return ASSESSMENT_TYPES

# Cache results in Redis
def get_result(assessment_id: str):
    # Try cache first
    cached = redis_client.get(f"result:{assessment_id}")
    if cached:
        return json.loads(cached)

    # Fetch from DB
    result = db.query(AssessmentResult).filter_by(
        assessment_id=assessment_id
    ).first()

    # Store in cache
    redis_client.setex(f"result:{assessment_id}", 3600, json.dumps(result))

    return result
```

#### 4. Async Processing
```python
# For long-running AI analysis
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def analyze_assessment_async(assessment_id: str):
    """Process assessment in background"""
    assessment = db.get_assessment(assessment_id)
    result = analyze_with_ai(assessment)
    db.save_result(result)
    send_notification_to_user(assessment.user_id)
```

---

### Performance Metrics

**Target SLAs:**
- API Response Time: < 200ms (95th percentile)
- Assessment Analysis: < 30s (Big Five), < 45s (DISC)
- Database Queries: < 50ms
- Cache Hit Rate: > 80%
- Uptime: 99.9%

---

## Data Flow Diagrams

### Big Five Assessment Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database
    participant AI as Claude AI

    U->>F: Start Big Five Test
    F->>A: POST /api/v1/assessment/start (type=big_five)
    A->>D: Create Assessment Record
    A->>A: Load IPIP-50 Questions
    A->>D: Store Questions
    D-->>A: assessment_id
    A-->>F: Questions + assessment_id
    F-->>U: Display Questions

    U->>F: Submit Answers
    F->>A: POST /api/v1/assessment/submit
    A->>D: Store Answers
    A->>A: Calculate Raw Scores
    A->>AI: Analyze Personality (Big Five prompt)
    AI-->>A: Analysis + Interpretation
    A->>D: Store Result
    A->>D: Update Assessment (completed)
    A->>D: Log Audit Event
    D-->>A: Success
    A-->>F: Result with Scores
    F-->>U: Display Report
```

---

### DISC Assessment Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database
    participant AI as Claude AI

    U->>F: Start DISC Test
    F->>A: POST /api/v1/assessment/start (type=disc)
    A->>AI: Generate DISC Questions
    AI-->>A: 24 Situational Questions
    A->>D: Create Assessment Record
    A->>D: Store Questions
    D-->>A: assessment_id
    A-->>F: Questions + assessment_id
    F-->>U: Display Questions

    U->>F: Submit Answers
    F->>A: POST /api/v1/assessment/submit
    A->>D: Store Answers
    A->>A: Calculate DISC Scores
    A->>AI: Analyze Behavior (DISC prompt)
    AI-->>A: DISC Profile + Interpretation
    A->>D: Store Result
    A->>D: Update Assessment (completed)
    A->>D: Log Audit Event
    D-->>A: Success
    A-->>F: Result with DISC Profile
    F-->>U: Display Report
```

---

### GDPR Data Export Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Request Data Export
    F->>A: POST /api/v1/gdpr/export
    A->>D: Verify User Consent
    D-->>A: Consent Valid
    A->>D: Query User Data
    A->>D: Query All Assessments (Big Five + DISC)
    A->>D: Query Consents
    A->>D: Query Audit Logs
    D-->>A: Complete User Data
    A->>A: Generate JSON Export
    A->>D: Log Export Event
    A-->>F: Download Link (JSON)
    F-->>U: Download File
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.0+
- **AI**: Anthropic Claude API (Sonnet 4.5)

### Database
- **Primary**: PostgreSQL 15+ (Vercel Postgres)
- **Cache**: Redis 7+ (optional)
- **Development**: SQLite 3.35+

### Deployment
- **Platform**: Vercel (Serverless Functions)
- **Adapter**: Mangum (FastAPI → Lambda)
- **Monitoring**: Sentry
- **Logging**: Vercel Logs

### Security
- **Password Hashing**: bcrypt
- **CORS**: FastAPI CORSMiddleware
- **Rate Limiting**: Custom middleware
- **Input Validation**: Pydantic models

---

## Future Architecture Considerations

### Planned Enhancements

1. **Microservices Split**
   - Separate Big Five and DISC services
   - Independent scaling
   - Service mesh (Kubernetes)

2. **Real-Time Features**
   - WebSocket support for live progress
   - Server-Sent Events for long operations
   - Real-time admin dashboard

3. **Multi-Region Deployment**
   - Edge functions in EU, US, Asia
   - Regional database replicas
   - Reduced latency

4. **Advanced Caching**
   - CDN for static results
   - GraphQL for flexible queries
   - Materialized views for analytics

5. **Machine Learning Pipeline**
   - ML-based scoring (reduce AI API costs)
   - Personalized question selection
   - Anomaly detection for fake answers

---

**Last Updated:** March 7, 2026
**Version:** 1.0.0
**Maintainer:** Persona Platform Team
