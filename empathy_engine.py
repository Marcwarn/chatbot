"""
Empathy Engine - Emotional Intelligence for Conversational AI
Detects emotional tone in user messages and suggests appropriate empathetic responses
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class EmotionalTone(Enum):
    """Detected emotional tones in user messages"""
    HAPPY = "happy"
    EXCITED = "excited"
    CURIOUS = "curious"
    CONFUSED = "confused"
    ANXIOUS = "anxious"
    WORRIED = "worried"
    FRUSTRATED = "frustrated"
    SAD = "sad"
    DISAPPOINTED = "disappointed"
    DEFENSIVE = "defensive"
    SKEPTICAL = "skeptical"
    NEUTRAL = "neutral"
    REFLECTIVE = "reflective"


class EmotionalIntensity(Enum):
    """Intensity of emotional expression"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EmotionalState:
    """Represents detected emotional state"""
    primary_tone: EmotionalTone
    intensity: EmotionalIntensity
    secondary_tone: Optional[EmotionalTone] = None
    confidence: float = 0.0  # 0.0 to 1.0


class EmpathyEngine:
    """
    Analyzes user messages for emotional content and suggests
    appropriate empathetic response patterns
    """

    def __init__(self, language: str = "sv"):
        self.language = language
        self.emotional_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[EmotionalTone, Dict[str, List[str]]]:
        """Initialize emotional detection patterns for Swedish and English"""

        if self.language == "sv":
            return {
                EmotionalTone.ANXIOUS: {
                    'keywords': ['orolig', 'nervös', 'ängslig', 'rädd', 'stressad', 'ångest', 'panik'],
                    'phrases': ['jag är rädd att', 'vad om', 'tänk om', 'är orolig för', 'känner mig orolig'],
                    'punctuation': ['...', '??']
                },
                EmotionalTone.WORRIED: {
                    'keywords': ['bekymrad', 'fundersam', 'osäker', 'tveksam', 'tvivlar'],
                    'phrases': ['vet inte om', 'är det verkligen', 'kan det vara så att', 'undrar om'],
                    'punctuation': []
                },
                EmotionalTone.CONFUSED: {
                    'keywords': ['förvirrad', 'fattar inte', 'förstår inte', 'begriper inte', 'oklar'],
                    'phrases': ['vad betyder', 'hur kan det', 'varför är', 'förstår inte riktigt', 'hur ska jag'],
                    'punctuation': ['??', '?!']
                },
                EmotionalTone.FRUSTRATED: {
                    'keywords': ['frustrerad', 'irriterad', 'trött på', 'less', 'arg', 'förbannad'],
                    'phrases': ['det funkar inte', 'jag orkar inte', 'varför måste', 'alltid samma'],
                    'punctuation': ['!', '!!']
                },
                EmotionalTone.SAD: {
                    'keywords': ['ledsen', 'sorgsen', 'deprimerad', 'nere', 'deppig', 'mår dåligt'],
                    'phrases': ['känner mig ledsen', 'mår inte bra', 'känns hopplöst', 'allt är'],
                    'punctuation': ['...']
                },
                EmotionalTone.DISAPPOINTED: {
                    'keywords': ['besviken', 'misslyckad', 'dåligt', 'inte som jag trodde', 'tråkigt'],
                    'phrases': ['hade hoppats', 'trodde att', 'förväntade mig', 'inte vad jag'],
                    'punctuation': []
                },
                EmotionalTone.DEFENSIVE: {
                    'keywords': ['men', 'dock', 'faktiskt', 'verkligen', 'absolut inte'],
                    'phrases': ['det stämmer inte', 'jag är inte', 'det är inte sant', 'varför skulle jag'],
                    'punctuation': ['!']
                },
                EmotionalTone.SKEPTICAL: {
                    'keywords': ['verkligen', 'säkert', 'tveksam', 'tvivlar', 'osannolik'],
                    'phrases': ['är det verkligen', 'kan det stämma', 'låter konstigt', 'är säker på'],
                    'punctuation': ['?']
                },
                EmotionalTone.HAPPY: {
                    'keywords': ['glad', 'nöjd', 'positiv', 'kul', 'härligt', 'bra', 'toppen'],
                    'phrases': ['känns bra', 'gillar det', 'ser fram emot', 'det är kul'],
                    'punctuation': ['!']
                },
                EmotionalTone.EXCITED: {
                    'keywords': ['exalterad', 'entusiastisk', 'taggad', 'peppad', 'wow', 'fantastiskt'],
                    'phrases': ['så kul', 'jättebra', 'älskar det', 'underbart'],
                    'punctuation': ['!', '!!', '!!!']
                },
                EmotionalTone.CURIOUS: {
                    'keywords': ['nyfiken', 'intresserad', 'undrar', 'funderar', 'vill veta'],
                    'phrases': ['kan du berätta', 'hur fungerar', 'vad händer om', 'skulle vilja veta'],
                    'punctuation': ['?']
                },
                EmotionalTone.REFLECTIVE: {
                    'keywords': ['tänker', 'funderar', 'reflekterar', 'resonerar', 'överväger'],
                    'phrases': ['när jag tänker på det', 'ju mer jag funderar', 'har märkt att'],
                    'punctuation': []
                },
                EmotionalTone.NEUTRAL: {
                    'keywords': [],
                    'phrases': [],
                    'punctuation': []
                }
            }
        else:  # English
            return {
                EmotionalTone.ANXIOUS: {
                    'keywords': ['worried', 'nervous', 'anxious', 'scared', 'stressed', 'anxiety', 'panic'],
                    'phrases': ["i'm afraid that", 'what if', 'worried about', 'feeling anxious'],
                    'punctuation': ['...', '??']
                },
                EmotionalTone.WORRIED: {
                    'keywords': ['concerned', 'uncertain', 'unsure', 'hesitant', 'doubt'],
                    'phrases': ["don't know if", 'is it really', 'could it be that', 'wonder if'],
                    'punctuation': []
                },
                EmotionalTone.CONFUSED: {
                    'keywords': ['confused', "don't understand", "don't get", 'unclear', 'puzzled'],
                    'phrases': ['what does', 'how can', 'why is', "don't really understand", 'how should i'],
                    'punctuation': ['??', '?!']
                },
                EmotionalTone.FRUSTRATED: {
                    'keywords': ['frustrated', 'annoyed', 'tired of', 'angry', 'mad'],
                    'phrases': ["doesn't work", "can't take", 'why must', 'always the same'],
                    'punctuation': ['!', '!!']
                },
                EmotionalTone.SAD: {
                    'keywords': ['sad', 'depressed', 'down', 'feel bad', 'unhappy'],
                    'phrases': ['feel sad', "don't feel good", 'feels hopeless', 'everything is'],
                    'punctuation': ['...']
                },
                EmotionalTone.DISAPPOINTED: {
                    'keywords': ['disappointed', 'let down', 'failed', 'not as expected'],
                    'phrases': ['had hoped', 'thought that', 'expected', 'not what i'],
                    'punctuation': []
                },
                EmotionalTone.DEFENSIVE: {
                    'keywords': ['but', 'however', 'actually', 'really', 'absolutely not'],
                    'phrases': ["that's not true", "i'm not", "that's not right", 'why would i'],
                    'punctuation': ['!']
                },
                EmotionalTone.SKEPTICAL: {
                    'keywords': ['really', 'sure', 'doubt', 'unlikely', 'skeptical'],
                    'phrases': ['is it really', 'can that be', 'sounds strange', 'are you sure'],
                    'punctuation': ['?']
                },
                EmotionalTone.HAPPY: {
                    'keywords': ['happy', 'pleased', 'positive', 'fun', 'great', 'good', 'awesome'],
                    'phrases': ['feels good', 'like it', 'looking forward', "it's fun"],
                    'punctuation': ['!']
                },
                EmotionalTone.EXCITED: {
                    'keywords': ['excited', 'enthusiastic', 'pumped', 'wow', 'fantastic', 'amazing'],
                    'phrases': ['so fun', 'really great', 'love it', 'wonderful'],
                    'punctuation': ['!', '!!', '!!!']
                },
                EmotionalTone.CURIOUS: {
                    'keywords': ['curious', 'interested', 'wonder', 'thinking about', 'want to know'],
                    'phrases': ['can you tell', 'how does', 'what happens if', 'would like to know'],
                    'punctuation': ['?']
                },
                EmotionalTone.REFLECTIVE: {
                    'keywords': ['thinking', 'pondering', 'reflecting', 'considering'],
                    'phrases': ['when i think about', 'the more i think', 'have noticed that'],
                    'punctuation': []
                },
                EmotionalTone.NEUTRAL: {
                    'keywords': [],
                    'phrases': [],
                    'punctuation': []
                }
            }

    def detect_emotion(self, message: str) -> EmotionalState:
        """
        Detect emotional tone in user message
        Returns primary emotion, intensity, and confidence
        """

        message_lower = message.lower()
        emotion_scores = {}

        # Score each emotion based on pattern matching
        for emotion, patterns in self.emotional_patterns.items():
            if emotion == EmotionalTone.NEUTRAL:
                continue

            score = 0

            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in message_lower:
                    score += 2

            # Check phrases (more weight)
            for phrase in patterns['phrases']:
                if phrase in message_lower:
                    score += 3

            # Check punctuation
            for punct in patterns['punctuation']:
                if punct in message:
                    score += 1

            if score > 0:
                emotion_scores[emotion] = score

        # If no emotion detected, return neutral
        if not emotion_scores:
            return EmotionalState(
                primary_tone=EmotionalTone.NEUTRAL,
                intensity=EmotionalIntensity.LOW,
                confidence=0.5
            )

        # Get primary and secondary emotions
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        primary_emotion, primary_score = sorted_emotions[0]

        secondary_emotion = None
        if len(sorted_emotions) > 1:
            secondary_emotion = sorted_emotions[1][0]

        # Calculate intensity based on score
        if primary_score >= 6:
            intensity = EmotionalIntensity.HIGH
        elif primary_score >= 3:
            intensity = EmotionalIntensity.MEDIUM
        else:
            intensity = EmotionalIntensity.LOW

        # Confidence based on score difference
        if len(sorted_emotions) > 1:
            score_diff = primary_score - sorted_emotions[1][1]
            confidence = min(0.9, 0.5 + (score_diff * 0.1))
        else:
            confidence = 0.8

        return EmotionalState(
            primary_tone=primary_emotion,
            intensity=intensity,
            secondary_tone=secondary_emotion,
            confidence=confidence
        )

    def get_empathy_response_template(
        self,
        emotional_state: EmotionalState,
        language: str = "sv"
    ) -> Dict[str, List[str]]:
        """
        Get appropriate empathetic response templates based on detected emotion
        Returns dict with different types of responses
        """

        if language == "sv":
            return self._get_swedish_empathy_templates(emotional_state)
        else:
            return self._get_english_empathy_templates(emotional_state)

    def _get_swedish_empathy_templates(self, state: EmotionalState) -> Dict[str, List[str]]:
        """Swedish empathy response templates"""

        templates = {
            EmotionalTone.ANXIOUS: {
                'validation': [
                    "Jag kan förstå att du känner dig orolig.",
                    "Det är helt förståeligt att känna ångest kring det här.",
                    "Din oro är helt legitim.",
                ],
                'normalization': [
                    "Det är helt normalt att känna sig nervös i sådana situationer.",
                    "Många människor känner samma oro.",
                    "Du är inte ensam om att känna så.",
                ],
                'support': [
                    "Låt oss prata igenom det här tillsammans.",
                    "Jag är här för att hjälpa dig navigera de här känslorna.",
                    "Vi kan ta det steg för steg.",
                ]
            },
            EmotionalTone.CONFUSED: {
                'validation': [
                    "Jag hör att det känns oklart.",
                    "Det är helt okej att känna sig förvirrad.",
                    "Det här kan definitivt vara svårt att förstå.",
                ],
                'clarification': [
                    "Låt mig försöka förklara det på ett tydligare sätt.",
                    "Jag ska bryta ner det här så det blir lättare att greppa.",
                    "Låt mig ge ett konkret exempel.",
                ],
                'exploration': [
                    "Vad är det specifikt som känns oklart?",
                    "Vilken del känns mest förvirrande?",
                    "Kan du berätta mer om vad som inte riktigt klickar?",
                ]
            },
            EmotionalTone.FRUSTRATED: {
                'validation': [
                    "Jag hör din frustration.",
                    "Det låter verkligen frustrerande.",
                    "Jag förstår att det känns jobbigt.",
                ],
                'empathy': [
                    "Det är helt legitimt att känna så när saker inte går som man vill.",
                    "Frustration är ofta ett tecken på att något är viktigt för dig.",
                    "Jag kan förstå varför du känner så.",
                ],
                'reframing': [
                    "Låt oss se om vi kan hitta ett nytt perspektiv på det här.",
                    "Ibland kan frustration peka på vad vi verkligen behöver.",
                    "Vad tror du din frustration försöker säga dig?",
                ]
            },
            EmotionalTone.SAD: {
                'validation': [
                    "Det låter tungt.",
                    "Jag hör att du mår dåligt.",
                    "Det är okej att känna sorg.",
                ],
                'compassion': [
                    "Jag är ledsen att du känner så här.",
                    "Det låter som en svår period.",
                    "Tack för att du delar det med mig.",
                ],
                'gentle_support': [
                    "Skulle du vilja prata mer om vad som känns tungt?",
                    "Jag är här och lyssnar.",
                    "Ta den tid du behöver.",
                ]
            },
            EmotionalTone.DISAPPOINTED: {
                'validation': [
                    "Besvikelse är en svår känsla.",
                    "Jag förstår att det inte blev som du hoppats.",
                    "Det är helt okej att känna sig besviken.",
                ],
                'normalization': [
                    "När förväntningar inte möts är besvikelse naturlig.",
                    "Det visar att du hade hopp och förväntningar, vilket är mänskligt.",
                ],
                'forward': [
                    "Vad tror du att du kan lära dig av det här?",
                    "Hur skulle du vilja att det hade varit istället?",
                    "Finns det något du kan göra framåt?",
                ]
            },
            EmotionalTone.DEFENSIVE: {
                'gentle': [
                    "Jag märker att det här känns känsligt.",
                    "Jag vill absolut inte attackera dig.",
                    "Låt mig förtydliga vad jag menar.",
                ],
                'clarification': [
                    "Kanske formulerade jag mig otydligt.",
                    "Jag tror vi kan ha missförstått varandra.",
                    "Låt mig säga det på ett annat sätt.",
                ],
                'respect': [
                    "Din upplevelse är giltig.",
                    "Jag respekterar din synvinkel helt.",
                    "Det du känner är viktigt.",
                ]
            },
            EmotionalTone.SKEPTICAL: {
                'respect': [
                    "Det är bra att vara kritisk.",
                    "Din skepsis är helt förståelig.",
                    "Det är smart att ifrågasätta.",
                ],
                'evidence': [
                    "Låt mig dela vad forskningen säger.",
                    "Det finns evidens för det här från...",
                    "Jag förstår att det låter konstigt, men...",
                ],
                'dialogue': [
                    "Vad är det specifikt som du tvivlar på?",
                    "Vilka delar känns mest osannolika?",
                    "Vad skulle göra det mer trovärdigt för dig?",
                ]
            },
            EmotionalTone.HAPPY: {
                'sharing_joy': [
                    "Kul att höra!",
                    "Det låter jättebra!",
                    "Härligt att det känns så!",
                ],
                'encouragement': [
                    "Det är fantastiskt!",
                    "Fortsätt på den vägen!",
                    "Du verkar vara på rätt spår!",
                ],
                'exploration': [
                    "Vad är det som gör det så bra?",
                    "Berätta mer om vad som fungerar!",
                    "Hur kan du bygga vidare på det här?",
                ]
            },
            EmotionalTone.EXCITED: {
                'matching_energy': [
                    "Vilken energi!",
                    "Jag delar din entusiasm!",
                    "Det är så kul att se dig så taggad!",
                ],
                'validation': [
                    "Din entusiasm är smittande!",
                    "Det är underbart att se sådan glädje!",
                ],
                'channeling': [
                    "Hur ska du använda den här energin?",
                    "Vad blir nästa steg?",
                    "Vad gör dig mest exalterad?",
                ]
            },
            EmotionalTone.CURIOUS: {
                'welcoming': [
                    "Fantastisk fråga!",
                    "Kul att du är nyfiken!",
                    "Jag älskar när folk undrar över sådant här!",
                ],
                'engagement': [
                    "Låt mig förklara...",
                    "Det är faktiskt riktigt intressant...",
                    "Bra att du frågar om det!",
                ],
                'dialogue': [
                    "Vad fick dig att tänka på det?",
                    "Har du några egna teorier?",
                    "Vad tror du själv?",
                ]
            },
            EmotionalTone.REFLECTIVE: {
                'validation': [
                    "Det är värdefullt att reflektera.",
                    "Jag uppskattar din tankeprocess.",
                    "Det är bra att du tänker djupt på det här.",
                ],
                'deepening': [
                    "Fortsätt utveckla den tanken...",
                    "Vart leder dina funderingar?",
                    "Vad mer märker du när du reflekterar?",
                ],
                'insight': [
                    "Det låter som att du är på väg till en insikt.",
                    "Du verkar ha en viktig tanke där.",
                    "Den reflektionen kan leda till något viktigt.",
                ]
            },
            EmotionalTone.NEUTRAL: {
                'engagement': [
                    "Intressant.",
                    "Jag lyssnar.",
                    "Berätta mer.",
                ],
                'exploration': [
                    "Hur tänker du kring det?",
                    "Vad mer finns att säga?",
                    "Vill du utveckla det?",
                ]
            }
        }

        return templates.get(state.primary_tone, templates[EmotionalTone.NEUTRAL])

    def _get_english_empathy_templates(self, state: EmotionalState) -> Dict[str, List[str]]:
        """English empathy response templates"""

        templates = {
            EmotionalTone.ANXIOUS: {
                'validation': [
                    "I can understand that you're feeling worried.",
                    "It's completely understandable to feel anxious about this.",
                    "Your worry is completely legitimate.",
                ],
                'normalization': [
                    "It's completely normal to feel nervous in such situations.",
                    "Many people feel the same worry.",
                    "You're not alone in feeling this way.",
                ],
                'support': [
                    "Let's talk through this together.",
                    "I'm here to help you navigate these feelings.",
                    "We can take this step by step.",
                ]
            },
            EmotionalTone.CONFUSED: {
                'validation': [
                    "I hear that it feels unclear.",
                    "It's completely okay to feel confused.",
                    "This can definitely be hard to understand.",
                ],
                'clarification': [
                    "Let me try to explain this more clearly.",
                    "I'll break this down so it's easier to grasp.",
                    "Let me give you a concrete example.",
                ],
                'exploration': [
                    "What specifically feels unclear?",
                    "Which part feels most confusing?",
                    "Can you tell me more about what's not quite clicking?",
                ]
            },
            EmotionalTone.FRUSTRATED: {
                'validation': [
                    "I hear your frustration.",
                    "That sounds really frustrating.",
                    "I understand that feels difficult.",
                ],
                'empathy': [
                    "It's completely legitimate to feel that way when things don't go as planned.",
                    "Frustration is often a sign that something is important to you.",
                    "I can understand why you feel that way.",
                ],
                'reframing': [
                    "Let's see if we can find a new perspective on this.",
                    "Sometimes frustration can point to what we really need.",
                    "What do you think your frustration is trying to tell you?",
                ]
            },
            EmotionalTone.HAPPY: {
                'sharing_joy': [
                    "Great to hear!",
                    "That sounds wonderful!",
                    "Lovely that it feels that way!",
                ],
                'encouragement': [
                    "That's fantastic!",
                    "Keep going on that path!",
                    "You seem to be on the right track!",
                ],
                'exploration': [
                    "What makes it so good?",
                    "Tell me more about what's working!",
                    "How can you build on this?",
                ]
            },
            # Add more English templates as needed
        }

        return templates.get(state.primary_tone, templates.get(EmotionalTone.NEUTRAL, {}))

    def generate_empathetic_opening(
        self,
        emotional_state: EmotionalState,
        language: str = "sv"
    ) -> str:
        """
        Generate an empathetic opening line based on detected emotion
        This should be used at the start of a response
        """

        templates = self.get_empathy_response_template(emotional_state, language)

        # Priority: validation > normalization > support
        if 'validation' in templates and templates['validation']:
            return templates['validation'][0]
        elif 'normalization' in templates and templates['normalization']:
            return templates['normalization'][0]
        elif 'support' in templates and templates['support']:
            return templates['support'][0]
        else:
            return list(templates.values())[0][0] if templates else ""


# Example usage
if __name__ == "__main__":
    engine = EmpathyEngine(language="sv")

    # Test various messages
    test_messages = [
        "Jag är så orolig över mina resultat på testet...",
        "Fattar inte vad låg samvetsgrannhet betyder??",
        "Det här är så frustrerande! Varför fick jag låg extraversion?",
        "Jag känner mig ledsen över att jag är så neurotisk",
        "Wow! Det här stämmer ju perfekt på mig!",
        "Jag undrar hur jag kan använda det här i mitt jobb?",
        "Är det verkligen säkert att låg vänlighet är okej?",
    ]

    print("=== EMPATHY ENGINE TEST ===\n")

    for msg in test_messages:
        print(f"USER: {msg}")
        emotion = engine.detect_emotion(msg)
        print(f"DETECTED: {emotion.primary_tone.value} (intensity: {emotion.intensity.value}, confidence: {emotion.confidence:.2f})")

        opening = engine.generate_empathetic_opening(emotion, "sv")
        print(f"EMPATHETIC OPENING: {opening}")
        print("-" * 80)
