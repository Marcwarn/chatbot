"""
Therapeutic Techniques - Motivational Interviewing, Cognitive Reframing, Socratic Method
Professional psychological conversation patterns for AI coaching
"""

from typing import Dict, List, Tuple
import re
from enum import Enum


class TherapeuticTechnique(Enum):
    """Types of therapeutic techniques"""
    MOTIVATIONAL_INTERVIEWING = "motivational_interviewing"
    COGNITIVE_REFRAMING = "cognitive_reframing"
    SOCRATIC_METHOD = "socratic_method"
    VALIDATION = "validation"
    STRENGTHS_BASED = "strengths_based"


class MotivationalInterviewing:
    """
    Motivational Interviewing techniques: OARS (Open questions, Affirmations,
    Reflective listening, Summarizing)
    """

    @staticmethod
    def generate_open_question(context: str, user_profile: Dict[str, float] = None) -> str:
        """
        Generate open-ended questions that encourage exploration.
        These questions cannot be answered with yes/no.
        """
        # Detect topic from context
        context_lower = context.lower()

        # Career exploration
        if any(word in context_lower for word in ['karriär', 'jobb', 'arbete', 'yrke']):
            questions = [
                "Vad får dig att känna dig energisk och engagerad när du arbetar?",
                "Berätta mer om vad som är viktigt för dig i din karriär - bortom lön och titel?",
                "Tänk på en dag när du kände dig riktigt nöjd med ditt arbete - vad gjorde den dagen speciell?",
                "Hur ser din idealiska arbetsdag ut, från morgon till kväll?",
                "Vilka delar av ditt nuvarande arbete får tiden att flyga - och vilka får den att krypa?"
            ]

        # Relationships
        elif any(word in context_lower for word in ['relation', 'vän', 'partner', 'familj', 'människor']):
            questions = [
                "Vad kännetecknar de relationer där du känner dig mest du själv?",
                "Berätta om en vänskap som fungerar riktigt bra - vad gör den så bra?",
                "Hur skulle du beskriva ditt ideala sätt att umgås med andra?",
                "När känner du att du ger mest i dina relationer, och när tar du emot mest?",
                "Vilka egenskaper värderar du högst hos de människor du känner dig närmast?"
            ]

        # Personal growth
        elif any(word in context_lower for word in ['utveckla', 'förändra', 'bättre', 'växa', 'lära']):
            questions = [
                "Vad har du lärt dig om dig själv det senaste året?",
                "Om du tänker framåt - vilken version av dig själv vill du bli?",
                "Vad skulle det innebära för dig att lyckas med denna förändring?",
                "Vilka små steg har du redan tagit i den här riktningen?",
                "När du tänker på tidigare förändringar du gjort - vad hjälpte dig då?"
            ]

        # Struggles/challenges
        elif any(word in context_lower for word in ['svårt', 'problem', 'kämpa', 'struggle', 'utmaning']):
            questions = [
                "När du tänker på de gånger du faktiskt lyckats navigera liknande utmaningar - vad var annorlunda då?",
                "Vad skulle behöva hända för att denna situation skulle kännas lite lättare?",
                "Hur påverkar det här dig i ditt vardagliga liv?",
                "Om en god vän hade samma utmaning - vad skulle du säga till dem?",
                "Vilka resurser eller styrkor har du som kan hjälpa dig här?"
            ]

        # Personality/self-understanding
        else:
            questions = [
                "Vad resonerar mest med dig när du tänker på din personlighetsprofil?",
                "Hur märker du av dessa drag i ditt vardagliga liv?",
                "Vilka situationer får dig att känna dig mest som dig själv?",
                "När du tänker på din personlighet - vad är du mest nöjd med?",
                "Vad skulle du vilja förstå bättre om dig själv?"
            ]

        # Return the most relevant question (could be enhanced with ML)
        return questions[0]

    @staticmethod
    def create_affirmation(user_statement: str, profile: Dict[str, float] = None) -> str:
        """
        Recognize and affirm user's strengths, efforts, and positive qualities.
        """
        statement_lower = user_statement.lower()

        # Recognize effort/action
        if any(word in statement_lower for word in ['försöker', 'jobbar på', 'arbetar med', 'försökt']):
            return "Jag ser att du aktivt arbetar på det här - det kräver både mod och självinsikt att ta tag i sådant."

        # Recognize self-awareness
        if any(word in statement_lower for word in ['märkt', 'insett', 'förstått', 'reflekterat']):
            return "Din självinsikt är verkligen värdefull - att kunna se och reflektera över sina egna mönster är en styrka i sig."

        # Recognize openness to change
        if any(word in statement_lower for word in ['vill', 'skulle vilja', 'hoppas', 'tänker utveckla']):
            return "Din vilja att utvecklas och växa är imponerande - det är där all verklig förändring börjar."

        # Recognize honesty about struggles
        if any(word in statement_lower for word in ['svårt', 'kämpat', 'utmaning', 'struggle']):
            return "Det krävs styrka att vara så ärlig om sina utmaningar - det visar på äkta självkännedom."

        # Generic positive affirmation
        return "Det du berättar visar på en djup förståelse för dig själv."

    @staticmethod
    def reflective_listening(user_statement: str, emotion: str = None) -> str:
        """
        Mirror back the user's feelings and content to show understanding.
        Format: "Det låter som att du [feeling] när [situation]"
        """
        statement_lower = user_statement.lower()

        # Detect emotions if not provided
        if not emotion:
            if any(word in statement_lower for word in ['frustrerande', 'irriterande', 'störande']):
                emotion = "frustrerad"
            elif any(word in statement_lower for word in ['orolig', 'nervös', 'ängslig']):
                emotion = "orolig"
            elif any(word in statement_lower for word in ['ledsen', 'sorglig', 'tråkig']):
                emotion = "besviken"
            elif any(word in statement_lower for word in ['glad', 'nöjd', 'lycklig']):
                emotion = "nöjd"
            elif any(word in statement_lower for word in ['förvirrad', 'osäker', 'vet inte']):
                emotion = "osäker"
            else:
                emotion = "påverkad"

        # Create reflective statement
        templates = [
            f"Det låter som att du känner dig {emotion} över det här.",
            f"Jag hör att detta {emotion} dig på ett djupt plan.",
            f"Om jag förstår dig rätt känns det {emotion}t för dig när detta händer.",
            f"Du verkar {emotion} när du tänker på det här."
        ]

        return templates[0]

    @staticmethod
    def summarize_conversation(messages: List[str], themes: List[str] = None) -> str:
        """
        Tie together themes from the conversation to show you're listening
        and help user see the bigger picture.
        """
        if not themes:
            themes = ["dina styrkor", "de utmaningar du navigerar", "vad som är viktigt för dig"]

        if len(themes) == 1:
            return f"Låt mig sammanfatta vad jag hört: Du har pratat mycket om {themes[0]}."
        elif len(themes) == 2:
            return f"Jag hör flera trådar här: dels {themes[0]}, dels {themes[1]}. Båda verkar viktiga för dig."
        else:
            theme_list = ", ".join(themes[:-1]) + f" och {themes[-1]}"
            return f"Det jag hör i det du berättar är flera teman som hänger ihop: {theme_list}. Stämmer det?"


class CognitiveReframing:
    """
    Help users see situations from new, more adaptive perspectives.
    Challenge negative self-talk gently. Highlight strengths in weaknesses.
    """

    @staticmethod
    def reframe_low_trait(trait_name: str, trait_value: float, context: str = "") -> str:
        """
        Reframe low personality trait scores as strengths in different contexts.
        """
        reframes = {
            'extraversion': {
                'low': "Din introversion betyder att du laddar batterierna bäst i lugnare miljöer. Medan extroverta kan uppleva stora sociala events som energigivande, finner du din energi i djupare, mer meningsfulla samtal med några få personer. Det här är inte en svaghet - det är en annan, lika värdefull väg till kontakt och kreativitet.",
                'strength': "djup reflektion, meningsfulla relationer, självständigt tänkande"
            },
            'agreeableness': {
                'low': "Din låga agreeableness betyder inte att du är otrevlig - det betyder att du inte kompromissar med dina värderingar för att behaga andra. Du är direkt, ärlig och självständig i ditt tänkande. I många sammanhang är detta ovärderligt - särskilt där kritiskt tänkande och ärlighet behövs.",
                'strength': "kritiskt tänkande, ärlighet, förhandlingsförmåga, självständighet"
            },
            'conscientiousness': {
                'low': "Låg conscientiousness betyder hög spontanitet och kreativ flexibilitet. Medan strukturerade personer kan fastna i planer, kan du anpassa dig snabbt när situationen förändras. Din förmåga att vara närvarande i nuet och tänka utanför boxen är en styrka i dynamiska miljöer.",
                'strength': "spontanitet, flexibilitet, kreativitet, anpassningsförmåga"
            },
            'neuroticism': {
                'high': "Din känslomässiga lyhördhet (hög neuroticism) betyder att du känner djupt och reagerar starkt på världen omkring dig. Detta kan vara utmanande, men det innebär också att du har tillgång till ett rikt känsloliv, hög empati och förmåga att uppfatta nyanser som andra missar.",
                'strength': "emotionell djup, empati, vaksamhet, passionerad engagemang"
            },
            'openness': {
                'low': "Din preferens för det konkreta och beprövade (låg openness) betyder att du är praktisk, jordnära och pålitlig. I en värld full av ständig förändring är din förmåga att värdera tradition och etablerade metoder ovärderlig. Du är den som håller skeppet stadigt medan andra jagar varje ny trend.",
                'strength': "praktisk visdom, stabilitet, konsekvens, verklighetförankring"
            }
        }

        trait_lower = trait_name.lower()
        if trait_lower in reframes:
            # Determine if low or high
            if trait_lower == 'neuroticism':
                key = 'high' if trait_value > 50 else 'low'
            else:
                key = 'low' if trait_value < 50 else 'high'

            if key in reframes[trait_lower]:
                return reframes[trait_lower][key]

        return f"Din position på {trait_name}-skalan ger dig en unik kombination av styrkor."

    @staticmethod
    def challenge_negative_self_talk(statement: str) -> Tuple[str, str]:
        """
        Gently challenge negative self-talk patterns.
        Returns: (identified_pattern, reframing_question)
        """
        statement_lower = statement.lower()

        # All-or-nothing thinking
        if any(word in statement_lower for word in ['alltid', 'aldrig', 'varje gång', 'ingen gång']):
            pattern = "all-or-nothing tänkande"
            reframe = "Jag hör ord som 'alltid' eller 'aldrig'. Låt oss nyansera: Finns det situationer där detta faktiskt inte stämmer? Även små undantag är viktiga."

        # Catastrophizing
        elif any(word in statement_lower for word in ['katastrofalt', 'fruktansvärt', 'hopplöst', 'värsta']):
            pattern = "katastrofiserande"
            reframe = "Det låter som en verkligt svår situation. Om vi skalar det från 1-10, var skulle du placera hur allvarligt detta faktiskt är versus hur allvarligt det känns just nu?"

        # Mind reading
        elif any(word in statement_lower for word in ['tycker säkert', 'tänker nog att', 'ser mig som']):
            pattern = "tankläsning"
            reframe = "Jag märker att du tolkar vad andra tänker. Vad har de faktiskt sagt eller gjort som fick dig att tro detta? Finns det alternativa tolkningar?"

        # Should statements
        elif any(word in statement_lower for word in ['borde', 'måste', 'ska', 'bör']):
            pattern = "should-statements"
            reframe = "Du använder ord som 'borde' eller 'måste'. Vad händer om vi byter ut det mot 'vill' eller 'väljer'? Vad förändras då?"

        # Labeling
        elif any(word in statement_lower for word in ['jag är en', 'jag är så', 'jag är typ']):
            pattern = "självetikettering"
            reframe = "Du definierar dig själv med en etikett. Men du är mer än ett adjektiv - du är en komplex person som ibland beter dig på olika sätt. Kan vi se på beteendet snarare än identiteten?"

        # Generic negative thought
        else:
            pattern = "negativ kognitiv bias"
            reframe = "Jag hör en negativ tolkning av situationen. Låt oss utforska: Vilka bevis har du FÖR denna tanke? Vilka bevis EMOT? Vad skulle en vän säga?"

        return (pattern, reframe)

    @staticmethod
    def strengths_in_weaknesses(perceived_weakness: str, profile: Dict[str, float] = None) -> str:
        """
        Find the hidden strength in a perceived weakness.
        """
        weakness_lower = perceived_weakness.lower()

        common_reframes = {
            'känslig': "Din känslighet betyder att du har djup empati och förmåga att förstå andra på ett sätt som många saknar. Det som känns som sårbarhet är också din superkraft i relationer.",
            'oorganiserad': "Din flexibla approach till struktur betyder att du kan tänka kreativt och anpassa dig snabbt. Där andra fastnar i sina planners, ser du möjligheter de missar.",
            'stubbornhet': "Din beslutsamhet och förmåga att stå på dig betyder att du inte kompromissar på dina värderingar. Det andra kallar 'stubborn' är ofta principfasthet och integritet.",
            'överdrivet försiktig': "Din noggrannhet och förmåga att se risker betyder att du fattar genomtänkta beslut. I en impulsiv värld är din försiktighet ofta klokhet.",
            'introvert': "Din introversion ger dig förmåga till djup reflektion och meningsfulla relationer. Kvalitet över kvantitet är inte en svaghet - det är en medveten prioritering.",
            'konfliktsky': "Din strävan efter harmoni betyder att du är skicklig på att hitta gemensam mark och bygga broar mellan människor. Det är diplomati, inte svaghet.",
        }

        for keyword, reframe in common_reframes.items():
            if keyword in weakness_lower:
                return reframe

        # Generic reframe
        return "Det du ser som en svaghet kan ofta vara en styrka i olika sammanhang. Samma egenskap som skapar utmaningar i en situation kan vara ovärderlig i en annan."


class SocraticMethod:
    """
    Guide discovery through questions rather than direct advice.
    Help users reach their own conclusions.
    """

    @staticmethod
    def generate_guiding_questions(topic: str, user_profile: Dict[str, float] = None) -> List[str]:
        """
        Generate a sequence of Socratic questions that guide discovery.
        """
        topic_lower = topic.lower()

        # Career guidance
        if any(word in topic_lower for word in ['karriär', 'jobb', 'arbete']):
            return [
                "Vad innebär framgång för dig i din karriär - bortom titel och lön?",
                "Tänk på ett arbete där du känner dig energisk och engagerad. Vad är det i själva arbetet som skapar den känslan?",
                "Vilka av dina naturliga styrkor används inte fullt ut just nu?",
                "Om pengar inte var ett hinder - hur skulle din arbetsvardag se ut?",
                "Vad skulle du behöva lära dig eller utveckla för att komma närmare det?",
                "Vilket första lilla steg kan du ta den här veckan?"
            ]

        # Personal development
        elif any(word in topic_lower for word in ['utveckla', 'förändra', 'bättre']):
            return [
                "Vad skulle det innebära för dig att lyckas med denna förändring?",
                "Vilka delar av förändringen känns möjliga, och vilka känns svåra?",
                "När har du tidigare lyckats förändra något i ditt liv? Vad hjälpte dig då?",
                "Vad skulle behöva vara annorlunda för att förändringen ska vara hållbar?",
                "Vilka är de första tecknen på att du rör dig i rätt riktning?",
                "Hur kommer du veta att du nått dit du vill?"
            ]

        # Relationships
        elif any(word in topic_lower for word in ['relation', 'vän', 'partner']):
            return [
                "Vad kännetecknar de relationer där du känner dig mest sedd och förstådd?",
                "Hur bidrar du själv till dynamiken i denna relation?",
                "Om relationen fungerade perfekt - vad skulle vara annorlunda?",
                "Vad behöver du för att känna dig trygg nog att vara helt dig själv?",
                "Vilka av dina behov är viktigast att kommunicera just nu?",
                "Hur kan du uttrycka det på ett sätt som öppnar för dialog snarare än försvar?"
            ]

        # Self-understanding
        else:
            return [
                "När känner du dig mest som dig själv?",
                "Vilka situationer får dig att blomma, och vilka får dig att krympa?",
                "Vad skulle människor som känner dig bäst säga är dina styrkor?",
                "Vilka delar av din personlighet är du mest nöjd med?",
                "Om du kunde behålla allt men justera en sak - vad skulle det vara?",
                "Vad behöver du förstå bättre om dig själv för att må bra?"
            ]

    @staticmethod
    def avoid_direct_advice(user_request: str, context: str = "") -> str:
        """
        When user asks for direct advice, redirect to self-discovery.
        """
        advice_templates = [
            "Det är en viktig fråga. Istället för att ge dig ett färdigt svar, vill jag hjälpa dig hitta svaret som passar just dig. {question}",
            "Jag skulle kunna ge dig ett generiskt råd, men du känner din situation bäst. {question}",
            "Låt mig vända på det: {question} Ditt svar kommer guida oss till en lösning som faktiskt passar dig.",
            "Jag tror du redan har insikter om detta, även om de kanske inte är fullt medvetna än. {question}"
        ]

        # Generate contextual question
        request_lower = user_request.lower()
        if 'borde' in request_lower or 'ska' in request_lower:
            question = "Vad känns rätt för dig när du lyssnar på din magkänsla?"
        elif 'hur' in request_lower:
            question = "Vad har du redan provat, och vad lärde du dig av det?"
        else:
            question = "Vad tror du själv - vad säger din intuition?"

        return advice_templates[0].format(question=question)


class Validation:
    """
    Acknowledge feelings as legitimate. Normalize experiences. Reduce shame.
    """

    @staticmethod
    def validate_emotion(emotion: str, context: str = "") -> str:
        """
        Validate the user's emotional experience as legitimate and normal.
        """
        validations = {
            'frustration': "Det är helt naturligt att känna frustration när saker inte går som vi vill. Din frustration är legitim och säger något viktigt om vad som är meningsfullt för dig.",
            'anxiety': "Oro är människans sätt att förbereda sig för framtiden. Det är obehagligt, men det är inte farligt - och det säger ingenting om din styrka som person.",
            'sadness': "Att känna sorg är ett tecken på att något är viktigt för dig. Din ledsenhet är giltig och förtjänar att få ta plats.",
            'confusion': "Förvirring är ofta ett tecken på att du står inför något komplext eller nytt. Det är okej att inte ha alla svar just nu.",
            'disappointment': "Besvikelse visar att du hade hopp och förväntningar - det är mänskligt och förståeligt. Tillåt dig själv att känna det.",
            'anger': "Ilska säger ofta att en gräns har kränkts eller ett behov inte mötts. Din ilska har ett budskap - låt oss lyssna på det.",
            'shame': "Skam är en av de tyngsta känslorna, och jag vill att du vet: Du är inte din känsla, och du är inte ensam om att känna så här.",
            'joy': "Din glädje är värdefull och förtjänar att firas. Låt dig själv känna den fullt ut.",
        }

        emotion_lower = emotion.lower()
        for key, validation in validations.items():
            if key in emotion_lower:
                return validation

        # Generic validation
        return f"Dina känslor är legitima och värda att utforska. Det du känner är en naturlig reaktion på din upplevelse."

    @staticmethod
    def normalize_experience(experience: str, profile: Dict[str, float] = None) -> str:
        """
        Help user understand their experience is normal/common.
        """
        experience_lower = experience.lower()

        normalizations = {
            'ensam': "Många människor känner ensamhet, även när de är omgivna av folk. Du är absolut inte ensam om att känna så här - det är faktiskt en av de mest universella mänskliga upplevelserna.",
            'inte tillräcklig': "Känslan av att inte räcka till är oerhört vanlig, särskilt bland personer med höga krav på sig själva. Det är ofta ett tecken på ambition, inte brist på förmåga.",
            'annorlunda': "Att känna sig annorlunda är något de flesta människor bär på. Ironiskt nog är det att känna sig unik i sin annorlundahet något av det mest mänskliga som finns.",
            'överväldigad': "Att känna sig överväldigad är en helt naturlig reaktion när livet känns för stort. Det betyder inte att du är svag - det betyder att du är mänsklig.",
            'fast': "Att känna sig fast i livet eller i ett mönster är något många upplever. Det är ofta just i denna känsla som förändring börjar.",
        }

        for keyword, normalization in normalizations.items():
            if keyword in experience_lower:
                return normalization

        return "Det du upplever är mer vanligt än du kanske tror. Många känner liknande saker, även om det sällan pratas om öppet."

    @staticmethod
    def reduce_shame(statement: str) -> str:
        """
        Actively work to reduce shame and self-judgment.
        """
        statement_lower = statement.lower()

        # Detect shame-laden statements
        shame_indicators = ['skäms', 'patetisk', 'värdelös', 'dålig', 'fel på mig', 'svag', 'misslyckande']

        if any(indicator in statement_lower for indicator in shame_indicators):
            return "Jag hör mycket själv-kritik i det du säger, och jag vill pausa där ett ögonblick. Det du beskriver är mänskligt - det är inte något att skämmas för. Skulle du prata så här till en vän som kände likadant?"

        return "Det krävs mod att vara så ärlig. Tack för att du delar det med mig."


# Convenience function to select appropriate technique
def select_technique(
    user_message: str,
    context: str = "",
    profile: Dict[str, float] = None
) -> Tuple[TherapeuticTechnique, str]:
    """
    Analyze user message and select the most appropriate therapeutic technique.
    Returns: (technique_type, generated_response)
    """
    message_lower = user_message.lower()

    # Detect if validation is needed (emotion words present)
    emotion_words = ['känner', 'mår', 'ledsen', 'arg', 'glad', 'orolig', 'rädd', 'frustrerad']
    if any(word in message_lower for word in emotion_words):
        emotion = "frustration" if 'frustrera' in message_lower else "anxiety"
        response = Validation.validate_emotion(emotion, user_message)
        return (TherapeuticTechnique.VALIDATION, response)

    # Detect if reframing is needed (negative self-talk)
    negative_words = ['dålig', 'värdelös', 'fel', 'misslyckande', 'aldrig', 'alltid']
    if any(word in message_lower for word in negative_words):
        pattern, reframe = CognitiveReframing.challenge_negative_self_talk(user_message)
        return (TherapeuticTechnique.COGNITIVE_REFRAMING, reframe)

    # Detect if user wants advice (use Socratic instead)
    advice_words = ['vad ska jag', 'vad borde jag', 'hur ska jag', 'ge mig råd']
    if any(word in message_lower for word in advice_words):
        response = SocraticMethod.avoid_direct_advice(user_message)
        return (TherapeuticTechnique.SOCRATIC_METHOD, response)

    # Default to motivational interviewing
    question = MotivationalInterviewing.generate_open_question(user_message, profile)
    return (TherapeuticTechnique.MOTIVATIONAL_INTERVIEWING, question)
