"""
Conversation Flow Manager
Manages natural dialogue state, context switching, and conversation memory
Ensures the chatbot doesn't sound robotic and maintains coherent conversation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


class ConversationStage(Enum):
    """Stages of conversation"""
    OPENING = "opening"  # Initial greeting
    EXPLORATION = "exploration"  # Understanding user's situation
    INSIGHT = "insight"  # Providing analysis and explanation
    ACTION = "action"  # Giving practical advice
    REFLECTION = "reflection"  # Helping user reflect
    CLOSING = "closing"  # Wrapping up


class QuestionType(Enum):
    """Types of questions user might ask"""
    ABOUT_REPORT = "about_report"  # "What does my score mean?"
    GENERAL_PSYCHOLOGY = "general"  # "What is Big Five?"
    CAREER_ADVICE = "career"  # "What jobs fit me?"
    RELATIONSHIP = "relationship"  # "How does this affect my relationships?"
    PERSONAL_GROWTH = "growth"  # "Can I change?"
    COMPARISON = "comparison"  # "Am I normal?"
    VALIDATION = "validation"  # "Is this bad?"
    OFF_TOPIC = "off_topic"  # Unrelated to personality


@dataclass
class ConversationContext:
    """Tracks conversation context and memory"""
    user_id: str
    conversation_id: str
    started_at: datetime = field(default_factory=datetime.now)
    current_stage: ConversationStage = ConversationStage.OPENING

    # Memory of conversation
    topics_discussed: List[str] = field(default_factory=list)
    traits_discussed: List[str] = field(default_factory=list)  # E, A, C, N, O
    questions_asked_count: int = 0
    insights_shared_count: int = 0

    # Track used phrases to avoid repetition
    used_opening_phrases: List[str] = field(default_factory=list)
    last_technique_used: Optional[str] = None

    # User state
    user_emotional_state: Optional[str] = None
    user_concerns: List[str] = field(default_factory=list)

    # Metadata
    message_count: int = 0
    last_message_timestamp: Optional[datetime] = None


class ConversationFlowManager:
    """
    Manages conversation flow to ensure natural, non-robotic dialogue
    Handles context switching, memory, and variation
    """

    def __init__(self, language: str = "sv"):
        self.language = language
        self.contexts: Dict[str, ConversationContext] = {}  # user_id -> context

    def get_or_create_context(self, user_id: str, conversation_id: str) -> ConversationContext:
        """Get existing conversation context or create new one"""

        key = f"{user_id}_{conversation_id}"

        if key not in self.contexts:
            self.contexts[key] = ConversationContext(
                user_id=user_id,
                conversation_id=conversation_id
            )

        return self.contexts[key]

    def classify_question(self, message: str) -> QuestionType:
        """
        Classify what type of question/message the user sent
        This helps determine appropriate response strategy
        """

        message_lower = message.lower()

        # About their report/scores
        if any(phrase in message_lower for phrase in [
            'min poäng', 'mitt resultat', 'min profil', 'mina scores',
            'my score', 'my result', 'my profile',
            'låg samvetsgrannhet', 'hög extraversion', 'low conscient', 'high extra',
            'vad betyder', 'what does', 'betyder det att jag', 'does it mean'
        ]):
            return QuestionType.ABOUT_REPORT

        # Career advice
        if any(phrase in message_lower for phrase in [
            'jobb', 'karriär', 'yrke', 'arbete', 'jobba',
            'job', 'career', 'work', 'profession',
            'passar för', 'suitable for', 'bra på', 'good at'
        ]):
            return QuestionType.CAREER_ADVICE

        # Relationship questions
        if any(phrase in message_lower for phrase in [
            'relation', 'partner', 'vän', 'familj', 'kärlek',
            'relationship', 'friend', 'family', 'love',
            'hur påverkar', 'how affects', 'tillsammans med'
        ]):
            return QuestionType.RELATIONSHIP

        # Personal growth
        if any(phrase in message_lower for phrase in [
            'ändra', 'utveckla', 'förbättra', 'träna',
            'change', 'develop', 'improve', 'train',
            'kan jag bli', 'can i become', 'är det möjligt', 'is it possible'
        ]):
            return QuestionType.PERSONAL_GROWTH

        # Comparison/normalization
        if any(phrase in message_lower for phrase in [
            'normalt', 'vanligt', 'andra', 'jämfört',
            'normal', 'common', 'others', 'compared',
            'är jag konstig', 'am i weird', 'de flesta', 'most people'
        ]):
            return QuestionType.COMPARISON

        # Seeking validation
        if any(phrase in message_lower for phrase in [
            'dåligt', 'fel på mig', 'problem', 'orolig',
            'bad', 'wrong with me', 'worried', 'concern',
            'betyder det att jag är', 'does that mean i am'
        ]):
            return QuestionType.VALIDATION

        # General psychology
        if any(phrase in message_lower for phrase in [
            'vad är big five', 'vad är disc', 'hur funkar',
            'what is big five', 'what is disc', 'how does',
            'berätta om', 'tell me about', 'förklara', 'explain'
        ]):
            return QuestionType.GENERAL_PSYCHOLOGY

        # Default: exploration
        return QuestionType.ABOUT_REPORT

    def detect_conversation_stage(
        self,
        context: ConversationContext,
        question_type: QuestionType,
        message: str
    ) -> ConversationStage:
        """
        Detect what stage of conversation we're in
        This helps adjust response style
        """

        # Opening stage: First few messages
        if context.message_count <= 2:
            return ConversationStage.OPENING

        # If user asks specific question after general chat
        if question_type in [QuestionType.CAREER_ADVICE, QuestionType.PERSONAL_GROWTH]:
            return ConversationStage.ACTION

        # If user is reflecting ("när jag tänker på det", "jag har märkt")
        if any(phrase in message.lower() for phrase in [
            'när jag tänker', 'jag har märkt', 'det stämmer',
            'when i think', 'i have noticed', 'that fits'
        ]):
            return ConversationStage.REFLECTION

        # If providing deep explanation
        if context.insights_shared_count >= 2:
            return ConversationStage.INSIGHT

        # Default: exploration
        return ConversationStage.EXPLORATION

    def should_ask_question(
        self,
        context: ConversationContext,
        messages_since_last_question: int = 0
    ) -> bool:
        """
        Decide if we should ask a follow-up question
        Avoids asking questions in every single response (feels interrogating)
        """

        # Don't ask question in opening
        if context.current_stage == ConversationStage.OPENING:
            return False

        # Ask question if we haven't for a while
        if messages_since_last_question >= 2:
            return True

        # Don't ask too many questions in a row
        if context.questions_asked_count >= 3:
            return False

        # 50% chance in exploration stage
        if context.current_stage == ConversationStage.EXPLORATION:
            return context.message_count % 2 == 0

        return False

    def get_varied_transition_phrase(
        self,
        context: ConversationContext,
        transition_type: str,
        language: str = "sv"
    ) -> str:
        """
        Get varied transition phrases to avoid sounding robotic

        Types: 'agreement', 'transition', 'reflection', 'insight'
        """

        if language == "sv":
            phrases = {
                'agreement': [
                    "Absolut.",
                    "Helt rätt.",
                    "Precis.",
                    "Ja, exakt.",
                    "Mmm, det stämmer.",
                ],
                'transition': [
                    "Låt mig tänka på det här...",
                    "Intressant fråga.",
                    "Det du tar upp är viktigt.",
                    "Bra att du frågar om det.",
                    "Hmm, det här är en klok fundering.",
                ],
                'reflection': [
                    "Om jag förstår dig rätt...",
                    "Det jag hör är...",
                    "Så du undrar...",
                    "Det låter som att...",
                    "Vad jag uppfattar är att...",
                ],
                'insight': [
                    "Det som händer här är...",
                    "En sak att tänka på är...",
                    "Det intressanta med din profil är...",
                    "Något jag märker är...",
                    "Ur ett psykologiskt perspektiv...",
                ]
            }
        else:  # English
            phrases = {
                'agreement': [
                    "Absolutely.",
                    "Exactly right.",
                    "Precisely.",
                    "Yes, exactly.",
                    "Mmm, that's true.",
                ],
                'transition': [
                    "Let me think about that...",
                    "Interesting question.",
                    "What you're bringing up is important.",
                    "Good that you ask about that.",
                    "Hmm, that's a thoughtful question.",
                ],
                'reflection': [
                    "If I understand you correctly...",
                    "What I hear is...",
                    "So you're wondering...",
                    "It sounds like...",
                    "What I'm picking up is that...",
                ],
                'insight': [
                    "What's happening here is...",
                    "One thing to consider is...",
                    "What's interesting about your profile is...",
                    "Something I notice is...",
                    "From a psychological perspective...",
                ]
            }

        available_phrases = phrases.get(transition_type, phrases['transition'])

        # Filter out recently used phrases
        unused_phrases = [p for p in available_phrases if p not in context.used_opening_phrases]

        if not unused_phrases:
            # Reset if all have been used
            context.used_opening_phrases.clear()
            unused_phrases = available_phrases

        # Select phrase (could add randomization here)
        selected = unused_phrases[context.message_count % len(unused_phrases)]
        context.used_opening_phrases.append(selected)

        # Keep only last 10 to avoid list growing forever
        if len(context.used_opening_phrases) > 10:
            context.used_opening_phrases = context.used_opening_phrases[-10:]

        return selected

    def build_response_guidance(
        self,
        context: ConversationContext,
        question_type: QuestionType,
        emotional_state: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Build guidance for the AI on how to respond
        This is added to the system prompt to ensure appropriate response
        """

        guidance = {
            'stage': context.current_stage.value,
            'question_type': question_type.value,
            'should_ask_question': self.should_ask_question(context),
            'topics_to_avoid_repeating': context.topics_discussed[-3:],  # Last 3
            'emotional_tone': emotional_state,
            'response_length': 'medium',  # short, medium, long
            'include_example': False,
            'include_research': False,
        }

        # Adjust based on question type
        if question_type == QuestionType.VALIDATION:
            guidance['response_length'] = 'medium'
            guidance['emotional_tone'] = 'warm_and_validating'
            guidance['should_ask_question'] = True  # Help them explore

        elif question_type == QuestionType.CAREER_ADVICE:
            guidance['response_length'] = 'long'
            guidance['include_example'] = True
            guidance['include_research'] = True

        elif question_type == QuestionType.GENERAL_PSYCHOLOGY:
            guidance['response_length'] = 'medium'
            guidance['include_research'] = True

        elif question_type == QuestionType.PERSONAL_GROWTH:
            guidance['response_length'] = 'long'
            guidance['include_example'] = True

        # Adjust based on stage
        if context.current_stage == ConversationStage.OPENING:
            guidance['response_length'] = 'short'

        elif context.current_stage == ConversationStage.REFLECTION:
            guidance['should_ask_question'] = True
            guidance['response_length'] = 'medium'

        return guidance

    def update_context_after_message(
        self,
        context: ConversationContext,
        user_message: str,
        question_type: QuestionType,
        traits_mentioned: List[str] = None
    ):
        """Update conversation context after processing a message"""

        context.message_count += 1
        context.last_message_timestamp = datetime.now()

        # Track topics
        topic = question_type.value
        if topic not in context.topics_discussed:
            context.topics_discussed.append(topic)

        # Track traits discussed
        if traits_mentioned:
            for trait in traits_mentioned:
                if trait not in context.traits_discussed:
                    context.traits_discussed.append(trait)

        # Update stage
        new_stage = self.detect_conversation_stage(context, question_type, user_message)
        if new_stage != context.current_stage:
            context.current_stage = new_stage

    def extract_traits_from_message(self, message: str) -> List[str]:
        """Extract which Big Five traits user is asking about"""

        traits = []
        message_lower = message.lower()

        trait_keywords = {
            'E': ['extraversion', 'extravert', 'introvert', 'introversion', 'social', 'utåtriktad'],
            'A': ['vänlighet', 'agreeableness', 'empati', 'samarbete', 'empath'],
            'C': ['samvetsgrannhet', 'conscientiousness', 'organisation', 'struktur', 'planering'],
            'N': ['neuroticism', 'emotionell stabilitet', 'ångest', 'stress', 'oro', 'känslomässig'],
            'O': ['öppenhet', 'openness', 'kreativ', 'nyfiken', 'kreativitet']
        }

        for trait, keywords in trait_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                traits.append(trait)

        return traits

    def generate_contextual_system_addition(
        self,
        context: ConversationContext,
        guidance: Dict[str, any],
        language: str = "sv"
    ) -> str:
        """
        Generate additional system prompt based on conversation context
        This is appended to the base psychologist persona prompt
        """

        if language == "sv":
            additions = f"""
**KONVERSATIONSKONTEXT (använd detta för att anpassa ditt svar):**

- **Samtalsstadium**: {context.current_stage.value}
- **Frågetyp**: {guidance['question_type']}
- **Antal meddelanden**: {context.message_count}
- **Tidigare diskuterade ämnen**: {', '.join(context.topics_discussed[-3:]) if context.topics_discussed else 'Inga än'}
- **Tidigare diskuterade drag**: {', '.join(context.traits_discussed) if context.traits_discussed else 'Inga än'}

**SVARSINSTRUKTIONER för detta meddelande:**

1. **Längd**: {guidance['response_length']} (short = 2-3 meningar, medium = 1 paragraf, long = 2-3 paragrafer)

2. **Fråga användaren?**: {'JA - avsluta med en reflekterande fråga' if guidance['should_ask_question'] else 'NEJ - avsluta med en insikt eller uppmuntran'}

3. **Inkludera exempel?**: {'JA - ge konkret exempel' if guidance['include_example'] else 'NEJ'}

4. **Inkludera forskning?**: {'JA - referera till forskning' if guidance['include_research'] else 'NEJ'}

5. **Emotional ton**: {guidance.get('emotional_tone', 'neutral_professional')}

6. **VIKTIGT - Undvik upprepning**:
   - Du har redan pratat om: {', '.join(context.topics_discussed[-3:]) if context.topics_discussed else 'inget'}
   - Använd INTE fraser som du nyligen använt
   - Variera ditt språk - säg INTE "Det är intressant att..." varje gång
   - Var naturlig och mänsklig, inte robotisk

**Svara nu enligt ovanstående riktlinjer:**
"""
        else:  # English
            additions = f"""
**CONVERSATION CONTEXT (use this to adapt your response):**

- **Conversation stage**: {context.current_stage.value}
- **Question type**: {guidance['question_type']}
- **Message count**: {context.message_count}
- **Previously discussed topics**: {', '.join(context.topics_discussed[-3:]) if context.topics_discussed else 'None yet'}
- **Previously discussed traits**: {', '.join(context.traits_discussed) if context.traits_discussed else 'None yet'}

**RESPONSE INSTRUCTIONS for this message:**

1. **Length**: {guidance['response_length']} (short = 2-3 sentences, medium = 1 paragraph, long = 2-3 paragraphs)

2. **Ask user question?**: {'YES - end with reflective question' if guidance['should_ask_question'] else 'NO - end with insight or encouragement'}

3. **Include example?**: {'YES - give concrete example' if guidance['include_example'] else 'NO'}

4. **Include research?**: {'YES - reference research' if guidance['include_research'] else 'NO'}

5. **Emotional tone**: {guidance.get('emotional_tone', 'neutral_professional')}

6. **IMPORTANT - Avoid repetition**:
   - You've already talked about: {', '.join(context.topics_discussed[-3:]) if context.topics_discussed else 'nothing'}
   - Do NOT use phrases you've recently used
   - Vary your language - don't say "That's interesting that..." every time
   - Be natural and human, not robotic

**Respond now according to the above guidelines:**
"""

        return additions

    def should_show_warmth(self, question_type: QuestionType) -> bool:
        """Determine if response should be extra warm/validating"""

        warm_types = [
            QuestionType.VALIDATION,
            QuestionType.COMPARISON,
            QuestionType.PERSONAL_GROWTH
        ]

        return question_type in warm_types


# Example usage
if __name__ == "__main__":
    manager = ConversationFlowManager(language="sv")

    # Simulate conversation
    user_id = "test_user"
    conv_id = "conv_001"

    test_messages = [
        "Hej! Jag har gjort testet och vill förstå mina resultat.",
        "Jag fick låg samvetsgrannhet. Betyder det att jag är lat?",
        "Hur kan jag bli mer organiserad?",
        "Vilka jobb passar mig med min profil?",
    ]

    print("=== CONVERSATION FLOW TEST ===\n")

    for i, msg in enumerate(test_messages):
        print(f"\n--- Message {i+1} ---")
        print(f"USER: {msg}")

        context = manager.get_or_create_context(user_id, conv_id)
        question_type = manager.classify_question(msg)
        traits = manager.extract_traits_from_message(msg)

        print(f"CLASSIFIED AS: {question_type.value}")
        print(f"STAGE: {context.current_stage.value}")
        print(f"TRAITS MENTIONED: {traits if traits else 'None'}")

        guidance = manager.build_response_guidance(context, question_type)
        print(f"SHOULD ASK QUESTION: {guidance['should_ask_question']}")
        print(f"RESPONSE LENGTH: {guidance['response_length']}")

        # Update context
        manager.update_context_after_message(context, msg, question_type, traits)

        print(f"TOPICS DISCUSSED SO FAR: {context.topics_discussed}")
