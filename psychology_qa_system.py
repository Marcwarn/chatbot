"""
Psychology Q&A System - General Psychology Knowledge Base
Answers general psychology questions with research-backed information
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# KNOWLEDGE BASE - PSYCHOLOGY CONCEPTS
# ============================================================================

PSYCHOLOGY_KNOWLEDGE_BASE = {
    "big_five": {
        "question_variants": [
            "vad är big five",
            "what is big five",
            "big five modellen",
            "ocean modellen",
            "femfaktormodellen"
        ],
        "answer_sv": """
**Big Five (även kallad OCEAN eller Femfaktormodellen)** är den mest vetenskapligt validerade personlighetsmodellen.

**De fem dimensionerna är:**

1. **Openness (Öppenhet)** - Kreativitet, nyfikenhet, fantasi
2. **Conscientiousness (Samvetsgrannhet)** - Organisation, disciplin, pålitlighet
3. **Extraversion** - Social energi, utåtriktad, pratsam
4. **Agreeableness (Vänlighet)** - Empati, samarbete, omtanke
5. **Neuroticism** - Emotionell känslighet, oro, stress-reaktivitet

**Varför är den bra?**
- Baserad på 70+ års forskning
- Förutsäger karriärsuccess, relationer, hälsa
- Kulturellt validerad i över 50 länder
- Stabil över tid (men kan förändras gradvis)

**Användningsområden:**
Rekrytering, karriärvägledning, personlig utveckling, relationsterapi, forskning
        """,
        "sources": [
            "McCrae & Costa (1987) - Validation of the five-factor model",
            "Goldberg (1993) - The structure of phenotypic personality traits"
        ]
    },

    "disc": {
        "question_variants": [
            "vad är disc",
            "what is disc",
            "disc modellen",
            "disc test"
        ],
        "answer_sv": """
**DISC** är en beteendemodell som fokuserar på fyra huvudsakliga beteendestilar:

1. **D - Dominance (Dominans)** - Resultatorienterad, direkt, beslutsam
2. **I - Influence (Inflytande)** - Utåtriktad, entusiastisk, social
3. **S - Steadiness (Stabilitet)** - Pålitlig, tålmodig, teamorienterad
4. **C - Conscientiousness (Noggrannhet)** - Analytisk, detaljorienterad, kvalitetsmedveten

**Skillnad mot Big Five:**
- DISC fokuserar på *beteende* (hur du agerar)
- Big Five fokuserar på *personlighetsdrag* (vem du är)
- DISC är mer situationell och kan variera beroende på kontext
- Big Five är mer stabil över tid

**Bäst för:**
Teamdynamik, kommunikationsstilar, ledarskap, säljträning

**Forskningsbas:**
Mindre akademisk forskning än Big Five, men välanvänd i företagsvärlden sedan 1970-talet.
        """,
        "sources": [
            "Marston, W. (1928) - Emotions of Normal People",
            "Clarke, J. (1956) - Adaptation for business use"
        ]
    },

    "personality_change": {
        "question_variants": [
            "kan man ändra sin personlighet",
            "can personality change",
            "förändra personlighet",
            "är personlighet fixerad"
        ],
        "answer_sv": """
**Ja, personlighet kan förändras - men det kräver tid och ansträngning.**

**Vad säger forskningen?**

1. **Naturlig mognad** - Personlighet förändras gradvis över livet:
   - Conscientiousness ökar med åldern (vi blir mer ansvarsfulla)
   - Neuroticism minskar (vi blir mer emotionellt stabila)
   - Agreeableness ökar (vi blir mer empatiska)

2. **Aktiv förändring är möjlig:**
   - Studier visar att 16 veckors intervention kan förändra personlighetsdrag
   - Terapi (särskilt KBT) kan minska Neuroticism
   - Mindfulness-träning kan öka Openness och minska Neuroticism

3. **Vad krävs för förändring?**
   - Tydligt mål (vilket drag vill du förändra?)
   - Konkreta beteendeförändringar upprepade över tid
   - 3-6 månaders konsekvent träning
   - Feedback och reflektion

**Exempel:**
För att öka Extraversion: Sätt mål att initiera 3 sociala interaktioner/dag. Efter 4 månader av konsekvent träning kommer beteendet kännas naturligare.

**Begränsningar:**
Grundtemperamentet (genetisk bas) är svårare att förändra än inlärda beteenden.
        """,
        "sources": [
            "Hudson & Fraley (2015) - Volitional personality trait change",
            "Roberts et al. (2017) - A systematic review of personality trait change"
        ]
    },

    "emotional_intelligence": {
        "question_variants": [
            "vad är emotionell intelligens",
            "what is emotional intelligence",
            "eq",
            "emotional quotient"
        ],
        "answer_sv": """
**Emotionell Intelligens (EQ)** är förmågan att uppfatta, förstå och hantera känslor - både dina egna och andras.

**De fyra komponenterna (Goleman):**

1. **Självmedvetenhet** - Känna igen dina egna känslor och hur de påverkar dig
2. **Självhantering** - Kontrollera impulser, hantera stress, anpassa dig
3. **Social medvetenhet** - Empati, förstå andras perspektiv
4. **Relationshantering** - Kommunikation, konfliktlösning, samarbete

**Varför är EQ viktigt?**
- Förutsäger karriärsuccess bättre än IQ i många roller
- Avgörande för ledarskap och teamwork
- Korrelerar med bättre relationer och mental hälsa
- Kan tränas och förbättras (till skillnad från IQ som är mer fixerat)

**Koppling till Big Five:**
- Hög Agreeableness → ofta hög social medvetenhet
- Låg Neuroticism → ofta bättre självhantering
- Hög Extraversion → kan hjälpa social interaktion
- Men EQ är *träningsbar* även om personlighet är stabil

**Hur tränar man EQ?**
1. Mindfulness och meditation (självmedvetenhet)
2. Journaling om känslor (reflektion)
3. Aktivt lyssnande (empati)
4. Feedback från andra (blind spots)
        """,
        "sources": [
            "Goleman, D. (1995) - Emotional Intelligence",
            "Mayer & Salovey (1997) - What is emotional intelligence?"
        ]
    },

    "cognitive_dissonance": {
        "question_variants": [
            "vad är kognitiv dissonans",
            "what is cognitive dissonance",
            "cognitive dissonance"
        ],
        "answer_sv": """
**Kognitiv dissonans** är det obehagliga känslomässiga tillståndet som uppstår när du har motstridiga tankar, värderingar eller beteenden.

**Exempel:**
- Du värdesätter hälsa men röker → dissonans
- Du ser dig som ärlig men ljuger → dissonans
- Du vill spara pengar men shoppar impulsivt → dissonans

**Vad händer i hjärnan?**
Hjärnan hatar inkonsekvens. När dissonans uppstår försöker du minska den genom:

1. **Ändra beteende** - "Jag slutar röka"
2. **Ändra attityd** - "Rökning är inte SÅ farligt"
3. **Rationalisera** - "Jag rör mig mycket så det kompenserar"
4. **Undvika information** - Läser inte om rökningens risker

**Varför är det viktigt att förstå?**
- Förklarar varför förändring är svårt (hjärnan försvarar status quo)
- Hjälper förstå självbedrägeri och rationalisering
- Viktig i marknadsföring och påverkan

**Koppling till personlighet:**
- Hög Openness → ofta mer bekväm med dissonans (nyfiken på motargument)
- Hög Conscientiousness → kan känna stark dissonans vid inkonsekvent beteende
- Låg Neuroticism → hanterar dissonans-obehaget bättre
        """,
        "sources": [
            "Festinger, L. (1957) - A Theory of Cognitive Dissonance"
        ]
    },

    "nature_vs_nurture": {
        "question_variants": [
            "nature vs nurture",
            "arv och miljö",
            "genetik personlighet",
            "är personlighet ärftlig"
        ],
        "answer_sv": """
**Personlighet påverkas av BÅDE arv och miljö - men i vilken grad?**

**Vad säger forskningen?**

**Genetik (Nature):**
- Cirka 40-60% av personlighetsvariationen beror på genetik
- Tvillingstudier visar att identiska tvillingar (100% samma DNA) har mer lika personlighet än frånskilda tvillingar (50% samma DNA)
- Vissa drag är mer ärftliga än andra:
  - Extraversion: ~54% ärftligt
  - Neuroticism: ~48% ärftligt
  - Openness: ~57% ärftligt

**Miljö (Nurture):**
- Cirka 40-60% beror på miljö och erfarenheter
- Barndomstrauma kan öka Neuroticism
- Kulturell kontext formar uttryck av personlighet
- Livshändelser (förluster, framgångar) påverkar

**Det intressanta:**
Delad familjeuppväxelse (samma föräldrar, hem) har överraskande LITEN effekt på vuxen personlighet. Det som mest påverkar är:
- **Genetik** (arv)
- **Icke-delad miljö** (unika erfarenheter, vänner, händelser)

**Slutsats:**
Du föds med ett temperament (genetisk bas), men hur det uttrycks och utvecklas formas av dina erfarenheter. Du har alltså både begränsningar OCH möjligheter att påverka din personlighet.
        """,
        "sources": [
            "Bouchard & McGue (2003) - Genetic and environmental influences on personality",
            "Plomin et al. (2016) - Top 10 replicated findings from behavioral genetics"
        ]
    },

    "growth_mindset": {
        "question_variants": [
            "vad är growth mindset",
            "what is growth mindset",
            "utvecklingstänkande",
            "fixed vs growth mindset"
        ],
        "answer_sv": """
**Growth Mindset vs Fixed Mindset** - hur du ser på förmågor och talang.

**Fixed Mindset (Statiskt tänkande):**
- "Intelligens och talang är medfött"
- "Jag är inte bra på det här" → ger upp
- Undviker utmaningar (rädd att misslyckas)
- Ser feedback som kritik

**Growth Mindset (Utvecklingstänkande):**
- "Förmågor kan utvecklas genom ansträngning"
- "Jag är inte bra på det här **ännu**" → fortsätter träna
- Söker utmaningar (möjlighet att växa)
- Ser feedback som lärande

**Varför är det viktigt?**
- Elever med growth mindset presterar bättre (Dweck, 2006)
- Leder till större uthållighet och motståndskraft
- Minskar rädsla för misslyckande

**Hur utvecklar man growth mindset?**
1. Lägg till "ännu" - "Jag kan inte det här *ännu*"
2. Fokusera på process, inte resultat - "Jag tränade hårt" > "Jag är begåvad"
3. Omformulera misslyckanden - "Vad lärde jag mig?"
4. Sök konstruktiv feedback aktivt

**Koppling till Big Five:**
- Hög Openness → ofta naturligt growth mindset (nyfiken på att lära)
- Hög Conscientiousness → drar nytta av growth mindset (uthållighet)
- Låg Neuroticism → lättare att acceptera misslyckanden som lärande

**Viktigt att veta:**
Growth mindset betyder INTE att alla kan bli vad som helst. Det betyder att förbättring alltid är möjlig genom smart träning.
        """,
        "sources": [
            "Dweck, C. (2006) - Mindset: The New Psychology of Success"
        ]
    },

    "stress_anxiety": {
        "question_variants": [
            "skillnad stress ångest",
            "vad är stress",
            "vad är ångest",
            "difference stress anxiety"
        ],
        "answer_sv": """
**Stress vs Ångest - vad är skillnaden?**

**Stress:**
- **Reaktion på extern påfrestning** (deadline, konflikt, krav)
- Konkret, identifierbar källa
- Försvinner när påfrestningen är över
- Kan vara produktiv i lagom mängd (eustress)
- Symtom: spänning, irritation, koncentrationssvårigheter

**Ångest:**
- **Oro utan konkret yttre hot**
- Ofta diffus och svår att peka på orsak
- Kan kvarstå även när inget hotar
- Framtidsinriktad ("tänk om...")
- Symtom: oro, rastlöshet, svårt att koppla av, katastoftankar

**Vad händer i kroppen?**
Båda aktiverar "fight or flight" (stressystemet):
- Kortisol och adrenalin frisätts
- Hjärtfrekvens ökar
- Andning blir ytligare
- Muskelspänning ökar

**Skillnaden:**
- Stress: "Jag har en deadline imorgon" → systemet aktiveras för att hjälpa dig prestera
- Ångest: "Vad händer om jag misslyckas? Vad händer om de tycker jag är dum?" → systemet aktiveras utan konkret hot

**Koppling till Big Five:**
Hög Neuroticism (emotionell känslighet) är den starkaste prediktorn för både stress-reaktivitet och ångest. Personer med låg Neuroticism (hög emotionell stabilitet) påverkas mindre av stress och upplever mindre ångest.

**När söka hjälp?**
Om ångest påverkar din vardag (sömn, arbete, relationer) regelbundet i mer än 2 veckor - prata med vårdcentral.
        """,
        "sources": [
            "Lazarus & Folkman (1984) - Stress, Appraisal, and Coping",
            "American Psychological Association - Stress vs Anxiety"
        ]
    }
}


# ============================================================================
# TOPIC DETECTION
# ============================================================================

def find_matching_topic(question: str) -> Optional[str]:
    """
    Find which topic in knowledge base matches the question

    Args:
        question: User's question

    Returns:
        Topic key or None
    """
    question_lower = question.lower()

    for topic_key, topic_data in PSYCHOLOGY_KNOWLEDGE_BASE.items():
        variants = topic_data.get("question_variants", [])
        for variant in variants:
            if variant in question_lower:
                return topic_key

    return None


# ============================================================================
# PSYCHOLOGY Q&A SYSTEM
# ============================================================================

class PsychologyQA:
    """
    General psychology question answering system
    """

    def __init__(self, language: str = "sv"):
        self.language = language
        self.knowledge_base = PSYCHOLOGY_KNOWLEDGE_BASE

    def answer_question(self, question: str) -> Optional[Dict[str, any]]:
        """
        Answer a general psychology question

        Args:
            question: User's question

        Returns:
            Dict with answer and sources, or None if can't answer
        """
        topic = find_matching_topic(question)

        if not topic:
            return None

        topic_data = self.knowledge_base[topic]
        answer_key = f"answer_{self.language}"

        if answer_key not in topic_data:
            return None

        return {
            "topic": topic,
            "answer": topic_data[answer_key].strip(),
            "sources": topic_data.get("sources", []),
            "confidence": "high"
        }

    def can_answer(self, question: str) -> bool:
        """
        Check if we can answer this question

        Args:
            question: User's question

        Returns:
            True if we have knowledge about this topic
        """
        return find_matching_topic(question) is not None

    def get_related_topics(self, topic: str) -> List[str]:
        """
        Get topics related to a given topic

        Args:
            topic: Topic key

        Returns:
            List of related topic keys
        """
        # Define relationships between topics
        relationships = {
            "big_five": ["disc", "personality_change", "nature_vs_nurture"],
            "disc": ["big_five", "emotional_intelligence"],
            "personality_change": ["big_five", "growth_mindset", "nature_vs_nurture"],
            "emotional_intelligence": ["big_five", "stress_anxiety"],
            "cognitive_dissonance": ["growth_mindset"],
            "nature_vs_nurture": ["big_five", "personality_change"],
            "growth_mindset": ["personality_change", "cognitive_dissonance"],
            "stress_anxiety": ["emotional_intelligence", "big_five"]
        }

        return relationships.get(topic, [])

    def suggest_follow_up_questions(self, topic: str) -> List[str]:
        """
        Suggest follow-up questions based on topic

        Args:
            topic: Current topic

        Returns:
            List of suggested questions
        """
        suggestions = {
            "big_five": [
                "Kan man ändra sin personlighet?",
                "Vad är skillnaden mellan Big Five och DISC?",
                "Är personlighet ärftlig?"
            ],
            "disc": [
                "Hur skiljer sig DISC från Big Five?",
                "Vilken DISC-profil passar bäst för ledarskap?"
            ],
            "personality_change": [
                "Hur lång tid tar det att ändra ett personlighetsdrag?",
                "Vad är growth mindset?"
            ],
            "emotional_intelligence": [
                "Hur tränar man emotionell intelligens?",
                "Är EQ viktigare än IQ?"
            ],
            "growth_mindset": [
                "Hur utvecklar man growth mindset?",
                "Kan man ändra sin personlighet?"
            ],
            "stress_anxiety": [
                "Hur hänger stress ihop med personlighet?",
                "Kan man träna sin förmåga att hantera stress?"
            ]
        }

        return suggestions.get(topic, [])

    def get_out_of_scope_response(self) -> str:
        """
        Response for questions outside our scope

        Returns:
            Polite redirection message
        """
        if self.language == "sv":
            return """
Tyvärr ligger den frågan utanför min expertis inom personlighetspsykologi och Big Five/DISC-modellerna.

Jag är specialiserad på:
- Big Five och DISC personlighetsmodeller
- Personlighetsutveckling
- Karriärvägledning baserad på personlighet
- Relationsdynamik och kommunikationsstilar

Har du någon fråga inom dessa områden?
            """.strip()
        else:
            return "I'm sorry, that question is outside my area of expertise in personality psychology."


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_answer_with_sources(answer: str, sources: List[str]) -> str:
    """
    Format answer with source citations

    Args:
        answer: Answer text
        sources: List of source citations

    Returns:
        Formatted answer with sources
    """
    if not sources:
        return answer

    sources_text = "\n\n**Källor:**\n" + "\n".join(f"- {s}" for s in sources)
    return answer + sources_text


def extract_key_concepts(question: str) -> List[str]:
    """
    Extract key psychology concepts from question

    Args:
        question: User's question

    Returns:
        List of detected concepts
    """
    concepts = []
    concept_keywords = {
        "big five": ["big five", "ocean", "femfaktor"],
        "disc": ["disc"],
        "personality": ["personlighet", "personality"],
        "genetics": ["genetik", "arv", "ärftlig", "genetics", "hereditary"],
        "emotion": ["känslor", "emotion", "feeling"],
        "stress": ["stress", "ångest", "anxiety", "oro"],
        "intelligence": ["intelligens", "intelligence", "iq", "eq"],
        "change": ["förändring", "change", "develop"]
    }

    question_lower = question.lower()
    for concept, keywords in concept_keywords.items():
        if any(kw in question_lower for kw in keywords):
            concepts.append(concept)

    return concepts


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("PSYCHOLOGY Q&A SYSTEM TEST")
    print("=" * 80)

    qa = PsychologyQA(language="sv")

    test_questions = [
        "Vad är Big Five?",
        "Kan man ändra sin personlighet?",
        "Vad är skillnaden mellan stress och ångest?",
        "Vad är emotionell intelligens?",
        "Hur gör man glass?"  # Out of scope
    ]

    for question in test_questions:
        print(f"\n{'=' * 80}")
        print(f"Q: {question}")
        print("-" * 80)

        if qa.can_answer(question):
            result = qa.answer_question(question)
            if result:
                print(f"Topic: {result['topic']}")
                print(f"\nAnswer:\n{result['answer']}")

                if result['sources']:
                    print(f"\nSources:")
                    for source in result['sources']:
                        print(f"  - {source}")

                # Suggest follow-ups
                follow_ups = qa.suggest_follow_up_questions(result['topic'])
                if follow_ups:
                    print(f"\nRelaterade frågor du kan ställa:")
                    for fq in follow_ups:
                        print(f"  - {fq}")
        else:
            print(qa.get_out_of_scope_response())

    print("\n" + "=" * 80)
    print("✅ Psychology Q&A test completed!")
