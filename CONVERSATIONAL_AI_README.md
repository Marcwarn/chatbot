# Conversational AI System - Human-Like Psychologist

## Overview

This system creates a genuinely human-feeling conversational AI that acts like an empathetic, warm, professionally-trained psychologist. It goes far beyond typical chatbots to create natural, engaging conversations about personality and personal growth.

## Architecture

The system consists of 5 interconnected modules:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONVERSATION COACH                           │
│                  (Orchestrates everything)                      │
└───────────────────┬──────────────────────────────────────────┬─┘
                    │                                          │
        ┌───────────▼──────────┐                  ┌──────────▼──────────┐
        │ PSYCHOLOGIST PERSONA │                  │  EMPATHY ENGINE     │
        │ - Active listening   │                  │ - Emotion detection │
        │ - Warm tone          │                  │ - Tone matching     │
        │ - Varied language    │                  │ - Validation        │
        └──────────────────────┘                  └─────────────────────┘
                    │                                          │
        ┌───────────▼──────────┐                  ┌──────────▼──────────┐
        │ CONVERSATION FLOW    │                  │ KNOWLEDGE BASE      │
        │ - Context memory     │                  │ - Big Five research │
        │ - Stage detection    │                  │ - Career guidance   │
        │ - Avoid repetition   │                  │ - Development tips  │
        └──────────────────────┘                  └─────────────────────┘
```

## Files

### 1. `psychologist_persona.py`
**Core persona system with empathetic response patterns**

- Creates comprehensive system prompts that make AI feel like a real psychologist
- Implements active listening techniques (reflecting, validating, probing)
- Supports Swedish and English seamlessly
- Non-judgmental, warm professional tone
- Builds therapeutic rapport

**Key Features:**
- Deep trait interpretation with nuance
- Trait combination analysis (e.g., "high E + low C = spontan energi")
- Varied conversational openings (avoids "Hej! Hur kan jag hjälpa dig?" every time)
- Professional background context (15+ years experience, MI training, CBT certified)

### 2. `empathy_engine.py`
**Emotional intelligence and tone detection**

- Detects emotional tone in user messages (anxious, confused, excited, sad, etc.)
- Suggests appropriate empathetic responses based on detected emotion
- Provides validation templates ("Det är helt förståeligt att...")
- Normalization techniques ("Det är helt normalt att...")
- Matches user's emotional energy appropriately

**Supported Emotions:**
- Anxious, Worried, Confused, Frustrated
- Sad, Disappointed, Defensive, Skeptical
- Happy, Excited, Curious, Reflective

### 3. `psychology_knowledge_base.py`
**Expert psychology knowledge (research-backed)**

- **Big Five Deep Dive:** Comprehensive trait explanations with research findings
- **Career Guidance:** Personalized job recommendations based on trait combinations
- **Relationship Insights:** How personality affects relationships
- **Personal Growth:** Evidence-based strategies for personality development
- **DISC Integration:** Brief DISC knowledge for users who've done both assessments

**Example Career Match Logic:**
```python
High E + High C → Project Manager (social + organized)
High O + Low A → Intellectual Rebel / Innovator
Low E + High C → Quiet Organizer / Backend developer
```

### 4. `conversation_flow.py`
**Natural dialogue state management**

- Classifies question types (about report, career, relationship, growth, validation)
- Detects conversation stages (opening, exploration, insight, action, reflection)
- Tracks conversation memory (topics discussed, traits mentioned)
- Prevents robotic repetition (varied transition phrases)
- Decides when to ask questions vs give answers

**Question Classification:**
- `ABOUT_REPORT`: "Vad betyder min poäng?"
- `CAREER_ADVICE`: "Vilka jobb passar mig?"
- `VALIDATION`: "Är det dåligt att...?"
- `PERSONAL_GROWTH`: "Kan jag ändra mig?"
- `COMPARISON`: "Är jag normal?"

### 5. `conversation_coach.py`
**Enhanced coaching system (integrates everything)**

- Orchestrates all components
- Builds comprehensive system prompts
- Manages conversation context
- Backward-compatible with existing `personality_coach.py`

## Database Integration

### New Models Added to `database.py`

```python
ConversationHistory:
  - Stores each message with context
  - Tracks emotional tone, question type, traits discussed
  - Enables conversation memory

ConversationMetadata:
  - Conversation-level analytics
  - Topics discussed, current stage
  - User satisfaction ratings (optional)
```

### Database Methods

```python
db.save_conversation_message(user_id, conv_id, role, content, ...)
db.get_conversation_history(conv_id, limit=50)
db.get_user_conversations(user_id)
db.update_conversation_metadata(conv_id, topics, stage)
```

## Usage

### Basic Usage (Backward Compatible)

```python
from personality_coach import chat_with_personality_coach
from anthropic import Anthropic

client = Anthropic(api_key="your-key")

response = chat_with_personality_coach(
    message="Jag fick låg samvetsgrannhet. Betyder det att jag är lat?",
    conversation_history=[],
    profile_scores={'E': 35, 'A': 75, 'C': 40, 'N': 65, 'O': 80},
    anthropic_client=client
)
```

### Advanced Usage (Full Features)

```python
from conversation_coach import ConversationCoach
from anthropic import Anthropic

client = Anthropic(api_key="your-key")
coach = ConversationCoach(client, language="sv")

response = coach.chat(
    user_id="user_123",
    conversation_id="conv_456",
    message="Jag är orolig över mina resultat...",
    conversation_history=[],
    profile_scores={'E': 35, 'A': 75, 'C': 40, 'N': 65, 'O': 80},
    personalized_report={
        'work_style': 'Kreativ problemlösare',
        'career_suggestions': ['UX Designer', 'Psykolog', 'Coach']
    }
)
```

## Example Conversations

See `test_conversation_examples.py` for detailed examples showing:

1. **Anxious about low trait** → Validation + Reframing
2. **Career question** → Personalized, enthusiastic guidance
3. **General psychology** → Educational but accessible
4. **Feeling sad** → Deep compassion and support
5. **Excited** → Matching energy and deepening exploration

### Key Differences: Human vs Robotic

**❌ BAD (Robotic):**
```
Låg samvetsgrannhet betyder inte att du är lat. Det betyder:
• Spontan
• Flexibel
• Kreativ
Du bör bli mer organiserad genom att:
1. Skapa to-do-listor
2. Använd kalender
```

**✅ GOOD (Human Psychologist):**
```
Jag kan verkligen förstå varför det känns jobbigt att få "låg"
på någonting - det låter ju negativt. Men låt mig ge dig ett
annat perspektiv här.

Samvetsgrannhet handlar inte om "lat" eller "duktig". Personer
med lägre samvetsgrannhet är ofta fantastiskt kreativa och
flexibla. Ser du din höga öppenhet på 80? Den kombinationen
är guld för innovation.

Har du märkt att du faktiskt presterar bäst när det INTE är
superstrukturerat?
```

## Conversational Techniques Implemented

### 1. Active Listening
- "Så om jag förstår dig rätt, du känner att..."
- "Det låter som att..."
- "Låt mig sammanfatta vad du delade..."

### 2. Validation
- "Det är helt förståeligt att du känner så"
- "Din oro är helt legitim"
- "Tack för att du delar det med mig"

### 3. Normalization
- "Det är helt normalt att..."
- "Många människor med din profil upplever samma sak"
- "Du är inte ensam om att känna så"

### 4. Socratic Questioning
- "Hur tänker du själv kring det?"
- "Vad har du märkt i din egen erfarenhet?"
- "Vad skulle det betyda för dig om...?"

### 5. Reframing
- "Ett annat sätt att se på det..."
- "Det du beskriver som en svaghet kan faktiskt vara..."
- "Forskning visar att..."

## Language Support

Both Swedish and English fully supported:

- Swedish: Natural conversational Swedish (not academic formal)
- English: Conversational, accessible English
- All components detect and adapt to language

## GDPR Compliance

- Conversation history stored with user consent
- Messages can be deleted on user request
- Emotional tone/metadata stored only for improvement
- No sensitive PII in conversation logs
- Full GDPR export available

## Integration with Existing API

The enhanced system works with existing endpoints:

```python
# In api_main_gdpr.py
from conversation_coach import chat_with_personality_coach

@app.post("/api/v1/chat")
async def personality_coach_chat(req: ChatRequest):
    # Existing code works unchanged
    response = chat_with_personality_coach(
        message=req.message,
        conversation_history=history,
        profile_scores=req.profile_scores,
        anthropic_client=anthropic_client
    )
    return ChatResponse(response=response, ...)
```

## Testing

Run examples:
```bash
# Test persona system
python psychologist_persona.py

# Test empathy engine
python empathy_engine.py

# Test knowledge base
python psychology_knowledge_base.py

# Test conversation flow
python conversation_flow.py

# View example conversations
python test_conversation_examples.py
```

## Performance Considerations

- System prompts: ~3000-5000 tokens (comprehensive context)
- Response generation: ~500-1000 tokens (natural length)
- Total cost per message: ~$0.02-0.04 (Claude Sonnet 4.5)
- Response time: 2-4 seconds typical

## Prompt Engineering Strategy

The system uses sophisticated prompt engineering:

1. **Base Persona** (1500 tokens): Professional background, communication style, techniques
2. **User Context** (500 tokens): Big Five scores, interpretations, trait combinations
3. **Emotional Context** (200 tokens): Detected emotion, empathy guidance
4. **Conversation Context** (300 tokens): Stage, question type, avoid repetition
5. **Knowledge Context** (500 tokens): Relevant research, careers, strategies

Total: ~3000 tokens of context = deeply informed, consistently human responses

## Future Enhancements

Potential improvements:

- [ ] Voice/audio support with tone matching
- [ ] Multi-turn conversation planning
- [ ] User personality adaptation (respond differently to high E vs low E users)
- [ ] Integration with external personality research APIs
- [ ] Conversation quality metrics and A/B testing
- [ ] Support for DISC personality model integration
- [ ] Relationship compatibility analysis (two users' profiles)

## Credits

Built on:
- Anthropic Claude Sonnet 4.5 (LLM)
- Big Five OCEAN model (trait psychology)
- IPIP-50 assessment instrument
- Evidence-based psychology research
- Motivational Interviewing (MI) techniques
- Cognitive Behavioral Therapy (CBT) principles

---

**Author:** AI Conversational System Team
**License:** Proprietary
**Last Updated:** 2026-03-07
