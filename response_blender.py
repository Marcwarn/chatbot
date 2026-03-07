"""
Response Blender - Intelligent Contextual Response System
Combines personal report context, general knowledge, and conversation history
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

from question_classifier import (
    classify_question, QuestionClassification, QuestionType,
    UrgencyLevel, get_classification_summary
)
from context_manager import (
    ContextManager, ConversationContext, UserProfile, ConversationMessage, MoodState
)
from report_explainer import ReportExplainer, generate_personalized_examples
from psychology_qa_system import PsychologyQA, format_answer_with_sources


@dataclass
class ResponseStrategy:
    """Strategy for generating response"""
    primary_source: str  # "personal_report", "general_knowledge", "blended"
    include_profile_context: bool
    include_general_knowledge: bool
    tone: str  # "empathetic", "educational", "casual", "reassuring"
    add_examples: bool
    add_follow_up: bool


# ============================================================================
# RESPONSE BLENDER CLASS
# ============================================================================

class ResponseBlender:
    """
    Main orchestrator for intelligent contextual responses
    Decides how to blend different knowledge sources based on context
    """

    def __init__(self, db_session=None, language: str = "sv"):
        """
        Initialize response blender

        Args:
            db_session: Database session for loading user data
            language: Language code (sv or en)
        """
        self.language = language
        self.context_manager = ContextManager(db_session)
        self.report_explainer = ReportExplainer(language)
        self.psychology_qa = PsychologyQA(language)

    def generate_response(
        self,
        user_id: str,
        question: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent, contextual response to user question

        Args:
            user_id: User ID
            question: User's question
            session_id: Optional session ID
            conversation_history: Optional conversation history

        Returns:
            Dict with response and metadata
        """

        # 1. CLASSIFY QUESTION
        context = self.context_manager.get_or_create_context(
            user_id, session_id, conversation_history
        )

        # Get previous messages for context
        last_user_msg = context.get_last_user_message()
        last_assistant_msg = context.get_last_assistant_message()

        classification = classify_question(
            question,
            previous_question=last_user_msg.content if last_user_msg else None,
            previous_answer=last_assistant_msg.content if last_assistant_msg else None
        )

        # Update context with classification
        self.context_manager.update_context_with_classification(
            context, classification, question
        )

        # 2. DETERMINE RESPONSE STRATEGY
        strategy = self._determine_strategy(classification, context)

        # 3. GENERATE RESPONSE
        response_text = self._generate_response_text(
            question, classification, context, strategy
        )

        # 4. ADD ASSISTANT MESSAGE TO HISTORY
        assistant_msg = ConversationMessage(
            role="assistant",
            content=response_text,
            timestamp=ConversationMessage.__dataclass_fields__['timestamp'].default_factory(),
            topics=[t.value for t in classification.topics]
        )
        context.add_message(assistant_msg)

        # 5. PREPARE RESPONSE
        return {
            "response": response_text,
            "classification": get_classification_summary(classification),
            "strategy": {
                "primary_source": strategy.primary_source,
                "tone": strategy.tone
            },
            "context": {
                "has_profile": context.user_profile is not None and context.user_profile.has_any_profile(),
                "mood": context.current_mood.value,
                "engagement": context.engagement_level
            }
        }

    def _determine_strategy(
        self,
        classification: QuestionClassification,
        context: ConversationContext
    ) -> ResponseStrategy:
        """
        Determine response strategy based on question and context

        Args:
            classification: Question classification
            context: Conversation context

        Returns:
            ResponseStrategy
        """

        # Handle small talk
        if classification.question_type == QuestionType.SMALL_TALK:
            return ResponseStrategy(
                primary_source="none",
                include_profile_context=False,
                include_general_knowledge=False,
                tone="casual",
                add_examples=False,
                add_follow_up=True
            )

        # Handle personal report questions
        if classification.question_type == QuestionType.PERSONAL_REPORT:
            return ResponseStrategy(
                primary_source="personal_report",
                include_profile_context=True,
                include_general_knowledge=False,
                tone="empathetic" if classification.urgency in [UrgencyLevel.ANXIOUS, UrgencyLevel.DISTRESSED] else "educational",
                add_examples=True,
                add_follow_up=True
            )

        # Handle general psychology questions
        if classification.question_type == QuestionType.GENERAL_PSYCHOLOGY:
            # Check if user has profile - if so, blend general + personal
            has_profile = context.user_profile and context.user_profile.has_any_profile()

            return ResponseStrategy(
                primary_source="blended" if has_profile else "general_knowledge",
                include_profile_context=has_profile,
                include_general_knowledge=True,
                tone="educational",
                add_examples=has_profile,
                add_follow_up=True
            )

        # Handle career/relationship questions
        if classification.question_type in [QuestionType.CAREER_GUIDANCE, QuestionType.RELATIONSHIP]:
            return ResponseStrategy(
                primary_source="personal_report",
                include_profile_context=True,
                include_general_knowledge=True,
                tone="empathetic",
                add_examples=True,
                add_follow_up=True
            )

        # Handle comparisons
        if classification.question_type == QuestionType.COMPARISON:
            return ResponseStrategy(
                primary_source="blended",
                include_profile_context=True,
                include_general_knowledge=True,
                tone="educational",
                add_examples=False,
                add_follow_up=False
            )

        # Default strategy
        return ResponseStrategy(
            primary_source="general_knowledge",
            include_profile_context=False,
            include_general_knowledge=True,
            tone="educational",
            add_examples=False,
            add_follow_up=True
        )

    def _generate_response_text(
        self,
        question: str,
        classification: QuestionClassification,
        context: ConversationContext,
        strategy: ResponseStrategy
    ) -> str:
        """
        Generate the actual response text

        Args:
            question: User's question
            classification: Question classification
            context: Conversation context
            strategy: Response strategy

        Returns:
            Response text
        """

        # SMALL TALK
        if classification.question_type == QuestionType.SMALL_TALK:
            return self._handle_small_talk(question, context)

        # PERSONAL REPORT QUESTIONS
        if strategy.primary_source == "personal_report":
            return self._handle_personal_report_question(
                question, classification, context, strategy
            )

        # GENERAL KNOWLEDGE QUESTIONS
        if strategy.primary_source == "general_knowledge":
            return self._handle_general_question(
                question, classification, context, strategy
            )

        # BLENDED RESPONSES
        if strategy.primary_source == "blended":
            return self._handle_blended_question(
                question, classification, context, strategy
            )

        # FALLBACK
        return self._generate_fallback_response(classification, context)

    def _handle_small_talk(self, question: str, context: ConversationContext) -> str:
        """Handle small talk and greetings"""
        question_lower = question.lower()

        # Greetings
        if any(g in question_lower for g in ["hej", "hello", "hi", "hallå"]):
            if context.user_profile and context.user_profile.has_any_profile():
                return f"Hej! Jag är här för att hjälpa dig förstå din personlighetsprofil och svara på frågor om personlighetsutveckling. Vad funderar du på?"
            else:
                return "Hej! Jag är din personlighetscoach. Jag kan hjälpa dig förstå Big Five och DISC, samt svara på frågor om personlighetsutveckling. Vad kan jag hjälpa dig med?"

        # Thanks
        if any(t in question_lower for t in ["tack", "thank", "tackar"]):
            return "Varsågod! Har du fler frågor är det bara att ställa dem. Jag är här för att hjälpa dig!"

        # Generic
        return "Jag förstår inte riktigt. Kan du ställa en specifik fråga om din personlighetsprofil eller om personlighetspsykologi?"

    def _handle_personal_report_question(
        self,
        question: str,
        classification: QuestionClassification,
        context: ConversationContext,
        strategy: ResponseStrategy
    ) -> str:
        """Handle questions about user's personal assessment results"""

        # Check if user has profile
        if not context.user_profile or not context.user_profile.has_any_profile():
            return """
Jag ser att du ännu inte har genomfört något personlighetstest. För att jag ska kunna ge dig personliga råd behöver du först göra antingen Big Five eller DISC-testet.

Vill du veta mer om testterna kan jag förklara vad de mäter och varför de är användbara!
            """.strip()

        profile = context.user_profile

        # Detect which trait user is asking about
        trait = self._detect_trait_in_question(question)

        # Handle urgency with empathy
        response_parts = []

        if classification.urgency == UrgencyLevel.DISTRESSED:
            response_parts.append("Jag hör att du känner oro kring ditt resultat. Låt mig försäkra dig om att det inte finns några 'dåliga' personlighetsprofiler - varje profil har sina unika styrkor.")
            response_parts.append("")

        # If specific trait mentioned
        if trait and profile.big_five_scores and trait in profile.big_five_scores:
            score = profile.big_five_scores[trait]
            explanation = self.report_explainer.explain_single_trait(trait, score, "big_five")

            # Check if asking "why" question
            if any(w in question.lower() for w in ["varför", "why", "hur kommer det sig"]):
                why_answer = self.report_explainer.answer_why_score(trait, score, "big_five")
                response_parts.append(why_answer)
            else:
                # General explanation
                response_parts.append(f"**{explanation['trait_name']} - {explanation['percentile_explanation']}**")
                response_parts.append("")
                response_parts.append(explanation['description'])

                if 'career_suggestions' in explanation:
                    response_parts.append("")
                    response_parts.append(f"**Karriärområden som ofta passar:** {explanation['career_suggestions']}")

                if strategy.add_examples:
                    examples = generate_personalized_examples(trait, score, "work", self.language)
                    if examples:
                        response_parts.append("")
                        response_parts.append("**Konkreta exempel från arbetslivet:**")
                        for ex in examples:
                            response_parts.append(f"- {ex}")

        # If asking about multiple traits or general profile
        else:
            if profile.big_five_scores:
                full_explanation = self.report_explainer.explain_full_profile(
                    profile.big_five_scores, "big_five"
                )
                response_parts.append(full_explanation['summary'])
                response_parts.append("")
                response_parts.append("Vill du veta mer om något specifikt drag? Jag kan förklara i detalj!")

        # Add follow-up if needed
        if strategy.add_follow_up and classification.urgency != UrgencyLevel.DISTRESSED:
            response_parts.append("")
            response_parts.append("Har du fler frågor om din profil?")

        return "\n".join(response_parts)

    def _handle_general_question(
        self,
        question: str,
        classification: QuestionClassification,
        context: ConversationContext,
        strategy: ResponseStrategy
    ) -> str:
        """Handle general psychology questions"""

        # Try to answer from knowledge base
        qa_result = self.psychology_qa.answer_question(question)

        if qa_result:
            response_parts = [qa_result['answer']]

            # Add sources
            if qa_result.get('sources'):
                response_parts.append("")
                response_parts.append("**Källor:**")
                for source in qa_result['sources']:
                    response_parts.append(f"- {source}")

            # Suggest follow-ups
            if strategy.add_follow_up:
                follow_ups = self.psychology_qa.suggest_follow_up_questions(qa_result['topic'])
                if follow_ups:
                    response_parts.append("")
                    response_parts.append("**Du kanske också undrar:**")
                    for fq in follow_ups[:2]:  # Limit to 2
                        response_parts.append(f"- {fq}")

            return "\n".join(response_parts)

        # Can't answer - out of scope
        return self.psychology_qa.get_out_of_scope_response()

    def _handle_blended_question(
        self,
        question: str,
        classification: QuestionClassification,
        context: ConversationContext,
        strategy: ResponseStrategy
    ) -> str:
        """Handle questions requiring both general knowledge and personal context"""

        response_parts = []

        # Start with general knowledge
        qa_result = self.psychology_qa.answer_question(question)

        if qa_result:
            response_parts.append(qa_result['answer'])
        else:
            # Generic educational response
            response_parts.append("Det är en intressant fråga om personlighet och utveckling.")

        # Add personal context if available
        if context.user_profile and context.user_profile.has_any_profile():
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("")

            # Connect to their profile
            profile_connection = self._connect_to_profile(
                question, classification, context.user_profile
            )

            if profile_connection:
                response_parts.append("**Kopplat till din profil:**")
                response_parts.append(profile_connection)

        return "\n".join(response_parts)

    def _connect_to_profile(
        self,
        question: str,
        classification: QuestionClassification,
        profile: UserProfile
    ) -> str:
        """
        Connect general knowledge to user's specific profile

        Args:
            question: User's question
            classification: Question classification
            profile: User's profile

        Returns:
            Personalized connection text
        """
        if not profile.big_five_scores:
            return ""

        scores = profile.big_five_scores
        connections = []

        # Emotional intelligence connection
        if "emotionell intelligens" in question.lower() or "eq" in question.lower():
            if scores.get("A", 50) >= 65:
                connections.append("Med din höga Vänlighet (Agreeableness) har du förmodligen redan god social medvetenhet och empati - viktiga delar av EQ.")
            if scores.get("N", 50) <= 35:
                connections.append("Din emotionella stabilitet (låg Neuroticism) hjälper dig att hantera stress och bibehålla balans - en viktig del av emotionell intelligens.")

        # Personality change connection
        if "ändra" in question.lower() or "förändra" in question.lower():
            if scores.get("O", 50) >= 65:
                connections.append("Med din höga Öppenhet är du förmodligen mer benägen till personlig utveckling och förändring än genomsnittet - du är nyfiken och öppen för nya perspektiv.")
            if scores.get("C", 50) >= 65:
                connections.append("Din höga Samvetsgrannhet ger dig disciplin och uthållighet - viktiga egenskaper för att genomföra personlighetsförändringar över tid.")

        # Stress/anxiety connection
        if "stress" in question.lower() or "ångest" in question.lower():
            if scores.get("N", 50) >= 65:
                connections.append("Med din höga Neuroticism (emotionell känslighet) är du mer benägen att känna stress och oro än genomsnittet. Detta är normalt, men viktigt att du utvecklar goda stresshanteringsverktyg.")
            if scores.get("N", 50) <= 35:
                connections.append("Din emotionella stabilitet (låg Neuroticism) gör att du hanterar stress bättre än de flesta - du är lugn under press.")

        # Leadership connection
        if "ledarskap" in question.lower() or "ledare" in question.lower():
            if scores.get("E", 50) >= 65 and scores.get("C", 50) >= 65:
                connections.append("Din kombination av hög Extraversion och Samvetsgrannhet är idealisk för ledarskap - du är både engagerande och pålitlig.")

        return "\n\n".join(connections) if connections else ""

    def _detect_trait_in_question(self, question: str) -> Optional[str]:
        """
        Detect which personality trait the question is about

        Args:
            question: User's question

        Returns:
            Trait code (E, A, C, N, O) or None
        """
        question_lower = question.lower()

        trait_keywords = {
            "E": ["extraversion", "extrovert", "introvert", "social", "utåtriktad"],
            "A": ["vänlighet", "agreeableness", "agreeable", "empatisk", "omtänksam"],
            "C": ["samvetsgrann", "conscientiousness", "organiserad", "noggrann"],
            "N": ["neuroticism", "neurotisk", "oro", "ångest", "emotionell stabilitet"],
            "O": ["öppenhet", "openness", "kreativ", "nyfiken"]
        }

        for trait, keywords in trait_keywords.items():
            if any(kw in question_lower for kw in keywords):
                return trait

        return None

    def _generate_fallback_response(
        self,
        classification: QuestionClassification,
        context: ConversationContext
    ) -> str:
        """Generate fallback response when can't handle question properly"""

        if self.language == "sv":
            return """
Jag är inte helt säker på hur jag ska svara på den frågan. Jag är specialiserad på:

- Big Five och DISC personlighetsmodeller
- Din personliga assessment-rapport (om du har gjort testet)
- Personlighetsutveckling och förändring
- Karriärvägledning baserad på personlighet

Kan du omformulera din fråga eller ställa en fråga inom dessa områden?
            """.strip()

        return "I'm not sure how to answer that question. Could you rephrase it?"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_chat_response(
    user_id: str,
    question: str,
    db_session=None,
    session_id: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None,
    language: str = "sv"
) -> Dict[str, Any]:
    """
    High-level function to create chat response

    Args:
        user_id: User ID
        question: User's question
        db_session: Database session
        session_id: Session ID
        conversation_history: Conversation history
        language: Language code

    Returns:
        Response dict with answer and metadata
    """
    blender = ResponseBlender(db_session, language)
    return blender.generate_response(
        user_id, question, session_id, conversation_history
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from datetime import datetime

    print("=" * 80)
    print("RESPONSE BLENDER TEST")
    print("=" * 80)

    # Create test profile
    from context_manager import UserProfile

    test_profile = UserProfile(
        user_id="test_user",
        big_five_scores={"E": 25, "A": 70, "C": 30, "N": 65, "O": 80},
        big_five_completed=True,
        language="sv"
    )

    # Create blender
    blender = ResponseBlender(db_session=None, language="sv")

    # Inject test profile into context
    context = blender.context_manager.get_or_create_context("test_user")
    context.user_profile = test_profile

    # Test questions
    test_questions = [
        "Varför fick jag så låg Conscientiousness?",
        "Vad är Big Five?",
        "Kan man ändra sin personlighet?",
        "Vilka jobb passar min profil?",
        "Hej!",
        "Tack för hjälpen!"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {question}")
        print("-" * 80)

        result = blender.generate_response(
            user_id="test_user",
            question=question,
            conversation_history=[]
        )

        print(f"\nResponse:\n{result['response']}")
        print(f"\nClassification: {result['classification']['question_type']}")
        print(f"Strategy: {result['strategy']['primary_source']} ({result['strategy']['tone']})")
        print(f"Has Profile: {result['context']['has_profile']}")

    print("\n" + "=" * 80)
    print("✅ Response Blender test completed!")
