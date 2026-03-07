"""
Conversation Pacing - Timing, rhythm, and flow of therapeutic dialogue
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class ConversationPhase(Enum):
    """Phases of therapeutic conversation"""
    OPENING = "opening"  # Building rapport, understanding context
    EXPLORATION = "exploration"  # Deep dive into topics
    INSIGHT = "insight"  # Facilitating realizations
    ACTION = "action"  # Moving toward change
    CLOSING = "closing"  # Wrapping up, summarizing


class ConversationMove(Enum):
    """Types of conversational moves"""
    ASK_QUESTION = "ask_question"
    GIVE_INFORMATION = "give_information"
    VALIDATE_EMOTION = "validate_emotion"
    SUMMARIZE = "summarize"
    PAUSE_FOR_REFLECTION = "pause_for_reflection"
    CHANGE_TOPIC = "change_topic"
    DEEPEN = "deepen"
    CHALLENGE = "challenge"
    ENCOURAGE = "encourage"


class PacingAnalyzer:
    """
    Analyze conversation to determine appropriate pacing and next moves.
    """

    @staticmethod
    def detect_conversation_phase(
        conversation_history: List[Dict[str, str]],
        message_count: int
    ) -> ConversationPhase:
        """
        Detect what phase of conversation we're in.
        """
        # First 1-2 exchanges = Opening
        if message_count <= 4:
            return ConversationPhase.OPENING

        # Last few exchanges = Closing (if user signals ending)
        if conversation_history:
            recent_messages = [msg['content'].lower() for msg in conversation_history[-3:]
                             if msg['role'] == 'user']
            closing_signals = ['tack för hjälpen', 'det räcker', 'måste gå', 'vi ses', 'hejdå']
            if any(signal in ' '.join(recent_messages) for signal in closing_signals):
                return ConversationPhase.CLOSING

        # Check for insight moments (user has realization)
        if conversation_history:
            last_user_msg = next((msg['content'].lower() for msg in reversed(conversation_history)
                                if msg['role'] == 'user'), '')
            insight_signals = ['jaha', 'aha', 'nu förstår jag', 'det är intressant', 'aldrig tänkt på']
            if any(signal in last_user_msg for signal in insight_signals):
                return ConversationPhase.INSIGHT

        # Check for action-oriented discussion
        if conversation_history:
            recent_text = ' '.join([msg['content'].lower() for msg in conversation_history[-6:]])
            action_words = ['hur gör jag', 'vad ska jag', 'strategi', 'prova', 'börja med']
            if any(word in recent_text for word in action_words):
                return ConversationPhase.ACTION

        # Default to exploration
        return ConversationPhase.EXPLORATION

    @staticmethod
    def should_ask_question(conversation_history: List[Dict[str, str]]) -> Tuple[bool, str]:
        """
        Determine if it's appropriate to ask a question now.

        Returns:
            (should_ask, reason)
        """
        if not conversation_history:
            return (True, "Opening conversation")

        # Count recent questions from assistant
        recent_assistant_msgs = [msg for msg in conversation_history[-4:]
                                if msg['role'] == 'assistant']
        question_count = sum(1 for msg in recent_assistant_msgs if '?' in msg['content'])

        # Too many questions in a row = feels interrogative
        if question_count >= 3:
            return (False, "Too many recent questions - would feel interrogative")

        # If user just shared something emotional/deep
        last_user_msg = next((msg['content'] for msg in reversed(conversation_history)
                            if msg['role'] == 'user'), '')
        emotion_words = ['känner', 'mår', 'ledsen', 'rädd', 'orolig', 'svårt', 'jobbigt']
        if any(word in last_user_msg.lower() for word in emotion_words):
            return (False, "User shared emotions - validate first before asking")

        # If user seems reflective (good time for question)
        reflective_words = ['tänker', 'funderar', 'märkt att', 'intressant']
        if any(word in last_user_msg.lower() for word in reflective_words):
            return (True, "User is reflective - good time for guiding question")

        # If user asked a direct question (answer it, don't deflect with another Q)
        if '?' in last_user_msg and len(last_user_msg) < 200:
            return (False, "User asked direct question - answer it first")

        # Default: yes, questions are good
        return (True, "Appropriate to ask exploratory question")

    @staticmethod
    def should_give_information(user_message: str) -> Tuple[bool, str]:
        """
        Determine if user is asking for information.

        Returns:
            (should_inform, reason)
        """
        message_lower = user_message.lower()

        # Direct questions about concepts
        info_questions = ['vad är', 'vad betyder', 'hur fungerar', 'berätta om', 'förklara']
        if any(q in message_lower for q in info_questions):
            return (True, "User asking for information/explanation")

        # User expressed confusion
        if any(word in message_lower for word in ['förstår inte', 'oklart', 'förvirrad']):
            return (True, "User is confused - needs clarification")

        # User requesting advice/guidance
        if any(phrase in message_lower for phrase in ['vad borde jag', 'hur ska jag', 'tips', 'råd']):
            return (True, "User requesting guidance")

        return (False, "No information request detected")

    @staticmethod
    def should_validate_emotion(user_message: str) -> Tuple[bool, str]:
        """
        Determine if emotional validation is needed.
        """
        message_lower = user_message.lower()

        # Explicit emotion words
        emotion_words = ['känner', 'mår', 'ledsen', 'glad', 'arg', 'rädd', 'orolig',
                        'frustrerad', 'besviken', 'skäms', 'stolt']
        if any(word in message_lower for word in emotion_words):
            return (True, "User expressing emotion - validate")

        # Struggle/difficulty language
        if any(word in message_lower for word in ['svårt', 'jobbigt', 'tufft', 'kämpigt', 'utmaning']):
            return (True, "User describing struggle - validate experience")

        return (False, "No strong emotion detected")

    @staticmethod
    def should_summarize(
        conversation_history: List[Dict[str, str]],
        current_topic: str = None
    ) -> Tuple[bool, str]:
        """
        Determine if it's time to summarize.
        """
        if not conversation_history:
            return (False, "No history to summarize")

        message_count = len(conversation_history)

        # Long conversation (every ~10 exchanges)
        if message_count > 0 and message_count % 10 == 0:
            return (True, "Long conversation - time to tie threads together")

        # Multiple topics discussed
        if current_topic and len(set([msg.get('topic', '') for msg in conversation_history])) > 3:
            return (True, "Multiple topics - helpful to summarize")

        # User seems lost/overwhelmed
        if conversation_history:
            last_user_msg = next((msg['content'].lower() for msg in reversed(conversation_history)
                                if msg['role'] == 'user'), '')
            if any(word in last_user_msg for word in ['förvirrad', 'mycket att ta in', 'överväldigad']):
                return (True, "User seems overwhelmed - summarize to clarify")

        return (False, "No need to summarize yet")

    @staticmethod
    def should_change_topic(
        conversation_history: List[Dict[str, str]],
        current_topic: str
    ) -> Tuple[bool, str]:
        """
        Determine if conversation is stuck or stale on current topic.
        """
        if not conversation_history or len(conversation_history) < 6:
            return (False, "Too early to change topic")

        # Count how many recent messages about same topic
        recent_msgs = conversation_history[-6:]
        topic_repetition = sum(1 for msg in recent_msgs
                              if msg.get('topic') == current_topic)

        # Same topic for too long without progress
        if topic_repetition >= 5:
            return (True, "Stuck on same topic - might be time to shift perspective")

        # User seems disengaged (short responses)
        if conversation_history:
            last_user_msgs = [msg['content'] for msg in conversation_history[-3:]
                            if msg['role'] == 'user']
            avg_length = sum(len(msg) for msg in last_user_msgs) / len(last_user_msgs) if last_user_msgs else 100

            if avg_length < 30:  # Very short responses
                return (True, "User seems disengaged - try new angle or topic")

        return (False, "Topic still productive")

    @staticmethod
    def should_pause_for_reflection(user_message: str) -> Tuple[bool, str]:
        """
        Determine if user just had a deep insight that needs space.
        """
        message_lower = user_message.lower()

        # Insight markers
        insight_markers = ['aha', 'jaha', 'nu förstår jag', 'aldrig tänkt så', 'wow',
                          'det är sant', 'shit', 'fan va']
        if any(marker in message_lower for marker in insight_markers):
            return (True, "User having insight - give space to process")

        # Deep vulnerability shared
        vulnerability_markers = ['aldrig sagt det', 'första gången jag', 'svårt att säga']
        if any(marker in message_lower for marker in vulnerability_markers):
            return (True, "Deep sharing - honor with space")

        return (False, "No need to pause")


class PacingGuide:
    """
    Guide conversation pacing decisions.
    """

    @staticmethod
    def select_next_move(
        user_message: str,
        conversation_history: List[Dict[str, str]],
        phase: ConversationPhase = None
    ) -> ConversationMove:
        """
        Select the most appropriate next conversational move.
        """
        analyzer = PacingAnalyzer()

        # Detect phase if not provided
        if not phase:
            phase = analyzer.detect_conversation_phase(
                conversation_history,
                len(conversation_history)
            )

        # Priority 1: Validate emotion if present (always)
        should_validate, _ = analyzer.should_validate_emotion(user_message)
        if should_validate:
            return ConversationMove.VALIDATE_EMOTION

        # Priority 2: Pause if deep insight
        should_pause, _ = analyzer.should_pause_for_reflection(user_message)
        if should_pause:
            return ConversationMove.PAUSE_FOR_REFLECTION

        # Priority 3: Answer if direct question
        should_inform, _ = analyzer.should_give_information(user_message)
        if should_inform:
            return ConversationMove.GIVE_INFORMATION

        # Priority 4: Summarize if needed
        should_sum, _ = analyzer.should_summarize(conversation_history)
        if should_sum:
            return ConversationMove.SUMMARIZE

        # Priority 5: Change topic if stuck
        current_topic = conversation_history[-1].get('topic', 'general') if conversation_history else 'general'
        should_change, _ = analyzer.should_change_topic(conversation_history, current_topic)
        if should_change:
            return ConversationMove.CHANGE_TOPIC

        # Phase-specific moves
        if phase == ConversationPhase.OPENING:
            return ConversationMove.ASK_QUESTION  # Explore in opening

        elif phase == ConversationPhase.EXPLORATION:
            should_ask, _ = analyzer.should_ask_question(conversation_history)
            if should_ask:
                return ConversationMove.ASK_QUESTION
            else:
                return ConversationMove.DEEPEN  # Give reflection instead

        elif phase == ConversationPhase.INSIGHT:
            return ConversationMove.ENCOURAGE  # Reinforce insights

        elif phase == ConversationPhase.ACTION:
            return ConversationMove.GIVE_INFORMATION  # Provide strategies

        elif phase == ConversationPhase.CLOSING:
            return ConversationMove.SUMMARIZE

        # Default
        return ConversationMove.ASK_QUESTION

    @staticmethod
    def get_response_length_guidance(phase: ConversationPhase, move: ConversationMove) -> str:
        """
        Get guidance on how long the response should be.
        """
        length_guide = {
            (ConversationPhase.OPENING, ConversationMove.ASK_QUESTION): "short",  # 2-3 sentences
            (ConversationPhase.EXPLORATION, ConversationMove.DEEPEN): "medium",  # 1 paragraph
            (ConversationPhase.INSIGHT, ConversationMove.ENCOURAGE): "short",  # Don't overshadow their insight
            (ConversationPhase.ACTION, ConversationMove.GIVE_INFORMATION): "long",  # Detailed strategies
            (ConversationPhase.CLOSING, ConversationMove.SUMMARIZE): "medium",  # Comprehensive but concise
        }

        return length_guide.get((phase, move), "medium")


class FlowController:
    """
    Control the flow and rhythm of conversation.
    """

    @staticmethod
    def avoid_information_dumping(information: str, max_length: int = 500) -> str:
        """
        Break information into digestible chunks.
        """
        if len(information) <= max_length:
            return information

        # If too long, add a check-in point
        midpoint = len(information) // 2
        # Find nearest sentence break
        break_point = information.find('. ', midpoint)
        if break_point == -1:
            break_point = midpoint

        part1 = information[:break_point + 1]
        part2 = information[break_point + 1:]

        return f"{part1}\n\nFöljer du med hittills? Jag kan fortsätta:\n\n{part2}"

    @staticmethod
    def avoid_rapid_fire_questions(questions: List[str]) -> str:
        """
        If multiple questions needed, frame them as options not interrogation.
        """
        if len(questions) <= 1:
            return questions[0] if questions else ""

        if len(questions) == 2:
            return f"Två saker jag undrar: {questions[0]} Och {questions[1]}"

        # More than 2 = frame as "things to explore"
        intro = "Det finns några saker som skulle vara värdefulla att utforska:\n\n"
        formatted = "\n".join([f"- {q}" for q in questions])
        outro = "\n\nVilken av dessa känns mest relevant att börja med?"

        return intro + formatted + outro

    @staticmethod
    def create_pause_for_reflection(insight: str) -> str:
        """
        Create space for user to process a deep insight.
        """
        validations = [
            "Det där är en kraftfull insikt. Ta en stund och känn efter hur det landar.",
            "Låt det där sjunka in lite. Det är en viktig realisering.",
            "Wow. Det där är stort. Hur känns det att säga det högt?",
            "Stanna i det där ett ögonblick. Vad väcker det i dig?",
        ]

        return validations[0]  # Could be randomized

    @staticmethod
    def transition_topic_smoothly(from_topic: str, to_topic: str) -> str:
        """
        Create smooth transition between topics.
        """
        transitions = [
            f"Vi har pratat en del om {from_topic}. Jag undrar om vi kan utforska {to_topic} också - de verkar hänga ihop.",
            f"Det du säger om {from_topic} får mig att tänka på {to_topic}. Ska vi titta på det perspektivet?",
            f"Innan vi går djupare i {from_topic}, skulle det vara värdefullt att först förstå {to_topic}.",
        ]

        return transitions[0]

    @staticmethod
    def vary_language(conversation_history: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Track what phrases have been used to avoid repetition.
        Returns alternative phrasings.
        """
        # Extract phrases from assistant messages
        if not conversation_history:
            return {}

        assistant_msgs = [msg['content'] for msg in conversation_history
                         if msg['role'] == 'assistant']
        all_text = ' '.join(assistant_msgs).lower()

        # Common therapeutic phrases to vary
        alternatives = {
            'jag hör': ['jag märker', 'jag ser', 'jag uppfattar', 'det låter som'],
            'det är intressant': ['fascinerande', 'det är värdefullt', 'det är insiktsfullt', 'det säger något viktigt'],
            'berätta mer': ['utforska det', 'utveckla det där', 'vad mer finns där', 'gå djupare'],
            'hur känns det': ['vad väcker det i dig', 'hur landar det', 'vad märker du', 'hur upplever du det'],
        }

        # Count usage
        used_counts = {}
        for phrase, alts in alternatives.items():
            count = all_text.count(phrase)
            # If used more than twice, suggest alternatives
            if count >= 2:
                used_counts[phrase] = alts

        return used_counts


def pace_conversation(
    user_message: str,
    base_response: str,
    conversation_history: List[Dict[str, str]],
    current_phase: ConversationPhase = None
) -> Tuple[str, ConversationMove]:
    """
    Main function to pace the conversation appropriately.

    Args:
        user_message: Current user message
        base_response: Base response before pacing adjustments
        conversation_history: Previous messages
        current_phase: Current conversation phase (detected if not provided)

    Returns:
        (paced_response, move_made)
    """
    guide = PacingGuide()
    flow = FlowController()

    # Determine next move
    move = guide.select_next_move(user_message, conversation_history, current_phase)

    # Get phase
    if not current_phase:
        current_phase = PacingAnalyzer.detect_conversation_phase(
            conversation_history,
            len(conversation_history)
        )

    # Adjust response based on move
    if move == ConversationMove.PAUSE_FOR_REFLECTION:
        paced_response = flow.create_pause_for_reflection(user_message)

    elif move == ConversationMove.GIVE_INFORMATION:
        # Prevent information dumping
        paced_response = flow.avoid_information_dumping(base_response)

    else:
        paced_response = base_response

    # Check for repetitive language
    alternatives = flow.vary_language(conversation_history)
    if alternatives:
        # Note: In production, you'd actually replace repetitive phrases
        # For now, just return as-is
        pass

    return (paced_response, move)
