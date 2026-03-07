"""
Demo: Therapeutic Conversation System
Shows how the AI uses psychological techniques to feel like a trained psychologist
"""

from therapeutic_integration import TherapeuticConversation, TherapeuticResponse
from therapeutic_techniques import MotivationalInterviewing, CognitiveReframing, SocraticMethod, Validation
from emotional_calibration import EmotionDetector
from insight_generator import StrengthsBasedApproach, PatternRecognition
from rapport_builder import RapportBuilder
from typing import Dict


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def demo_scenario_1():
    """
    Scenario 1: User disappointed with low extraversion
    Shows: Validation + Reframing + Self-discovery
    """
    print_section("SCENARIO 1: User Disappointed with Low Extraversion")

    profile = {
        'E': 25,  # Very low extraversion
        'A': 70,
        'C': 55,
        'N': 60,
        'O': 75,
    }

    convo = TherapeuticConversation(profile)
    user_msg = "Jag fick låg extraversion. Betyder det att jag är tråkig?"

    print(f"USER: {user_msg}\n")

    response = convo.respond(user_msg)
    print(f"AI: {response}\n")

    print("\n--- THERAPEUTIC TECHNIQUES USED ---")
    print("✓ Validation: Acknowledges the disappointment")
    print("✓ Reframing: Low E → 'Introversion is a strength'")
    print("✓ Psychoeducation: Explains what extraversion actually measures")
    print("✓ Self-discovery question: Asks user to reflect on own experience")


def demo_scenario_2():
    """
    Scenario 2: User asking for career advice
    Shows: Socratic method (exploration before prescription)
    """
    print_section("SCENARIO 2: User Asking for Career Advice")

    profile = {
        'E': 45,
        'A': 60,
        'C': 30,  # Low conscientiousness
        'N': 55,
        'O': 85,  # Very high openness
    }

    convo = TherapeuticConversation(profile)

    # Show opening first
    print("AI:", convo.get_opening_message())
    print("\n" + "-"*80 + "\n")

    user_msg = "Vilken karriär passar min personlighet?"

    print(f"USER: {user_msg}\n")

    response = convo.respond(user_msg)
    print(f"AI: {response}\n")

    print("\n--- THERAPEUTIC TECHNIQUES USED ---")
    print("✓ Socratic Method: Guides discovery through questions")
    print("✓ Avoids direct advice: Helps user find their own answer")
    print("✓ Personalization: References user's specific profile")
    print("✓ Collaborative: Frames it as working together")


def demo_scenario_3():
    """
    Scenario 3: User struggling with procrastination
    Shows: Emotion detection + Pattern recognition + Strengths-based
    """
    print_section("SCENARIO 3: User Struggling with Procrastination")

    profile = {
        'E': 60,
        'A': 65,
        'C': 25,  # Very low conscientiousness
        'N': 70,  # High neuroticism
        'O': 80,
    }

    convo = TherapeuticConversation(profile)

    # First message
    msg1 = "Jag kämpar verkligen med att få saker gjorda. Alltid prokrastinerar."
    print(f"USER: {msg1}\n")
    response1 = convo.respond(msg1)
    print(f"AI: {response1}\n")

    print("-"*80 + "\n")

    # Follow-up with frustration
    msg2 = "Det är så jävla frustrerande! Jag försöker och försöker men kommer ingen vart."
    print(f"USER: {msg2}\n")

    # Detect emotion first
    emotion, confidence = EmotionDetector.detect_emotion(msg2)
    print(f"[EMOTION DETECTED: {emotion.value} (confidence: {confidence:.2f})]\n")

    response2 = convo.respond(msg2)
    print(f"AI: {response2}\n")

    print("\n--- THERAPEUTIC TECHNIQUES USED ---")
    print("✓ Emotion calibration: Detected frustration and responded with validation")
    print("✓ Pattern recognition: Connected low C to procrastination")
    print("✓ Normalization: 'It's not laziness, it's how your brain works'")
    print("✓ Strengths-based: Reframed as 'deadline-driven motivation'")
    print("✓ Practical: Offered strategies that work WITH their profile")


def demo_scenario_4():
    """
    Scenario 4: User showing defensive response
    Shows: Alliance repair + Non-judgmental language
    """
    print_section("SCENARIO 4: User Showing Defensiveness (Alliance Rupture)")

    profile = {
        'E': 40,
        'A': 35,  # Low agreeableness
        'C': 70,
        'N': 50,
        'O': 60,
    }

    convo = TherapeuticConversation(profile)

    # Setup context
    msg1 = "Berätta om min låga agreeableness"
    convo.respond(msg1)

    # Defensive response
    msg2 = "Men jag är inte otrevlig! Det stämmer inte alls. Du förstår inte."

    print(f"USER: {msg2}\n")

    # Check for rupture
    from rapport_builder import TherapeuticAlliance
    rupture = TherapeuticAlliance.check_alliance_rupture(msg2)
    print(f"[ALLIANCE RUPTURE DETECTED: {rupture}]\n")

    response = convo.respond(msg2)
    print(f"AI: {response}\n")

    print("\n--- THERAPEUTIC TECHNIQUES USED ---")
    print("✓ Alliance repair: Acknowledged the rupture immediately")
    print("✓ Validation: 'You know yourself best'")
    print("✓ Non-judgmental: Softened language, emphasized choice")
    print("✓ Empowerment: User controls interpretation")


def demo_technique_showcase():
    """
    Show individual techniques in action
    """
    print_section("THERAPEUTIC TECHNIQUES SHOWCASE")

    # Motivational Interviewing
    print("1. MOTIVATIONAL INTERVIEWING - Open Questions:")
    question = MotivationalInterviewing.generate_open_question(
        "Jag vill hitta ett jobb jag trivs med",
        {'E': 50, 'A': 60, 'C': 45, 'N': 55, 'O': 70}
    )
    print(f"   → {question}\n")

    # Cognitive Reframing
    print("2. COGNITIVE REFRAMING - Challenge Negative Self-Talk:")
    pattern, reframe = CognitiveReframing.challenge_negative_self_talk(
        "Jag är alltid så oorganiserad och misslyckad"
    )
    print(f"   Pattern detected: {pattern}")
    print(f"   → {reframe}\n")

    # Validation
    print("3. VALIDATION - Normalize Experience:")
    validation = Validation.validate_emotion("anxiety", "Jag är så orolig hela tiden")
    print(f"   → {validation}\n")

    # Strengths-Based
    print("4. STRENGTHS-BASED - Identify Profile Strengths:")
    strengths = StrengthsBasedApproach.identify_strengths_in_profile({
        'E': 30, 'A': 75, 'C': 80, 'N': 45, 'O': 65
    })
    print("   Strengths identified:")
    for strength in strengths:
        print(f"   • {strength}")
    print()

    # Pattern Recognition
    print("5. PATTERN RECOGNITION - Connect Traits to Behavior:")
    pattern = PatternRecognition.generate_pattern_insight(
        {'E': 25, 'A': 60, 'C': 40, 'N': 70, 'O': 75},
        "Jag känner mig alltid så trött efter sociala tillställningar"
    )
    if pattern:
        print(f"   → {pattern}\n")


def demo_emotion_detection():
    """
    Show emotion detection capabilities
    """
    print_section("EMOTION DETECTION DEMO")

    test_messages = [
        ("Jag är så orolig att jag kommer misslyckas", "Anxiety"),
        ("Det är så jävla frustrerande!", "Frustration"),
        ("Wow! Detta är fantastiskt, älskar det!", "Excitement"),
        ("Jag förstår inte vad du menar?", "Confusion"),
        ("Det stämmer inte! Jag är inte sådan.", "Defensiveness"),
        ("Jag är så besviken på mig själv", "Disappointment"),
    ]

    detector = EmotionDetector()

    for message, expected in test_messages:
        emotion, confidence = detector.detect_emotion(message)
        print(f"Message: \"{message}\"")
        print(f"Detected: {emotion.value} (confidence: {confidence:.2f})")
        print(f"Expected: {expected}")
        print("-"*80)


def demo_rapport_building():
    """
    Show rapport building elements
    """
    print_section("RAPPORT BUILDING DEMO")

    builder = RapportBuilder()

    print("1. TRUST SIGNALS:")
    print(f"   → {builder.create_trust_signal('initial')}\n")

    print("2. BOUNDARY SETTING (Crisis):")
    crisis_msg = "Jag vill inte leva längre"
    print(f"   User: \"{crisis_msg}\"")
    print(f"   → {builder.create_boundary_statement('crisis')}\n")

    print("3. EMPATHETIC ACKNOWLEDGMENT:")
    print(f"   → {builder.create_empathetic_acknowledgment('Det är så svårt')}\n")

    print("4. TONE MATCHING:")
    from rapport_builder import EmotionalTone
    excited_response = builder.match_tone(
        EmotionalTone.EXCITED,
        "Detta är verkligen intressant att utforska!"
    )
    print(f"   [Excited user] → {excited_response}\n")


def main():
    """
    Run all demos
    """
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                                ║")
    print("║              THERAPEUTIC CONVERSATION SYSTEM - DEMONSTRATION                   ║")
    print("║                                                                                ║")
    print("║  Shows how AI uses professional psychological techniques to feel like         ║")
    print("║  a trained psychologist: empathetic, insightful, and genuinely helpful        ║")
    print("║                                                                                ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")

    # Run demos
    demo_technique_showcase()
    demo_emotion_detection()
    demo_rapport_building()

    print("\n" + "="*80)
    print("  CONVERSATION SCENARIOS")
    print("="*80)

    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    demo_scenario_4()

    print_section("DEMO COMPLETE")
    print("The therapeutic system integrates:")
    print("  1. Motivational Interviewing (OARS)")
    print("  2. Cognitive Reframing")
    print("  3. Socratic Method")
    print("  4. Validation & Normalization")
    print("  5. Emotional Calibration")
    print("  6. Pattern Recognition")
    print("  7. Strengths-Based Approach")
    print("  8. Rapport Building")
    print("  9. Conversation Pacing")
    print("  10. Therapeutic Alliance Management")
    print("\nResult: AI that feels warm, professional, and psychologically sophisticated.")
    print()


if __name__ == "__main__":
    main()
