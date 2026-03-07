"""
Context Manager - Conversation and User Context Management
Loads user profiles, tracks conversation history, detects topic changes
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class MoodState(Enum):
    """User's emotional state throughout conversation"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    DEFENSIVE = "defensive"
    EXCITED = "excited"
    DISTRESSED = "distressed"


@dataclass
class ConversationMessage:
    """Single message in conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    topics: List[str] = field(default_factory=list)
    urgency: Optional[str] = None
    question_type: Optional[str] = None


@dataclass
class UserProfile:
    """User's personality profile (Big Five + DISC)"""
    user_id: str

    # Big Five scores (0-100 percentiles)
    big_five_scores: Optional[Dict[str, float]] = None

    # DISC scores (0-100)
    disc_scores: Optional[Dict[str, float]] = None
    disc_profile: Optional[str] = None  # e.g., "Di", "SC"

    # Assessment metadata
    big_five_completed: bool = False
    disc_completed: bool = False
    assessment_date: Optional[str] = None

    # Language preference
    language: str = "sv"

    def has_any_profile(self) -> bool:
        """Check if user has completed any assessment"""
        return self.big_five_completed or self.disc_completed

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "big_five_scores": self.big_five_scores,
            "disc_scores": self.disc_scores,
            "disc_profile": self.disc_profile,
            "big_five_completed": self.big_five_completed,
            "disc_completed": self.disc_completed,
            "assessment_date": self.assessment_date,
            "language": self.language
        }


@dataclass
class ConversationContext:
    """Complete context for a conversation"""
    user_profile: Optional[UserProfile] = None
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    current_mood: MoodState = MoodState.NEUTRAL
    topics_discussed: List[str] = field(default_factory=list)
    last_topic: Optional[str] = None
    session_start: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    engagement_level: str = "medium"  # low, medium, high

    def add_message(self, message: ConversationMessage):
        """Add message to history"""
        self.conversation_history.append(message)

        # Update topics discussed
        for topic in message.topics:
            if topic not in self.topics_discussed:
                self.topics_discussed.append(topic)

        # Track topic changes
        if message.topics:
            self.last_topic = message.topics[0]

        # Keep only last 20 messages (memory management)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def get_recent_messages(self, limit: int = 10) -> List[ConversationMessage]:
        """Get recent conversation messages"""
        return self.conversation_history[-limit:]

    def has_discussed_topic(self, topic: str) -> bool:
        """Check if topic was previously discussed"""
        return topic in self.topics_discussed

    def get_last_user_message(self) -> Optional[ConversationMessage]:
        """Get last message from user"""
        for msg in reversed(self.conversation_history):
            if msg.role == "user":
                return msg
        return None

    def get_last_assistant_message(self) -> Optional[ConversationMessage]:
        """Get last message from assistant"""
        for msg in reversed(self.conversation_history):
            if msg.role == "assistant":
                return msg
        return None

    def update_mood(self, new_mood: MoodState):
        """Update current mood state"""
        self.current_mood = new_mood

    def calculate_engagement_level(self) -> str:
        """Calculate user engagement level based on conversation"""
        if len(self.conversation_history) < 2:
            return "low"

        # Count user messages
        user_messages = [m for m in self.conversation_history if m.role == "user"]

        if len(user_messages) >= 5:
            # Check message length (deep questions = higher engagement)
            avg_length = sum(len(m.content.split()) for m in user_messages) / len(user_messages)

            if avg_length > 15:
                return "high"
            elif avg_length > 8:
                return "medium"

        return "medium"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "user_profile": self.user_profile.to_dict() if self.user_profile else None,
            "conversation_history": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "topics": m.topics
                }
                for m in self.conversation_history
            ],
            "current_mood": self.current_mood.value,
            "topics_discussed": self.topics_discussed,
            "last_topic": self.last_topic,
            "session_start": self.session_start,
            "engagement_level": self.engagement_level
        }


# ============================================================================
# CONTEXT MANAGER
# ============================================================================

class ContextManager:
    """
    Manages conversation context and user profiles
    """

    def __init__(self, db_session=None):
        """
        Initialize context manager

        Args:
            db_session: Database session for loading user data
        """
        self.db_session = db_session
        self._context_cache: Dict[str, ConversationContext] = {}

    def load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Load user's personality profile from database

        Args:
            user_id: User ID

        Returns:
            UserProfile or None if not found
        """
        if not self.db_session:
            return None

        from database import User, Assessment, AssessmentResult, AssessmentType

        try:
            # Get user
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            profile = UserProfile(user_id=user_id)

            # Get Big Five assessment
            big_five = self.db_session.query(Assessment).filter(
                Assessment.user_id == user_id,
                Assessment.assessment_type == AssessmentType.BIG_FIVE,
                Assessment.status == "completed"
            ).order_by(Assessment.completed_at.desc()).first()

            if big_five and big_five.result:
                profile.big_five_completed = True
                profile.assessment_date = big_five.completed_at.isoformat()

                # Extract Big Five scores
                scores = big_five.result.scores
                if isinstance(scores, list):
                    # Convert list format to dict
                    profile.big_five_scores = {}
                    for score in scores:
                        if isinstance(score, dict):
                            dim = score.get("dimension", "").upper()
                            val = score.get("percentile", 50)
                            if dim in ["E", "A", "C", "N", "O"]:
                                profile.big_five_scores[dim] = val
                elif isinstance(scores, dict):
                    profile.big_five_scores = scores

            # Get DISC assessment
            disc = self.db_session.query(Assessment).filter(
                Assessment.user_id == user_id,
                Assessment.assessment_type == AssessmentType.DISC,
                Assessment.status == "completed"
            ).order_by(Assessment.completed_at.desc()).first()

            if disc and disc.result:
                profile.disc_completed = True
                if not profile.assessment_date:
                    profile.assessment_date = disc.completed_at.isoformat()

                # Extract DISC scores
                profile.disc_scores = {
                    "D": disc.result.dominance_score or 50,
                    "I": disc.result.influence_score or 50,
                    "S": disc.result.steadiness_score or 50,
                    "C": disc.result.conscientiousness_score or 50
                }
                profile.disc_profile = disc.result.disc_profile

            return profile

        except Exception as e:
            print(f"Error loading user profile: {e}")
            return None

    def load_conversation_history(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[ConversationMessage]:
        """
        Load conversation history from database

        Args:
            user_id: User ID
            session_id: Optional session ID to filter by
            limit: Max number of messages to load

        Returns:
            List of ConversationMessage objects
        """
        if not self.db_session:
            return []

        # TODO: Implement database storage for chat history
        # For now, return empty list (in-memory only)
        return []

    def get_or_create_context(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> ConversationContext:
        """
        Get existing context or create new one

        Args:
            user_id: User ID
            session_id: Optional session ID
            conversation_history: Optional conversation history from request

        Returns:
            ConversationContext with loaded profile and history
        """
        cache_key = f"{user_id}:{session_id or 'default'}"

        # Check cache
        if cache_key in self._context_cache:
            context = self._context_cache[cache_key]
        else:
            # Create new context
            context = ConversationContext()
            self._context_cache[cache_key] = context

        # Load user profile if not already loaded
        if not context.user_profile:
            context.user_profile = self.load_user_profile(user_id)

        # Load or update conversation history
        if conversation_history:
            # Convert dict history to ConversationMessage objects
            for msg in conversation_history:
                if isinstance(msg, dict):
                    conv_msg = ConversationMessage(
                        role=msg.get("role", "user"),
                        content=msg.get("content", ""),
                        timestamp=msg.get("timestamp", datetime.utcnow().isoformat()),
                        topics=msg.get("topics", [])
                    )
                    # Only add if not already in history
                    if not any(
                        m.content == conv_msg.content and m.timestamp == conv_msg.timestamp
                        for m in context.conversation_history
                    ):
                        context.add_message(conv_msg)

        # Update engagement level
        context.engagement_level = context.calculate_engagement_level()

        return context

    def detect_topic_change(self, context: ConversationContext, new_topics: List[str]) -> bool:
        """
        Detect if conversation topic has changed

        Args:
            context: Current conversation context
            new_topics: Topics from current question

        Returns:
            True if topic has significantly changed
        """
        if not context.last_topic or not new_topics:
            return False

        # If no overlap between old and new topics, it's a change
        return context.last_topic not in new_topics

    def should_avoid_repetition(self, context: ConversationContext, topic: str) -> bool:
        """
        Check if we should avoid repeating information about a topic

        Args:
            context: Current conversation context
            topic: Topic to check

        Returns:
            True if topic was recently discussed in detail
        """
        # Check last 5 messages for this topic
        recent_messages = context.get_recent_messages(5)

        topic_mentions = sum(
            1 for msg in recent_messages
            if topic in msg.topics and msg.role == "assistant"
        )

        # If mentioned 2+ times in last 5 messages, avoid repetition
        return topic_mentions >= 2

    def get_profile_summary(self, profile: UserProfile) -> str:
        """
        Get a concise summary of user's personality profile

        Args:
            profile: UserProfile object

        Returns:
            Human-readable summary string
        """
        if not profile or not profile.has_any_profile():
            return "Ingen personlighetsprofil tillgänglig ännu."

        summary_parts = []

        # Big Five summary
        if profile.big_five_scores:
            bf = profile.big_five_scores

            # Identify high and low traits
            high_traits = []
            low_traits = []

            trait_names = {
                "E": "Extraversion",
                "A": "Vänlighet",
                "C": "Samvetsgrannhet",
                "N": "Neuroticism",
                "O": "Öppenhet"
            }

            for dim, score in bf.items():
                name = trait_names.get(dim, dim)
                if score >= 65:
                    high_traits.append(f"hög {name}")
                elif score <= 35:
                    low_traits.append(f"låg {name}")

            if high_traits:
                summary_parts.append(f"Höga drag: {', '.join(high_traits)}")
            if low_traits:
                summary_parts.append(f"Låga drag: {', '.join(low_traits)}")

        # DISC summary
        if profile.disc_profile:
            summary_parts.append(f"DISC-profil: {profile.disc_profile}")

        return "; ".join(summary_parts) if summary_parts else "Profil tillgänglig"

    def update_context_with_classification(
        self,
        context: ConversationContext,
        classification: Any,
        message_content: str
    ):
        """
        Update context based on question classification

        Args:
            context: ConversationContext to update
            classification: QuestionClassification object
            message_content: The actual message text
        """
        from question_classifier import UrgencyLevel, MoodState as QMoodState

        # Create conversation message
        msg = ConversationMessage(
            role="user",
            content=message_content,
            timestamp=datetime.utcnow().isoformat(),
            topics=[t.value for t in classification.topics],
            urgency=classification.urgency.value,
            question_type=classification.question_type.value
        )

        context.add_message(msg)

        # Update mood based on urgency
        mood_mapping = {
            UrgencyLevel.NEUTRAL: MoodState.NEUTRAL,
            UrgencyLevel.ANXIOUS: MoodState.ANXIOUS,
            UrgencyLevel.DISTRESSED: MoodState.DISTRESSED,
            UrgencyLevel.CURIOUS: MoodState.EXCITED,
            UrgencyLevel.CONFUSED: MoodState.CONFUSED
        }

        new_mood = mood_mapping.get(classification.urgency, MoodState.NEUTRAL)
        context.update_mood(new_mood)

    def clear_context(self, user_id: str, session_id: Optional[str] = None):
        """Clear cached context for user/session"""
        cache_key = f"{user_id}:{session_id or 'default'}"
        if cache_key in self._context_cache:
            del self._context_cache[cache_key]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_trait_description(dimension: str, score: float, language: str = "sv") -> str:
    """
    Get human-readable description of a trait score

    Args:
        dimension: Trait dimension (E, A, C, N, O, or D, I, S, C for DISC)
        score: Score 0-100
        language: "sv" or "en"

    Returns:
        Description string
    """
    if language == "sv":
        level = "hög" if score >= 65 else "låg" if score <= 35 else "medel"

        descriptions = {
            "E": f"{level} Extraversion ({"utåtriktad" if score >= 65 else "introvert" if score <= 35 else "balanserad"})",
            "A": f"{level} Vänlighet ({"empatisk" if score >= 65 else "direkt" if score <= 35 else "balanserad"})",
            "C": f"{level} Samvetsgrannhet ({"organiserad" if score >= 65 else "spontan" if score <= 35 else "balanserad"})",
            "N": f"{level} Neuroticism ({"känslosam" if score >= 65 else "stabil" if score <= 35 else "balanserad"})",
            "O": f"{level} Öppenhet ({"kreativ" if score >= 65 else "praktisk" if score <= 35 else "balanserad"})",
            "D": f"{level} Dominance ({"resultatorienterad" if score >= 65 else "samarbetande" if score <= 35 else "balanserad"})",
            "I": f"{level} Influence ({"utåtriktad" if score >= 65 else "reserverad" if score <= 35 else "balanserad"})",
            "S": f"{level} Steadiness ({"stabil" if score >= 65 else "dynamisk" if score <= 35 else "balanserad"})",
            "C": f"{level} Conscientiousness ({"analytisk" if score >= 65 else "intuitiv" if score <= 35 else "balanserad"})",
        }
    else:
        level = "high" if score >= 65 else "low" if score <= 35 else "medium"
        descriptions = {
            "E": f"{level} Extraversion",
            "A": f"{level} Agreeableness",
            "C": f"{level} Conscientiousness",
            "N": f"{level} Neuroticism",
            "O": f"{level} Openness",
        }

    return descriptions.get(dimension, f"{level} {dimension}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("CONTEXT MANAGER TEST")
    print("=" * 80)

    # Create test profile
    profile = UserProfile(
        user_id="test_user_123",
        big_five_scores={"E": 75, "A": 45, "C": 30, "N": 60, "O": 85},
        big_five_completed=True,
        disc_scores={"D": 70, "I": 55, "S": 40, "C": 45},
        disc_profile="Di",
        disc_completed=True,
        language="sv"
    )

    print(f"\nUser Profile:")
    print(f"  User ID: {profile.user_id}")
    print(f"  Big Five Scores: {profile.big_five_scores}")
    print(f"  DISC Profile: {profile.disc_profile}")
    print(f"  Has Profile: {profile.has_any_profile()}")

    # Create context manager
    manager = ContextManager()

    # Create context
    context = ConversationContext(user_profile=profile)

    # Add test messages
    test_messages = [
        ConversationMessage(
            role="user",
            content="Varför är jag så låg i Conscientiousness?",
            timestamp=datetime.utcnow().isoformat(),
            topics=["conscientiousness"],
            question_type="personal_report"
        ),
        ConversationMessage(
            role="assistant",
            content="Din låga Conscientiousness betyder att du är mer spontan...",
            timestamp=datetime.utcnow().isoformat(),
            topics=["conscientiousness"]
        )
    ]

    for msg in test_messages:
        context.add_message(msg)

    print(f"\nConversation Context:")
    print(f"  Messages: {len(context.conversation_history)}")
    print(f"  Topics Discussed: {context.topics_discussed}")
    print(f"  Current Mood: {context.current_mood.value}")
    print(f"  Engagement Level: {context.engagement_level}")

    # Test profile summary
    summary = manager.get_profile_summary(profile)
    print(f"\nProfile Summary:")
    print(f"  {summary}")

    # Test trait descriptions
    print(f"\nTrait Descriptions:")
    for dim, score in profile.big_five_scores.items():
        desc = get_trait_description(dim, score, "sv")
        print(f"  {dim}: {desc}")

    print("\n" + "=" * 80)
    print("✅ Context Manager test completed!")
