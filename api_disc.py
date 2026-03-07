"""
DISC Assessment API - GDPR-Compliant DISC Personality Assessment
Parallel system to Big Five assessment with complete security integration
"""

from fastapi import APIRouter, HTTPException, Request
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
    AuditLog, AssessmentType
)
from validators import (
    validate_user_id,
    validate_assessment_id,
    validate_language,
    validate_message_length
)
from disc_analysis import (
    analyze_disc_assessment,
    DISCProfile,
    DISCScores,
    get_dimension_interpretation,
    get_strengths_from_profile,
    get_development_areas
)
from disc_report_generator import generate_disc_report
from disc_prompts import get_profile_name, get_profile_traits
from api_admin import track_assessment, track_chat_message, update_user_consents

# ── Router Setup ─────────────────────────────────────────────────────────────

router = APIRouter(prefix="/disc", tags=["DISC Assessment"])

# ── Anthropic AI Client ──────────────────────────────────────────────────────

anthropic_client = None
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        anthropic_client = Anthropic(api_key=api_key)
except Exception:
    pass  # AI reports optional if no API key

# ── DISC Question Bank (Swedish, professional) ───────────────────────────────

DISC_QUESTIONS = [
    # DOMINANCE (D) - 6 questions
    {"id": 1,  "text": "Jag tar snabbt beslut även när informationen är begränsad",              "dim": "D", "keyed": "+"},
    {"id": 2,  "text": "Jag undviker helst att ta kommandot i en grupp",                           "dim": "D", "keyed": "-"},
    {"id": 3,  "text": "Jag trivs med utmaningar och konkurrens",                                  "dim": "D", "keyed": "+"},
    {"id": 4,  "text": "Jag föredrar att låta andra ta ledningen",                                 "dim": "D", "keyed": "-"},
    {"id": 5,  "text": "Jag driver igenom mina idéer även när andra är tveksamma",                 "dim": "D", "keyed": "+"},
    {"id": 6,  "text": "Jag tar sällan initiativ till förändring",                                 "dim": "D", "keyed": "-"},

    # INFLUENCE (I) - 6 questions
    {"id": 7,  "text": "Jag bygger relationer lätt med nya människor",                             "dim": "I", "keyed": "+"},
    {"id": 8,  "text": "Jag är ganska reserverad i sociala sammanhang",                            "dim": "I", "keyed": "-"},
    {"id": 9,  "text": "Jag inspirerar och motiverar andra med min entusiasm",                     "dim": "I", "keyed": "+"},
    {"id": 10, "text": "Jag föredrar att jobba själv framför att arbeta i team",                   "dim": "I", "keyed": "-"},
    {"id": 11, "text": "Jag är ofta den som får andra på gott humör",                              "dim": "I", "keyed": "+"},
    {"id": 12, "text": "Jag håller mina känslor för mig själv",                                    "dim": "I", "keyed": "-"},

    # STEADINESS (S) - 6 questions
    {"id": 13, "text": "Jag är tålmodig även i stressiga situationer",                             "dim": "S", "keyed": "+"},
    {"id": 14, "text": "Jag blir lätt otålig när saker går långsamt",                              "dim": "S", "keyed": "-"},
    {"id": 15, "text": "Jag söker harmoni och undviker konflikter",                                "dim": "S", "keyed": "+"},
    {"id": 16, "text": "Jag tycker om snabba förändringar och variation",                          "dim": "S", "keyed": "-"},
    {"id": 17, "text": "Jag är en pålitlig och lojal teammedlem",                                  "dim": "S", "keyed": "+"},
    {"id": 18, "text": "Jag känner mig rastlös i stabila rutiner",                                  "dim": "S", "keyed": "-"},

    # CONSCIENTIOUSNESS (C) - 6 questions
    {"id": 19, "text": "Jag analyserar noggrant innan jag fattar beslut",                          "dim": "C", "keyed": "+"},
    {"id": 20, "text": "Jag litar ofta på min magkänsla",                                          "dim": "C", "keyed": "-"},
    {"id": 21, "text": "Jag följer processer och regler systematiskt",                             "dim": "C", "keyed": "+"},
    {"id": 22, "text": "Jag tar genvägar om det sparar tid",                                       "dim": "C", "keyed": "-"},
    {"id": 23, "text": "Jag värdesätter kvalitet framför hastighet",                               "dim": "C", "keyed": "+"},
    {"id": 24, "text": "Jag är mer spontan än planerande",                                         "dim": "C", "keyed": "-"},
]

DIMENSION_META = {
    "D": {"name": "Dominance",           "name_sv": "Dominans"},
    "I": {"name": "Influence",           "name_sv": "Inflytande"},
    "S": {"name": "Steadiness",          "name_sv": "Stabilitet"},
    "C": {"name": "Conscientiousness",   "name_sv": "Samvetsgrannhet"},
}

LIKERT_OPTIONS = [
    "1 - Stämmer inte alls",
    "2 - Stämmer dåligt",
    "3 - Neutral",
    "4 - Stämmer ganska bra",
    "5 - Stämmer helt",
]

# ── Pydantic Models ──────────────────────────────────────────────────────────

class StartDISCAssessmentRequest(BaseModel):
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
    assessment_type: str = "disc"
    questions: List[QuestionOut]
    total_questions: int
    gdpr_notice: str


class AnswerIn(BaseModel):
    question_id: int
    value: int = Field(..., ge=1, le=5)


class SubmitDISCAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[AnswerIn]


class DimensionScore(BaseModel):
    dimension: str
    dimension_name: str
    score: float  # 0-100
    level: str  # "high", "medium", "low"
    label: str
    description: str


class DISCAssessmentResultOut(BaseModel):
    assessment_id: str
    user_id: str
    assessment_type: str = "disc"
    completed_at: datetime
    profile_code: str
    profile_name: str
    profile_traits: str
    primary_style: str
    secondary_style: Optional[str]
    scores: List[DimensionScore]
    summary: str
    strengths: List[str]
    development_areas: List[str]
    work_style: str
    communication_style: str
    career_recommendations: List[str]
    team_dynamics: str
    personalized_insights: Optional[Dict] = None
    gdpr_notice: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class DISCChatRequest(BaseModel):
    user_id: str
    message: str
    disc_profile: Optional[Dict[str, float]] = Field(default=None, description="User's DISC scores")
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    include_profile: bool = Field(default=True, description="Use user's DISC profile if available")


class DISCChatResponse(BaseModel):
    response: str
    conversation_history: List[ChatMessage]


# ── In-memory session store (Vercel serverless compatible) ──────────────────

_sessions: Dict[str, dict] = {}
_user_profiles: Dict[str, Dict] = {}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/start", response_model=AssessmentStartResponse)
async def start_disc_assessment(req: StartDISCAssessmentRequest, request: Request):
    """
    Begin a new DISC personality assessment. GDPR consent required.

    DISC measures 4 personality dimensions:
    - D (Dominance): Direct, results-oriented, decisive
    - I (Influence): Outgoing, enthusiastic, relationship-oriented
    - S (Steadiness): Patient, loyal, harmony-seeking
    - C (Conscientiousness): Analytical, precise, quality-conscious
    """

    # GDPR compliance check
    if not req.consent_data_processing or not req.consent_analysis:
        raise HTTPException(
            status_code=400,
            detail="GDPR: Consent for data processing and analysis is required."
        )

    # Validate inputs
    if req.language:
        req.language = validate_language(req.language)

    # Generate IDs
    user_id = req.user_id or str(uuid.uuid4())
    if req.user_id:
        user_id = validate_user_id(user_id)

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
        for q in DISC_QUESTIONS
    ]

    # Store session (in-memory for Vercel serverless compatibility)
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

    # Track user consents for admin
    update_user_consents(user_id, {
        "data_processing": req.consent_data_processing,
        "analysis": req.consent_analysis,
        "storage": req.consent_storage,
    })

    return AssessmentStartResponse(
        assessment_id=assessment_id,
        user_id=user_id,
        assessment_type="disc",
        questions=questions_out,
        total_questions=len(questions_out),
        gdpr_notice=(
            "Dina svar behandlas GDPR-säkert. Du kan begära export eller radering via /api/v1/gdpr/export och /api/v1/gdpr/delete."
            if req.language == "sv"
            else "Your responses are processed in accordance with GDPR. Export or delete via /api/v1/gdpr/export and /api/v1/gdpr/delete."
        ),
    )


@router.post("/submit", response_model=DISCAssessmentResultOut)
async def submit_disc_assessment(req: SubmitDISCAssessmentRequest, request: Request):
    """
    Submit DISC assessment answers and receive comprehensive profile analysis.

    Returns:
    - DISC scores (D, I, S, C)
    - Profile code (e.g., "DI", "SC")
    - Strengths and development areas
    - Work style and communication preferences
    - Career recommendations
    - Team dynamics insights
    """

    # Validate assessment ID
    req.assessment_id = validate_assessment_id(req.assessment_id)

    # Get session
    session = _sessions.get(req.assessment_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found.")

    lang = session.get("language", "sv")

    # Convert answers to dict
    answers_map: Dict[int, int] = {a.question_id: a.value for a in req.answers}

    # Validate all questions answered
    if len(answers_map) != len(DISC_QUESTIONS):
        raise HTTPException(
            status_code=400,
            detail=f"All {len(DISC_QUESTIONS)} questions must be answered. Received {len(answers_map)}."
        )

    # Analyze DISC profile
    profile = analyze_disc_assessment(DISC_QUESTIONS, answers_map)

    # Generate comprehensive report
    report = generate_disc_report(
        profile=profile,
        language=lang,
        anthropic_client=anthropic_client,
        include_ai_insights=True
    )

    # Build dimension scores for response
    dim_scores_out: List[DimensionScore] = []
    for dim_interp in report["dimension_interpretations"]:
        dim_scores_out.append(DimensionScore(
            dimension=dim_interp["dimension"],
            dimension_name=DIMENSION_META[dim_interp["dimension"]]["name_sv"],
            score=dim_interp["score"],
            level=dim_interp["level"],
            label=dim_interp["label"],
            description=dim_interp["description"]
        ))

    # Save profile for chat
    _user_profiles[session["user_id"]] = {
        "disc_scores": profile.scores.to_dict(),
        "profile_code": profile.profile_code,
        "report": report,
        "saved_at": datetime.utcnow().isoformat()
    }

    # Clean session
    _sessions.pop(req.assessment_id, None)

    # Track assessment for admin analytics
    track_assessment(
        assessment_id=req.assessment_id,
        user_id=session["user_id"],
        scores={
            "D": profile.scores.dominance,
            "I": profile.scores.influence,
            "S": profile.scores.steadiness,
            "C": profile.scores.conscientiousness
        },
        language=lang,
        assessment_type="disc"
    )

    return DISCAssessmentResultOut(
        assessment_id=req.assessment_id,
        user_id=session["user_id"],
        assessment_type="disc",
        completed_at=datetime.utcnow(),
        profile_code=report["profile_code"],
        profile_name=report["profile_name"],
        profile_traits=report["profile_traits"],
        primary_style=profile.primary_style,
        secondary_style=profile.secondary_style,
        scores=dim_scores_out,
        summary=report["summary"],
        strengths=report["strengths"],
        development_areas=report["development_areas"],
        work_style=report["work_style"],
        communication_style=report["communication_style"],
        career_recommendations=report["career_recommendations"],
        team_dynamics=report["team_dynamics"],
        personalized_insights=report["personalized_insights"],
        gdpr_notice=(
            "Dina uppgifter lagras säkert. Begär radering via /api/v1/gdpr/delete."
            if lang == "sv"
            else "Your data is stored securely. Request deletion via /api/v1/gdpr/delete."
        ),
    )


@router.get("/questions")
async def get_disc_questions_preview():
    """
    Preview the DISC question bank without starting a session.

    Returns all 24 DISC questions organized by dimension:
    - 6 Dominance (D) questions
    - 6 Influence (I) questions
    - 6 Steadiness (S) questions
    - 6 Conscientiousness (C) questions
    """
    return {
        "assessment_type": "DISC",
        "total": len(DISC_QUESTIONS),
        "dimensions": [
            {"code": d, "name": DIMENSION_META[d]["name_sv"], "count": sum(1 for q in DISC_QUESTIONS if q["dim"] == d)}
            for d in ["D", "I", "S", "C"]
        ],
        "questions": [{"id": q["id"], "text": q["text"], "dimension": q["dim"]} for q in DISC_QUESTIONS],
    }


@router.post("/chat", response_model=DISCChatResponse)
async def disc_coach_chat(req: DISCChatRequest, request: Request):
    """
    Chat with AI DISC coach. If user has completed DISC assessment,
    coach will provide personalized advice based on their DISC profile.

    The coach specializes in:
    - Leadership development based on DISC
    - Communication strategies for different DISC types
    - Team dynamics and collaboration
    - Career guidance aligned with DISC strengths
    """

    if not anthropic_client:
        raise HTTPException(
            status_code=503,
            detail="Chat feature unavailable - no API key configured"
        )

    # Validate message
    req.message = validate_message_length(req.message, max_length=5000)

    # Get user's DISC profile
    disc_profile = req.disc_profile
    profile_code = None
    full_report = None

    # Fallback to in-memory storage if profile not provided
    if not disc_profile and req.include_profile and req.user_id in _user_profiles:
        user_data = _user_profiles[req.user_id]
        disc_profile = user_data.get("disc_scores")
        profile_code = user_data.get("profile_code")
        full_report = user_data.get("report")

    # Build system prompt
    system_prompt = create_disc_coach_prompt(disc_profile, profile_code, full_report)

    # Convert ChatMessage objects to dicts
    history = [{"role": msg.role, "content": msg.content} for msg in req.conversation_history]

    # Add current message
    messages = history + [{"role": "user", "content": req.message}]

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )

        response_text = response.content[0].text

        # Build updated conversation history
        updated_history = history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": response_text}
        ]

        # Track chat message for admin analytics
        track_chat_message()

        return DISCChatResponse(
            response=response_text,
            conversation_history=[ChatMessage(**msg) for msg in updated_history]
        )

    except Exception as e:
        print(f"DISC chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Chat service temporarily unavailable. Please try again."
        )


@router.post("/chat/save-profile")
async def save_disc_profile(
    user_id: str,
    disc_scores: Dict[str, float],
    profile_code: str,
    report: Optional[Dict[str, Any]] = None
):
    """
    Save user's DISC profile for use in chat.
    Called automatically after completing assessment.
    """
    user_id = validate_user_id(user_id)

    _user_profiles[user_id] = {
        "disc_scores": disc_scores,
        "profile_code": profile_code,
        "report": report,
        "saved_at": datetime.utcnow().isoformat()
    }
    return {"status": "saved", "user_id": user_id}


@router.get("/chat/profile/{user_id}")
async def get_disc_chat_profile(user_id: str):
    """Check if user has a saved DISC profile for chat context."""
    user_id = validate_user_id(user_id)

    if user_id in _user_profiles:
        return {
            "has_profile": True,
            "profile_code": _user_profiles[user_id].get("profile_code"),
            "saved_at": _user_profiles[user_id].get("saved_at")
        }
    return {"has_profile": False}


# ── Helper Functions ─────────────────────────────────────────────────────────

def create_disc_coach_prompt(
    disc_profile: Optional[Dict[str, float]] = None,
    profile_code: Optional[str] = None,
    full_report: Optional[Dict] = None
) -> str:
    """
    Creates a deep, expert system prompt for the DISC coach grounded in the user's profile.
    """

    def level_sv(score):
        if score >= 70: return "hög"
        elif score >= 40: return "medel"
        return "låg"

    base_prompt = """Du är en djupt erfaren DISC-coach och beteendeanalytiker med 25+ års erfarenhet.
Du har ingående kunskap om DISC-modellen baserad på William Moulton Marstons forskning.

**DISC-RAMVERK (din expertkunskap):**
DISC mäter fyra beteendedimensioner:
- **D (Dominans/Röd)**: Hur personen hanterar utmaningar och problem
  - Hög D: resultatdriven, direkt, tävlingsinriktad, riskbenägen, kan upplevas dominant
  - Låg D: samarbetsorienterad, söker konsensus, avvaktande, föredrar att andra tar beslut
- **I (Inflytande/Gul)**: Hur personen kommunicerar och påverkar sin omgivning
  - Hög I: social, entusiastisk, övertygande, behöver uppskattning, kan tala före de tänker
  - Låg I: analytisk, kritisk, misstänksam, föredrar fakta, arbetar hellre ensam
- **S (Stabilitet/Grön)**: Hur personen svarar på omgivningens tempo och förändringar
  - Hög S: tålmodig, lojal, harmonisökande, slutför uppgifter, motståndsam mot plötslig förändring
  - Låg S: snabb, aktiv, trivs med variation, otålig, kan ha svårt att slutföra
- **C (Följsamhet/Blå)**: Hur personen förhåller sig till regler och kvalitetskrav
  - Hög C: noggrann, analytisk, regelföljande, kräver fakta och precision, svårt med deadlines
  - Låg C: okonventionell, tar risker, ser regler som riktlinjer, kan upplevas taktlös

**Vad som skapar engagemang vs stress per DISC-stil:**
- Hög D: Engageras av autonomi, utmaningar, snabba resultat, kontroll. Stressas av mikromanagement, långsamma processer.
- Hög I: Engageras av socialt samspel, uppskattning, nya idéer, kreativitet. Stressas av isolering, kritik, rigid struktur.
- Hög S: Engageras av stabilitet, teamharmoni, långsiktiga relationer. Stressas av plötsliga förändringar, konflikter.
- Hög C: Engageras av kvalitet, analys, tydliga processer. Stressas av brådska, otydlighet, kompromisser med kvalitet.

**Beteendetendenser:**
Prestationsinriktad (hög D) | Påverkande (hög I) | Principfast (hög C) | Uppmärksam (hög C)
Självmotiverande (hög D) | Uthållig (hög S) | Självsäker (låg C+hög DI) | Försiktig (hög C)
Entusiastisk (hög I) | Eftertänksam (hög SC) | Oberoende (hög D+låg C) | Samverkande (låg D+hög SC)

**Grundbeteende vs anpassat beteende:**
Grundbeteende = hur personen naturligt agerar i trygg miljö (kräver ingen energi)
Anpassat beteende = hur de anpassar sig till omgivningens krav (kräver psykisk energi och är svårt att hålla långsiktigt)
"""

    if disc_profile:
        d = disc_profile.get('D', disc_profile.get('dominance', 50))
        i_val = disc_profile.get('I', disc_profile.get('influence', 50))
        s = disc_profile.get('S', disc_profile.get('steadiness', 50))
        c = disc_profile.get('C', disc_profile.get('conscientiousness', 50))

        # Build combination insights
        combo_insights = []
        if d >= 60 and i_val >= 60:
            combo_insights.append("DI-kombinationen = karismatisk ledare som driver resultat genom inflytande och energi")
        if d >= 60 and c >= 60:
            combo_insights.append("DC-kombinationen = analytisk drivkraft som kräver både kvalitet och snabba resultat - kan skapa inre spänning")
        if d >= 60 and s >= 60:
            combo_insights.append("DS-kombinationen = stabil ledare som balanserar resultatfokus med omtanke om teamet")
        if i_val >= 60 and s >= 60:
            combo_insights.append("IS-kombinationen = varm relationsskapare som kombinerar entusiasm med lojalitet")
        if i_val >= 60 and c >= 60:
            combo_insights.append("IC-kombinationen = kreativ analytiker som balanserar innovation med precision")
        if s >= 60 and c >= 60:
            combo_insights.append("SC-kombinationen = metodisk specialist som levererar pålitlig hög kvalitet")

        profile_name = get_profile_name(profile_code, "sv") if profile_code else "Okänd profil"

        base_prompt += f"""
**DENNA ANVÄNDARES DISC-PROFIL:**
- D (Dominans/Röd): {d:.0f}/100 [{level_sv(d)} laddning - {'resultatdriven, direkt, riskbenägen' if d >= 70 else 'samarbetsorienterad, konsensussökande' if d <= 40 else 'balanserad mellan drivkraft och samarbete'}]
- I (Inflytande/Gul): {i_val:.0f}/100 [{level_sv(i_val)} laddning - {'social, entusiastisk, behöver uppskattning' if i_val >= 70 else 'analytisk, kritisk, föredrar fakta' if i_val <= 40 else 'balanserad mellan socialt och analytiskt'}]
- S (Stabilitet/Grön): {s:.0f}/100 [{level_sv(s)} laddning - {'tålmodig, lojal, harmonisökande' if s >= 70 else 'snabb, förändringsbenägen, otålig' if s <= 40 else 'balanserad mellan stabilitet och rörlighet'}]
- C (Följsamhet/Blå): {c:.0f}/100 [{level_sv(c)} laddning - {'noggrann, analytisk, kräver precision' if c >= 70 else 'okonventionell, spontan, regelflexibel' if c <= 40 else 'balanserad mellan struktur och flexibilitet'}]
- Profilkod: {profile_code or 'ej beräknad'} ({profile_name})
"""
        if combo_insights:
            base_prompt += "
**Kombinationsinsikter:**
" + "
".join(f"- {ci}" for ci in combo_insights) + "
"

        if full_report:
            if full_report.get('work_style'):
                base_prompt += f"
**Arbetsstil**: {full_report['work_style'][:300]}
"
            if full_report.get('personalized_insights'):
                pi = full_report['personalized_insights']
                if pi.get('unique_combination'):
                    base_prompt += f"
**Unik kombination**: {pi['unique_combination'][:400]}
"

    base_prompt += """
**DITT UPPDRAG:**
- Ge konkreta, actionable råd baserade på DISC-teorin
- Var varm, stödjande och coachande - inte akademisk eller distanserad
- Referera alltid till användarens specifika DISC-profil och poäng
- Förklara VARFÖR beteendemönstren uppstår baserat på DISC-dimensionerna
- Ge praktiska examples från verkliga situationer
- Hjälp personen se sin profil som en styrka

**OBLIGATORISKA REGLER:**
1. Koppla alltid svaret till deras specifika DISC-profil
2. Ge minst ett konkret, omedelbart steg användaren kan ta
3. Ställ en nyfiken uppföljningsfråga i slutet av varje svar
4. Hjälp dem förstå hur de kommunicerar bättre med andra DISC-stilar (Röd/Gul/Grön/Blå)
5. Nämn ALDRIG externa företag, varumärken eller system
6. Använd "du"-form och tilltala personen direkt och personligt
7. Om personen mår dåligt - visa empati och hänvisa till professionell hjälp (du är coach, inte terapeut)"""

    return base_prompt
