"""
Therapeutic Integration - Main orchestrator that combines all therapeutic techniques
into a cohesive, psychologist-like conversation system
"""

from typing import Dict, List, Optional, Tuple
from therapeutic_techniques import (
    MotivationalInterviewing, CognitiveReframing, SocraticMethod,
    Validation, TherapeuticTechnique, select_technique
)
from rapport_builder import (
    RapportBuilder, TherapeuticAlliance, EmotionalTone,
    build_rapport_response
)
from insight_generator import (
    PatternRecognition, StrengthsBasedApproach, GrowthMindset,
    generate_insight
)
from emotional_calibration import (
    EmotionDetector, ResponseCalibrator, EmotionType,
    calibrate_response
)
from conversation_pacing import (
    PacingAnalyzer, PacingGuide, FlowController,
    ConversationPhase, ConversationMove, pace_conversation
)


class TherapeuticResponse:
    """
    Main class to generate therapeutic responses that integrate all techniques.
    """

    @staticmethod
    def generate_therapeutic_response(
        user_message: str,
        user_profile: Dict[str, float],
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> str:
        """
        Generate a sophisticated therapeutic response using all available techniques.

        Args:
            user_message: User's current message
            user_profile: User's Big Five scores (E, A, C, N, O as 0-100)
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            session_context: Optional context like topic, goals, etc.

        Returns:
            Therapeutic response string
        """
        # Initialize components
        builder = RapportBuilder()
        alliance = TherapeuticAlliance()
        flow = FlowController()

        # Step 1: Check for alliance rupture (highest priority)
        rupture_type = alliance.check_alliance_rupture(user_message)
        if rupture_type:
            return alliance.repair_alliance(rupture_type)

        # Step 2: Check for crisis/boundaries
        boundary_response = TherapeuticResponse._check_boundaries(user_message)
        if boundary_response:
            return boundary_response

        # Step 3: Detect emotion
        emotion, emotion_confidence = EmotionDetector.detect_emotion(
            user_message,
            conversation_history
        )

        # Step 4: Determine conversation phase and next move
        phase = PacingAnalyzer.detect_conversation_phase(
            conversation_history,
            len(conversation_history)
        )
        move = PacingGuide.select_next_move(user_message, conversation_history, phase)

        # Step 5: Build core response based on move
        core_response = TherapeuticResponse._build_core_response(
            user_message=user_message,
            user_profile=user_profile,
            conversation_history=conversation_history,
            move=move,
            emotion=emotion
        )

        # Step 6: Add validation if emotion detected
        if emotion != EmotionType.NEUTRAL and emotion_confidence > 0.5:
            validation = Validation.validate_emotion(emotion.value, user_message)
            core_response = validation + "\n\n" + core_response

        # Step 7: Try to generate insight
        insight = generate_insight(
            user_profile,
            user_message,
            [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        )
        if insight and move in [ConversationMove.DEEPEN, ConversationMove.GIVE_INFORMATION]:
            core_response = core_response + "\n\n" + insight

        # Step 8: Calibrate for emotion
        calibrated_response = calibrate_response(
            user_message,
            core_response,
            [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        )

        # Step 9: Build rapport elements
        rapport_enhanced = build_rapport_response(
            user_message,
            calibrated_response,
            conversation_history,
            user_profile
        )

        # Step 10: Apply pacing
        paced_response, _ = pace_conversation(
            user_message,
            rapport_enhanced,
            conversation_history,
            phase
        )

        # Step 11: Final polish - ensure non-judgmental, warm tone
        final_response = TherapeuticResponse._final_polish(paced_response)

        return final_response

    @staticmethod
    def _check_boundaries(user_message: str) -> Optional[str]:
        """
        Check if we need to set boundaries (crisis, medical, etc.)
        """
        message_lower = user_message.lower()
        builder = RapportBuilder()

        # Crisis indicators
        crisis_words = ['vill dö', 'ta mitt liv', 'döda mig', 'suicide', 'självmord',
                       'inte värt att leva', 'slut på allt']
        if any(word in message_lower for word in crisis_words):
            return builder.create_boundary_statement('crisis')

        # Medical concerns
        medical_words = ['diagnos', 'medicin', 'adhd', 'autism', 'depression diagnos',
                        'bipolär', 'schizofreni', 'psykos']
        if any(word in message_lower for word in medical_words):
            return builder.create_boundary_statement('diagnosis')

        # Trauma
        trauma_words = ['traumat', 'övergrepp', 'våldtäkt', 'misshandel', 'ptsd']
        if any(word in message_lower for word in trauma_words):
            return builder.create_boundary_statement('trauma')

        return None

    @staticmethod
    def _build_core_response(
        user_message: str,
        user_profile: Dict[str, float],
        conversation_history: List[Dict[str, str]],
        move: ConversationMove,
        emotion: EmotionType
    ) -> str:
        """
        Build the core response based on conversation move.
        """
        if move == ConversationMove.VALIDATE_EMOTION:
            # Validation + empathy
            return Validation.validate_emotion(emotion.value, user_message)

        elif move == ConversationMove.ASK_QUESTION:
            # Motivational interviewing question
            question = MotivationalInterviewing.generate_open_question(
                user_message,
                user_profile
            )
            # Add brief acknowledgment before question
            acknowledge = MotivationalInterviewing.create_affirmation(user_message, user_profile)
            return f"{acknowledge}\n\n{question}"

        elif move == ConversationMove.GIVE_INFORMATION:
            # Educational response with personalization
            return TherapeuticResponse._give_personalized_information(
                user_message,
                user_profile
            )

        elif move == ConversationMove.DEEPEN:
            # Reflective listening + deeper question
            reflection = MotivationalInterviewing.reflective_listening(user_message)
            questions = SocraticMethod.generate_guiding_questions(user_message, user_profile)
            return f"{reflection}\n\n{questions[0] if questions else 'Berätta mer om det där.'}"

        elif move == ConversationMove.SUMMARIZE:
            # Summarize conversation themes
            user_statements = [msg['content'] for msg in conversation_history
                             if msg['role'] == 'user']
            themes = TherapeuticResponse._extract_themes(user_statements)
            return MotivationalInterviewing.summarize_conversation(user_statements, themes)

        elif move == ConversationMove.PAUSE_FOR_REFLECTION:
            # Simple acknowledgment with space
            return FlowController.create_pause_for_reflection(user_message)

        elif move == ConversationMove.ENCOURAGE:
            # Celebrate insight
            return GrowthMindset.celebrate_insight(user_message)

        elif move == ConversationMove.CHALLENGE:
            # Gentle challenge of negative thinking
            pattern, reframe = CognitiveReframing.challenge_negative_self_talk(user_message)
            return reframe

        else:
            # Default: empathetic exploration
            return f"Berätta mer om det där. Jag lyssnar."

    @staticmethod
    def _give_personalized_information(
        user_message: str,
        user_profile: Dict[str, float]
    ) -> str:
        """
        Give educational information personalized to user's profile.
        """
        message_lower = user_message.lower()

        # Detect what they're asking about
        if any(word in message_lower for word in ['extraversion', 'introvert', 'extrovert', 'social']):
            trait_value = user_profile.get('E', 50)
            return PatternRecognition.connect_traits_to_experiences(
                'extraversion',
                trait_value,
                'relationships' if 'relation' in message_lower else 'work'
            )

        elif any(word in message_lower for word in ['conscientiousness', 'organisera', 'struktur', 'disciplin']):
            trait_value = user_profile.get('C', 50)
            return PatternRecognition.connect_traits_to_experiences(
                'conscientiousness',
                trait_value,
                'work' if 'jobb' in message_lower or 'arbete' in message_lower else 'relationships'
            )

        elif any(word in message_lower for word in ['neuroticism', 'ångest', 'oro', 'stress', 'känslor']):
            trait_value = user_profile.get('N', 50)
            return PatternRecognition.connect_traits_to_experiences(
                'neuroticism',
                trait_value,
                'work' if 'jobb' in message_lower or 'arbete' in message_lower else 'relationships'
            )

        elif any(word in message_lower for word in ['openness', 'kreativ', 'nyfiken', 'nytänkande']):
            trait_value = user_profile.get('O', 50)
            return PatternRecognition.connect_traits_to_experiences(
                'openness',
                trait_value,
                'work' if 'jobb' in message_lower or 'arbete' in message_lower else 'relationships'
            )

        elif any(word in message_lower for word in ['agreeableness', 'vänlig', 'empatisk', 'konflikt']):
            trait_value = user_profile.get('A', 50)
            return PatternRecognition.connect_traits_to_experiences(
                'agreeableness',
                trait_value,
                'work' if 'jobb' in message_lower or 'arbete' in message_lower else 'relationships'
            )

        # Generic information
        return "Bra fråga! Låt mig förklara det i relation till din profil."

    @staticmethod
    def _extract_themes(user_statements: List[str]) -> List[str]:
        """
        Extract main themes from user's statements.
        """
        all_text = ' '.join(user_statements).lower()
        themes = []

        theme_keywords = {
            'karriär': ['karriär', 'jobb', 'arbete', 'yrke', 'chef', 'kolleg'],
            'relationer': ['relation', 'vän', 'partner', 'familj', 'kärlek', 'ensam'],
            'personlig utveckling': ['utveckla', 'bättre', 'förändra', 'lära', 'växa'],
            'stress/utmaningar': ['stress', 'oro', 'ångest', 'svårt', 'problem', 'utmaning'],
            'självförståelse': ['personlighet', 'vem jag är', 'förstå mig', 'traits'],
        }

        for theme, keywords in theme_keywords.items():
            if any(kw in all_text for kw in keywords):
                themes.append(theme)

        return themes[:3] if themes else ['dina upplevelser']

    @staticmethod
    def _final_polish(response: str) -> str:
        """
        Final polish to ensure warm, professional, therapeutic tone.
        """
        # Remove any overly clinical language
        clinical_replacements = {
            'patienten': 'du',
            'klienten': 'du',
            'subjektet': 'du',
            'individen': 'du',
        }

        polished = response
        for clinical, warm in clinical_replacements.items():
            polished = polished.replace(clinical, warm)

        # Ensure it doesn't end with a question if it's very long
        # (can feel interrogative)
        if len(polished) > 400 and polished.strip().endswith('?'):
            polished = polished + "\n\nTa den tid du behöver att reflektera."

        return polished


class TherapeuticConversation:
    """
    Manages a full therapeutic conversation session.
    """

    def __init__(self, user_profile: Dict[str, float]):
        """
        Initialize a therapeutic conversation session.

        Args:
            user_profile: User's Big Five scores
        """
        self.user_profile = user_profile
        self.conversation_history: List[Dict[str, str]] = []
        self.session_context = {
            'themes': [],
            'insights': [],
            'goals': []
        }

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({
            'role': role,
            'content': content
        })

    def respond(self, user_message: str) -> str:
        """
        Generate therapeutic response to user message.

        Args:
            user_message: User's message

        Returns:
            AI's therapeutic response
        """
        # Add user message to history
        self.add_message('user', user_message)

        # Generate response
        response = TherapeuticResponse.generate_therapeutic_response(
            user_message,
            self.user_profile,
            self.conversation_history,
            self.session_context
        )

        # Add response to history
        self.add_message('assistant', response)

        return response

    def get_opening_message(self) -> str:
        """
        Generate warm opening message for new conversation.
        """
        # Get strengths from profile
        strengths = StrengthsBasedApproach.identify_strengths_in_profile(self.user_profile)

        # Build personalized opening
        opening = (
            "Hej! Jag är här för att hjälpa dig utforska din personlighet och hur den påverkar "
            "ditt liv - dina relationer, karriär och personliga utveckling.\n\n"
            "Jag ser i din Big Five-profil flera spännande styrkor:\n"
        )

        # Add top 2-3 strengths
        for strength in strengths[:3]:
            opening += f"• {strength}\n"

        opening += (
            "\nDetta är ett tryggt utrymme för reflektion. Du styr samtalet - jag finns här för "
            "att lyssna, ställa frågor och erbjuda perspektiv baserat på psykologisk forskning.\n\n"
            "Vad skulle du vilja utforska idag?"
        )

        return opening

    def get_closing_message(self) -> str:
        """
        Generate closing summary and encouragement.
        """
        # Extract themes from conversation
        user_statements = [msg['content'] for msg in self.conversation_history
                          if msg['role'] == 'user']
        themes = TherapeuticResponse._extract_themes(user_statements)

        closing = (
            "Låt mig sammanfatta vad vi utforskat idag:\n\n"
        )

        if themes:
            closing += f"Vi har pratat om {', '.join(themes)}. "

        closing += (
            "Du har visat stor självinsikt och mod i att utforska dessa frågor.\n\n"
            "Kom ihåg: Personlighetsutveckling är en pågående resa, inte ett mål. De insikter "
            "du fått idag är början på ny förståelse.\n\n"
            "Jag finns här när du vill utforska mer. Ta hand om dig!"
        )

        return closing


# Convenience function for quick testing
def therapeutic_demo():
    """
    Demo of therapeutic conversation system.
    """
    # Example profile
    profile = {
        'E': 35,  # Low extraversion (introverted)
        'A': 70,  # High agreeableness
        'C': 45,  # Moderate-low conscientiousness
        'N': 65,  # High neuroticism (emotionally reactive)
        'O': 80,  # Very high openness
    }

    # Create conversation
    convo = TherapeuticConversation(profile)

    # Opening
    print("=== THERAPEUTIC CONVERSATION DEMO ===\n")
    print("AI:", convo.get_opening_message())
    print("\n" + "="*50 + "\n")

    # Example exchanges
    test_messages = [
        "Jag fick låg extraversion. Betyder det att jag är tråkig?",
        "Jag kämpar verkligen med att få saker gjorda. Alltid prokrastinerar.",
        "Det är så frustrerande! Jag försöker och försöker men kommer ingen vart.",
    ]

    for user_msg in test_messages:
        print(f"User: {user_msg}\n")
        response = convo.respond(user_msg)
        print(f"AI: {response}\n")
        print("="*50 + "\n")

    print("AI:", convo.get_closing_message())


if __name__ == "__main__":
    therapeutic_demo()
