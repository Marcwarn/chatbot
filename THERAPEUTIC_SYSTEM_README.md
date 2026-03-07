# Therapeutic Conversation System

## Overview

This system implements professional psychological conversation techniques to make the AI feel like a trained psychologist. It combines evidence-based therapeutic approaches with personality psychology to create warm, insightful, and genuinely helpful conversations.

## Architecture

### Core Modules

```
therapeutic_integration.py          # Main orchestrator
├── therapeutic_techniques.py       # MI, Reframing, Socratic Method
├── rapport_builder.py             # Trust, Attunement, Boundaries
├── insight_generator.py           # Pattern Recognition, Strengths
├── emotional_calibration.py       # Emotion Detection & Response
└── conversation_pacing.py         # Timing, Rhythm, Flow
```

## 1. Therapeutic Techniques (`therapeutic_techniques.py`)

### Motivational Interviewing (OARS)

**Open Questions**
- Encourage exploration beyond yes/no
- Contextually relevant to user's situation
- Examples:
  ```python
  "Vad får dig att känna dig energisk och engagerad när du arbetar?"
  "Berätta mer om vad som är viktigt för dig i din karriär?"
  ```

**Affirmations**
- Recognize user's strengths and efforts
- Examples:
  ```python
  "Din självinsikt är verkligen värdefull"
  "Det krävs styrka att vara så ärlig om sina utmaningar"
  ```

**Reflective Listening**
- Mirror back feelings and content
- Format: "Det låter som att du [feeling] när [situation]"

**Summarizing**
- Tie together conversation themes
- Show you're listening and help user see bigger picture

### Cognitive Reframing

**Reframe Low Traits as Strengths**
- Low Extraversion → Deep reflection, meaningful relationships
- Low Agreeableness → Critical thinking, integrity
- Low Conscientiousness → Spontaneity, flexibility
- High Neuroticism → Emotional depth, empathy
- Low Openness → Practical wisdom, stability

**Challenge Negative Self-Talk**
- All-or-nothing thinking: "alltid" → "finns det situationer där detta inte stämmer?"
- Catastrophizing: Scale 1-10 perspective
- Mind reading: "Vad har de faktiskt sagt?"
- Should statements: Replace "borde" with "vill"
- Labeling: Focus on behavior vs identity

### Socratic Method

**Guiding Questions**
- Help users discover their own answers
- Avoid direct advice
- Example sequence:
  1. "Vad innebär framgång för dig?"
  2. "När känner du dig mest engagerad?"
  3. "Vilka styrkor används inte fullt ut?"
  4. "Vilket första lilla steg kan du ta?"

### Validation

**Validate Emotions**
- Anxiety: "Oro är människans sätt att förbereda sig"
- Frustration: "Din frustration är legitim"
- Sadness: "Din ledsenhet förtjänar att få ta plats"
- Shame: "Det är inte något att skämmas för"

**Normalize Experiences**
- "Många människor känner ensamhet..."
- "Det är helt naturligt att känna sig överväldigad..."

## 2. Rapport Building (`rapport_builder.py`)

### Trust Signals

- Confidentiality reminders
- Non-judgmental stance
- Safe space messaging
- Examples:
  ```python
  "Det här är en trygg plats för reflektion"
  "Jag är här för att lyssna utan att döma"
  ```

### Emotional Attunement

**Detect Tone**
- Distressed → Calm, reassuring
- Excited → Match enthusiasm
- Skeptical → Validate questioning
- Reflective → Deepen exploration
- Serious → Professional, measured

**Match Language Style**
- Formal ↔ Casual
- Technical ↔ Accessible
- Emotional ↔ Rational

### Boundaries

**Crisis Response**
```
🔴 112 för akut hjälp
📞 Mind Självmordslinjen: 90101
💬 1177 för vårdråd
```

**Scope Limitations**
- Can't diagnose
- Can't prescribe treatment
- Can't replace professional therapy
- CAN offer psychoeducation and coaching

### Alliance Management

**Detect Ruptures**
- Defensiveness: "Men jag är inte..."
- Disconnection: "Spelar ingen roll..."
- Mistrust: "Hur vet du..."
- Frustration: "Detta hjälper inte..."

**Repair Alliance**
```python
"Jag märker att något jag sa fick dig att gå i försvar.
Det var inte min mening. Kan du hjälpa mig förstå?"
```

## 3. Insight Generation (`insight_generator.py`)

### Pattern Recognition

**Connect Traits to Experiences**
- Low E + social exhaustion → "Ditt nervsystem upplever social interaktion som energikrävande"
- Low C + procrastination → "Din hjärna hanterar tid genom deadline-driven motivation"
- High O + High N + overthinking → "Kreativ hjärna + känslomässig intensitet = djup reflektion som kan bli övertänkande"

**Trait Combinations**
- High E + Low C = Spontan social energi
- High O + High A = Kreativ empati
- High O + Low A = Intellektuell självständighet

### Strengths-Based Approach

**Identify Core Strengths**
```python
strengths = [
    "Social energi: Du laddas av kontakt med andra",
    "Empatisk förståelse: Du bryr dig genuint om andra",
    "Pålitlig organisation: Du levererar kvalitet",
    ...
]
```

**Frame Challenges as Opportunities**
- Procrastination → Learn your brain's optimal rhythm
- Social anxiety → Discover which social settings work for YOU
- Perfectionism → Transform high standards into sustainable performance

### Growth Mindset

**Emphasize Malleability**
```
"Din position på [trait] är din baseline.
Men du kan utveckla nya beteenden och strategier
som arbetar MED dina naturliga tendenser."
```

**Celebrate Insights**
```
"Wow, det där är en kraftfull insikt!"
"Det där är exakt rätt observation."
```

**Encourage Experimentation**
```
"Tänk på detta som ett experiment. Det finns inget 'misslyckas'
här - bara data om vad som fungerar för DIG."
```

## 4. Emotional Calibration (`emotional_calibration.py`)

### Emotion Detection

**Patterns Recognized**
- Anxiety: "orolig", "nervös", "vad om...", repeated questions
- Confusion: "förstår inte", "oklart", multiple questions
- Defensiveness: "men jag är inte", "det stämmer inte"
- Excitement: "wow!", "fantastiskt!", multiple exclamation marks
- Disappointment: "besviken", "tråkigt att", "hade hoppats"
- Frustration: "frustrerad", "jobbigt", "försökt men..."
- Sadness: "ledsen", "mår dåligt", "orkar inte"
- Anger: "arg", "förbannad", profanity
- Shame: "skäms", "patetisk", "fel på mig"

### Response Calibration

**For Each Emotion**

| Emotion | Calibration |
|---------|-------------|
| Anxiety | Reassurance first, then information. Calm response. "Ta det i din egen takt." |
| Confusion | Simplify, use examples, check understanding. "Ger det mer mening nu?" |
| Defensiveness | Validate feelings, gentle reframing, emphasize choice. "Du vet bäst hur det är för dig." |
| Excitement | Match enthusiasm, dive deeper. "Jag älskar din energi!" |
| Disappointment | Empathy, alternative perspectives, hope. "Detta är inte hela bilden." |
| Frustration | Acknowledge, validate effort, problem-solve. "Låt oss hitta en ny approach." |
| Sadness | Empathy, validation, gentle hope. Spacious response. |
| Anger | Validate anger, explore underneath. "Din ilska har ett budskap." |
| Shame | Active shame reduction, compassion. "Du är inte 'fel'." |

## 5. Conversation Pacing (`conversation_pacing.py`)

### Conversation Phases

1. **Opening** - Building rapport, understanding context
2. **Exploration** - Deep dive into topics
3. **Insight** - Facilitating realizations
4. **Action** - Moving toward change
5. **Closing** - Wrapping up, summarizing

### Conversational Moves

**When to:**
- **Ask questions** - User is reflective, not after emotional sharing
- **Give information** - User asked direct question, expressed confusion
- **Validate emotions** - User shared feelings (always priority)
- **Summarize** - Long conversation (~10 exchanges), multiple topics
- **Pause for reflection** - User had deep insight, shared vulnerability
- **Change topics** - Stuck on same topic without progress

**Avoid:**
- Information dumping (>500 chars without check-in)
- Rapid-fire questions (>3 questions in a row)
- Premature advice (listen first)
- Repetitive phrases (track and vary language)

### Flow Control

**Prevent Information Dumping**
```python
if len(information) > 500:
    # Add check-in point
    "Följer du med hittills? Jag kan fortsätta..."
```

**Avoid Interrogation**
```python
if multiple_questions:
    "Det finns några saker som skulle vara värdefulla att utforska:
    - Question 1
    - Question 2
    Vilken känns mest relevant?"
```

**Create Reflection Pauses**
```
"Det där är en kraftfull insikt.
Ta en stund och känn efter hur det landar."
```

## Integration Example

```python
from therapeutic_integration import TherapeuticConversation

# Create conversation with user's profile
profile = {
    'E': 35,  # Introverted
    'A': 70,  # High agreeableness
    'C': 45,  # Moderate-low conscientiousness
    'N': 65,  # Emotionally reactive
    'O': 80,  # Very open
}

convo = TherapeuticConversation(profile)

# Opening
print(convo.get_opening_message())

# User messages
response1 = convo.respond("Jag fick låg extraversion. Betyder det att jag är tråkig?")
print(response1)

response2 = convo.respond("Jag kämpar med att få saker gjorda. Alltid prokrastinerar.")
print(response2)

# Closing
print(convo.get_closing_message())
```

## Response Generation Flow

```
User Message
     ↓
1. Check Alliance Rupture → Repair if needed
     ↓
2. Check Boundaries (crisis/medical) → Set boundaries if needed
     ↓
3. Detect Emotion (anxiety, frustration, etc.)
     ↓
4. Determine Conversation Phase (opening, exploration, etc.)
     ↓
5. Select Next Move (validate, ask, inform, etc.)
     ↓
6. Build Core Response (using appropriate technique)
     ↓
7. Add Validation (if emotion detected)
     ↓
8. Generate Insight (pattern recognition if applicable)
     ↓
9. Calibrate for Emotion (adjust tone and content)
     ↓
10. Build Rapport (match tone, empathy)
     ↓
11. Apply Pacing (prevent dumping, vary language)
     ↓
12. Final Polish (ensure warm, non-judgmental tone)
     ↓
Therapeutic Response
```

## Example Conversations

### Scenario 1: Disappointment with Low Extraversion

```
User: "Jag fick låg extraversion. Betyder det att jag är tråkig?"

AI: "Jag hör att du känner en viss besvikelse i det där. Först och
främst - introversion har absolut ingenting med att vara tråkig att göra.
Några av världens mest fascinerande personer är introverta.

Din låga extraversion betyder att du troligen laddar batterierna bäst i
lugnare miljöer och kanske föredrar djupare samtal med några få personer
framför stora sociala events.

Tänk dig - har du märkt att du faktiskt trivs i mindre grupper eller
enskilda samtal? Att du kanske behöver lite återhämtningstid efter stora
sociala tillställningar?

Det som extroverta kan uppleva som 'energigivande' kan för dig kräva mer
energi - och det är helt okej. Din introspektiva natur kan ge dig djup,
eftertänksamhet och meningsfulla relationer."
```

**Techniques Used:**
- ✓ Validation (besvikelse)
- ✓ Reframing (introversion = styrka)
- ✓ Psychoeducation (what E measures)
- ✓ Self-discovery question
- ✓ Strengths focus

### Scenario 2: Seeking Career Advice

```
User: "Vilken karriär passar min personlighet?"

AI: "Bra fråga! Innan jag ger förslag, skulle jag vilja förstå mer om
vad som är viktigt för dig.

Din profil visar hög Openness och låg Conscientiousness - vilket betyder
att du troligen trivs med kreativitet och variation, men kanske mindre
med rigid struktur.

Men låt mig fråga:
- Vad får dig att känna dig energisk och engagerad i arbetet?
- Föredrar du arbete med tydlig struktur eller flexibilitet?
- Trivs du bäst när du arbetar självständigt eller i team?
- Är variation eller specialisering viktigare för dig?

Dina svar på dessa frågor, kombinerat med din personlighetsprofil,
kommer ge oss en mycket tydligare bild av vilka karriärvägar som
skulle kunna passa dig."
```

**Techniques Used:**
- ✓ Socratic Method (exploration before prescription)
- ✓ Personalization (references profile)
- ✓ Collaborative framing
- ✓ Open questions

### Scenario 3: Procrastination Struggle

```
User: "Jag kämpar verkligen med att få saker gjorda. Alltid prokrastinerar."

AI: "Det låter som en verkligt utmanande situation. Jag uppskattar att
du delar det med mig.

Din låga Conscientiousness förklarar mycket av det du beskriver. Det är
inte lathet eller dålig karaktär - det är hur din hjärna hanterar tid
och motivation. Du arbetar bäst med närhet till deadline (deadline-driven
motivation) snarare än långsiktig planering.

Istället för att kämpa mot din naturliga rytm, kan vi designa system som
utnyttjar din deadline-driven energi - t.ex. artificiella deadlines,
accountability partners, eller kortare sprints istället för långsiktiga
projekt.

När du tänker på de gånger du faktiskt lyckats få saker gjorda - vad var
annorlunda då?"
```

**Techniques Used:**
- ✓ Validation (struggle acknowledgment)
- ✓ Pattern recognition (low C → procrastination)
- ✓ Normalization (not character flaw)
- ✓ Practical strategies
- ✓ Self-discovery question

## Quality Standards

Every response should have:

1. **Validation component** - Acknowledge feelings/experience
2. **Accessible language** - Avoid clinical jargon
3. **Balance** - Supportive AND informative
4. **Natural flow** - Swedish conversation patterns
5. **Appropriate boundaries** - Clear about AI limitations

Avoid:

- ❌ Clinical/academic tone
- ❌ Generic advice
- ❌ Judgment or "should" statements
- ❌ Information dumping
- ❌ Rapid-fire questioning

Aim for:

- ✅ Warm, professional tone
- ✅ Specific, personalized insights
- ✅ Collaborative exploration
- ✅ Balanced pacing
- ✅ Genuine empathy

## Testing

Run the demo:
```bash
python demo_therapeutic_system.py
```

This shows:
- Individual technique examples
- Emotion detection in action
- Rapport building elements
- Full conversation scenarios

## Integration with Main Chat

To integrate with existing personality coach:

```python
from therapeutic_integration import TherapeuticResponse

def chat_with_coach(message, profile, history):
    # Use therapeutic system for response
    response = TherapeuticResponse.generate_therapeutic_response(
        user_message=message,
        user_profile=profile,
        conversation_history=history
    )
    return response
```

## Future Enhancements

- [ ] Improve Swedish emotion keyword coverage
- [ ] Add session goal tracking
- [ ] Implement conversation theme detection
- [ ] Add psychoeducation content library
- [ ] Track intervention effectiveness
- [ ] Add multi-turn insight tracking
- [ ] Implement homework/practice suggestions
- [ ] Add crisis assessment scoring
- [ ] Create therapist supervision mode (for training)

## References

**Therapeutic Approaches:**
- Motivational Interviewing (Miller & Rollnick)
- Cognitive Behavioral Therapy (Beck)
- Socratic Questioning (Overholser)
- Person-Centered Therapy (Rogers)
- Strengths-Based Approach (Saleebey)

**Personality Psychology:**
- Big Five / OCEAN Model
- IPIP Assessment
- Trait Psychology

## License

Part of the Chatbot Personality Assessment System.
