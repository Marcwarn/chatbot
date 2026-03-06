# Personality Coach Chat Feature

## Översikt

Användare kan nu **chatta med en AI-driven personlighetscoach** som känner till deras Big Five-profil och ger personaliserad vägledning.

## Funktionalitet

### Backend (`api_main_gdpr.py` + `personality_coach.py`)

**Endpoints:**
- `POST /api/v1/chat` - Chatta med personlighetscoachen
- `POST /api/v1/chat/save-profile` - Spara användarprofil (anropas automatiskt efter test)
- `GET /api/v1/chat/profile/{user_id}` - Kolla om profil finns sparad

**AI-coach features:**
- Känner till användarens OCEAN-poäng (E, A, C, N, O)
- Analyserar **trait combinations** (inte bara enskilda dimensioner)
- Ger konkreta, actionable råd
- Specialiserad på: karriärvägledning, relationer, kommunikation, stresshantering, personlig utveckling
- Varmt, coachande tonläge (inte kliniskt)

**System prompt:**
Coachen får ett dynamiskt system prompt som innehåller:
1. Användarens percentiler för alla Big Five-dimensioner
2. Viktiga trait combinations (t.ex. "hög E + hög C = strukturerad social förmåga")
3. Personaliserad rapport (om genererad)
4. Expert-instruktioner om Big Five-psykologi

**Säkerhet:**
- Rekommenderar professionell hjälp vid tecken på psykisk ohälsa
- Håller sig till personlighetsutveckling (inte terapi)
- GDPR-kompatibel (användardata i minnet, kan raderas)

### Frontend (Demo: `big-five-demo.html`)

**Chat UI:**
- Fullskärms chatvy med smooth animationer
- Välkomstmeddelande som listar vad coachen kan hjälpa till med
- Visar användarens OCEAN-profil i chatten
- Loading-animation med tre pulserande prickar
- Auto-scroll till senaste meddelandet
- Responsiv på mobil

**Mock API (för demo):**
Demo innehåller regelbaserade svar för vanliga frågor:
- "Vilka jobb passar mig?" → Använder `getCareerSuggestions()`
- "Hur hanterar jag stress?" → Anpassat efter emotionell stabilitet
- "Kommunikationstips?" → Använder `getCommunicationStyle()`
- Default: Visar profil och frågar vad de vill veta

**Ersätt med riktig backend:**
I `sendChatMessage()`, byt ut `mockChatAPI()` mot:

```javascript
const response = await fetch('https://your-api.com/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 'USER_ID_HERE',
        message: message,
        conversation_history: chatHistory.map(m => ({
            role: m.role,
            content: m.content
        }))
    })
});
const data = await response.json();
return data.response;
```

## Användningsexempel

### Starta backend med AI-coach
```bash
# Sätt API-nyckel
export ANTHROPIC_API_KEY="sk-ant-..."

# Starta server
uvicorn api_main_gdpr:app --reload --port 8000
```

### Testa i demon
1. Gör Big Five-testet
2. På resultatsidan, klicka **"Chatta med din personlighetscoach"**
3. Ställ frågor som:
   - "Vilka jobb passar min profil?"
   - "Hur kan jag bli bättre på att sätta gränser?"
   - "Varför är jag så organiserad?"
   - "Tips på hur jag kan hantera stress?"

## Arkitektur

```
┌─────────────────┐
│  User completes │
│   assessment    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Profile saved   │◄── Automatic
│ to _user_profiles│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User opens     │
│   chat view     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  User sends     │─────►│  Backend         │
│  message        │      │  /api/v1/chat    │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ personality_coach│
                         │ .py creates      │
                         │ profile-aware    │
                         │ system prompt    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Claude API       │
                         │ generates        │
                         │ personalized     │
                         │ response         │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Response returned│
                         │ to frontend      │
                         └──────────────────┘
```

## Trait Combination Examples

Coachen analyserar hur dimensioner samverkar:

- **Hög E + Hög C**: "Strukturerad social förmåga" → Passar HR, projektledning
- **Hög E + Låg C**: "Spontan social energi" → Passar försäljning, events
- **Låg E + Hög C**: "Fokuserad eftertänksam" → Passar utveckling, research
- **Hög O + Hög A**: "Kreativ empati" → Passar UX design, coaching
- **Hög O + Låg A**: "Intellektuell självständighet" → Passar innovation, entreprenörskap

## Utvecklingsmöjligheter

1. **Persistent chat history** - Spara konversationer i databasen
2. **Suggested questions** - Visa förslag på relevanta frågor baserat på profil
3. **Voice input** - Tala istället för att skriva
4. **Export conversation** - Ladda ner chat som PDF
5. **Multi-language** - Stöd för fler språk än svenska/engelska
6. **Follow-up system** - Coachen följer upp tidigare råd efter X dagar
7. **Goal tracking** - Sätt personliga mål och följ upp
8. **Team dynamics** - Analysera team-kompatibilitet mellan flera profiler

## GDPR & Privacy

- Konversationer sparas INTE permanent (endast i minnet under session)
- Användare kan begära radering via `/api/v1/gdpr/delete`
- Ingen data säljs till tredje part
- Claude API används endast för att generera svar (Anthropic lagrar ej data permanent)

## Teknisk Stack

- **Frontend**: Vanilla JS, Tailwind CSS, Lucide icons
- **Backend**: FastAPI, Python 3.10+
- **AI**: Claude Sonnet 4.5 via Anthropic API
- **Psykologi**: Big Five/OCEAN, IPIP-50 instrument
