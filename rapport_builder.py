"""
Rapport Builder - Build therapeutic alliance through trust, attunement, and boundaries
"""

from typing import Dict, List, Optional
from enum import Enum


class EmotionalTone(Enum):
    """User's emotional tone detected from messages"""
    SERIOUS = "serious"
    CASUAL = "casual"
    DISTRESSED = "distressed"
    EXCITED = "excited"
    SKEPTICAL = "skeptical"
    REFLECTIVE = "reflective"


class LanguageStyle(Enum):
    """User's language style"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"


class RapportBuilder:
    """
    Build therapeutic alliance - the relationship between coach and client
    that enables effective work together.
    """

    @staticmethod
    def create_trust_signal(context: str = "initial") -> str:
        """
        Build trust through confidentiality reminders and non-judgmental stance.
        """
        signals = {
            'initial': "Innan vi börjar vill jag att du ska veta: Det här är en trygg plats för reflektion. Jag är här för att lyssna utan att döma, och allt du delar stannar mellan oss.",

            'vulnerability': "Tack för att du delar något så personligt. Det krävs mod att vara sårbar, och jag vill att du ska veta att din öppenhet tas emot med respekt och utan bedömning.",

            'shame': "Det du berättar om är ingenting att skämmas för. Jag är här för att stötta dig, inte för att döma. Du är trygg att utforska även de svåraste känslorna här.",

            'doubt': "Jag förstår om du känner dig osäker på om detta hjälper. Det är helt okej att ifrågasätta processen - din ärlighet gör faktiskt vår dialog starkare.",

            'sensitive_topic': "Jag märker att vi rör vid något känsligt. Vi tar det i den takt som känns rätt för dig. Du bestämmer vad du vill dela och när.",
        }

        return signals.get(context, signals['initial'])

    @staticmethod
    def create_boundary_statement(situation: str) -> str:
        """
        Clear communication about AI limitations and when to seek professional help.
        """
        boundaries = {
            'crisis': "Jag märker att du mår mycket dåligt just nu. Som AI kan jag erbjuda stöd och reflektion, men inte akut hjälp. Om du har tankar på att skada dig själv eller andra, vänligen kontakta:\n\n🔴 112 för akut hjälp\n📞 Mind Självmordslinjen: 90101\n💬 1177 för vårdråd\n\nJag finns här för samtal när du är i säkerhet.",

            'medical': "Det du beskriver kan ha medicinska orsaker. Jag är baserad på psykologisk forskning och kan hjälpa dig utforska mönster och strategier, men för medicinska bedömningar behöver du kontakta läkare eller legitimerad psykolog.",

            'trauma': "Det du berättar om låter som en traumatisk upplevelse. Trauma kräver ofta professionell behandling som EMDR eller traumafokuserad KBT. Jag kan ge stöd och psykoedukation, men jag rekommenderar starkt att du pratar med en legitimerad psykolog som är specialist på trauma.",

            'diagnosis': "Jag kan inte ställa diagnoser eller bedöma om du har en psykisk funktionsnedsättning. Om du misstänker att du har ADHD, autism, depression eller liknande, kontakta en legitimerad psykolog eller psykiater för utredning.",

            'limitation': "Som AI-coach är jag baserad på evidensbaserad psykologi och Big Five-forskning, men jag är inte en ersättning för en mänsklig terapeut. Jag kan inte:\n- Ställa diagnoser\n- Förskriva behandling\n- Hantera akuta kriser\n- Ersätta professionell terapi\n\nJag kan däremot erbjuda psykoedukation, självreflektion och coachning kring personlighetsutveckling.",

            'scope': "Det där faller lite utanför min expertis som personlighetscoach. Jag är specialist på Big Five och personlighetsutveckling, men för medicinska eller juridiska frågor behöver du prata med en relevant expert.",
        }

        return boundaries.get(situation, boundaries['limitation'])

    @staticmethod
    def detect_emotional_tone(message: str, conversation_history: List[Dict] = None) -> EmotionalTone:
        """
        Detect the user's emotional tone to match appropriately.
        """
        message_lower = message.lower()

        # Distressed - immediate priority
        distress_indicators = ['vill dö', 'orkar inte', 'mår så dåligt', 'hopplöst', 'ger upp', 'ingen mening']
        if any(indicator in message_lower for indicator in distress_indicators):
            return EmotionalTone.DISTRESSED

        # Excited - high energy, positive
        excitement_indicators = ['wow', 'amazing', 'fantastiskt', 'älskar', 'superbra', '!']
        exclamation_count = message.count('!')
        if exclamation_count >= 2 or any(indicator in message_lower for indicator in excitement_indicators):
            return EmotionalTone.EXCITED

        # Skeptical - questioning, doubting
        skeptical_indicators = ['verkligen', 'tveksam', 'osäker på', 'stämmer det', 'låter konstigt']
        if any(indicator in message_lower for indicator in skeptical_indicators) and '?' in message:
            return EmotionalTone.SKEPTICAL

        # Reflective - thoughtful, introspective
        reflective_indicators = ['tänker på', 'funderar', 'reflekterar', 'märkt att', 'insett att']
        if any(indicator in message_lower for indicator in reflective_indicators):
            return EmotionalTone.REFLECTIVE

        # Serious - longer messages, serious topics, no emojis
        serious_topics = ['karriär', 'depression', 'ångest', 'relation', 'problem', 'svårt']
        if any(topic in message_lower for topic in serious_topics) and len(message) > 100:
            return EmotionalTone.SERIOUS

        # Default to casual
        return EmotionalTone.CASUAL

    @staticmethod
    def detect_language_style(message: str) -> LanguageStyle:
        """
        Detect user's language style to mirror appropriately.
        """
        message_lower = message.lower()

        # Formal - uses formal pronouns, complete sentences
        formal_indicators = ['vore', 'vänligen', 'tack så mycket', 'skulle vilja']
        if any(indicator in message_lower for indicator in formal_indicators):
            return LanguageStyle.FORMAL

        # Technical - uses psychological terms
        technical_terms = ['neuroticism', 'extroversion', 'trait', 'percentil', 'korrelation']
        if any(term in message_lower for term in technical_terms):
            return LanguageStyle.TECHNICAL

        # Emotional - shares feelings, uses emotion words
        emotion_words = ['känner', 'mår', 'ledsen', 'glad', 'arg', 'rädd', 'orolig', 'älskar', 'hatar']
        emotion_count = sum(1 for word in emotion_words if word in message_lower)
        if emotion_count >= 2:
            return LanguageStyle.EMOTIONAL

        # Default to casual
        return LanguageStyle.CASUAL

    @staticmethod
    def match_tone(tone: EmotionalTone, base_response: str) -> str:
        """
        Adjust response to match user's emotional tone.
        """
        prefixes = {
            EmotionalTone.DISTRESSED: "Jag hör att du mår riktigt dåligt. ",
            EmotionalTone.EXCITED: "Jag hör din entusiasm! ",
            EmotionalTone.SKEPTICAL: "Det är bra att du ifrågasätter. ",
            EmotionalTone.REFLECTIVE: "Du låter eftertänksam. ",
            EmotionalTone.SERIOUS: "",
            EmotionalTone.CASUAL: "",
        }

        # Add appropriate prefix
        prefix = prefixes.get(tone, "")

        # Adjust punctuation/energy level
        if tone == EmotionalTone.EXCITED:
            # Can add slightly more energy (but still professional)
            return prefix + base_response
        elif tone == EmotionalTone.DISTRESSED:
            # Calm, reassuring, slower pace (use more periods, shorter sentences)
            return prefix + base_response.replace('. ', '.\n\n')
        else:
            return prefix + base_response

    @staticmethod
    def create_empathetic_acknowledgment(user_message: str, detected_emotion: str = None) -> str:
        """
        Acknowledge what user is experiencing with empathy.
        """
        message_lower = user_message.lower()

        # Detect emotion if not provided
        if not detected_emotion:
            if any(word in message_lower for word in ['svårt', 'jobbigt', 'tufft', 'kämpigt']):
                detected_emotion = 'struggle'
            elif any(word in message_lower for word in ['förvirrad', 'osäker', 'vet inte']):
                detected_emotion = 'confusion'
            elif any(word in message_lower for word in ['glad', 'nöjd', 'lycklig']):
                detected_emotion = 'joy'
            elif any(word in message_lower for word in ['besviken', 'ledsen', 'sorglig']):
                detected_emotion = 'disappointment'
            else:
                detected_emotion = 'neutral'

        acknowledgments = {
            'struggle': "Det låter som en verkligt utmanande situation. Jag uppskattar att du delar det med mig.",
            'confusion': "Jag förstår att det känns förvirrande. Låt oss utforska det tillsammans.",
            'joy': "Det är härligt att höra! Din glädje smittar.",
            'disappointment': "Jag hör din besvikelse, och den är helt förståelig.",
            'neutral': "Tack för att du delar det med mig.",
        }

        return acknowledgments.get(detected_emotion, acknowledgments['neutral'])

    @staticmethod
    def appropriate_self_disclosure(topic: str) -> Optional[str]:
        """
        Fictional but relatable self-disclosure to build connection.
        Use sparingly and only when it serves the client.
        """
        # NOTE: These are fictional examples that an AI might use to build rapport
        # They should be clearly framed as general observations, not personal experiences

        disclosures = {
            'introversion': "Många av de personer jag pratar med som är introverta beskriver en känsla av att 'något är fel' med dem i en extrovert kultur. Men när vi utforskar det djupare upptäcker de ofta att deras introversion är en styrka.",

            'perfectionism': "Perfektionism är något jag möter ofta i samtal här. Det är intressant hur det kan driva oss till excellens men samtidigt lamslå oss med rädsla att misslyckas.",

            'career_change': "Karriäromställning är något många brottas med - särskilt personer med hög openness som ser alla möjligheter men har svårt att välja.",

            'imposter_syndrome': "Så många högt presterande personer jag pratar med känner sig som bedragare. Det är nästan som att framgång och imposter syndrome hänger ihop.",
        }

        topic_lower = topic.lower()
        for key, disclosure in disclosures.items():
            if key in topic_lower:
                return disclosure

        return None

    @staticmethod
    def adjust_pacing(user_preference: str = "moderate") -> Dict[str, any]:
        """
        Adjust conversation pacing based on user's apparent preference.
        Returns configuration for response generation.
        """
        pacing_configs = {
            'quick': {
                'response_length': 'short',  # 2-3 sentences
                'questions_per_response': 1,
                'depth': 'surface',
                'example_usage': 'minimal',
                'tone': 'direct'
            },
            'moderate': {
                'response_length': 'medium',  # 1 paragraph
                'questions_per_response': 1-2,
                'depth': 'balanced',
                'example_usage': 'moderate',
                'tone': 'warm'
            },
            'deep': {
                'response_length': 'long',  # 2-3 paragraphs
                'questions_per_response': 2-3,
                'depth': 'deep',
                'example_usage': 'extensive',
                'tone': 'reflective'
            }
        }

        return pacing_configs.get(user_preference, pacing_configs['moderate'])

    @staticmethod
    def non_judgmental_language(statement: str) -> str:
        """
        Convert potentially judgmental language to non-judgmental.
        """
        replacements = {
            'du borde': 'du kanske vill överväga',
            'du måste': 'det kan vara värdefullt att',
            'det är fel': 'det kan finnas andra perspektiv',
            'du har fel': 'jag undrar om det finns andra sätt att se på det',
            'problemet är': 'utmaningen verkar vara',
            'du ska': 'en möjlighet är att',
            'varför gjorde du': 'vad låg bakom ditt val att',
        }

        modified = statement.lower()
        for judgmental, neutral in replacements.items():
            modified = modified.replace(judgmental, neutral)

        return modified


class TherapeuticAlliance:
    """
    Manage the overall therapeutic relationship quality.
    """

    @staticmethod
    def check_alliance_rupture(message: str) -> Optional[str]:
        """
        Detect if there's a rupture in the therapeutic alliance (user seems
        disconnected, defensive, or mistrustful).
        """
        message_lower = message.lower()

        # Signs of rupture
        rupture_signs = {
            'defensiveness': ['men jag är inte', 'det stämmer inte', 'du förstår inte', 'det är inte så'],
            'disconnection': ['spelar ingen roll', 'låt vara', 'whatever', 'okej då'],
            'mistrust': ['hur vet du', 'vem säger att', 'det är lätt för dig att säga'],
            'frustration': ['detta hjälper inte', 'vi kommer ingen vart', 'slösar min tid'],
        }

        for rupture_type, indicators in rupture_signs.items():
            if any(indicator in message_lower for indicator in indicators):
                return rupture_type

        return None

    @staticmethod
    def repair_alliance(rupture_type: str) -> str:
        """
        Repair therapeutic alliance when rupture is detected.
        """
        repairs = {
            'defensiveness': "Jag märker att något jag sa fick dig att gå i försvar. Det var inte min mening. Kan du hjälpa mig förstå vad som inte stämde för dig i det jag sa?",

            'disconnection': "Jag känner att vi tappade kontakten lite där. Vad skulle göra det här samtalet mer värdefullt för dig just nu?",

            'mistrust': "Du har helt rätt i att ifrågasätta. Jag kan inte veta exakt hur det är för dig - bara du vet det. Hjälp mig förstå bättre.",

            'frustration': "Jag hör din frustration och jag förstår den. Det här samtalet ska vara till hjälp, inte försvåra. Vad behöver du från mig istället?",
        }

        return repairs.get(rupture_type, "Jag märker att något inte känns rätt. Vad behöver du från mig just nu?")

    @staticmethod
    def build_collaboration(context: str = "general") -> str:
        """
        Frame the work as collaborative, not expert-to-patient.
        """
        collaborative_frames = {
            'general': "Vi är ett team här - du är experten på ditt liv, jag bidrar med psykologisk kunskap. Tillsammans utforskar vi vad som fungerar för dig.",

            'goal_setting': "Låt oss sätta upp det här tillsammans. Vad känns som ett meningsfullt mål för dig? Jag kan hjälpa dig bryta ner det i steg.",

            'feedback': "Hur känns det här samtalet för dig? Får du ut vad du behöver? Din feedback hjälper mig stötta dig bättre.",

            'direction': "Vart vill du att vi ska gå härifrån? Du styr riktningen, jag hjälper dig navigera.",
        }

        return collaborative_frames.get(context, collaborative_frames['general'])


def build_rapport_response(
    user_message: str,
    base_response: str,
    conversation_history: List[Dict] = None,
    user_profile: Dict[str, float] = None
) -> str:
    """
    Enhance a base response with rapport-building elements.

    Args:
        user_message: The user's message
        base_response: The core response content
        conversation_history: Previous messages
        user_profile: User's Big Five scores

    Returns:
        Enhanced response with rapport elements
    """
    builder = RapportBuilder()

    # Detect tone and style
    tone = builder.detect_emotional_tone(user_message, conversation_history)
    style = builder.detect_language_style(user_message)

    # Check for alliance rupture
    rupture = TherapeuticAlliance.check_alliance_rupture(user_message)
    if rupture:
        # Prioritize alliance repair
        return TherapeuticAlliance.repair_alliance(rupture)

    # Add empathetic acknowledgment if emotion detected
    acknowledgment = builder.create_empathetic_acknowledgment(user_message)

    # Match tone
    enhanced_response = builder.match_tone(tone, base_response)

    # Add acknowledgment at beginning if appropriate
    if tone in [EmotionalTone.DISTRESSED, EmotionalTone.SERIOUS]:
        enhanced_response = acknowledgment + " " + enhanced_response

    # Ensure non-judgmental language
    enhanced_response = builder.non_judgmental_language(enhanced_response)

    return enhanced_response
