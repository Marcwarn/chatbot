# 🧠 AI-Driven Personality Assessment Platform

En komplett plattform för personlighetsbedömningar med AI-genererade frågor och analys.

## 📦 Vad Finns I Detta Repo?

### 1. 🎯 Personality Assessment API (api_main.py)
**Huvudfokus**: AI-driven REST API för personlighetsbedömningar

- **Big Five, DISC, Jung/MBTI** assessments
- **Claude AI** genererar dynamiska frågor och analyserar svar
- **RESTful API** för enkel integration med Lovable eller andra frontends
- **Svenska & Engelska** språkstöd

**Quick Start:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Lägg till ANTHROPIC_API_KEY i .env
python api_main.py
```

📖 **Dokumentation:** Se [ASSESSMENT_README.md](ASSESSMENT_README.md)
🔗 **Lovable Integration:** Se [LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md)
🧪 **Testa API:** `python test_api.py`

### 2. 💬 Streamlit Chatbot (streamlit_app.py)
**Bonus**: En enkel chatbot template med OpenAI GPT-3.5

```bash
streamlit run streamlit_app.py
```

---

## 🚀 Snabbstart - Assessment API

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

### Steg 3: Starta API
```bash
python api_main.py
```

API körs på: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### Steg 4: Testa
```bash
python test_api.py
```

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
├── api_main.py                 # FastAPI Assessment API ⭐
├── test_api.py                 # Test script för API
├── streamlit_app.py            # Streamlit chatbot
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── ASSESSMENT_README.md        # Detaljerad API dokumentation
├── LOVABLE_INTEGRATION.md      # Guide för Lovable integration
└── README.md                   # Denna fil
```

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
