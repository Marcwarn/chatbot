"""
Question Classifier - Intent and Topic Detection
Classifies user questions into categories and detects urgency/emotional state
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class QuestionType(Enum):
    """Question type classification"""
    PERSONAL_REPORT = "personal_report"  # Questions about their own assessment
    GENERAL_PSYCHOLOGY = "general_psychology"  # General psychology questions
    CLARIFICATION = "clarification"  # Follow-up questions about previous answer
    SMALL_TALK = "small_talk"  # Greetings, thanks, etc.
    CAREER_GUIDANCE = "career_guidance"  # Career-related questions
    RELATIONSHIP = "relationship"  # Relationship/interpersonal questions
    PERSONAL_GROWTH = "personal_growth"  # Self-improvement questions
    COMPARISON = "comparison"  # Comparing traits or profiles


class QuestionTopic(Enum):
    """Specific topics within psychology/personality"""
    # Big Five traits
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    CONSCIENTIOUSNESS = "conscientiousness"
    NEUROTICISM = "neuroticism"
    EMOTIONAL_STABILITY = "emotional_stability"
    OPENNESS = "openness"

    # DISC dimensions
    DISC_DOMINANCE = "disc_dominance"
    DISC_INFLUENCE = "disc_influence"
    DISC_STEADINESS = "disc_steadiness"
    DISC_CONSCIENTIOUSNESS_DISC = "disc_conscientiousness"

    # General topics
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    PERSONAL_GROWTH = "personal_growth"
    STRESS_ANXIETY = "stress_anxiety"
    COMMUNICATION = "communication"
    LEADERSHIP = "leadership"
    CREATIVITY = "creativity"
    MOTIVATION = "motivation"

    # Psychology concepts
    BIG_FIVE_MODEL = "big_five_model"
    DISC_MODEL = "disc_model"
    PERSONALITY_THEORY = "personality_theory"
    COGNITIVE_PSYCHOLOGY = "cognitive_psychology"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"

    OTHER = "other"


class UrgencyLevel(Enum):
    """Urgency/emotional state of user"""
    NEUTRAL = "neutral"  # Standard question
    ANXIOUS = "anxious"  # User seems worried/anxious
    DISTRESSED = "distressed"  # User seems significantly upset
    CURIOUS = "curious"  # Positive curiosity
    CONFUSED = "confused"  # User is confused


@dataclass
class QuestionClassification:
    """Complete classification of a user question"""
    question_type: QuestionType
    topics: List[QuestionTopic]
    urgency: UrgencyLevel
    is_personal_pronoun: bool  # Contains "my", "min", "mitt", "mina"
    confidence: float  # 0-1 confidence score
    emotional_indicators: List[str]  # Words indicating emotion
    requires_profile: bool  # Whether we need user's assessment data
    is_trait_specific: bool  # Asking about specific personality trait


# ============================================================================
# PATTERN MATCHING DICTIONARIES
# ============================================================================

# Personal pronouns (Swedish + English)
PERSONAL_PRONOUNS = {
    "swedish": ["min", "mitt", "mina", "jag", "mig", "mitt resultat", "min profil"],
    "english": ["my", "mine", "i am", "i'm", "me", "my result", "my profile"]
}

# Big Five trait keywords
BIG_FIVE_KEYWORDS = {
    QuestionTopic.EXTRAVERSION: [
        "extraversion", "extrovert", "introvert", "social", "utåtriktad",
        "inåtvänd", "pratsam", "tystlåten", "energi", "fest"
    ],
    QuestionTopic.AGREEABLENESS: [
        "agreeableness", "vänlighet", "agreeable", "snäll", "empatisk",
        "omtänksam", "samarbete", "konflikt", "empati"
    ],
    QuestionTopic.CONSCIENTIOUSNESS: [
        "conscientiousness", "samvetsgrannhet", "conscientious", "organiserad",
        "noggrann", "strukturerad", "disciplin", "ansvar", "planerare"
    ],
    QuestionTopic.NEUROTICISM: [
        "neuroticism", "neurotisk", "oro", "ångest", "stress", "känslosam",
        "nervös", "neurotic", "worry"
    ],
    QuestionTopic.EMOTIONAL_STABILITY: [
        "emotional stability", "emotionell stabilitet", "lugn", "stabil",
        "balans", "jämn", "calm", "stable"
    ],
    QuestionTopic.OPENNESS: [
        "openness", "öppenhet", "kreativ", "nyfiken", "fantasifull",
        "open", "curious", "creative", "imagination"
    ]
}

# DISC keywords
DISC_KEYWORDS = {
    QuestionTopic.DISC_DOMINANCE: [
        "dominance", "dominant", "decisive", "resultatinriktad", "direkt",
        "bestämd", "kontroll", "makt"
    ],
    QuestionTopic.DISC_INFLUENCE: [
        "influence", "influential", "entusiasm", "socialt", "optimistisk",
        "övertalning", "charmerande"
    ],
    QuestionTopic.DISC_STEADINESS: [
        "steadiness", "steady", "stabil", "pålitlig", "lugn", "tålmodig",
        "metodisk", "konsistent"
    ],
    QuestionTopic.DISC_CONSCIENTIOUSNESS_DISC: [
        "compliance", "conscientiousness", "noggrann", "analytisk", "detaljerad",
        "kvalitet", "precision"
    ]
}

# Topic keywords
TOPIC_KEYWORDS = {
    QuestionTopic.CAREER: [
        "karriär", "jobb", "arbete", "yrke", "profession", "career", "job",
        "work", "chef", "ledare", "anställning"
    ],
    QuestionTopic.RELATIONSHIPS: [
        "relation", "partner", "vän", "familj", "kärlek", "relationship",
        "dating", "marriage", "friend", "social"
    ],
    QuestionTopic.PERSONAL_GROWTH: [
        "utveckling", "förändring", "förbättra", "growth", "change", "improve",
        "bättre", "utvecklas", "lära", "träna"
    ],
    QuestionTopic.STRESS_ANXIETY: [
        "stress", "ångest", "oro", "rädsla", "anxiety", "worry", "fear",
        "panic", "overwhelmed", "utmattad"
    ],
    QuestionTopic.COMMUNICATION: [
        "kommunikation", "prata", "samtala", "lyssna", "communication",
        "talk", "speak", "listen", "konversation"
    ],
    QuestionTopic.LEADERSHIP: [
        "ledarskap", "ledare", "chef", "leadership", "lead", "manage",
        "team", "grupp", "delegera"
    ],
    QuestionTopic.BIG_FIVE_MODEL: [
        "big five", "ocean", "femfaktormodellen", "personlighetsmodell",
        "ipip", "trait"
    ],
    QuestionTopic.DISC_MODEL: [
        "disc", "disc-modellen", "disc profil", "disc test"
    ],
    QuestionTopic.EMOTIONAL_INTELLIGENCE: [
        "emotionell intelligens", "eq", "emotional intelligence",
        "känslor", "emotions", "empati"
    ]
}

# Urgency/emotional indicators
URGENCY_KEYWORDS = {
    UrgencyLevel.ANXIOUS: [
        "orolig", "nervös", "worried", "anxious", "nervous", "osäker",
        "rädd", "afraid", "concerned"
    ],
    UrgencyLevel.DISTRESSED: [
        "deprimerad", "ledsen", "hopplös", "depressed", "sad", "hopeless",
        "desperate", "kan inte", "mår dåligt", "hjälp"
    ],
    UrgencyLevel.CURIOUS: [
        "intressant", "spännande", "fascinerande", "interesting", "fascinating",
        "cool", "wow", "undrar", "wondering"
    ],
    UrgencyLevel.CONFUSED: [
        "förvirrad", "förstår inte", "confused", "don't understand",
        "oklart", "unclear", "vad menar", "what does", "hur ska jag"
    ]
}

# Question patterns for type detection
PERSONAL_REPORT_PATTERNS = [
    r"\b(varför|why)\s+(fick|har)\s+jag\b",  # "varför fick jag"
    r"\b(min|mitt|mina)\s+(låg|hög|resultat|profil)\b",  # "min låga"
    r"\b(jag|i am|i'm)\s+(låg|hög|high|low)\b",  # "jag är låg"
    r"\b(mitt resultat|my result|my score)\b",
    r"\b(vad betyder|what does)\s+.*(min|mitt|my)\b"
]

GENERAL_PSYCHOLOGY_PATTERNS = [
    r"\b(vad är|what is|define)\s+\w+",
    r"\b(hur fungerar|how does)\s+\w+",
    r"\b(kan man|is it possible)\s+\w+",
    r"\b(forskning|research|studies)\b"
]


# ============================================================================
# CLASSIFICATION FUNCTIONS
# ============================================================================

def contains_personal_pronoun(text: str) -> bool:
    """Check if text contains personal pronouns"""
    text_lower = text.lower()

    for pronoun in PERSONAL_PRONOUNS["swedish"] + PERSONAL_PRONOUNS["english"]:
        if pronoun in text_lower:
            return True

    return False


def detect_urgency(text: str) -> Tuple[UrgencyLevel, List[str]]:
    """Detect urgency level and emotional indicators"""
    text_lower = text.lower()
    emotional_indicators = []

    # Check for distress first (highest priority)
    for keyword in URGENCY_KEYWORDS[UrgencyLevel.DISTRESSED]:
        if keyword in text_lower:
            emotional_indicators.append(keyword)
    if emotional_indicators:
        return UrgencyLevel.DISTRESSED, emotional_indicators

    # Check for anxiety
    emotional_indicators = []
    for keyword in URGENCY_KEYWORDS[UrgencyLevel.ANXIOUS]:
        if keyword in text_lower:
            emotional_indicators.append(keyword)
    if emotional_indicators:
        return UrgencyLevel.ANXIOUS, emotional_indicators

    # Check for confusion
    emotional_indicators = []
    for keyword in URGENCY_KEYWORDS[UrgencyLevel.CONFUSED]:
        if keyword in text_lower:
            emotional_indicators.append(keyword)
    if emotional_indicators:
        return UrgencyLevel.CONFUSED, emotional_indicators

    # Check for curiosity
    emotional_indicators = []
    for keyword in URGENCY_KEYWORDS[UrgencyLevel.CURIOUS]:
        if keyword in text_lower:
            emotional_indicators.append(keyword)
    if emotional_indicators:
        return UrgencyLevel.CURIOUS, emotional_indicators

    return UrgencyLevel.NEUTRAL, []


def detect_topics(text: str) -> List[QuestionTopic]:
    """Detect which topics the question is about"""
    text_lower = text.lower()
    topics = []

    # Check Big Five traits
    for topic, keywords in BIG_FIVE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(topic)
                break

    # Check DISC dimensions
    for topic, keywords in DISC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(topic)
                break

    # Check general topics
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(topic)
                break

    # Remove duplicates
    topics = list(set(topics))

    # Default to OTHER if no topics found
    if not topics:
        topics.append(QuestionTopic.OTHER)

    return topics


def detect_question_type(text: str, has_personal_pronoun: bool) -> QuestionType:
    """Detect the type of question"""
    text_lower = text.lower()

    # Check for personal report patterns
    for pattern in PERSONAL_REPORT_PATTERNS:
        if re.search(pattern, text_lower):
            return QuestionType.PERSONAL_REPORT

    # If has personal pronoun and mentions trait, likely personal
    if has_personal_pronoun:
        for keywords in BIG_FIVE_KEYWORDS.values():
            if any(k in text_lower for k in keywords):
                return QuestionType.PERSONAL_REPORT
        for keywords in DISC_KEYWORDS.values():
            if any(k in text_lower for k in keywords):
                return QuestionType.PERSONAL_REPORT

    # Check for career guidance
    if any(k in text_lower for k in TOPIC_KEYWORDS[QuestionTopic.CAREER]):
        if has_personal_pronoun or "passa" in text_lower or "suit" in text_lower:
            return QuestionType.CAREER_GUIDANCE

    # Check for relationship questions
    if any(k in text_lower for k in TOPIC_KEYWORDS[QuestionTopic.RELATIONSHIPS]):
        if has_personal_pronoun:
            return QuestionType.RELATIONSHIP

    # Check for personal growth
    if any(k in text_lower for k in TOPIC_KEYWORDS[QuestionTopic.PERSONAL_GROWTH]):
        if has_personal_pronoun:
            return QuestionType.PERSONAL_GROWTH

    # Check for comparison questions
    if ("jämför" in text_lower or "compare" in text_lower or
        "skillnad" in text_lower or "difference" in text_lower):
        return QuestionType.COMPARISON

    # Check for general psychology patterns
    for pattern in GENERAL_PSYCHOLOGY_PATTERNS:
        if re.search(pattern, text_lower):
            return QuestionType.GENERAL_PSYCHOLOGY

    # Check for small talk
    greetings = ["hej", "hello", "hi", "tack", "thanks", "thank you", "okej", "ok"]
    if any(g == text_lower.strip() or text_lower.strip().startswith(g) for g in greetings):
        if len(text_lower.split()) <= 3:
            return QuestionType.SMALL_TALK

    # Default to general psychology
    return QuestionType.GENERAL_PSYCHOLOGY


def is_trait_specific(topics: List[QuestionTopic]) -> bool:
    """Check if question is about specific personality traits"""
    trait_topics = list(BIG_FIVE_KEYWORDS.keys()) + list(DISC_KEYWORDS.keys())
    return any(topic in trait_topics for topic in topics)


def calculate_confidence(
    question_type: QuestionType,
    has_personal_pronoun: bool,
    topics: List[QuestionTopic],
    is_trait_specific: bool
) -> float:
    """Calculate confidence score for classification"""
    confidence = 0.5  # Base confidence

    # High confidence if personal pronoun + personal question type
    if has_personal_pronoun and question_type == QuestionType.PERSONAL_REPORT:
        confidence += 0.3

    # High confidence if specific topics detected
    if len(topics) > 1 and QuestionTopic.OTHER not in topics:
        confidence += 0.2

    # High confidence if trait-specific
    if is_trait_specific:
        confidence += 0.1

    # Cap at 0.95 (never 100% certain)
    return min(confidence, 0.95)


def classify_question(
    question: str,
    previous_question: Optional[str] = None,
    previous_answer: Optional[str] = None
) -> QuestionClassification:
    """
    Classify a user question into type, topics, urgency, etc.

    Args:
        question: The user's question
        previous_question: Previous question in conversation (for context)
        previous_answer: Previous answer (to detect clarifications)

    Returns:
        QuestionClassification with all detected attributes
    """

    # Detect personal pronouns
    has_personal_pronoun = contains_personal_pronoun(question)

    # Detect urgency and emotional state
    urgency, emotional_indicators = detect_urgency(question)

    # Detect topics
    topics = detect_topics(question)

    # Detect question type
    question_type = detect_question_type(question, has_personal_pronoun)

    # Check if clarification question
    if previous_answer and len(question.split()) < 20:
        clarification_words = ["vad menar", "what do you mean", "förstår inte",
                               "don't understand", "förklara", "explain"]
        if any(w in question.lower() for w in clarification_words):
            question_type = QuestionType.CLARIFICATION

    # Check if trait-specific
    trait_specific = is_trait_specific(topics)

    # Determine if profile is required
    requires_profile = (
        question_type in [
            QuestionType.PERSONAL_REPORT,
            QuestionType.CAREER_GUIDANCE,
            QuestionType.RELATIONSHIP,
            QuestionType.PERSONAL_GROWTH
        ] or has_personal_pronoun
    )

    # Calculate confidence
    confidence = calculate_confidence(
        question_type, has_personal_pronoun, topics, trait_specific
    )

    return QuestionClassification(
        question_type=question_type,
        topics=topics,
        urgency=urgency,
        is_personal_pronoun=has_personal_pronoun,
        confidence=confidence,
        emotional_indicators=emotional_indicators,
        requires_profile=requires_profile,
        is_trait_specific=trait_specific
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_classification_summary(classification: QuestionClassification) -> Dict:
    """Convert classification to dictionary for API response"""
    return {
        "question_type": classification.question_type.value,
        "topics": [t.value for t in classification.topics],
        "urgency": classification.urgency.value,
        "is_personal": classification.is_personal_pronoun,
        "confidence": round(classification.confidence, 2),
        "emotional_indicators": classification.emotional_indicators,
        "requires_profile": classification.requires_profile,
        "is_trait_specific": classification.is_trait_specific
    }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test cases
    test_questions = [
        "Varför fick jag så låg Conscientiousness?",
        "Vad är Big Five?",
        "Kan man ändra sin personlighet?",
        "Vilka jobb passar min profil?",
        "Vad betyder det att jag är hög i Openness men låg i Extraversion?",
        "Hur fungerar emotionell intelligens?",
        "Jag är orolig för mitt resultat",
        "Tack för hjälpen!",
        "Vad är skillnaden mellan DISC och Big Five?"
    ]

    print("=" * 80)
    print("QUESTION CLASSIFIER TEST")
    print("=" * 80)

    for q in test_questions:
        print(f"\nQuestion: {q}")
        classification = classify_question(q)
        summary = get_classification_summary(classification)

        print(f"  Type: {summary['question_type']}")
        print(f"  Topics: {', '.join(summary['topics'])}")
        print(f"  Urgency: {summary['urgency']}")
        print(f"  Requires Profile: {summary['requires_profile']}")
        print(f"  Confidence: {summary['confidence']}")
        if summary['emotional_indicators']:
            print(f"  Emotional Indicators: {', '.join(summary['emotional_indicators'])}")
