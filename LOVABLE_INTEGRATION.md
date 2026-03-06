# 🔗 Integration med Lovable Web App

Detta dokument beskriver hur du integrerar Personality Assessment API med din Lovable web app.

## 📋 Översikt

**Backend (denna repo):** FastAPI server med AI-drivna personlighetsbedömningar
**Frontend (Lovable):** Din React/TypeScript web app som gör HTTP requests till API:et

---

## 🚀 Steg 1: Starta Backend API

### Lokalt (för utveckling)

```bash
# Installera dependencies
pip install -r requirements.txt

# Skapa .env fil
cp .env.example .env

# Lägg till din Anthropic API key i .env
# ANTHROPIC_API_KEY=sk-ant-xxxxx

# Starta API servern
python api_main.py

# Eller med uvicorn:
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

API:et körs nu på: `http://localhost:8000`

### Produktion (deploy till cloud)

**Alternativ 1: Railway.app**
```bash
# railway.toml redan konfigurerad
railway up
```

**Alternativ 2: Render.com**
- Skapa ny Web Service
- Connecta GitHub repo
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api_main:app --host 0.0.0.0 --port $PORT`

**Alternativ 3: Fly.io**
```bash
fly launch
fly deploy
```

---

## 🔌 Steg 2: Integrera med Lovable

### A. Skapa Assessment Service i Lovable

Skapa en ny fil `src/services/assessmentService.ts`:

```typescript
// src/services/assessmentService.ts

const API_BASE_URL = import.meta.env.VITE_ASSESSMENT_API_URL || 'http://localhost:8000';

export interface AssessmentType {
  id: 'big_five' | 'disc' | 'jung_mbti' | 'comprehensive';
  name: string;
  description: string;
}

export interface Question {
  question_id: number;
  question_text: string;
  scale_type: 'likert' | 'choice' | 'open';
  options?: string[];
  dimension: string;
}

export interface AssessmentQuestions {
  assessment_id: string;
  questions: Question[];
  total_questions: number;
  assessment_type: string;
}

export interface Answer {
  question_id: number;
  answer: number | string;
}

export interface PersonalityScore {
  dimension: string;
  score: number;
  percentile?: number;
  interpretation: string;
}

export interface AssessmentResult {
  assessment_id: string;
  user_id: string;
  assessment_type: string;
  scores: PersonalityScore[];
  summary: string;
  detailed_analysis: string;
  strengths: string[];
  development_areas: string[];
  recommendations: string[];
}

// API Client
class AssessmentAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Starta ett nytt assessment
  async startAssessment(
    userId: string,
    assessmentType: string = 'big_five',
    language: string = 'sv',
    numQuestions: number = 30
  ): Promise<AssessmentQuestions> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        assessment_type: assessmentType,
        language,
        num_questions: numQuestions,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to start assessment: ${response.statusText}`);
    }

    return await response.json();
  }

  // Skicka in svar
  async submitAssessment(
    assessmentId: string,
    answers: Answer[]
  ): Promise<AssessmentResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        assessment_id: assessmentId,
        answers: answers.map(a => ({
          assessment_id: assessmentId,
          question_id: a.question_id,
          answer: a.answer,
        })),
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit assessment: ${response.statusText}`);
    }

    return await response.json();
  }

  // Hämta resultat
  async getResult(assessmentId: string): Promise<AssessmentResult> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/assessment/result/${assessmentId}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get result: ${response.statusText}`);
    }

    return await response.json();
  }

  // Hämta tillgängliga assessment types
  async getAssessmentTypes(): Promise<AssessmentType[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/assessment/types`);

    if (!response.ok) {
      throw new Error(`Failed to get assessment types: ${response.statusText}`);
    }

    const data = await response.json();
    return data.assessment_types;
  }
}

export const assessmentAPI = new AssessmentAPIClient();
```

### B. Skapa Assessment Component

Skapa `src/components/PersonalityAssessment.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { assessmentAPI, Question, Answer, AssessmentResult } from '../services/assessmentService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';

export function PersonalityAssessment() {
  const [stage, setStage] = useState<'start' | 'questions' | 'results'>('start');
  const [assessmentId, setAssessmentId] = useState<string>('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);

  const startAssessment = async (type: string) => {
    setLoading(true);
    try {
      const userId = `user_${Date.now()}`; // Eller hämta från din auth
      const response = await assessmentAPI.startAssessment(userId, type, 'sv', 30);

      setAssessmentId(response.assessment_id);
      setQuestions(response.questions);
      setStage('questions');
    } catch (error) {
      console.error('Failed to start assessment:', error);
      alert('Kunde inte starta testet. Försök igen.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answer: number | string) => {
    const currentQuestion = questions[currentQuestionIndex];

    setAnswers([
      ...answers,
      {
        question_id: currentQuestion.question_id,
        answer,
      },
    ]);

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      submitAssessment();
    }
  };

  const submitAssessment = async () => {
    setLoading(true);
    try {
      const result = await assessmentAPI.submitAssessment(assessmentId, answers);
      setResult(result);
      setStage('results');
    } catch (error) {
      console.error('Failed to submit assessment:', error);
      alert('Kunde inte skicka in svaren. Försök igen.');
    } finally {
      setLoading(false);
    }
  };

  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  if (stage === 'start') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">Personlighetsbedömning</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Välj vilken typ av personlighetsbedömning du vill göra:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={() => startAssessment('big_five')}
                disabled={loading}
                className="h-auto p-6 flex flex-col items-start"
              >
                <h3 className="text-xl font-bold mb-2">Big Five (OCEAN)</h3>
                <p className="text-sm text-left">
                  Mäter fem huvuddimensioner av personlighet
                </p>
              </Button>

              <Button
                onClick={() => startAssessment('disc')}
                disabled={loading}
                className="h-auto p-6 flex flex-col items-start"
              >
                <h3 className="text-xl font-bold mb-2">DISC</h3>
                <p className="text-sm text-left">
                  Beteendeprofil baserat på fyra dimensioner
                </p>
              </Button>

              <Button
                onClick={() => startAssessment('jung_mbti')}
                disabled={loading}
                className="h-auto p-6 flex flex-col items-start"
              >
                <h3 className="text-xl font-bold mb-2">Jung/MBTI</h3>
                <p className="text-sm text-left">
                  Myers-Briggs Type Indicator
                </p>
              </Button>

              <Button
                onClick={() => startAssessment('comprehensive')}
                disabled={loading}
                className="h-auto p-6 flex flex-col items-start"
              >
                <h3 className="text-xl font-bold mb-2">Comprehensive</h3>
                <p className="text-sm text-left">
                  Heltäckande analys med alla modeller
                </p>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (stage === 'questions') {
    const currentQuestion = questions[currentQuestionIndex];

    return (
      <div className="max-w-2xl mx-auto p-6">
        <Card>
          <CardHeader>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-500">
                <span>Fråga {currentQuestionIndex + 1} av {questions.length}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <h2 className="text-2xl font-semibold">
              {currentQuestion.question_text}
            </h2>

            {currentQuestion.scale_type === 'likert' && (
              <RadioGroup onValueChange={(value) => handleAnswer(parseInt(value))}>
                {currentQuestion.options?.map((option, idx) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <RadioGroupItem value={String(idx + 1)} id={`option-${idx}`} />
                    <Label htmlFor={`option-${idx}`}>{option}</Label>
                  </div>
                ))}
              </RadioGroup>
            )}

            <div className="text-sm text-gray-500">
              Dimension: {currentQuestion.dimension}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (stage === 'results' && result) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">Dina Resultat</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-2">Sammanfattning</h3>
              <p className="text-gray-700">{result.summary}</p>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-4">Personlighetspoäng</h3>
              <div className="space-y-4">
                {result.scores.map((score, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-semibold">{score.dimension}</span>
                      <span>{score.score.toFixed(1)}/100</span>
                    </div>
                    <Progress value={score.score} />
                    <p className="text-sm text-gray-600">{score.interpretation}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-2">Styrkor</h3>
              <ul className="list-disc list-inside space-y-1">
                {result.strengths.map((strength, idx) => (
                  <li key={idx} className="text-gray-700">{strength}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-2">Utvecklingsområden</h3>
              <ul className="list-disc list-inside space-y-1">
                {result.development_areas.map((area, idx) => (
                  <li key={idx} className="text-gray-700">{area}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-2">Rekommendationer</h3>
              <ul className="list-disc list-inside space-y-1">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>

            <Button onClick={() => window.location.reload()}>
              Gör ett nytt test
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return null;
}
```

### C. Environment Variables i Lovable

Lägg till i din `.env` fil i Lovable projektet:

```bash
VITE_ASSESSMENT_API_URL=https://your-api-url.com
```

För lokal utveckling:
```bash
VITE_ASSESSMENT_API_URL=http://localhost:8000
```

---

## 🎯 Steg 3: Använd Component i din Lovable App

I din `App.tsx` eller relevant route:

```typescript
import { PersonalityAssessment } from './components/PersonalityAssessment';

function App() {
  return (
    <div className="App">
      <PersonalityAssessment />
    </div>
  );
}
```

---

## 🔒 Säkerhet & Best Practices

### CORS
API:et har redan CORS konfigurerat. Uppdatera `ALLOWED_ORIGINS` i `.env` med din Lovable domän:

```bash
ALLOWED_ORIGINS=https://your-app.lovable.app,http://localhost:3000
```

### Rate Limiting (för produktion)
Lägg till rate limiting middleware:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/assessment/start")
@limiter.limit("5/minute")
async def start_assessment(...):
    ...
```

### Authentication (optional)
För att skydda API:et kan du lägga till JWT authentication:

```typescript
// I Lovable
const response = await fetch(`${API_URL}/api/v1/assessment/start`, {
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json',
  },
  ...
});
```

---

## 📊 API Endpoints Referens

### GET /api/v1/assessment/types
Hämta alla tillgängliga assessment types

**Response:**
```json
{
  "assessment_types": [
    {
      "id": "big_five",
      "name": "Big Five (OCEAN)",
      "description": "...",
      "dimensions": 5,
      "recommended_questions": 30
    }
  ]
}
```

### POST /api/v1/assessment/start
Starta nytt assessment

**Request:**
```json
{
  "user_id": "user_123",
  "assessment_type": "big_five",
  "language": "sv",
  "num_questions": 30
}
```

**Response:**
```json
{
  "assessment_id": "assess_user123_20231206120000",
  "questions": [...],
  "total_questions": 30,
  "assessment_type": "big_five"
}
```

### POST /api/v1/assessment/submit
Skicka in svar

**Request:**
```json
{
  "assessment_id": "assess_user123_20231206120000",
  "answers": [
    {
      "assessment_id": "assess_user123_20231206120000",
      "question_id": 1,
      "answer": 4
    }
  ]
}
```

**Response:**
```json
{
  "assessment_id": "assess_user123_20231206120000",
  "scores": [...],
  "summary": "...",
  "detailed_analysis": "...",
  "strengths": [...],
  "development_areas": [...],
  "recommendations": [...]
}
```

### GET /api/v1/assessment/result/{assessment_id}
Hämta resultat

---

## 🧪 Testa Integration

### Test med cURL:

```bash
# 1. Starta assessment
curl -X POST http://localhost:8000/api/v1/assessment/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "assessment_type": "big_five",
    "language": "sv",
    "num_questions": 10
  }'

# 2. Skicka in svar (använd assessment_id från steg 1)
curl -X POST http://localhost:8000/api/v1/assessment/submit \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_id": "assess_test_user_...",
    "answers": [...]
  }'
```

---

## 🚀 Deploy Checklist

- [ ] Backend deployed och tillgängligt via HTTPS
- [ ] ANTHROPIC_API_KEY konfigurerad i environment
- [ ] CORS origins uppdaterade med Lovable domän
- [ ] Environment variable `VITE_ASSESSMENT_API_URL` satt i Lovable
- [ ] Assessment component importerad och använd i Lovable app
- [ ] Testat hela flödet från start till resultat

---

## 💡 Tips

1. **Caching:** Spara resultat i localStorage för att visa tidigare tester
2. **Progress Saving:** Implementera auto-save av svar under testet
3. **PDF Export:** Lägg till möjlighet att exportera resultat som PDF
4. **Sharing:** Implementera delningsfunktion för resultat
5. **Analytics:** Track vilka test-typer som är mest populära

---

## 🆘 Troubleshooting

**CORS Error:**
- Kontrollera att `ALLOWED_ORIGINS` inkluderar din Lovable domän
- Verifiera att API:et körs och är tillgängligt

**API Not Responding:**
- Kolla att `VITE_ASSESSMENT_API_URL` är rätt konfigurerad
- Kontrollera att backend servern körs
- Kolla network tab i browser developer tools

**Questions Not Generated:**
- Verifiera att `ANTHROPIC_API_KEY` är korrekt satt
- Kolla API logs för error messages
- Testa med färre frågor först (num_questions: 10)

---

Lycka till med din assessment app! 🎉
