# 🧠 Persona - Big Five Personality Assessment App

Din kompletta personlighetstest-app med AI-driven coaching!

## 📦 Vad finns i denna repository

### Huvudfiler
- **`big-five-demo.html`** - Komplett demo med chat-funktion (ingen server behövs!)
- **`api_main_gdpr.py`** - FastAPI server med GDPR-compliance
- **`personality_coach.py`** - AI personality coach (Claude API)
- **`database.py`** - SQLAlchemy databas för användardata

### Dokumentation
- **`CHAT_FEATURE_GUIDE.md`** - Komplett guide till chat-funktionen
- **`TEST_CHAT.md`** - Testinstruktioner och exempel
- **`README.md`** - Huvuddokumentation

### Nyckel-features

#### ✅ Implementerade funktioner
1. **Big Five Assessment (IPIP-50)**
   - 50 vetenskapligt validerade frågor
   - Mäter OCEAN-dimensionerna (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
   
2. **AI Personality Coach**
   - Chattar baserat på din Big Five-profil
   - Ger personliga karriärråd
   - Analyserar trait-kombinationer
   - Mock API för demo (ingen API-nyckel behövs!)

3. **Personaliserade Rapporter**
   - Detaljerade beskrivningar per dimension
   - Karriärförslag baserade på profil
   - Interaktionsmönster mellan traits

4. **GDPR-Compliant**
   - Samtycke för databehandling
   - Dataradering på begäran
   - Transparent dathantering

5. **Mobile-First UI**
   - Full responsiv design
   - Touch-optimerad
   - Smooth animationer

## 🚀 Hur du testar

### Demo (enklast)
1. Öppna `big-five-demo.html` i webbläsare
2. Gör testet
3. Testa chatten (använder mock API)

### Med riktig AI (Claude API)
```bash
# Installera dependencies
pip install -r requirements.txt

# Sätt API-nyckel
export ANTHROPIC_API_KEY="din-nyckel"

# Starta server
uvicorn api_main_gdpr:app --reload

# Öppna http://localhost:8000/docs
```

## 📊 Teknisk stack
- **Frontend**: Vanilla JS + TailwindCSS
- **Backend**: FastAPI + SQLAlchemy
- **AI**: Anthropic Claude API
- **Database**: SQLite (kan uppgraderas till PostgreSQL)

## 🔮 Nästa steg

1. **Deploy till produktion**
   - Hosting: Vercel/Netlify (frontend) + Railway/Fly.io (backend)
   - Databas: PostgreSQL

2. **Utökningar**
   - Jämför med andra profiler
   - Teamanalys
   - Longitudinell tracking

## 📁 Filstruktur
```
chatbot/
├── big-five-demo.html          # Demo med chat
├── api_main_gdpr.py           # FastAPI server
├── personality_coach.py       # AI coach
├── database.py                # Databas
├── CHAT_FEATURE_GUIDE.md     # Chat-guide
├── TEST_CHAT.md              # Testguide
└── requirements.txt          # Python dependencies
```

## 🎯 Brancher
- `master` - Huvudbranch
- `claude/personality-assessment-app-*` - Feature branches

---

**Skapat med Claude Code** 🤖
Repository: https://github.com/Marcwarn/chatbot
