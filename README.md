# 🧠 AI-Driven Personality Assessment Platform

En komplett plattform för personlighetsbedömningar med AI-genererade frågor och analys.

## 📦 Vad Finns I Detta Repo?

### 1. 🔒 GDPR-Compliant Assessment API (api_main_gdpr.py) ⭐ **REKOMMENDERAD**
**Huvudfokus**: AI-driven REST API med **FULL GDPR-compliance**

- **Big Five, DISC, Jung/MBTI** assessments
- **Claude AI** genererar dynamiska frågor och analyserar svar
- **🔒 GDPR-compliant**: Consent management, data export, right to erasure
- **📊 Databas**: SQLite med audit logging och data retention
- **🛡️ Privacy by Design**: Pseudonymisering, kryptering, anonymisering
- **Svenska & Engelska** språkstöd

**Quick Start:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Lägg till ANTHROPIC_API_KEY i .env
python api_main_gdpr.py
```

🔒 **GDPR Guide:** Se [GDPR_GUIDE.md](GDPR_GUIDE.md)
📖 **API Docs:** Se [ASSESSMENT_README.md](ASSESSMENT_README.md)
🔗 **Lovable Integration:** Se [LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md)
🧪 **Testa API:** `python test_gdpr_api.py`

---

### 2. 🎯 Basic Assessment API (api_main.py)
**Enklare version**: AI-driven REST API utan databas (in-memory only)

- Samma features som GDPR-versionen men utan persistent storage
- Bra för quick prototyping och testing
- Ingen databas krävs

**Quick Start:**
```bash
python api_main.py
```

🧪 **Testa:** `python test_api.py`

---

### 3. 💬 Streamlit Chatbot (streamlit_app.py)
**Bonus**: En enkel chatbot template med OpenAI GPT-3.5

```bash
streamlit run streamlit_app.py
```

---

## 🚀 Snabbstart - GDPR-Compliant API

### Steg 1: Installation
```bash
git clone <your-repo>
cd chatbot
pip install -r requirements.txt
cp .env.example .env
```

### Steg 2: Konfigurera
Redigera `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### Steg 3: Starta GDPR-Compliant API
```bash
python api_main_gdpr.py
```

API körs på: http://localhost:8000
Swagger UI: http://localhost:8000/docs
Database: `assessment_gdpr.db` (skapas automatiskt)

### Steg 4: Testa
```bash
python test_gdpr_api.py
```

Välj option 1 för komplett GDPR flow test (consent → assessment → export → delete)

---

## 🔒 GDPR Features

### ✅ Full GDPR Compliance

- **Consent Management**: Explicit samtycke innan data samlas
- **Right to Access**: Exportera all data (JSON)
- **Right to Erasure**: "Radera mig" funktion
- **Right to Rectification**: Uppdatera data
- **Data Portability**: Export i maskinläsbart format
- **Privacy by Design**: Pseudonymisering, kryptering, minimering
- **Audit Logging**: All databehandling spåras
- **Data Retention**: Auto-radering efter viss tid (default: 365 dagar)
- **Anonymization**: Gamla assessments anonymiseras automatiskt

### GDPR Endpoints

| Endpoint | Beskrivning |
|----------|-------------|
| `POST /api/v1/gdpr/consent` | Ge/dra tillbaka samtycke |
| `GET /api/v1/gdpr/consent/{user_id}` | Visa samtycken |
| `POST /api/v1/gdpr/export` | Exportera all användardata |
| `POST /api/v1/gdpr/delete` | Begär radering |
| `POST /api/v1/gdpr/delete/confirm/{token}` | Bekräfta radering |
| `GET /api/v1/gdpr/privacy-info/{user_id}` | Privacy dashboard |
| `GET /api/v1/gdpr/audit/{user_id}` | Audit logs |

Se [GDPR_GUIDE.md](GDPR_GUIDE.md) för komplett dokumentation.

---

## 🔗 Integration med Lovable

Din Lovable web app kan enkelt använda detta API:

```typescript
// I din Lovable app
const response = await fetch('https://your-api.com/api/v1/assessment/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_123',
    assessment_type: 'big_five',
    language: 'sv',
    num_questions: 30
  })
});

const { assessment_id, questions } = await response.json();
```

**Komplett guide:** [LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md)

---

## 📊 Assessment Typer

| Typ | Dimensioner | Användning |
|-----|-------------|------------|
| **Big Five** | 5 dimensioner (OCEAN) | Karriärvägledning, rekrytering |
| **DISC** | 4 beteendeprofiler | Kommunikation, ledarskap |
| **Jung/MBTI** | 16 personlighetstyper | Teamdynamik, utveckling |
| **Comprehensive** | Kombinerar alla | Heltäckande analys |

---

## 📁 Filstruktur

```
chatbot/
├── api_main_gdpr.py            # GDPR-Compliant API ⭐ REKOMMENDERAD
├── api_main.py                 # Basic API (no database)
├── api_gdpr.py                 # GDPR endpoints module
├── database.py                 # SQLAlchemy models + GDPR functions
├── test_gdpr_api.py            # Test script för GDPR API ⭐
├── test_api.py                 # Test script för basic API
├── streamlit_app.py            # Streamlit chatbot
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── GDPR_GUIDE.md               # GDPR compliance guide 🔒
├── ASSESSMENT_README.md        # Detaljerad API dokumentation
├── LOVABLE_INTEGRATION.md      # Guide för Lovable integration
└── README.md                   # Denna fil
```

**Databas (skapas automatiskt):**
- `assessment_gdpr.db` - SQLite databas med all användardata

---

## 🎯 API Endpoints

| Endpoint | Metod | Beskrivning |
|----------|-------|-------------|
| `/api/v1/assessment/start` | POST | Starta nytt assessment |
| `/api/v1/assessment/submit` | POST | Skicka in svar |
| `/api/v1/assessment/result/{id}` | GET | Hämta resultat |
| `/api/v1/assessment/types` | GET | Lista assessment typer |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

---

## 🌍 Deploy till Produktion

### Railway.app
```bash
railway up
```

### Render.com
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api_main:app --host 0.0.0.0 --port $PORT`

### Fly.io
```bash
fly launch
fly secrets set ANTHROPIC_API_KEY=sk-ant-xxxxx
fly deploy
```

---

## 🤝 Support & Dokumentation

- **📖 API Docs:** [ASSESSMENT_README.md](ASSESSMENT_README.md)
- **🔗 Lovable Guide:** [LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md)
- **💻 Swagger UI:** http://localhost:8000/docs
- **🧪 Test API:** `python test_api.py`

---

## 📄 License

MIT License

---

**Byggd med ❤️ för bättre självkännedom och personlig utveckling**

<!-- deploy trigger -->
