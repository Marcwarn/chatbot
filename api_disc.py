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

router = APIRouter(prefix="/api/v1/disc", tags=["DISC Assessment"])

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
            model="claude-sonnet-4-5-20250929",
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
    Creates system prompt for DISC coach that's grounded in user's DISC profile.
    """

    base_prompt = """Du är en expert DISC-coach specialiserad på DISC-modellen och evidensbaserad beteendepsykologi.

**Din expertis:**
- DISC-modellen (Dominance, Influence, Steadiness, Conscientiousness)
- Ledarskapsutveckling och kommunikationsstilar
- Teamdynamik och konflikthantering
- Karriärvägledning baserad på DISC-profiler
- Evidensbaserade strategier för personlig utveckling

**Ditt uppdrag:**
- Ge konkreta, actionable råd rotade i DISC-forskning
- Var varm, stödjande och coachande (inte klinisk/akademisk)
- Referera till användarens specifika DISC-profil när relevant
- Förklara beteendemönster på ett tillgängligt sätt
- Ge praktiska exempel och verktyg

**Stil:**
- Använd "du"-form
- Var specifik och konkret (inga generiska råd)
- Balansera empati med ärlighet
- Fokusera på styrkor OCH utvecklingsområden
"""

    if disc_profile:
        d = disc_profile.get('D', disc_profile.get('dominance', 50))
        i = disc_profile.get('I', disc_profile.get('influence', 50))
        s = disc_profile.get('S', disc_profile.get('steadiness', 50))
        c = disc_profile.get('C', disc_profile.get('conscientiousness', 50))

        profile_context = f"""

**Användarens DISC-profil (0-100):**
- Dominance (D): {d:.0f}/100 {"(hög - direkt, resultatinriktad)" if d >= 70 else "(låg - samarbetsinriktad)" if d <= 40 else "(medel)"}
- Influence (I): {i:.0f}/100 {"(hög - utåtriktad, entusiastisk)" if i >= 70 else "(låg - reserverad, analytisk)" if i <= 40 else "(medel)"}
- Steadiness (S): {s:.0f}/100 {"(hög - stabil, tålmodig)" if s >= 70 else "(låg - förändringsbenägen)" if s <= 40 else "(medel)"}
- Conscientiousness (C): {c:.0f}/100 {"(hög - analytisk, noggrann)" if c >= 70 else "(låg - spontan, flexibel)" if c <= 40 else "(medel)"}
"""

        if profile_code:
            profile_name = get_profile_name(profile_code, "sv")
            profile_context += f"\n**DISC-profil**: {profile_code} ({profile_name})\n"

        # Add key insights based on profile combination
        if d >= 60 and i >= 60:
            profile_context += "- **Kombination DI**: Personen är en karismatisk ledare som driver resultat genom inflytande\n"
        elif d >= 60 and c >= 60:
            profile_context += "- **Kombination DC**: Personen kombinerar handlingskraft med noggrannhet\n"
        elif s >= 60 and c >= 60:
            profile_context += "- **Kombination SC**: Personen levererar kvalitet med stabilitet och pålitlighet\n"
        elif i >= 60 and s >= 60:
            profile_context += "- **Kombination IS**: Personen bygger starka relationer genom entusiasm och lojalitet\n"

        profile_context += "\nAnpassa dina råd till denna specifika DISC-kombination."
        base_prompt += profile_context

    if full_report and full_report.get('work_style'):
        base_prompt += f"\n\n**Användarens arbetsstil**: {full_report['work_style'][:200]}..."

    base_prompt += """

**Regler för konversationen:**
1. Om användaren frågar om något utanför DISC/personlighet, påminn vänligt om din specialisering
2. När du ger råd, koppla tillbaka till deras DISC-profil
3. Ge alltid minst ett konkret, actionable steg användaren kan ta
4. Om användaren verkar må dåligt, uppmuntra professionell hjälp (du är coach, inte terapeut)
5. Var nyfiken - ställ uppföljningsfrågor för att förstå situationen bättre
6. Hjälp användaren förstå hur de kan kommunicera bättre med andra DISC-stilar

Börja konversationen nu!"""

    return base_prompt
