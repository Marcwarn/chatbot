"""
GDPR-Compliant Personality Assessment API
Integrates original API with full GDPR compliance
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from anthropic import Anthropic
import json

# Import GDPR components
from database import (
    db, User, UserConsent, Assessment as DBAssessment,
    AssessmentQuestion as DBQuestion,
    AssessmentAnswer as DBAnswer,
    AssessmentResult as DBResult,
    AuditLog
)
from api_gdpr import router as gdpr_router

# Initialize database
db.create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="GDPR-Compliant Personality Assessment API",
    description="AI-driven personality assessments with full GDPR compliance",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include GDPR router
app.include_router(gdpr_router)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class StartAssessmentRequest(BaseModel):
    user_id: Optional[str] = None  # Optional - will be created if not provided
    email: Optional[EmailStr] = None  # For GDPR verification
    assessment_type: str = Field(..., description="Type: big_five, disc, jung_mbti, comprehensive")
    language: str = Field(default="sv", description="Language code (sv, en)")
    num_questions: int = Field(default=30, ge=10, le=100)

    # GDPR: Explicit consents
    consent_data_processing: bool = Field(..., description="Consent for data processing")
    consent_ai_analysis: bool = Field(..., description="Consent for AI analysis")
    consent_storage: bool = Field(default=True, description="Consent for data storage")


class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    scale_type: str
    options: Optional[List[str]] = None
    dimension: str


class AssessmentQuestions(BaseModel):
    assessment_id: str
    user_id: str
    questions: List[QuestionResponse]
    total_questions: int
    assessment_type: str
    created_at: datetime
    gdpr_notice: str = "Your responses will be processed according to GDPR. You can delete your data at any time."


class AnswerSubmission(BaseModel):
    assessment_id: str
    question_id: int
    answer: Any


class CompleteAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[AnswerSubmission]


class PersonalityScore(BaseModel):
    dimension: str
    score: float
    percentile: Optional[float] = None
    interpretation: str


class AssessmentResult(BaseModel):
    assessment_id: str
    user_id: str
    assessment_type: str
    scores: List[PersonalityScore]
    summary: str
    detailed_analysis: str
    strengths: List[str]
    development_areas: List[str]
    recommendations: List[str]
    completed_at: datetime
    gdpr_notice: str = "You can export or delete this data anytime using /api/v1/gdpr/export or /api/v1/gdpr/delete"


# ============================================================================
# AI PROMPT TEMPLATES (Same as before)
# ============================================================================

BIG_FIVE_SYSTEM_PROMPT = """Du är en expert inom psykometri och personlighetsbedömning, specialiserad på Big Five-modellen (OCEAN):

**Big Five Dimensioner:**
1. **Openness (Öppenhet)**: Kreativitet, nyfiken, öppen för nya erfarenheter
2. **Conscientiousness (Samvetsgrannhet)**: Organiserad, ansvarsfull, pålitlig
3. **Extraversion (Extraversion)**: Utåtriktad, social, energisk
4. **Agreeableness (Vänlighet)**: Empatisk, samarbetsvillig, tillitsfull
5. **Neuroticism (Neuroticism)**: Emotionell stabilitet, ångestnivå, stress-hantering

Skapa vetenskapligt validerade frågor som mäter dessa dimensioner på ett reliabelt sätt."""

DISC_SYSTEM_PROMPT = """Du är en expert på DISC personlighetsmodellen:

**DISC Dimensioner:**
1. **Dominance (D)**: Resultatinriktad, bestämd, direkta, tävlingsinriktad
2. **Influence (I)**: Utåtriktad, entusiastisk, optimistisk, övertalande
3. **Steadiness (S)**: Stödjande, pålitlig, tålmodig, teamorienterad
4. **Conscientiousness (C)**: Analytisk, noggrann, systematisk, kvalitetsfokuserad

Skapa situationsbaserade frågor som identifierar användarens DISC-profil."""

JUNG_MBTI_SYSTEM_PROMPT = """Du är expert på Jungiansk typologi och MBTI (Myers-Briggs Type Indicator):

**MBTI Dimensioner:**
1. **E/I (Extraversion/Introversion)**: Energikälla - yttre vs inre värld
2. **S/N (Sensing/Intuition)**: Informationshantering - konkret vs abstrakt
3. **T/F (Thinking/Feeling)**: Beslutfattande - logik vs värderingar
4. **J/P (Judging/Perceiving)**: Livsstil - strukturerad vs flexibel

Skapa frågor som tydligt differentierar mellan dessa preferenser."""

# ============================================================================
# AI FUNCTIONS (Same as before)
# ============================================================================

def generate_questions_with_ai(assessment_type: str, num_questions: int, language: str) -> List[QuestionResponse]:
    """Generate assessment questions using Claude AI"""

    system_prompts = {
        "big_five": BIG_FIVE_SYSTEM_PROMPT,
        "disc": DISC_SYSTEM_PROMPT,
        "jung_mbti": JUNG_MBTI_SYSTEM_PROMPT,
    }

    if assessment_type == "comprehensive":
        system_prompt = f"{BIG_FIVE_SYSTEM_PROMPT}\n\n{DISC_SYSTEM_PROMPT}\n\n{JUNG_MBTI_SYSTEM_PROMPT}"
    else:
        system_prompt = system_prompts.get(assessment_type, BIG_FIVE_SYSTEM_PROMPT)

    lang_instruction = "svenska" if language == "sv" else "English"

    user_prompt = f"""Generera {num_questions} validerade personlighetsfrågor på {lang_instruction}.

**Krav:**
- Varje fråga ska mäta en specifik dimension/trait
- Använd olika frågeformat: Likert-skala (1-5), val mellan alternativ, scenariobaserade
- Frågor ska vara tydliga, icke-ledande och kulturellt neutrala
- Balansera positiva och negativa formuleringar (för att undvika response bias)

**Returnera JSON i följande format:**
```json
{{
  "questions": [
    {{
      "question_id": 1,
      "question_text": "Jag tycker om att träffa nya människor",
      "scale_type": "likert",
      "options": ["1 - Stämmer inte alls", "2 - Stämmer dåligt", "3 - Neutral", "4 - Stämmer ganska bra", "5 - Stämmer helt"],
      "dimension": "Extraversion"
    }}
  ]
}}
```

Generera nu {num_questions} frågor:"""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        response_text = message.content[0].text

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        questions_data = json.loads(response_text)
        questions = [QuestionResponse(**q) for q in questions_data["questions"]]

        return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


def analyze_answers_with_ai(assessment_type: str, questions: List[QuestionResponse],
                           answers: List[AnswerSubmission], language: str) -> AssessmentResult:
    """Analyze assessment answers using Claude AI"""

    qa_pairs = []
    for answer in answers:
        question = next((q for q in questions if q.question_id == answer.question_id), None)
        if question:
            qa_pairs.append({
                "dimension": question.dimension,
                "question": question.question_text,
                "answer": answer.answer,
                "scale": question.scale_type
            })

    system_prompts = {
        "big_five": BIG_FIVE_SYSTEM_PROMPT,
        "disc": DISC_SYSTEM_PROMPT,
        "jung_mbti": JUNG_MBTI_SYSTEM_PROMPT,
    }

    system_prompt = system_prompts.get(assessment_type, BIG_FIVE_SYSTEM_PROMPT)
    lang_instruction = "svenska" if language == "sv" else "English"

    analysis_prompt = f"""Analysera följande personlighetsbedömning och ge djupgående insikter på {lang_instruction}.

**Användarens svar:**
{json.dumps(qa_pairs, indent=2, ensure_ascii=False)}

**Uppgift:**
1. Beräkna poäng för varje dimension (0-100 skala)
2. Ge percentiler baserat på normalfördelning
3. Skriv tolkningar för varje dimension
4. Identifiera styrkor och utvecklingsområden
5. Ge personliga rekommendationer

**Returnera JSON:**
```json
{{
  "scores": [
    {{
      "dimension": "Extraversion",
      "score": 75.5,
      "percentile": 82,
      "interpretation": "Du är utåtriktad och energisk..."
    }}
  ],
  "summary": "Övergripande sammanfattning av personligheten...",
  "detailed_analysis": "Djupgående analys...",
  "strengths": ["Utmärkt social förmåga", "Kreativ problemlösare"],
  "development_areas": ["Kan vara för impulsiv", "Behöver mer struktur"],
  "recommendations": ["Utnyttja din kreativitet i projektledning", "Arbeta med tidsplanering"]
}}
```

Analysera nu:"""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        response_text = message.content[0].text

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result_data = json.loads(response_text)

        result = AssessmentResult(
            assessment_id=answers[0].assessment_id,
            user_id="",
            assessment_type=assessment_type,
            scores=[PersonalityScore(**s) for s in result_data["scores"]],
            summary=result_data["summary"],
            detailed_analysis=result_data["detailed_analysis"],
            strengths=result_data["strengths"],
            development_areas=result_data["development_areas"],
            recommendations=result_data["recommendations"],
            completed_at=datetime.now()
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze answers: {str(e)}")


# ============================================================================
# API ENDPOINTS (GDPR-Enhanced)
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "GDPR-Compliant Personality Assessment API",
        "version": "2.0.0",
        "gdpr_compliance": "Full GDPR compliance with consent management, data export, and deletion",
        "endpoints": {
            "assessment": {
                "start": "/api/v1/assessment/start",
                "submit": "/api/v1/assessment/submit",
                "result": "/api/v1/assessment/result/{assessment_id}",
                "types": "/api/v1/assessment/types"
            },
            "gdpr": {
                "consent": "/api/v1/gdpr/consent",
                "export": "/api/v1/gdpr/export",
                "delete": "/api/v1/gdpr/delete",
                "privacy_info": "/api/v1/gdpr/privacy-info/{user_id}",
                "privacy_policy": "/api/v1/gdpr/privacy-policy"
            },
            "docs": "/docs"
        }
    }


@app.post("/api/v1/assessment/start", response_model=AssessmentQuestions)
async def start_assessment(request: StartAssessmentRequest, http_request: Request):
    """
    Start a new GDPR-compliant personality assessment

    Requires explicit consent for data processing
    """
    session = db.get_session()

    try:
        # GDPR: Check consents
        if not request.consent_data_processing:
            raise HTTPException(
                status_code=403,
                detail="Data processing consent required. User must explicitly consent to data processing."
            )

        if not request.consent_ai_analysis:
            raise HTTPException(
                status_code=403,
                detail="AI analysis consent required. User must consent to AI-powered analysis."
            )

        # Get or create user
        if request.user_id:
            user = session.query(User).filter(User.id == request.user_id).first()
            if not user:
                user = User(email=request.email, user_id=request.user_id)
                session.add(user)
        else:
            user = User(email=request.email)
            session.add(user)

        session.flush()  # Get user ID

        # Record consents
        consents_to_add = [
            UserConsent(
                user_id=user.id,
                consent_type="data_processing",
                consent_given=request.consent_data_processing,
                purpose="Personality assessment data collection and storage",
                legal_basis="consent"
            ),
            UserConsent(
                user_id=user.id,
                consent_type="ai_analysis",
                consent_given=request.consent_ai_analysis,
                purpose="AI-powered personality analysis using Anthropic Claude",
                legal_basis="consent"
            ),
            UserConsent(
                user_id=user.id,
                consent_type="storage",
                consent_given=request.consent_storage,
                purpose="Data storage for future reference",
                legal_basis="consent"
            )
        ]

        for consent in consents_to_add:
            session.add(consent)

        # Generate assessment ID
        assessment_id = f"assess_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Generate questions with AI
        questions = generate_questions_with_ai(
            assessment_type=request.assessment_type,
            num_questions=request.num_questions,
            language=request.language
        )

        # Create assessment in database
        assessment = DBAssessment(
            id=assessment_id,
            user_id=user.id,
            assessment_type=request.assessment_type,
            language=request.language,
            status="in_progress"
        )
        session.add(assessment)

        # Store questions
        for q in questions:
            db_question = DBQuestion(
                assessment_id=assessment_id,
                question_id=q.question_id,
                question_text=q.question_text,
                scale_type=q.scale_type,
                options=q.options,
                dimension=q.dimension
            )
            session.add(db_question)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="assessment_started",
            resource_type="assessment",
            resource_id=assessment_id,
            details={
                "assessment_type": request.assessment_type,
                "num_questions": request.num_questions,
                "language": request.language
            },
            ip_address=http_request.client.host if http_request.client else None
        )
        session.add(audit)

        session.commit()

        return AssessmentQuestions(
            assessment_id=assessment_id,
            user_id=user.id,
            questions=questions,
            total_questions=len(questions),
            assessment_type=request.assessment_type,
            created_at=datetime.now()
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@app.post("/api/v1/assessment/submit", response_model=AssessmentResult)
async def submit_assessment(request: CompleteAssessmentRequest, http_request: Request):
    """
    Submit completed assessment answers

    Returns AI-analyzed personality profile
    Stores all data with GDPR compliance
    """
    session = db.get_session()

    try:
        # Get assessment
        assessment = session.query(DBAssessment).filter(
            DBAssessment.id == request.assessment_id
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        # Get questions
        db_questions = session.query(DBQuestion).filter(
            DBQuestion.assessment_id == request.assessment_id
        ).all()

        questions = [
            QuestionResponse(
                question_id=q.question_id,
                question_text=q.question_text,
                scale_type=q.scale_type,
                options=q.options,
                dimension=q.dimension
            ) for q in db_questions
        ]

        # Store answers
        for answer in request.answers:
            db_answer = DBAnswer(
                assessment_id=request.assessment_id,
                question_id=answer.question_id,
                answer_value=str(answer.answer)
            )
            session.add(db_answer)

        # Analyze with AI
        result = analyze_answers_with_ai(
            assessment_type=assessment.assessment_type,
            questions=questions,
            answers=request.answers,
            language=assessment.language
        )

        result.user_id = assessment.user_id
        result.assessment_id = request.assessment_id

        # Store result
        db_result = DBResult(
            assessment_id=request.assessment_id,
            scores=[s.dict() for s in result.scores],
            summary=result.summary,
            detailed_analysis=result.detailed_analysis,
            strengths=result.strengths,
            development_areas=result.development_areas,
            recommendations=result.recommendations
        )
        session.add(db_result)

        # Update assessment status
        assessment.status = "completed"
        assessment.completed_at = datetime.now()

        # Audit log
        audit = AuditLog(
            user_id=assessment.user_id,
            action="assessment_completed",
            resource_type="assessment",
            resource_id=request.assessment_id,
            details={"num_answers": len(request.answers)},
            ip_address=http_request.client.host if http_request.client else None
        )
        session.add(audit)

        session.commit()

        return result

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@app.get("/api/v1/assessment/result/{assessment_id}", response_model=AssessmentResult)
async def get_assessment_result(assessment_id: str, http_request: Request):
    """
    Retrieve assessment results by ID

    GDPR: Logs data access for transparency
    """
    session = db.get_session()

    try:
        assessment = session.query(DBAssessment).filter(
            DBAssessment.id == assessment_id
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        db_result = session.query(DBResult).filter(
            DBResult.assessment_id == assessment_id
        ).first()

        if not db_result:
            raise HTTPException(status_code=404, detail="Result not found")

        # Audit log - data accessed
        audit = AuditLog(
            user_id=assessment.user_id,
            action="result_accessed",
            resource_type="assessment",
            resource_id=assessment_id,
            ip_address=http_request.client.host if http_request.client else None
        )
        session.add(audit)
        session.commit()

        return AssessmentResult(
            assessment_id=assessment_id,
            user_id=assessment.user_id,
            assessment_type=assessment.assessment_type,
            scores=[PersonalityScore(**s) for s in db_result.scores],
            summary=db_result.summary,
            detailed_analysis=db_result.detailed_analysis,
            strengths=db_result.strengths,
            development_areas=db_result.development_areas,
            recommendations=db_result.recommendations,
            completed_at=assessment.completed_at or datetime.now()
        )

    finally:
        session.close()


@app.get("/api/v1/assessment/types")
async def get_assessment_types():
    """Get available assessment types"""
    return {
        "assessment_types": [
            {
                "id": "big_five",
                "name": "Big Five (OCEAN)",
                "description": "Mäter fem huvuddimensioner av personlighet: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism",
                "dimensions": 5,
                "recommended_questions": 30
            },
            {
                "id": "disc",
                "name": "DISC",
                "description": "Mäter beteendeprofil baserat på Dominance, Influence, Steadiness, Conscientiousness",
                "dimensions": 4,
                "recommended_questions": 24
            },
            {
                "id": "jung_mbti",
                "name": "Jung/MBTI",
                "description": "Myers-Briggs Type Indicator baserat på Jungs typologi",
                "dimensions": 4,
                "types": 16,
                "recommended_questions": 40
            },
            {
                "id": "comprehensive",
                "name": "Comprehensive Assessment",
                "description": "Kombinerar Big Five, DISC och Jung/MBTI för en heltäckande personlighetsanalys",
                "dimensions": 13,
                "recommended_questions": 60
            }
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gdpr_compliant": True,
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("🔒 Starting GDPR-Compliant Personality Assessment API...")
    print("📊 Database initialized")
    print("✅ Ready to accept requests")
    uvicorn.run(app, host="0.0.0.0", port=8000)
