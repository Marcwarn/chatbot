# Testa Chat-funktionen

## Snabbstart (Demo utan backend)

1. **Öppna demon:**
   ```bash
   # Om servern inte kör:
   python3 -m http.server 8000

   # Öppna i webbläsare:
   # http://127.0.0.1:8000/big-five-demo.html
   ```

2. **Gör testet:**
   - Godkänn GDPR-samtycken
   - Svara på alla 50 frågor
   - Vänta tills du ser din resultatprofil

3. **Öppna chatten:**
   - Klicka på den gröna knappen **"Chatta med din personlighetscoach"**
   - Du ser ett välkomstmeddelande med din profil

4. **Testa frågor:**

   **Karriärfrågor:**
   - "Vilka jobb passar mig?"
   - "Skulle jag trivas som projektledare?"
   - "Passar jag för entreprenörskap?"

   **Stressfrågor:**
   - "Hur kan jag hantera stress?"
   - "Varför blir jag så lätt orolig?"
   - "Tips på mindfulness?"

   **Kommunikation:**
   - "Hur kommunicerar jag bäst?"
   - "Varför föredrar jag 1-on-1 samtal?"
   - "Tips för gruppdiskussioner?"

   **Allmänt:**
   - "Berätta om min personlighet"
   - "Vad är mina största styrkor?"
   - "Hur kan jag utvecklas?"

## Med riktig AI-backend

### 1. Sätt API-nyckel
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### 2. Starta backend
```bash
cd /home/user/chatbot
uvicorn api_main_gdpr:app --reload --port 8000 --host 0.0.0.0
```

### 3. Uppdatera demo för riktig API

Öppna `big-five-demo.html` och ersätt `mockChatAPI()` med:

```javascript
async function realChatAPI(message) {
    const userId = "demo-user-123"; // I produktion: från session/auth

    const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            message: message,
            conversation_history: chatHistory
        })
    });

    if (!response.ok) {
        throw new Error('Chat request failed');
    }

    const data = await response.json();
    return data.response;
}
```

Sedan i `sendChatMessage()`, byt:
```javascript
const response = await mockChatAPI(message);
```
Till:
```javascript
const response = await realChatAPI(message);
```

### 4. Testa

Nu får du **riktiga AI-svar** från Claude baserat på din profil!

## Förväntade svar

### Med Mock API (demo):
- Regelbaserade svar
- Känner igen nyckelord: "jobb", "karriär", "stress", "oro", "kommunikation"
- Använder fördefinierade funktioner (getCareerSuggestions, getCommunicationStyle)
- Snabbt men begränsat

### Med riktig AI:
- Djupt personaliserade svar
- Analyserar trait combinations
- Följer upp med relevanta frågor
- Ger konkreta, actionable råd
- Varmt, coachande tonläge
- Känner till hela din rapport (arbetsstil, relationer, etc.)

## Felsökning

**Problem: "Chat feature unavailable - no API key"**
→ Sätt `ANTHROPIC_API_KEY` i miljövariabler

**Problem: Chatten öppnas inte**
→ Kontrollera att du är på resultatvyn (inte start/consent/frågor)

**Problem: Mock API ger alltid samma svar**
→ Detta är förväntat - byt till riktig API för personaliserade svar

**Problem: Inga ikoner syns**
→ Kör `lucide.createIcons()` eller reload sidan

## Exempel-konversation

```
USER: Vilka jobb passar mig?

COACH: Baserat på din Big Five-profil passar dessa roller dig särskilt väl:

• UX/UI Designer eller Product Manager
• Arkitekt eller Ingenjör
• Projektledare inom kreativa fält

Din kombination av hög samvetsgrannhet (78) och hög öppenhet (82)
gör dig perfekt för roller där både kreativitet OCH genomförande krävs.

Vill du att jag går djupare in på någon av dessa?

USER: Ja, berätta mer om UX design

COACH: Perfekt match! Som UX designer får du:

✓ Använda din kreativa problemlösning (hög O)
✓ Jobba strukturerat med research och iteration (hög C)
✓ Samarbeta tätt med team (medel-hög E)

Din profil passar särskilt bra för:
- User research & testing
- Interaction design
- Design systems & komponentbibliotek

Konkret steg: Börja med ett gratis UX-cert från Google eller
Interaction Design Foundation. Bygg en portfoliosida med 2-3 case studies.

Vill du tips på hur du kommer in i branschen?
```

## Nästa steg

- [ ] Integrera med Lovable-appen
- [ ] Lägg till persistent chat history (databas)
- [ ] Föreslå relevanta frågor baserat på profil
- [ ] Export av konversation till PDF
- [ ] Röstinput för chatten
