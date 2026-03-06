# 🧠 AI-Driven Personality Assessment API

En modern, AI-driven personlighetsbedömnings-plattform baserad på vetenskaplig psykometri.

## ✨ Features

- **🤖 AI-Genererade Frågor**: Claude AI skapar dynamiska, validerade frågor baserat på psykometrisk teori
- **📊 Tre Assessment-Modeller**:
  - **Big Five (OCEAN)**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
  - **DISC**: Dominance, Influence, Steadiness, Conscientiousness
  - **Jung/MBTI**: Myers-Briggs Type Indicator (16 personlighetstyper)
  - **Comprehensive**: Kombinerar alla tre modeller
- **🔬 Vetenskapligt Grundad**: Baserad på etablerad psykometrisk forskning
- **🌍 Flerspråkig**: Stöd för svenska och engelska (lätt att utöka)
- **🚀 RESTful API**: Enkel integration med vilken frontend som helst
- **📱 Lovable-Ready**: Komplett guide för integration med Lovable web apps

## 🏗️ Arkitektur

```
┌─────────────────┐         HTTP/REST        ┌──────────────────┐
│   Lovable       │ ◄──────────────────────► │   FastAPI        │
│   Web App       │                          │   Backend        │
│   (Frontend)    │                          │                  │
└─────────────────┘                          └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌─────────────────┐
                                             │  Claude AI      │
                                             │  (Anthropic)    │
                                             └─────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Klona repo
git clone <your-repo>
cd chatbot

# Installera dependencies
pip install -r requirements.txt

# Skapa .env fil
cp .env.example .env
```

### 2. Konfigurera API Keys

Redigera `.env` och lägg till din Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

Få din API key här: https://console.anthropic.com/

### 3. Starta Server

```bash
# Starta FastAPI server
python api_main.py

# Eller med uvicorn:
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

API:et är nu tillgängligt på: **http://localhost:8000**

### 4. Testa API:et

Öppna: **http://localhost:8000/docs** för interaktiv API dokumentation (Swagger UI)

Eller använd test scriptet:
```bash
python test_api.py
```

## 📖 API Användning

### Exempel: Komplett Assessment Flow

```python
import requests

API_URL = "http://localhost:8000"

# 1. Starta assessment
response = requests.post(f"{API_URL}/api/v1/assessment/start", json={
    "user_id": "user_123",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 30
})

data = response.json()
assessment_id = data["assessment_id"]
questions = data["questions"]

# 2. Visa frågor till användaren och samla svar
answers = []
for question in questions:
    print(f"\n{question['question_text']}")
    for i, option in enumerate(question['options'], 1):
        print(f"{i}. {option}")

    user_answer = int(input("Ditt svar (1-5): "))

    answers.append({
        "assessment_id": assessment_id,
        "question_id": question["question_id"],
        "answer": user_answer
    })

# 3. Skicka in svar och få resultat
response = requests.post(f"{API_URL}/api/v1/assessment/submit", json={
    "assessment_id": assessment_id,
    "answers": answers
})

result = response.json()

# 4. Visa resultat
print(f"\n{'='*60}")
print("DINA RESULTAT")
print(f"{'='*60}\n")

print(f"Sammanfattning: {result['summary']}\n")

print("Personlighetspoäng:")
for score in result['scores']:
    print(f"  {score['dimension']}: {score['score']:.1f}/100")
    print(f"  → {score['interpretation']}\n")

print(f"\nStyrkor:")
for strength in result['strengths']:
    print(f"  • {strength}")

print(f"\nUtvecklingsområden:")
for area in result['development_areas']:
    print(f"  • {area}")

print(f"\nRekommendationer:")
for rec in result['recommendations']:
    print(f"  • {rec}")
```

## 🔗 Integration med Lovable

Se **[LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md)** för komplett guide.

**Snabbversion:**

1. Deploy detta API till cloud (Railway, Render, Fly.io)
2. Kopiera TypeScript service och component från integration guiden
3. Sätt `VITE_ASSESSMENT_API_URL` i Lovable environment
4. Importera och använd `<PersonalityAssessment />` component

## 🎯 API Endpoints

| Method | Endpoint | Beskrivning |
|--------|----------|-------------|
| GET | `/` | API root information |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI dokumentation |
| GET | `/api/v1/assessment/types` | Hämta assessment typer |
| POST | `/api/v1/assessment/start` | Starta nytt assessment |
| POST | `/api/v1/assessment/submit` | Skicka in svar |
| GET | `/api/v1/assessment/result/{id}` | Hämta resultat |

## 🧪 Assessment Typer

### Big Five (OCEAN)

Mäter fem fundamentala personlighetsdimensioner:

1. **Openness (Öppenhet)** - Kreativitet, nyfikenhet, öppenhet för nya erfarenheter
2. **Conscientiousness (Samvetsgrannhet)** - Organisation, ansvar, pålitlighet
3. **Extraversion (Extraversion)** - Social energi, utåtriktadhet
4. **Agreeableness (Vänlighet)** - Empati, samarbete, tillitsfullhet
5. **Neuroticism (Neuroticism)** - Emotionell stabilitet, stresshantering

**Användningsområden:**
- Karriärvägledning
- Teamsammansättning
- Personlig utveckling
- Rekrytering

### DISC

Mäter beteendeprofil baserat på fyra dimensioner:

1. **Dominance (D)** - Resultatinriktad, bestämd, tävlingsinriktad
2. **Influence (I)** - Utåtriktad, entusiastisk, övertalande
3. **Steadiness (S)** - Stödjande, pålitlig, teamorienterad
4. **Conscientiousness (C)** - Analytisk, noggrann, systematisk

**Användningsområden:**
- Kommunikationsstilar
- Ledarskapsträning
- Konflikthantering
- Försäljning

### Jung/MBTI

Myers-Briggs Type Indicator baserat på Jungiansk typologi (16 typer):

**Dimensioner:**
1. **E/I** - Extraversion vs Introversion
2. **S/N** - Sensing vs Intuition
3. **T/F** - Thinking vs Feeling
4. **J/P** - Judging vs Perceiving

**Användningsområden:**
- Karriärval
- Team dynamics
- Relationsutveckling
- Personlig tillväxt

## 🔬 Psykometrisk Validitet

API:et använder AI för att:

1. **Generera Frågor** med hög test-retest reliabilitet
2. **Balansera Frågor** över olika dimensioner
3. **Undvika Bias** genom randomisering och omvänd kodning
4. **Validera Svar** för konsistens och ärlighet
5. **Beräkna Percentiler** baserat på normalfördelning

## 🛡️ Säkerhet & Privacy

- **CORS**: Konfigurerbar för din domän
- **Rate Limiting**: Förhindrar missbruk
- **Ingen Data Lagring**: Använder in-memory storage (lägg till databas vid behov)
- **API Keys**: Säker hantering via environment variables

## 📦 Deployment

### Railway.app

```bash
railway login
railway init
railway up
```

### Render.com

1. Skapa ny Web Service
2. Connecta GitHub repo
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn api_main:app --host 0.0.0.0 --port $PORT`
5. Lägg till `ANTHROPIC_API_KEY` i environment

### Fly.io

```bash
fly launch
fly secrets set ANTHROPIC_API_KEY=sk-ant-xxxxx
fly deploy
```

### Docker

```bash
docker build -t personality-api .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-xxxxx personality-api
```

## 🎨 Anpassa & Utöka

### Lägg till Nya Assessment Typer

Skapa ny prompt template i `api_main.py`:

```python
ENNEAGRAM_SYSTEM_PROMPT = """Du är expert på Enneagram..."""

system_prompts = {
    "big_five": BIG_FIVE_SYSTEM_PROMPT,
    "disc": DISC_SYSTEM_PROMPT,
    "jung_mbti": JUNG_MBTI_SYSTEM_PROMPT,
    "enneagram": ENNEAGRAM_SYSTEM_PROMPT,  # Ny!
}
```

### Lägg till Databas Persistens

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

# Spara resultat till databas
db = SessionLocal()
db.add(result)
db.commit()
```

### Lägg till Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v1/assessment/start")
async def start_assessment(
    request: StartAssessmentRequest,
    token: str = Depends(security)
):
    # Validera token
    ...
```

## 📊 Exempel Output

```json
{
  "assessment_id": "assess_user123_20231206120000",
  "scores": [
    {
      "dimension": "Extraversion",
      "score": 75.5,
      "percentile": 82,
      "interpretation": "Du är utåtriktad och energisk. Du trivs i sociala situationer och får energi av att vara med andra människor."
    }
  ],
  "summary": "Du har en utåtriktad och kreativ personlighet med stark social förmåga...",
  "strengths": [
    "Utmärkt kommunikationsförmåga",
    "Kreativ problemlösare",
    "Teamorienterad"
  ],
  "development_areas": [
    "Kan vara för impulsiv i beslut",
    "Behöver utveckla tålamod"
  ],
  "recommendations": [
    "Utnyttja din kreativitet i projektledning",
    "Arbeta med mindfulness för bättre fokus"
  ]
}
```

## 🤝 Contributing

Bidrag är välkomna! Områden att förbättra:

- Fler assessment-modeller (Enneagram, VIA Character Strengths, etc.)
- Databas-integration
- PDF-export av resultat
- Jämförelser med populationsnormer
- Machine learning för förbättrad validitet

## 📄 License

MIT License - Se LICENSE fil

## 🙏 Credits

Baserat på vetenskaplig forskning från:
- Costa & McCrae (Big Five)
- William Marston (DISC)
- Carl Jung & Isabel Myers (MBTI)

AI-powered av:
- Anthropic Claude (Sonnet 4.5)

---

**Byggd med ❤️ för bättre självkännedom och personlig utveckling**
