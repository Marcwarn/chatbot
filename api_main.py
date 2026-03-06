"""
Personality Assessment API
Baserad på Big Five, DISC, Jung/MBTI och modern psykometri
AI-driven question generation och analys
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from anthropic import Anthropic
import json

# Initialize FastAPI app
app = FastAPI(
    title="Personality Assessment API",
    description="AI-driven personality assessments based on Big Five, DISC, Jung/MBTI",
    version="1.0.0"
)

# CORS - Tillåt Lovable och andra frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # I produktion: specificera Lovable domän
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AssessmentType(BaseModel):
    """Types of personality assessments available"""
    BIG_FIVE = "big_five"
    DISC = "disc"
    JUNG_MBTI = "jung_mbti"
    COMPREHENSIVE = "comprehensive"  # Kombinerar alla

class StartAssessmentRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    assessment_type: str = Field(..., description="Type: big_five, disc, jung_mbti, comprehensive")
    language: str = Field(default="sv", description="Language code (sv, en)")
    num_questions: int = Field(default=30, ge=10, le=100, description="Number of questions to generate")

class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    scale_type: str  # likert, choice, open
    options: Optional[List[str]] = None
    dimension: str  # Vilken dimension/trait som mäts

class AssessmentQuestions(BaseModel):
    assessment_id: str
    questions: List[QuestionResponse]
    total_questions: int
    assessment_type: str
    created_at: datetime

class AnswerSubmission(BaseModel):
    assessment_id: str
    question_id: int
    answer: Any  # Can be int (1-5), string, or list

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

# ============================================================================
# AI PROMPT TEMPLATES
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
# AI QUESTION GENERATION
# ============================================================================

def generate_questions_with_ai(assessment_type: str, num_questions: int, language: str) -> List[QuestionResponse]:
    """Generate assessment questions using Claude AI"""

    # Välj rätt system prompt
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
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Parse JSON response
        response_text = message.content[0].text

        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        questions_data = json.loads(response_text)

        # Convert to Pydantic models
        questions = [
            QuestionResponse(**q) for q in questions_data["questions"]
        ]

        return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

# ============================================================================
# AI ANSWER ANALYSIS
# ============================================================================

def analyze_answers_with_ai(assessment_type: str, questions: List[QuestionResponse],
                           answers: List[AnswerSubmission], language: str) -> AssessmentResult:
    """Analyze assessment answers using Claude AI"""

    # Prepare answers context
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
            messages=[
                {"role": "user", "content": analysis_prompt}
            ]
        )

        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result_data = json.loads(response_text)

        # Create result object
        result = AssessmentResult(
            assessment_id=answers[0].assessment_id,
            user_id="",  # Will be filled from stored data
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
# IN-MEMORY STORAGE (För demo - använd databas i produktion)
# ============================================================================

assessments_db = {}  # assessment_id -> assessment data
results_db = {}  # assessment_id -> results

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Personality Assessment API",
        "version": "1.0.0",
        "endpoints": {
            "start_assessment": "/api/v1/assessment/start",
            "submit_answers": "/api/v1/assessment/submit",
            "get_result": "/api/v1/assessment/result/{assessment_id}",
            "docs": "/docs"
        }
    }

@app.post("/api/v1/assessment/start", response_model=AssessmentQuestions)
async def start_assessment(request: StartAssessmentRequest):
    """
    Start a new personality assessment
    Generates AI-powered questions based on selected assessment type
    """

    # Generate unique assessment ID
    assessment_id = f"assess_{request.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Generate questions using AI
    questions = generate_questions_with_ai(
        assessment_type=request.assessment_type,
        num_questions=request.num_questions,
        language=request.language
    )

    # Store assessment data
    assessment_data = {
        "assessment_id": assessment_id,
        "user_id": request.user_id,
        "assessment_type": request.assessment_type,
        "language": request.language,
        "questions": questions,
        "created_at": datetime.now(),
        "status": "in_progress"
    }

    assessments_db[assessment_id] = assessment_data

    return AssessmentQuestions(
        assessment_id=assessment_id,
        questions=questions,
        total_questions=len(questions),
        assessment_type=request.assessment_type,
        created_at=datetime.now()
    )

@app.post("/api/v1/assessment/submit", response_model=AssessmentResult)
async def submit_assessment(request: CompleteAssessmentRequest):
    """
    Submit completed assessment answers
    Returns AI-analyzed personality profile
    """

    # Retrieve assessment data
    if request.assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment_data = assessments_db[request.assessment_id]

    # Analyze answers using AI
    result = analyze_answers_with_ai(
        assessment_type=assessment_data["assessment_type"],
        questions=assessment_data["questions"],
        answers=request.answers,
        language=assessment_data["language"]
    )

    # Add user_id to result
    result.user_id = assessment_data["user_id"]
    result.assessment_id = request.assessment_id

    # Store result
    results_db[request.assessment_id] = result
    assessments_db[request.assessment_id]["status"] = "completed"

    return result

@app.get("/api/v1/assessment/result/{assessment_id}", response_model=AssessmentResult)
async def get_assessment_result(assessment_id: str):
    """
    Retrieve assessment results by ID
    """

    if assessment_id not in results_db:
        raise HTTPException(status_code=404, detail="Result not found")

    return results_db[assessment_id]

@app.get("/api/v1/assessment/types")
async def get_assessment_types():
    """
    Get available assessment types and their descriptions
    """
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
