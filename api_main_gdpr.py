"""
Persona – GDPR-Compliant Big Five Personality Assessment API
Uses validated IPIP-50 questions (static, not AI-generated)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import json
from anthropic import Anthropic

from database import (
    db, User, UserConsent, Assessment as DBAssessment,
    AssessmentQuestion as DBQuestion,
    AssessmentAnswer as DBAnswer,
    AssessmentResult as DBResult,
    AuditLog
)
from api_gdpr import router as gdpr_router

# ── Bootstrap ────────────────────────────────────────────────────────────────
db.create_tables()

app = FastAPI(
    title="Persona – Big Five Assessment API",
    description="Scientifically-validated IPIP-50 personality assessment with GDPR compliance",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gdpr_router)

# ── Anthropic AI Client ──────────────────────────────────────────────────────
anthropic_client = None
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        anthropic_client = Anthropic(api_key=api_key)
except Exception:
    pass  # AI reports optional if no API key

# ── IPIP-50 Question Bank (Swedish, validated) ───────────────────────────────

IPIP_QUESTIONS = [
    # EXTRAVERSION
    {"id": 1,  "text": "Jag är den som pratar mest på en fest",                "dim": "E", "keyed": "+"},
    {"id": 2,  "text": "Jag pratar inte särskilt mycket",                      "dim": "E", "keyed": "-"},
    {"id": 3,  "text": "Jag känner mig bekväm i grupp",                        "dim": "E", "keyed": "+"},
    {"id": 4,  "text": "Jag håller mig hellre i bakgrunden",                   "dim": "E", "keyed": "-"},
    {"id": 5,  "text": "Jag tar gärna initiativ till samtal",                  "dim": "E", "keyed": "+"},
    {"id": 6,  "text": "Jag har lite att säga i sociala sammanhang",           "dim": "E", "keyed": "-"},
    {"id": 7,  "text": "Jag pratar gärna med många på fester",                 "dim": "E", "keyed": "+"},
    {"id": 8,  "text": "Jag vill inte vara i centrum av uppmärksamheten",      "dim": "E", "keyed": "-"},
    {"id": 9,  "text": "Jag tar gärna ledningen i grupp",                      "dim": "E", "keyed": "+"},
    {"id": 10, "text": "Jag är tyst och tillbakadragen med okända",            "dim": "E", "keyed": "-"},
    # AGREEABLENESS
    {"id": 11, "text": "Jag bryr mig genuint om andras välmående",             "dim": "A", "keyed": "+"},
    {"id": 12, "text": "Jag kan vara hård och direkt mot folk",                "dim": "A", "keyed": "-"},
    {"id": 13, "text": "Jag förstår andras känslor",                           "dim": "A", "keyed": "+"},
    {"id": 14, "text": "Jag är sällan intresserad av andras problem",          "dim": "A", "keyed": "-"},
    {"id": 15, "text": "Jag har ett varmt och omtänksamt hjärta",              "dim": "A", "keyed": "+"},
    {"id": 16, "text": "Jag är inte alltid intresserad av hur andra mår",      "dim": "A", "keyed": "-"},
    {"id": 17, "text": "Jag tar tid att hjälpa andra",                         "dim": "A", "keyed": "+"},
    {"id": 18, "text": "Jag är lyhörd för andras känslor",                     "dim": "A", "keyed": "+"},
    {"id": 19, "text": "Jag skapar en bekväm stämning runt mig",               "dim": "A", "keyed": "+"},
    {"id": 20, "text": "Jag är svår att lära känna på djupet",                 "dim": "A", "keyed": "-"},
    # CONSCIENTIOUSNESS
    {"id": 21, "text": "Jag är alltid väl förberedd",                          "dim": "C", "keyed": "+"},
    {"id": 22, "text": "Jag lämnar saker och ting i oordning",                 "dim": "C", "keyed": "-"},
    {"id": 23, "text": "Jag uppmärksammar detaljer noga",                      "dim": "C", "keyed": "+"},
    {"id": 24, "text": "Jag skapar lätt röra hemma och på jobbet",             "dim": "C", "keyed": "-"},
    {"id": 25, "text": "Jag slutför uppgifter snabbt och direkt",              "dim": "C", "keyed": "+"},
    {"id": 26, "text": "Jag skjuter upp saker på framtiden",                   "dim": "C", "keyed": "-"},
    {"id": 27, "text": "Jag arbetar systematiskt och följer en plan",          "dim": "C", "keyed": "+"},
    {"id": 28, "text": "Jag missar ibland viktiga deadlines",                  "dim": "C", "keyed": "-"},
    {"id": 29, "text": "Jag avslutar alltid det jag börjar",                   "dim": "C", "keyed": "+"},
    {"id": 30, "text": "Jag gör inte mer än vad som absolut krävs",           "dim": "C", "keyed": "-"},
    # NEUROTICISM
    {"id": 31, "text": "Jag blir lätt upprörd eller stressad",                 "dim": "N", "keyed": "+"},
    {"id": 32, "text": "Jag är avslappnad de flesta dagar",                    "dim": "N", "keyed": "-"},
    {"id": 33, "text": "Jag oroar mig ofta för saker",                         "dim": "N", "keyed": "+"},
    {"id": 34, "text": "Jag blir sällan stressad",                             "dim": "N", "keyed": "-"},
    {"id": 35, "text": "Jag kan bli irriterad snabbt",                         "dim": "N", "keyed": "+"},
    {"id": 36, "text": "Jag hanterar stress bra",                              "dim": "N", "keyed": "-"},
    {"id": 37, "text": "Jag har humörsvängningar",                             "dim": "N", "keyed": "+"},
    {"id": 38, "text": "Jag störs sällan av oro eller ångest",                 "dim": "N", "keyed": "-"},
    {"id": 39, "text": "Jag kan bli melankolisk eller nedstämd",               "dim": "N", "keyed": "+"},
    {"id": 40, "text": "Jag är känslomässigt stabil och jämn",                 "dim": "N", "keyed": "-"},
    # OPENNESS
    {"id": 41, "text": "Jag har en livlig och aktiv fantasi",                  "dim": "O", "keyed": "+"},
    {"id": 42, "text": "Jag har ibland svårt att förstå abstrakta idéer",     "dim": "O", "keyed": "-"},
    {"id": 43, "text": "Jag har intressanta och originella idéer",             "dim": "O", "keyed": "+"},
    {"id": 44, "text": "Jag saknar stark kreativ fantasi",                     "dim": "O", "keyed": "-"},
    {"id": 45, "text": "Jag lär mig snabbt och förstår saker lätt",           "dim": "O", "keyed": "+"},
    {"id": 46, "text": "Jag föredrar konkreta fakta framför teorier",          "dim": "O", "keyed": "-"},
    {"id": 47, "text": "Jag gillar att reflektera och leka med idéer",         "dim": "O", "keyed": "+"},
    {"id": 48, "text": "Jag är inte alltid intresserad av konst och kultur",   "dim": "O", "keyed": "-"},
    {"id": 49, "text": "Jag är nyfiken på allt möjligt",                       "dim": "O", "keyed": "+"},
    {"id": 50, "text": "Jag föredrar rutiner framför nya erfarenheter",        "dim": "O", "keyed": "-"},
]

DIMENSION_META = {
    "E": {"name": "Extraversion",         "name_sv": "Extraversion"},
    "A": {"name": "Agreeableness",        "name_sv": "Vänlighet"},
    "C": {"name": "Conscientiousness",    "name_sv": "Samvetsgrannhet"},
    "N": {"name": "Neuroticism",          "name_sv": "Emotionell stabilitet"},
    "O": {"name": "Openness",             "name_sv": "Öppenhet"},
}

INTERPRETATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "E": {
        "high": {
            "tag": "Extrovert",
            "sv": "Du drar energi från att vara med andra. Du är social, pratsam och trivs naturligt i centrum. Du tar gärna initiativ och skapar kontakter med lätthet.",
            "en": "You gain energy from others. You are social, talkative, and thrive in the spotlight.",
        },
        "mid": {
            "tag": "Ambivert",
            "sv": "Du är bekväm i både sociala och ensamma sammanhang och anpassar dig väl till situationen.",
            "en": "You are comfortable in both social and solitary settings, adapting well to either.",
        },
        "low": {
            "tag": "Introvert",
            "sv": "Du laddar dina batterier genom ensamtid och reflektion. Du lyssnar mer än du pratar och värdesätter djupa relationer.",
            "en": "You recharge through solitude and reflection, preferring depth over breadth in relationships.",
        },
    },
    "A": {
        "high": {
            "tag": "Samarbetsvillig",
            "sv": "Du är empatisk, omtänksam och genuint intresserad av andra. Du värdesätter harmoni och är en person folk gärna vänder sig till.",
            "en": "You are empathetic, cooperative, and genuinely interested in others' wellbeing.",
        },
        "mid": {
            "tag": "Balanserad",
            "sv": "Du balanserar samarbete med självhävdelse och navigerar sociala situationer med pragmatism.",
            "en": "You balance cooperation with self-assertion and navigate social dynamics pragmatically.",
        },
        "low": {
            "tag": "Självständig",
            "sv": "Du är direkt, självständig och konkurrensorienterad. Du värderar ärlighet framför diplomati.",
            "en": "You are direct, independent, and competitive, valuing honesty over diplomacy.",
        },
    },
    "C": {
        "high": {
            "tag": "Organiserad",
            "sv": "Du är strukturerad, pålitlig och målfokuserad. Du planerar noggrant och levererar konsekvent hög kvalitet.",
            "en": "You are organized, dependable, and goal-oriented, consistently delivering high quality.",
        },
        "mid": {
            "tag": "Flexibel",
            "sv": "Du balanserar struktur med flexibilitet och är organiserad när situationen kräver det.",
            "en": "You balance structure with flexibility, being organized when the situation calls for it.",
        },
        "low": {
            "tag": "Spontan",
            "sv": "Du är spontan, flexibel och kreativ. Du trivs med frihet och är anpassningsbar i förändring.",
            "en": "You are spontaneous, flexible, and creative, thriving with freedom and change.",
        },
    },
    "N": {
        # Displayed as emotional stability (inverted)
        "high": {
            "tag": "Känslosam",
            "sv": "Du är känslomässigt lyhörd och sensitiv. Du upplever djupa känslor och din empatiska förmåga är en styrka.",
            "en": "You are emotionally sensitive and experience deep feelings, with strong empathic capacity.",
        },
        "mid": {
            "tag": "Balanserad",
            "sv": "Du hanterar stress relativt bra men kan påverkas av svåra situationer. Du har en normal känslomässig variation.",
            "en": "You handle stress reasonably well with a normal range of emotional responses.",
        },
        "low": {
            "tag": "Stabil",
            "sv": "Du är lugn och samlad under press. Du återhämtar dig snabbt och behåller lugnet – en stark tillgång i team.",
            "en": "You are calm under pressure, recovering quickly from setbacks — a stabilizing force in teams.",
        },
    },
    "O": {
        "high": {
            "tag": "Kreativ",
            "sv": "Du är nyfiken, kreativ och öppen för nya erfarenheter. Du söker djup och mening och tänker gärna utanför boxen.",
            "en": "You are curious, creative, and open to new experiences, often thinking outside the box.",
        },
        "mid": {
            "tag": "Pragmatisk",
            "sv": "Du är pragmatisk men öppen för nya idéer och balanserar tradition med innovation.",
            "en": "You are pragmatic yet open to new ideas, balancing tradition with innovation.",
        },
        "low": {
            "tag": "Traditionell",
            "sv": "Du är praktisk, konkret och traditionell. Du föredrar beprövade metoder och trivs med rutiner.",
            "en": "You are practical, concrete, and conventional, preferring proven methods and routines.",
        },
    },
}

LIKERT_OPTIONS = [
    "1 - Stämmer inte alls",
    "2 - Stämmer dåligt",
    "3 - Neutral",
    "4 - Stämmer ganska bra",
    "5 - Stämmer helt",
]

# ── Pydantic Models ──────────────────────────────────────────────────────────

class StartAssessmentRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    language: str = Field(default="sv")
    # GDPR explicit consent
    consent_data_processing: bool = Field(..., description="Required: consent for data processing")
    consent_analysis: bool = Field(..., description="Required: consent for algorithmic analysis")
    consent_storage: bool = Field(default=True)


class QuestionOut(BaseModel):
    question_id: int
    text: str
    dimension: str
    dimension_name: str
    scale_type: str = "likert_5"
    options: List[str]


class AssessmentStartResponse(BaseModel):
    assessment_id: str
    user_id: str
    questions: List[QuestionOut]
    total_questions: int
    gdpr_notice: str


class AnswerIn(BaseModel):
    question_id: int
    value: int = Field(..., ge=1, le=5)


class SubmitAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[AnswerIn]


class DimensionScore(BaseModel):
    dimension: str
    dimension_name: str
    raw_score: float          # mean 1–5
    percentile: float         # 0–100
    display_score: float      # 0–100 (N is inverted)
    level: str                # "high" | "mid" | "low"
    tag: str
    interpretation: str


class PersonalizedReport(BaseModel):
    """AI-generated personalized insights based on unique trait combination"""
    profile_overview: str
    work_style: str
    communication_style: str
    career_suggestions: List[str]
    relationship_insights: str
    development_areas: List[str]


class AssessmentResultOut(BaseModel):
    assessment_id: str
    user_id: str
    completed_at: datetime
    headline: str
    scores: List[DimensionScore]
    strengths: List[str]
    personalized_report: Optional[PersonalizedReport] = None  # AI-generated if API key available
    gdpr_notice: str


# ── Scoring Logic ─────────────────────────────────────────────────────────────

def score_dimension(questions: list, answers: Dict[int, int]) -> float:
    """Returns mean score 1–5 with reverse scoring applied."""
    total = 0
    count = 0
    for q in questions:
        v = answers.get(q["id"], 3)
        if q["keyed"] == "-":
            v = 6 - v
        total += v
        count += 1
    return total / count if count else 3.0


def mean_to_percentile(mean: float) -> float:
    """Approximate percentile using population norms (mean≈3.0, sd≈0.7)."""
    import math
    z = (mean - 3.0) / 0.7
    return round(min(99, max(1, 50 * (1 + math.erf(z / math.sqrt(2))))), 1)


def level(percentile: float) -> str:
    if percentile >= 65:
        return "high"
    if percentile <= 35:
        return "low"
    return "mid"


def build_strengths(dim_scores: Dict[str, float], lang: str = "sv") -> List[str]:
    strengths = []
    key = "sv" if lang == "sv" else "en"
    if dim_scores.get("E", 50) >= 65:
        strengths.append("Du bygger nätverk och relationer med naturlig lätthet." if lang == "sv" else "You build networks and relationships with natural ease.")
    elif dim_scores.get("E", 50) <= 35:
        strengths.append("Du lyssnar aktivt och tänker innan du agerar — en sällsynt förmåga." if lang == "sv" else "You listen carefully and think before acting — a rare skill.")
    if dim_scores.get("A", 50) >= 65:
        strengths.append("Din empati gör dig till en uppskattad kollega och vän." if lang == "sv" else "Your empathy makes you a valued colleague and friend.")
    if dim_scores.get("C", 50) >= 65:
        strengths.append("Du levererar konsekvent hög kvalitet och kan litas på." if lang == "sv" else "You consistently deliver high quality and can be relied upon.")
    if dim_scores.get("N_display", 50) >= 65:
        strengths.append("Ditt lugn under press smittar av sig och stabiliserar team." if lang == "sv" else "Your calm under pressure stabilizes those around you.")
    if dim_scores.get("O", 50) >= 65:
        strengths.append("Din kreativitet och nyfikenhet driver innovation." if lang == "sv" else "Your creativity and curiosity drive innovation.")
    return strengths[:4] if strengths else (
        ["Du har en balanserad och mångsidig personlighet."] if lang == "sv"
        else ["You have a balanced and versatile personality."]
    )


def generate_headline(dim_scores: Dict[str, float], lang: str = "sv") -> str:
    traits = []
    if dim_scores.get("O", 50) >= 65:
        traits.append("kreativ" if lang == "sv" else "creative")
    if dim_scores.get("C", 50) >= 65:
        traits.append("strukturerad" if lang == "sv" else "structured")
    if dim_scores.get("E", 50) >= 65:
        traits.append("social")
    if dim_scores.get("A", 50) >= 65:
        traits.append("empatisk" if lang == "sv" else "empathetic")
    if dim_scores.get("N_display", 50) >= 65:
        traits.append("stabil" if lang == "sv" else "stable")
    if dim_scores.get("E", 50) <= 35:
        traits.append("reflekterad" if lang == "sv" else "reflective")
    if dim_scores.get("C", 50) <= 35:
        traits.append("spontan" if lang == "sv" else "spontaneous")

    if not traits:
        return "Balanserad och mångsidig personlighet" if lang == "sv" else "Balanced and versatile personality"
    if len(traits) == 1:
        return f"En {traits[0]} personlighet" if lang == "sv" else f"A {traits[0]} personality"
    last = traits.pop()
    return f"En {', '.join(traits)} och {last} personlighet" if lang == "sv" else f"A {', '.join(traits)} and {last} personality"


def generate_personalized_report(
    dim_scores: Dict[str, float],
    percentiles: Dict[str, float],
    lang: str = "sv"
) -> Optional[PersonalizedReport]:
    """
    Generate deeply personalized insights using Claude AI.
    Analyzes trait combinations for nuanced, individual-specific content.
    """
    if not anthropic_client:
        return None  # No API key - skip AI report

    # Build profile summary for AI
    profile_data = {
        "Extraversion": percentiles["E"],
        "Agreeableness": percentiles["A"],
        "Conscientiousness": percentiles["C"],
        "Emotional_Stability": 100 - percentiles["N"],  # Inverted N
        "Openness": percentiles["O"],
    }

    is_swedish = lang == "sv"
    lang_name = "svenska" if is_swedish else "English"

    prompt = f"""Du är en expert på personlighetspsykologi och Big Five-modellen (OCEAN) med 20+ års erfarenhet. Du ska skapa en EXCEPTIONELLT djup och personaliserad rapport baserad på följande Big Five-profil (percentiler 0-100, där 50 är median):

**Profil:**
- Extraversion: {profile_data['Extraversion']:.1f}
- Vänlighet (Agreeableness): {profile_data['Agreeableness']:.1f}
- Samvetsgrannhet (Conscientiousness): {profile_data['Conscientiousness']:.1f}
- Emotionell stabilitet (inverted Neuroticism): {profile_data['Emotional_Stability']:.1f}
- Öppenhet (Openness): {profile_data['Openness']:.1f}

**Uppgift:** Skriv en ovanligt insiktsfull, personlig rapport på {lang_name} som går DJUPT på KOMBINATIONEN av dessa drag. Detta är inte en generisk sammanfattning - det ska kännas som en personlig coaching-session där du verkligen FÖRSTÅR personen.

**Format (returnera som JSON):**
```json
{{
  "profile_overview": "3-4 meningar som fångar personens UNIKA kombination av drag med SPECIFIKA exempel på hur de samverkar. Börja med 'Din personlighet kännetecknas av...' och GE KONKRETA SCENARION (t.ex. 'När du står inför ett beslut tenderar du att...')",

  "work_style": "4-5 meningar om EXAKT hur personen arbetar optimalt. Inkludera: idealisk arbetsmiljö (öppet kontor vs eget rum? Musik vs tystnad?), beslutsfattande (snabbt vs analytiskt?), energihantering över dagen, projektarbete vs självständigt arbete, hur de hanterar deadlines och stress. GE KONKRETA EXEMPEL och HANDLINGSBARA TIPS.",

  "communication_style": "4-5 meningar om kommunikation med DJUPA insikter. Hur de tar emot kritik? Hur de ger feedback? Skillnad mellan skriftlig vs muntlig kommunikation? Hur de bygger förtroende? Vad som händer i konflikter? Hur de påverkar gruppdynamik? KONKRETA EXEMPEL och COACHANDE RÅD.",

  "career_suggestions": ["5-7 MYCKET SPECIFIKA karriärvägar/roller med kort motivering för varje. Inte bara 'UX-designer' utan 'UX-designer på produktteam (din kombination av kreativitet och empati gör dig perfekt för användarforskning och iterativt designarbete)'. VERKLIGT SPECIFIKA JOBBTITLAR."],

  "relationship_insights": "4-5 meningar om relationer (vänskap, romantik, team) med OVANLIG DJUP. Vad händer när personen blir stressad? Hur uttrycker de kärlek/uppskattning? Vad är deras 'osynliga gåvor' i relationer? Blinda fläckar? Hur kan partners/vänner KONKRET stötta dem? ACTIONABLE INSIGHTS.",

  "development_areas": ["3-4 utvecklingsområden med MYCKET KONKRETA, STEG-FÖR-STEG råd. Varje råd ska innehålla: (1) VAD problemet är, (2) VARFÖR det uppstår baserat på deras profil, (3) EXAKT HUR de kan jobba med det (specifika verktyg, övningar, mindsets). Exempel: 'Din höga öppenhet + låga samvetsgrannhet kan göra att projekt förblir halvfärdiga. PROVA: (1) Börja varje måndag med att välja MAX 3 projekt att fokusera på, (2) Använd Pomodoro (25 min fokus) för att kanalisera kreativitet till färdigställande, (3) Belöna dig när saker blir klara (din hjärna behöver dopamin-kickar för att bygga completion-vana).'"]
}}
```

**KRITISKA KVALITETSKRAV:**
1. **DJUP ANALYS av draginteraktioner** - Hur påverkar hög E + låg C SPECIFIKT arbetsvanor? Ge exempel!
2. **KONKRET och ACTIONABLE** - Varje insikt ska leda till handling
3. **PERSONLIGT och VARMT** - Skriv som en erfaren coach som bryr sig
4. **NUANSERAT** - Både styrkor OCH utmaningar, men alltid konstruktivt
5. **SPECIFIKA EXEMPEL** - "När du..." scenarios som personen känner igen sig i
6. **"DU"-FORM** genomgående
7. **LÄNGRE ÄN VANLIGT** - Detta ska vara en DJUP rapport, inte ytlig

GÖR DETTA EXCEPTIONELLT BRA. Personen ska känna "WOW, detta beskriver MIG på djupet!"

Generera rapporten nu:"""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,  # Increased for deeper, more detailed reports
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(response_text)

        return PersonalizedReport(
            profile_overview=data["profile_overview"],
            work_style=data["work_style"],
            communication_style=data["communication_style"],
            career_suggestions=data["career_suggestions"],
            relationship_insights=data["relationship_insights"],
            development_areas=data["development_areas"],
        )

    except Exception as e:
        print(f"AI report generation failed: {e}")
        return None  # Gracefully degrade - return None if AI fails


# ── In-memory session store (replace with DB in production) ──────────────────

_sessions: Dict[str, dict] = {}


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Persona – Big Five Assessment API",
        "version": "3.0.0",
        "docs": "/docs",
        "instrument": "IPIP-50 (International Personality Item Pool)",
        "status": "ready",
    }


@app.post("/api/v1/assessment/start", response_model=AssessmentStartResponse)
async def start_assessment(req: StartAssessmentRequest):
    """Begin a new IPIP-50 Big Five assessment. GDPR consent required."""

    if not req.consent_data_processing or not req.consent_analysis:
        raise HTTPException(
            status_code=400,
            detail="GDPR: Consent for data processing and analysis is required."
        )

    user_id = req.user_id or str(uuid.uuid4())
    assessment_id = str(uuid.uuid4())

    # Build question list
    questions_out = [
        QuestionOut(
            question_id=q["id"],
            text=q["text"],
            dimension=q["dim"],
            dimension_name=DIMENSION_META[q["dim"]]["name_sv"],
            options=LIKERT_OPTIONS,
        )
        for q in IPIP_QUESTIONS
    ]

    # Store session
    _sessions[assessment_id] = {
        "user_id": user_id,
        "language": req.language,
        "started_at": datetime.utcnow().isoformat(),
        "consents": {
            "data_processing": req.consent_data_processing,
            "analysis": req.consent_analysis,
            "storage": req.consent_storage,
        },
    }

    return AssessmentStartResponse(
        assessment_id=assessment_id,
        user_id=user_id,
        questions=questions_out,
        total_questions=len(questions_out),
        gdpr_notice=(
            "Dina svar behandlas GDPR-säkert. Du kan begära export eller radering via /api/v1/gdpr/export och /api/v1/gdpr/delete."
            if req.language == "sv"
            else "Your responses are processed in accordance with GDPR. Export or delete via /api/v1/gdpr/export and /api/v1/gdpr/delete."
        ),
    )


@app.post("/api/v1/assessment/submit", response_model=AssessmentResultOut)
async def submit_assessment(req: SubmitAssessmentRequest):
    """Submit answers and receive scored Big Five profile."""

    session = _sessions.get(req.assessment_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found.")

    lang = session.get("language", "sv")
    answers_map: Dict[int, int] = {a.question_id: a.value for a in req.answers}

    # Score each dimension
    dim_keys = ["E", "A", "C", "N", "O"]
    raw_means: Dict[str, float] = {}
    for d in dim_keys:
        q_subset = [q for q in IPIP_QUESTIONS if q["dim"] == d]
        raw_means[d] = score_dimension(q_subset, answers_map)

    percentiles: Dict[str, float] = {d: mean_to_percentile(raw_means[d]) for d in dim_keys}

    # Neuroticism → emotional stability for display
    n_display = 100 - percentiles["N"]
    display_scores: Dict[str, float] = {
        **{d: percentiles[d] for d in ["E", "A", "C", "O"]},
        "N": n_display,
        "N_display": n_display,
    }

    dim_scores_out: List[DimensionScore] = []
    for d in dim_keys:
        pct = percentiles[d]
        disp = display_scores[d]
        lvl = level(disp)
        interp = INTERPRETATIONS[d][lvl]
        dim_scores_out.append(DimensionScore(
            dimension=d,
            dimension_name=DIMENSION_META[d]["name_sv"],
            raw_score=round(raw_means[d], 2),
            percentile=pct,
            display_score=disp,
            level=lvl,
            tag=interp["tag"],
            interpretation=interp["sv"] if lang == "sv" else interp["en"],
        ))

    headline = generate_headline(display_scores, lang)
    strengths = build_strengths(display_scores, lang)

    _sessions.pop(req.assessment_id, None)
    # Generate AI-powered personalized report (if API key available)
    personalized_report = generate_personalized_report(display_scores, percentiles, lang)

    # Save profile for personality coach chat
    _user_profiles[session["user_id"]] = {
        "scores": display_scores,
        "report": personalized_report.dict() if personalized_report else None,
        "saved_at": datetime.utcnow().isoformat()
    }

    # Clean session
    _sessions.pop(req.assessment_id, None)

    return AssessmentResultOut(
        assessment_id=req.assessment_id,
        user_id=session["user_id"],
        completed_at=datetime.utcnow(),
        headline=headline,
        scores=dim_scores_out,
        strengths=strengths,
        personalized_report=personalized_report,  # AI-generated insights
        gdpr_notice=(
            "Dina uppgifter lagras säkert. Begär radering via /api/v1/gdpr/delete."
            if lang == "sv"
            else "Your data is stored securely. Request deletion via /api/v1/gdpr/delete."
        ),
    )


@app.get("/api/v1/assessment/questions")
async def get_questions_preview():
    """Preview the IPIP-50 question bank without starting a session."""
    return {
        "instrument": "IPIP-50",
        "total": len(IPIP_QUESTIONS),
        "dimensions": [
            {"code": d, "name": DIMENSION_META[d]["name_sv"], "count": sum(1 for q in IPIP_QUESTIONS if q["dim"] == d)}
            for d in ["E", "A", "C", "N", "O"]
        ],
        "questions": [{"id": q["id"], "text": q["text"], "dimension": q["dim"]} for q in IPIP_QUESTIONS],
    }


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════════════════════
# PERSONALITY COACH CHAT
# ══════════════════════════════════════════════════════════════════════════════

from personality_coach import chat_with_personality_coach

# Store user profiles in memory (replace with DB in production)
_user_profiles: Dict[str, Dict] = {}


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    user_id: str
    message: str
    profile_scores: Optional[Dict[str, float]] = Field(default=None, description="User's Big Five scores")
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    include_profile: bool = Field(default=True, description="Use user's assessment profile if available")


class ChatResponse(BaseModel):
    response: str
    conversation_history: List[ChatMessage]


@app.post("/api/v1/chat", response_model=ChatResponse)
async def personality_coach_chat(req: ChatRequest):
    """
    Chat with AI personality coach. If user has completed assessment,
    coach will provide personalized advice based on their Big Five profile.
    """

    if not anthropic_client:
        raise HTTPException(
            status_code=503,
            detail="Chat feature unavailable - no API key configured"
        )

    # Get user's profile from request (Vercel serverless compatible)
    profile_scores = req.profile_scores
    personalized_report = None

    # Fallback to in-memory storage if profile not provided (for local dev)
    if not profile_scores and req.include_profile and req.user_id in _user_profiles:
        user_data = _user_profiles[req.user_id]
        profile_scores = user_data.get("scores")
        personalized_report = user_data.get("report")

    # Convert ChatMessage objects to dicts
    history = [{"role": msg.role, "content": msg.content} for msg in req.conversation_history]

    # Get response from personality coach
    response_text = chat_with_personality_coach(
        message=req.message,
        conversation_history=history,
        profile_scores=profile_scores,
        personalized_report=personalized_report,
        anthropic_client=anthropic_client
    )

    # Build updated conversation history
    updated_history = history + [
        {"role": "user", "content": req.message},
        {"role": "assistant", "content": response_text}
    ]

    return ChatResponse(
        response=response_text,
        conversation_history=[ChatMessage(**msg) for msg in updated_history]
    )


@app.post("/api/v1/chat/save-profile")
async def save_user_profile(
    user_id: str,
    scores: Dict[str, float],
    report: Optional[Dict[str, Any]] = None
):
    """
    Save user's assessment profile for use in chat.
    Called automatically after completing assessment.
    """
    _user_profiles[user_id] = {
        "scores": scores,
        "report": report,
        "saved_at": datetime.utcnow().isoformat()
    }
    return {"status": "saved", "user_id": user_id}


@app.get("/api/v1/chat/profile/{user_id}")
async def get_user_chat_profile(user_id: str):
    """Check if user has a saved profile for chat context."""
    if user_id in _user_profiles:
        return {
            "has_profile": True,
            "saved_at": _user_profiles[user_id].get("saved_at")
        }
    return {"has_profile": False}
