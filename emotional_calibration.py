"""
Emotional Calibration - Detect emotions in user text and calibrate responses accordingly
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
import re


class EmotionType(Enum):
    """Types of emotions to detect"""
    ANXIETY = "anxiety"
    CONFUSION = "confusion"
    DEFENSIVENESS = "defensiveness"
    EXCITEMENT = "excitement"
    DISAPPOINTMENT = "disappointment"
    FRUSTRATION = "frustration"
    SADNESS = "sadness"
    ANGER = "anger"
    HOPE = "hope"
    CURIOSITY = "curiosity"
    SHAME = "shame"
    PRIDE = "pride"
    NEUTRAL = "neutral"


class EmotionDetector:
    """
    Detect emotions in user's text based on language patterns.
    """

    # Emotion vocabulary patterns
    EMOTION_PATTERNS = {
        EmotionType.ANXIETY: {
            'keywords': ['orolig', 'nervös', 'ängslig', 'stressad', 'rädd', 'spänd', 'panik'],
            'phrases': ['vad händer om', 'jag är rädd att', 'tänk om', 'oroar mig för'],
            'patterns': [r'vad om.*\?', r'skulle kunna.*fel'],
            'intensity_modifiers': ['mycket', 'jätte', 'så', 'extremt', 'verkligen']
        },
        EmotionType.CONFUSION: {
            'keywords': ['förvirrad', 'osäker', 'vet inte', 'förstår inte', 'oklart', 'lost'],
            'phrases': ['vad menar du', 'hur kan det', 'förstår inte hur', 'varför skulle'],
            'patterns': [r'begriper inte', r'hänger inte med'],
            'questions': True  # High question count indicates confusion
        },
        EmotionType.DEFENSIVENESS: {
            'keywords': ['men jag', 'faktiskt', 'verkligen'],
            'phrases': ['men jag är inte', 'det stämmer inte', 'du förstår inte', 'det är inte så',
                       'jag är inte sådan', 'det där är fel'],
            'patterns': [r'men.*inte', r'nej.*jag är'],
            'tone': 'contradictory'
        },
        EmotionType.EXCITEMENT: {
            'keywords': ['wow', 'amazing', 'fantastiskt', 'älskar', 'superbra', 'underbart', 'awesome'],
            'phrases': ['så coolt', 'hur kul', 'jag älskar', 'detta är fantastic'],
            'punctuation': ['!', '!!', '!!!'],
            'capitals': True  # ALL CAPS indicates excitement
        },
        EmotionType.DISAPPOINTMENT: {
            'keywords': ['besviken', 'tråkigt', 'synd', 'ledsen', 'hade hoppats'],
            'phrases': ['tråkigt att', 'synd att', 'hade hoppats på', 'jag önskade', 'tyvärr'],
            'patterns': [r'hade velat', r'önskade att'],
        },
        EmotionType.FRUSTRATION: {
            'keywords': ['frustrerad', 'irriterad', 'less', 'trött på', 'jobbigt', 'störande'],
            'phrases': ['så jobbigt', 'varför är det', 'detta funkar inte', 'går inte'],
            'patterns': [r'försökt.*men', r'alltid.*problem'],
        },
        EmotionType.SADNESS: {
            'keywords': ['ledsen', 'sorglig', 'deprimerad', 'nere', 'mörkt', 'tung', 'tom'],
            'phrases': ['mår dåligt', 'känner mig tom', 'ingen mening', 'orkar inte'],
            'patterns': [r'känner.*ingenting', r'allt.*meningslöst'],
        },
        EmotionType.ANGER: {
            'keywords': ['arg', 'förbannad', 'ilsk', 'rasande', 'vred'],
            'phrases': ['så jävla', 'fan också', 'blir arg', 'gör mig rasande'],
            'patterns': [r'hatar när', r'inte okej att'],
            'profanity': True
        },
        EmotionType.HOPE: {
            'keywords': ['hoppas', 'hoppfull', 'kanske', 'möjligen', 'skulle kunna'],
            'phrases': ['jag hoppas att', 'kanske kan', 'det skulle vara', 'ser fram emot'],
            'patterns': [r'om jag.*skulle', r'kanske.*bättre'],
        },
        EmotionType.CURIOSITY: {
            'keywords': ['intressant', 'nyfiken', 'fascinerande', 'undrar', 'spännande'],
            'phrases': ['jag undrar', 'skulle vilja veta', 'hur kommer det sig', 'berätta mer'],
            'questions': True,
            'tone': 'exploratory'
        },
        EmotionType.SHAME: {
            'keywords': ['skäms', 'pinsamt', 'patetisk', 'värdelös', 'generad', 'skam'],
            'phrases': ['skäms för', 'så pinsamt', 'fel på mig', 'borde inte'],
            'patterns': [r'är.*misslyckande', r'duger inte'],
        },
        EmotionType.PRIDE: {
            'keywords': ['stolt', 'lyckats', 'nöjd', 'äntligen', 'framgång'],
            'phrases': ['jag lyckades', 'äntligen fick jag', 'nöjd med', 'stolt över'],
            'patterns': [r'gjorde det!', r'klarade.*av'],
        }
    }

    @staticmethod
    def detect_emotion(text: str, conversation_history: List[str] = None) -> Tuple[EmotionType, float]:
        """
        Detect primary emotion in text.

        Args:
            text: The text to analyze
            conversation_history: Previous messages for context

        Returns:
            Tuple of (emotion_type, confidence_score 0-1)
        """
        text_lower = text.lower()
        emotion_scores = {}

        # Score each emotion
        for emotion_type, patterns in EmotionDetector.EMOTION_PATTERNS.items():
            score = 0.0

            # Check keywords
            if 'keywords' in patterns:
                keyword_matches = sum(1 for kw in patterns['keywords'] if kw in text_lower)
                score += keyword_matches * 0.3

            # Check phrases
            if 'phrases' in patterns:
                phrase_matches = sum(1 for phrase in patterns['phrases'] if phrase in text_lower)
                score += phrase_matches * 0.5

            # Check regex patterns
            if 'patterns' in patterns:
                for pattern in patterns['patterns']:
                    if re.search(pattern, text_lower):
                        score += 0.4

            # Check punctuation
            if 'punctuation' in patterns:
                for punct in patterns['punctuation']:
                    score += text.count(punct) * 0.2

            # Check for questions (confusion/curiosity)
            if patterns.get('questions') and '?' in text:
                question_count = text.count('?')
                score += question_count * 0.3

            # Check for capitals (excitement)
            if patterns.get('capitals'):
                capital_words = [word for word in text.split() if word.isupper() and len(word) > 2]
                score += len(capital_words) * 0.3

            # Intensity modifiers
            if 'intensity_modifiers' in patterns:
                modifier_count = sum(1 for mod in patterns['intensity_modifiers'] if mod in text_lower)
                score *= (1 + modifier_count * 0.2)  # Amplify score

            emotion_scores[emotion_type] = score

        # Find highest scoring emotion
        if not any(score > 0 for score in emotion_scores.values()):
            return (EmotionType.NEUTRAL, 1.0)

        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        emotion_type, raw_score = max_emotion

        # Normalize confidence (cap at 1.0)
        confidence = min(raw_score / 2.0, 1.0)  # Divide by 2 to normalize

        # Require minimum confidence threshold
        if confidence < 0.3:
            return (EmotionType.NEUTRAL, 1.0)

        return (emotion_type, confidence)

    @staticmethod
    def detect_multiple_emotions(text: str) -> List[Tuple[EmotionType, float]]:
        """
        Detect multiple emotions that might be present.
        Returns list of (emotion, confidence) sorted by confidence.
        """
        text_lower = text.lower()
        emotion_scores = []

        for emotion_type, patterns in EmotionDetector.EMOTION_PATTERNS.items():
            score = 0.0

            # Simplified scoring (same as detect_emotion but for all)
            if 'keywords' in patterns:
                keyword_matches = sum(1 for kw in patterns['keywords'] if kw in text_lower)
                score += keyword_matches * 0.3

            if 'phrases' in patterns:
                phrase_matches = sum(1 for phrase in patterns['phrases'] if phrase in text_lower)
                score += phrase_matches * 0.5

            confidence = min(score / 2.0, 1.0)

            if confidence >= 0.3:
                emotion_scores.append((emotion_type, confidence))

        # Sort by confidence
        emotion_scores.sort(key=lambda x: x[1], reverse=True)

        return emotion_scores if emotion_scores else [(EmotionType.NEUTRAL, 1.0)]


class ResponseCalibrator:
    """
    Calibrate responses based on detected emotion.
    """

    @staticmethod
    def calibrate_for_emotion(
        emotion: EmotionType,
        base_response: str,
        confidence: float = 1.0
    ) -> str:
        """
        Adjust response based on detected emotion.

        Args:
            emotion: Detected emotion
            base_response: The base response to calibrate
            confidence: Confidence in emotion detection (0-1)

        Returns:
            Calibrated response
        """
        # Only calibrate if confidence is reasonable
        if confidence < 0.4:
            return base_response

        calibrations = {
            EmotionType.ANXIETY: ResponseCalibrator._calibrate_anxiety,
            EmotionType.CONFUSION: ResponseCalibrator._calibrate_confusion,
            EmotionType.DEFENSIVENESS: ResponseCalibrator._calibrate_defensiveness,
            EmotionType.EXCITEMENT: ResponseCalibrator._calibrate_excitement,
            EmotionType.DISAPPOINTMENT: ResponseCalibrator._calibrate_disappointment,
            EmotionType.FRUSTRATION: ResponseCalibrator._calibrate_frustration,
            EmotionType.SADNESS: ResponseCalibrator._calibrate_sadness,
            EmotionType.ANGER: ResponseCalibrator._calibrate_anger,
            EmotionType.SHAME: ResponseCalibrator._calibrate_shame,
        }

        calibrator = calibrations.get(emotion)
        if calibrator:
            return calibrator(base_response)

        return base_response

    @staticmethod
    def _calibrate_anxiety(response: str) -> str:
        """Anxious user → Reassurance first, then information"""
        reassurance = "Först och främst: Du är inte ensam i det du känner, och det finns inga rätt eller fel här. "

        # Make response calmer, shorter sentences
        calm_response = response.replace('. ', '.\n\n')

        return reassurance + calm_response + "\n\nTa det i din egen takt."

    @staticmethod
    def _calibrate_confusion(response: str) -> str:
        """Confused user → Simplify, use examples, check understanding"""
        clarification = "Låt mig förklara det tydligare. "

        # Add understanding check
        check = "\n\nGer det mer mening nu? Säg till om något är oklart så förklarar jag annorlunda."

        return clarification + response + check

    @staticmethod
    def _calibrate_defensiveness(response: str) -> str:
        """Defensive user → Validate feelings, gentle reframing, emphasize choice"""
        validation = "Jag hör att något jag sa inte landade rätt. Det var inte min mening. "

        choice = "\n\nDu vet bäst hur det är för dig - jag erbjuder bara ett perspektiv att överväga eller ignorera."

        # Soften language
        softened = response.replace('du är', 'du verkar').replace('det betyder', 'det kan betyda')

        return validation + softened + choice

    @staticmethod
    def _calibrate_excitement(response: str) -> str:
        """Excited user → Match enthusiasm, dive deeper"""
        enthusiasm = "Jag älskar din energi! "

        deeper = " Låt oss dyka djupare i det här!"

        return enthusiasm + response + deeper

    @staticmethod
    def _calibrate_disappointment(response: str) -> str:
        """Disappointed user → Empathy, alternative perspectives, hope"""
        empathy = "Jag förstår din besvikelse. Det är helt naturligt att känna så. "

        hope = "\n\nOch ändå - detta är inte hela bilden av vem du är. Låt oss utforska andra perspektiv."

        return empathy + response + hope

    @staticmethod
    def _calibrate_frustration(response: str) -> str:
        """Frustrated user → Acknowledge frustration, validate effort, problem-solve"""
        acknowledgment = "Jag hör din frustration och den är helt legitim. "

        validate = "Det du kämpar med är genuint utmanande. "

        action = "\n\nLåt oss se om vi kan hitta en ny approach som fungerar bättre för dig."

        return acknowledgment + validate + response + action

    @staticmethod
    def _calibrate_sadness(response: str) -> str:
        """Sad user → Empathy, validation, gentle hope"""
        empathy = "Jag hör att du mår tungt just nu. Din sorg är legitim och förtjänar att få ta plats. "

        # Softer, more spacious response
        gentle_response = response.replace('. ', '.\n\n')

        gentle_hope = "\n\nDet är okej att må dåligt. Och när du är redo finns det vägar framåt."

        return empathy + gentle_response + gentle_hope

    @staticmethod
    def _calibrate_anger(response: str) -> str:
        """Angry user → Validate anger, explore what's underneath"""
        validation = "Din ilska är giltig - den säger att något viktigt för dig har kränkts. "

        explore = "\n\nIlska har ofta ett budskap. Vad är det som verkligen sårar eller frustrerar dig här?"

        return validation + response + explore

    @staticmethod
    def _calibrate_shame(response: str) -> str:
        """Shame → Active shame reduction, compassion"""
        compassion = "Jag vill pausa här och säga: Det du känner är mänskligt. Det är inte något att skämmas för. "

        normalize = "Många känner så här, även om det sällan pratas om. Du är inte ensam och du är inte 'fel'. "

        # Remove any language that could increase shame
        shame_free = response.replace('borde', 'kunde').replace('måste', 'kan')

        return compassion + normalize + shame_free


class EmotionalResponse:
    """
    Generate emotionally attuned responses.
    """

    @staticmethod
    def create_opening(emotion: EmotionType) -> str:
        """
        Create an emotion-appropriate opening for the response.
        """
        openings = {
            EmotionType.ANXIETY: "Jag hör din oro.",
            EmotionType.CONFUSION: "Låt mig klargöra det här.",
            EmotionType.DEFENSIVENESS: "Jag hör att du reagerar på det jag sa.",
            EmotionType.EXCITEMENT: "Din entusiasm är smittande!",
            EmotionType.DISAPPOINTMENT: "Jag hör din besvikelse.",
            EmotionType.FRUSTRATION: "Det låter verkligt frustrerande.",
            EmotionType.SADNESS: "Jag hör att du mår tungt.",
            EmotionType.ANGER: "Din ilska är legitim.",
            EmotionType.HOPE: "Jag hör hoppet i det du säger.",
            EmotionType.CURIOSITY: "Vilken bra fråga!",
            EmotionType.SHAME: "Tack för att du delar något så sårbart.",
            EmotionType.PRIDE: "Det är värt att fira!",
            EmotionType.NEUTRAL: "",
        }

        return openings.get(emotion, "")

    @staticmethod
    def suggest_emotion_regulation(emotion: EmotionType, intensity: str = "moderate") -> Optional[str]:
        """
        Suggest emotion regulation strategies when appropriate.
        Only for intense negative emotions.
        """
        if intensity != "high":
            return None

        strategies = {
            EmotionType.ANXIETY: (
                "När ångesten är stark, prova:\n"
                "• 4-7-8 andning: Andas in 4 sekunder, håll 7, andas ut 8\n"
                "• Grounding: Namnge 5 saker du ser, 4 du hör, 3 du känner, 2 du luktar, 1 du smakar\n"
                "• Skriv ner dina orostankar för att få dem ur huvudet"
            ),
            EmotionType.ANGER: (
                "När ilskan är intensiv:\n"
                "• Ta timeout innan du agerar\n"
                "• Fysisk aktivitet (spring, slå i kudde, gå snabbt)\n"
                "• Skriv ett brev du inte skickar\n"
                "• Fråga: 'Vad behöver jag verkligen här?'"
            ),
            EmotionType.SADNESS: (
                "När sorgen känns överväldigande:\n"
                "• Tillåt dig själv att gråta - tårar släpper ut stresshormoner\n"
                "• Fysisk kontakt (kram, varm dusch, mjuk filt)\n"
                "• Små, konkreta handlingar (duscha, dricka vatten, gå ut)\n"
                "• Nå ut till någon du litar på"
            ),
        }

        return strategies.get(emotion)


def calibrate_response(
    user_message: str,
    base_response: str,
    conversation_history: List[str] = None
) -> str:
    """
    Main function to detect emotion and calibrate response.

    Args:
        user_message: User's message
        base_response: Uncalibrated response
        conversation_history: Previous messages for context

    Returns:
        Emotionally calibrated response
    """
    # Detect emotion
    emotion, confidence = EmotionDetector.detect_emotion(user_message, conversation_history)

    # Add appropriate opening
    opening = EmotionalResponse.create_opening(emotion)

    # Calibrate the response
    calibrated = ResponseCalibrator.calibrate_for_emotion(emotion, base_response, confidence)

    # Add opening if we detected strong emotion
    if confidence > 0.6 and opening:
        calibrated = opening + " " + calibrated

    return calibrated
