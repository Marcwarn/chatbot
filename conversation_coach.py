"""
Conversation Coach - Enhanced Personality Coaching System
Integrates psychologist persona, empathy engine, knowledge base, and conversation flow
to create genuinely human-feeling psychological coaching conversations
"""

from anthropic import Anthropic
from typing import List, Dict, Optional, Tuple
import os

# Import our advanced components
from psychologist_persona import (
    PsychologistPersona,
    Language,
    PersonaContext,
    ConversationalTechnique
)
from empathy_engine import EmpathyEngine, EmotionalState, EmotionalTone
from psychology_knowledge_base import PsychologyKnowledgeBase
from conversation_flow import (
    ConversationFlowManager,
    ConversationContext,
    QuestionType,
    ConversationStage
)


class ConversationCoach:
    """
    Advanced conversational AI coach that feels like talking to a real,
    empathetic human psychologist
    """

    def __init__(
        self,
        anthropic_client: Optional[Anthropic] = None,
        language: str = "sv"
    ):
        self.anthropic_client = anthropic_client
        self.language = Language.SWEDISH if language == "sv" else Language.ENGLISH

        # Initialize all components
        self.persona = PsychologistPersona(self.language)
        self.empathy_engine = EmpathyEngine(language)
        self.knowledge_base = PsychologyKnowledgeBase(language)
        self.flow_manager = ConversationFlowManager(language)

    def chat(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        conversation_history: List[Dict[str, str]],
        profile_scores: Optional[Dict[str, float]] = None,
        personalized_report: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Main chat method that orchestrates all components to generate
        a warm, empathetic, psychologist-like response
        """

        if not self.anthropic_client:
            return "Chat-funktionen kräver API-nyckel. Kontakta administratör." if self.language == Language.SWEDISH else "Chat feature requires API key."

        # Step 1: Get or create conversation context
        context = self.flow_manager.get_or_create_context(user_id, conversation_id)

        # Step 2: Detect emotional state in user message
        emotional_state = self.empathy_engine.detect_emotion(message)

        # Step 3: Classify question type
        question_type = self.flow_manager.classify_question(message)

        # Step 4: Extract which traits user is asking about
        traits_mentioned = self.flow_manager.extract_traits_from_message(message)

        # Step 5: Build response guidance
        guidance = self.flow_manager.build_response_guidance(
            context,
            question_type,
            emotional_state.primary_tone.value
        )

        # Step 6: Create comprehensive system prompt
        system_prompt = self._build_system_prompt(
            context=context,
            guidance=guidance,
            emotional_state=emotional_state,
            profile_scores=profile_scores,
            personalized_report=personalized_report,
            question_type=question_type,
            traits_mentioned=traits_mentioned
        )

        # Step 7: Build message history
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        # Step 8: Get response from AI
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.8,  # Higher for more natural, varied responses
                system=system_prompt,
                messages=messages
            )

            response_text = response.content[0].text

            # Step 9: Update conversation context
            self.flow_manager.update_context_after_message(
                context,
                message,
                question_type,
                traits_mentioned
            )

            # Track that we've shared insight
            if question_type in [QuestionType.ABOUT_REPORT, QuestionType.CAREER_ADVICE]:
                context.insights_shared_count += 1

            # Track if we asked a question
            if '?' in response_text:
                context.questions_asked_count += 1
            else:
                context.questions_asked_count = 0  # Reset counter

            return response_text

        except Exception as e:
            print(f"Chat error: {e}")
            error_msg = "Tyvärr uppstod ett fel. Försök igen om en stund." if self.language == Language.SWEDISH else "Sorry, an error occurred. Please try again."
            return error_msg

    def _build_system_prompt(
        self,
        context: ConversationContext,
        guidance: Dict[str, any],
        emotional_state: EmotionalState,
        profile_scores: Optional[Dict[str, float]],
        personalized_report: Optional[Dict[str, any]],
        question_type: QuestionType,
        traits_mentioned: List[str]
    ) -> str:
        """
        Build comprehensive system prompt that includes:
        - Base psychologist persona
        - User's personality profile
        - Emotional context
        - Conversation flow guidance
        - Specific knowledge relevant to question
        """

        # Start with base persona prompt
        base_prompt = self.persona.create_system_prompt(
            user_scores=profile_scores,
            user_report=personalized_report,
            language=self.language
        )

        # Add empathy guidance based on emotional state
        empathy_guidance = self._build_empathy_guidance(emotional_state)

        # Add conversation flow context
        flow_guidance = self.flow_manager.generate_contextual_system_addition(
            context,
            guidance,
            "sv" if self.language == Language.SWEDISH else "en"
        )

        # Add specific knowledge if needed
        knowledge_addition = self._build_knowledge_addition(
            question_type,
            traits_mentioned,
            profile_scores
        )

        # Combine all parts
        full_prompt = f"""{base_prompt}

{empathy_guidance}

{knowledge_addition}

{flow_guidance}
"""

        return full_prompt

    def _build_empathy_guidance(self, emotional_state: EmotionalState) -> str:
        """Build empathy-specific guidance based on detected emotion"""

        if emotional_state.primary_tone == EmotionalTone.NEUTRAL:
            return ""

        empathetic_opening = self.empathy_engine.generate_empathetic_opening(
            emotional_state,
            "sv" if self.language == Language.SWEDISH else "en"
        )

        templates = self.empathy_engine.get_empathy_response_template(
            emotional_state,
            "sv" if self.language == Language.SWEDISH else "en"
        )

        if self.language == Language.SWEDISH:
            guidance = f"""
**EMOTIONELL KONTEXT:**
Användaren verkar känna: **{emotional_state.primary_tone.value}** (intensitet: {emotional_state.intensity.value})

**Rekommenderad empatisk respons:**
- Börja med validering: "{empathetic_opening}"
- Använd dessa tekniker: {', '.join(templates.keys())}
- Var särskilt varm och stödjande i denna situation
- Normalisera deras känslor om de känner sig oroliga eller besvikna
"""
        else:
            guidance = f"""
**EMOTIONAL CONTEXT:**
User seems to feel: **{emotional_state.primary_tone.value}** (intensity: {emotional_state.intensity.value})

**Recommended empathic response:**
- Start with validation: "{empathetic_opening}"
- Use these techniques: {', '.join(templates.keys())}
- Be especially warm and supportive in this situation
- Normalize their feelings if they seem worried or disappointed
"""

        return guidance

    def _build_knowledge_addition(
        self,
        question_type: QuestionType,
        traits_mentioned: List[str],
        profile_scores: Optional[Dict[str, float]]
    ) -> str:
        """Add relevant psychology knowledge based on question type"""

        knowledge = ""
        lang = "sv" if self.language == Language.SWEDISH else "en"

        # Add trait explanations if specific traits mentioned
        if traits_mentioned and profile_scores:
            if self.language == Language.SWEDISH:
                knowledge += "\n**RELEVANT TRAIT-KUNSKAP att referera till vid behov:**\n"
            else:
                knowledge += "\n**RELEVANT TRAIT KNOWLEDGE to reference if needed:**\n"

            for trait in traits_mentioned[:2]:  # Max 2 to avoid overwhelming
                score = profile_scores.get(trait, 50)
                explanation = self.knowledge_base.get_trait_explanation(trait, score, lang)

                if explanation:
                    knowledge += f"\n**{explanation.get('name', trait)}**: "
                    knowledge += explanation.get('description', '')[:500] + "...\n"

        # Add career knowledge if career question
        if question_type == QuestionType.CAREER_ADVICE and profile_scores:
            if self.language == Language.SWEDISH:
                knowledge += "\n**KARRIÄRPASSNINGAR (använd max 3-4 exempel):**\n"
            else:
                knowledge += "\n**CAREER MATCHES (use max 3-4 examples):**\n"

            careers = self.knowledge_base.get_career_recommendations(profile_scores, lang)
            for career in careers[:4]:
                knowledge += f"- {career.career} (fit: {career.fit_score:.0%}): {career.reasoning[:200]}...\n"

        # Add relationship knowledge if relationship question
        if question_type == QuestionType.RELATIONSHIP and profile_scores:
            insight = self.knowledge_base.get_relationship_insights(profile_scores, None, lang)
            if self.language == Language.SWEDISH:
                knowledge += f"\n**RELATIONSDYNAMIK:**\n"
            else:
                knowledge += f"\n**RELATIONSHIP DYNAMICS:**\n"

            knowledge += f"Styrkor: {', '.join(insight.strengths[:3])}\n"
            if insight.challenges:
                knowledge += f"Utmaningar: {', '.join(insight.challenges[:2])}\n"

        # Add development strategies if growth question
        if question_type == QuestionType.PERSONAL_GROWTH and traits_mentioned and profile_scores:
            trait = traits_mentioned[0]
            score = profile_scores.get(trait, 50)

            # Determine desired direction (simplified - could be smarter)
            direction = "increase" if score < 50 else "decrease"

            strategy = self.knowledge_base.get_development_strategies(trait, score, direction, lang)

            if strategy:
                if self.language == Language.SWEDISH:
                    knowledge += f"\n**UTVECKLINGSSTRATEGIER för {trait}:**\n"
                else:
                    knowledge += f"\n**DEVELOPMENT STRATEGIES for {trait}:**\n"

                if 'practical_steps' in strategy:
                    knowledge += "Praktiska steg:\n"
                    for step in strategy['practical_steps'][:4]:
                        knowledge += f"- {step}\n"

        return knowledge


# Backward compatibility: Keep old function signature working
def chat_with_personality_coach(
    message: str,
    conversation_history: List[Dict[str, str]],
    profile_scores: Optional[Dict[str, float]] = None,
    personalized_report: Optional[Dict[str, any]] = None,
    anthropic_client: Optional[Anthropic] = None,
    user_id: str = "anonymous",
    conversation_id: str = "default"
) -> str:
    """
    Backward-compatible wrapper for the enhanced conversation coach
    This maintains compatibility with existing code
    """

    coach = ConversationCoach(
        anthropic_client=anthropic_client,
        language="sv"
    )

    return coach.chat(
        user_id=user_id,
        conversation_id=conversation_id,
        message=message,
        conversation_history=conversation_history,
        profile_scores=profile_scores,
        personalized_report=personalized_report
    )


# For testing
if __name__ == "__main__":
    print("=== CONVERSATION COACH TEST ===")

    # Test without actual API (just show structure)
    coach = ConversationCoach(anthropic_client=None, language="sv")

    test_scores = {
        'E': 35,  # Introvert
        'A': 75,  # High agreeableness
        'C': 40,  # Lower conscientiousness
        'N': 65,  # Higher neuroticism
        'O': 80   # High openness
    }

    print("\nTest user profile:")
    for trait, score in test_scores.items():
        print(f"  {trait}: {score}")

    print("\nSimulated conversation flow:")

    messages = [
        "Hej! Jag har gjort testet och är lite orolig över resultaten...",
        "Jag fick låg samvetsgrannhet. Betyder det att jag är lat?",
        "Hur kan jag bli mer organiserad utan att förlora min kreativitet?",
    ]

    for i, msg in enumerate(messages):
        print(f"\n--- Meddelande {i+1} ---")
        print(f"USER: {msg}")

        # Simulate analysis
        context = coach.flow_manager.get_or_create_context("test_user", "conv_001")
        emotion = coach.empathy_engine.detect_emotion(msg)
        question_type = coach.flow_manager.classify_question(msg)

        print(f"EMOTION: {emotion.primary_tone.value} ({emotion.intensity.value})")
        print(f"QUESTION TYPE: {question_type.value}")
        print(f"STAGE: {context.current_stage.value}")

        coach.flow_manager.update_context_after_message(context, msg, question_type)

    print("\n✅ Conversation coach structure validated!")
    print("Note: Actual AI responses require Anthropic API key")
