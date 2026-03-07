"""
Insight Generator - Facilitate self-discovery through pattern recognition,
strengths-based approach, and growth mindset
"""

from typing import Dict, List, Tuple, Optional
import re


class PatternRecognition:
    """
    Help users see patterns in their behavior and connect personality traits
    to life experiences.
    """

    @staticmethod
    def identify_trait_patterns(
        profile: Dict[str, float],
        user_statements: List[str]
    ) -> List[str]:
        """
        Identify patterns between personality profile and user's descriptions
        of their behavior/experiences.
        """
        patterns = []

        # Extract trait values
        e = profile.get('E', 50)
        a = profile.get('A', 50)
        c = profile.get('C', 50)
        n = profile.get('N', 50)
        o = profile.get('O', 50)

        # Combine all user statements
        all_text = ' '.join(user_statements).lower()

        # Pattern 1: High Openness + mentions of boredom/routine
        if o >= 65 and any(word in all_text for word in ['tråkig', 'rutiner', 'samma', 'monoton']):
            patterns.append(
                "Jag ser ett mönster: Din höga Openness (nyfikenhet och kreativitet) kan förklara "
                "varför du beskriver rutiner och upprepning som utmanande. Din hjärna söker ständigt "
                "stimulans och nya perspektiv - det som andra upplever som trygg struktur kan för dig "
                "kännas begränsande."
            )

        # Pattern 2: Low Conscientiousness + stress over deadlines
        if c <= 35 and any(word in all_text for word in ['deadline', 'sen', 'prokrastinera', 'sista minuten']):
            patterns.append(
                "Din låga Conscientiousness hänger ihop med det du berättar om deadlines. Personer "
                "med låg C tenderar att arbeta i spontana bursts snarare än långsiktig planering. Det "
                "är inte lathet - det är hur din hjärna naturligt organiserar arbete. Tricket är att "
                "designa system som fungerar MED din spontanitet, inte emot den."
            )

        # Pattern 3: High Neuroticism + worry/anxiety mentions
        if n >= 65 and any(word in all_text for word in ['orolig', 'ångest', 'nervös', 'stress']):
            patterns.append(
                "Det du beskriver om oro och stress stämmer med din höga Neuroticism. Detta betyder "
                "att ditt nervsystem reagerar starkt på potentiella hot - en evolutionär fördel som "
                "i modern tid kan kännas som nackdel. Din oro är inte irrationell, den är en "
                "överaktiv säkerhetsmekanism."
            )

        # Pattern 4: Low Extraversion + energy drainage from socializing
        if e <= 35 and any(word in all_text for word in ['trött efter', 'energi', 'social', 'återhämta']):
            patterns.append(
                "Din introversion (låg Extraversion) förklarar perfekt det du berättar om energi. "
                "För introverta är social interaktion som att använda batteriet - för extroverta "
                "laddar det batteriet. Ingen är bättre eller sämre, men det innebär att du behöver "
                "återhämtningstid efter social aktivitet. Det är inte asocialt - det är biologiskt."
            )

        # Pattern 5: Low Agreeableness + conflict mentions
        if a <= 35 and any(word in all_text for word in ['konflikt', 'argument', 'oenighet', 'ifrågasätt']):
            patterns.append(
                "Din låga Agreeableness kopplad till det du berättar om konflikter är intressant. "
                "Personer med låg A är mer benägna att ifrågasätta och stå på sig - vilket andra "
                "kan uppleva som konflikt, men som egentligen är integritet och kritiskt tänkande. "
                "Du kompromissar inte på dina värderingar för att behaga - det är en styrka i rätt kontext."
            )

        # Pattern 6: High Openness + High Neuroticism = Rumination
        if o >= 65 and n >= 65 and any(word in all_text for word in ['tänker', 'grubblar', 'analysera']):
            patterns.append(
                "Kombinationen av hög Openness och hög Neuroticism skapar ett intressant mönster: "
                "din kreativa, filosofiska hjärna (O) kombinerat med känslomässig intensitet (N) kan "
                "leda till djup reflektion - men också till övertänkande. Du ser alla möjligheter "
                "OCH alla risker. Det är både gåva och utmaning."
            )

        # Pattern 7: High E + Low C = Social spontanitet
        if e >= 65 and c <= 35:
            patterns.append(
                "Din kombination av hög Extraversion och låg Conscientiousness skapar en energisk "
                "spontanitet. Du trivs i dynamiska, sociala miljöer och kan anpassa dig snabbt - "
                "men struktur och långsiktig planering kan kännas kvävande. Du är den som säger "
                "'vi tar det när vi kommer dit' - och ofta gör det bra ändå."
            )

        return patterns

    @staticmethod
    def connect_traits_to_experiences(
        trait_name: str,
        trait_value: float,
        life_domain: str
    ) -> str:
        """
        Explain how a specific trait manifests in a specific life domain.
        """
        connections = {
            'E': {
                'work': {
                    'high': "Din höga Extraversion innebär att du troligen presterar bäst i roller med "
                            "mycket människokontakt, teamwork och dynamisk aktivitet. Ensamarbete kan kännas "
                            "energidränande, medan möten och samarbete energigivande.",
                    'low': "Din introversion betyder att du troligen presterar bäst i roller som tillåter "
                           "fokuserat ensamarbete. Du bidrar med eftertänksamhet och djup, men kan behöva "
                           "återhämtning efter intensiva möten eller konferenser."
                },
                'relationships': {
                    'high': "I relationer är du troligen den som initierar kontakt, planerar sociala aktiviteter "
                            "och har stort nätverk. Du kan behöva partners som förstår ditt behov av social stimulans.",
                    'low': "I relationer värderar du troligen djup över bredd - några nära vänner istället för "
                           "stort nätverk. Du kan behöva partners som respekterar ditt behov av tid för dig själv."
                }
            },
            'A': {
                'work': {
                    'high': "Din höga Agreeableness gör dig till en naturlig teamspelare och medlare. Du bygger "
                            "goda relationer, men kan behöva öva på att säga nej och förhandla för dina intressen.",
                    'low': "Din låga Agreeableness innebär att du är direkt och principfast. Du är effektiv i "
                           "förhandlingar och kan fatta tuffa beslut - men kan behöva arbeta på diplomatisk kommunikation."
                },
                'relationships': {
                    'high': "I relationer är du empatisk, stöttande och harmonisökande. Du kan behöva vaka över "
                            "att inte försumma dina egna behov för andras skull.",
                    'low': "I relationer är du ärlig och direkt. Du värdesätter autenticitet över harmoni, vilket "
                           "skapar ärliga relationer - men kan kräva partners som hanterar direkthet."
                }
            },
            'C': {
                'work': {
                    'high': "Din höga Conscientiousness gör dig pålitlig, organiserad och effektiv. Du möter "
                            "deadlines och håller höga standarder - men kan behöva tillåta dig själv flexibilitet.",
                    'low': "Din låga Conscientiousness ger dig flexibilitet och spontanitet. Du kan snabbt "
                           "anpassa dig till förändring - men kan behöva externa strukturer för långsiktiga projekt."
                },
                'relationships': {
                    'high': "I relationer är du pålitlig och håller dina löften. Du planerar och organiserar, "
                            "vilket skapar trygghet - men spontanitet kan kräva medveten ansträngning.",
                    'low': "I relationer är du spontan och flexibel. Du lever i nuet och kan hantera oförutsägbarhet "
                           "- men partners kan behöva tydliga förväntningar kring åtaganden."
                }
            },
            'N': {
                'work': {
                    'high': "Din känslomässiga lyhördhet kan göra dig uppmärksam på teamdynamik och problem innan "
                            "andra märker dem. Men stress och osäkerhet påverkar dig mer - du behöver stabilitet.",
                    'low': "Din känslomässiga stabilitet gör dig lugn under press. Du hanterar kris väl - men kan "
                           "missa emotionella signaler från andra som behöver stöd."
                },
                'relationships': {
                    'high': "I relationer känner du djupt och intensivt. Du är empatisk och uppmärksam - men kan "
                            "behöva verktyg för att hantera relationsorolighet eller överkänslighet för kritik.",
                    'low': "I relationer är du stabil och lugn. Du påverkas inte lätt av konflikter - men kan behöva "
                           "arbeta på att uttrycka känslor och validera partners emotionella upplevelser."
                }
            },
            'O': {
                'work': {
                    'high': "Din höga Openness innebär att du trivs med komplexitet, innovation och nya idéer. "
                            "Du är kreativ och ser möjligheter - men kan ha svårt med repetitiva eller rigida roller.",
                    'low': "Din preferens för konkrethet och beprövade metoder gör dig effektiv i strukturerade "
                           "roller. Du värdesätter kompetens och tradition - men kan behöva utmana dig själv med nytt."
                },
                'relationships': {
                    'high': "I relationer uppskattar du djup, filosofiska samtal och nya upplevelser. Du behöver "
                            "intellektuell stimulans - men kan behöva acceptera att inte alla delar ditt introspektiva djup.",
                    'low': "I relationer värdesätter du stabilitet och delad verklighetsförankring. Du är praktisk "
                           "och jordnära - men kan behöva vara öppen för partners behov av variation och nytänkande."
                }
            }
        }

        # Determine if high or low
        is_high = trait_value >= 50

        trait_map = {
            'extraversion': 'E',
            'agreeableness': 'A',
            'conscientiousness': 'C',
            'neuroticism': 'N',
            'openness': 'O'
        }

        trait_key = trait_map.get(trait_name.lower())
        if trait_key and trait_key in connections:
            domain_key = life_domain.lower()
            if domain_key in connections[trait_key]:
                return connections[trait_key][domain_key]['high' if is_high else 'low']

        return f"Din position på {trait_name} påverkar hur du upplever {life_domain}."

    @staticmethod
    def generate_pattern_insight(
        profile: Dict[str, float],
        behavior_description: str
    ) -> Optional[str]:
        """
        Generate insight connecting specific behavior to personality profile.
        """
        behavior_lower = behavior_description.lower()

        # Extract traits
        e = profile.get('E', 50)
        a = profile.get('A', 50)
        c = profile.get('C', 50)
        n = profile.get('N', 50)
        o = profile.get('O', 50)

        # Social exhaustion + Low E
        if 'trött' in behavior_lower and 'social' in behavior_lower and e <= 35:
            return ("Ser du kopplingen mellan din låga Extraversion och den sociala trötthet du beskriver? "
                    "Det är inte att du inte gillar människor - det är att ditt nervsystem upplever social "
                    "interaktion som energikrävande snarare än energigivande. Det är neurologiskt, inte attityd.")

        # Procrastination + Low C
        if any(word in behavior_lower for word in ['prokrastinera', 'sista minuten', 'skjuter upp']) and c <= 35:
            return ("Din låga Conscientiousness förklarar mycket av det du beskriver. Det är inte lathet eller "
                    "dålig karaktär - det är hur din hjärna hanterar tid och motivation. Du arbetar bäst med "
                    "närhet till deadline (deadline-driven motivation) snarare än långsiktig planering.")

        # Overthinking + High O + High N
        if 'övertänker' in behavior_lower or 'grubblar' in behavior_lower:
            if o >= 60 and n >= 60:
                return ("Din kombination av hög Openness och hög Neuroticism skapar det du beskriver: en kreativ, "
                        "filosofisk hjärna som ser alla möjligheter och nyanser (O), kombinerat med känslomässig "
                        "intensitet och vaksamhet för hot (N). Resultatet? Djup reflektion som kan bli till övertänkande.")

        # Conflict avoidance + High A
        if any(word in behavior_lower for word in ['undviker konflikt', 'svårt säga nej']) and a >= 65:
            return ("Din höga Agreeableness visar sig i det du beskriver. Du är biologiskt disponerad att värdera "
                    "harmoni och andras välmående - vilket är vackert, men kan leda till att du försummar dina egna "
                    "behov. Du behöver inte bli mindre empatisk - bara mer empatisk även mot dig själv.")

        return None


class StrengthsBasedApproach:
    """
    Focus on what user does well. Frame challenges as opportunities.
    Build on existing capabilities.
    """

    @staticmethod
    def identify_strengths_in_profile(profile: Dict[str, float]) -> List[str]:
        """
        Identify core strengths based on personality profile.
        """
        strengths = []

        e = profile.get('E', 50)
        a = profile.get('A', 50)
        c = profile.get('C', 50)
        n = profile.get('N', 50)
        o = profile.get('O', 50)

        # Extraversion strengths
        if e >= 65:
            strengths.append("Social energi: Du laddas av kontakt med andra och bygger lätt relationer")
        elif e <= 35:
            strengths.append("Reflektiv djup: Du tänker innan du agerar och skapar meningsfulla relationer")

        # Agreeableness strengths
        if a >= 65:
            strengths.append("Empatisk förståelse: Du förstår och bryr dig om andra på ett genuint sätt")
        elif a <= 35:
            strengths.append("Kritiskt tänkande: Du ifrågasätter och står på dig för dina principer")

        # Conscientiousness strengths
        if c >= 65:
            strengths.append("Pålitlig organisation: Du håller ordning, möter deadlines och levererar kvalitet")
        elif c <= 35:
            strengths.append("Flexibel anpassning: Du kan snabbt ställa om och trivs i dynamiska miljöer")

        # Neuroticism strengths (reframe)
        if n >= 65:
            strengths.append("Emotionell lyhördhet: Du känner djupt, vilket ger empati och uppmärksamhet på detaljer")
        elif n <= 35:
            strengths.append("Emotionell stabilitet: Du förblir lugn under press och återhämtar dig snabbt")

        # Openness strengths
        if o >= 65:
            strengths.append("Kreativ nyfikenhet: Du utforskar nya idéer och ser möjligheter andra missar")
        elif o <= 35:
            strengths.append("Praktisk visdom: Du värdesätter beprövade metoder och håller skeppet stadigt")

        return strengths

    @staticmethod
    def frame_challenge_as_opportunity(challenge: str, profile: Dict[str, float] = None) -> str:
        """
        Reframe challenges as growth opportunities.
        """
        challenge_lower = challenge.lower()

        # Map common challenges to growth opportunities
        if 'prokrastinera' in challenge_lower or 'sista minuten' in challenge_lower:
            return ("Utmaningen med deadlines är faktiskt en möjlighet att lära dig hur DIN hjärna fungerar bäst. "
                    "Istället för att kämpa mot din naturliga rytm, kan vi designa system som utnyttjar din "
                    "deadline-driven energi - t.ex. artificiella deadlines, accountability partners, eller kortare "
                    "sprints istället för långsiktiga projekt.")

        if 'social ångest' in challenge_lower or 'socialt osäker' in challenge_lower:
            return ("Social osäkerhet är en chans att lära dig exakt vilka sociala situationer som fungerar för DIG. "
                    "Inte alla behöver vara extroverta sociala fjärilar. Kanske är du bäst i mindre grupper, eller "
                    "djupa 1-on-1 samtal? Detta är inte ett problem att 'fixa' - det är en preferens att förstå och respektera.")

        if 'perfektionism' in challenge_lower:
            return ("Perfektionism är en möjlighet att omvandla höga standarder (styrka) till hållbar prestation. "
                    "Din strävan efter excellens är värdefull - vi behöver bara lägga till 'good enough' i ditt "
                    "verktyg för situationer där det räcker. Du får behålla din kvalitet där det verkligen räknas.")

        if 'konflik' in challenge_lower:
            return ("Svårigheter med konflikter är en möjlighet att utveckla 'healthy conflict' skills. Målet är inte "
                    "att älska konflikt, utan att se den som information - ett tecken på att något viktigt behöver "
                    "adresseras. Du kan lära dig uttrycka oenighet med respekt.")

        # Generic opportunity framing
        return ("Varje utmaning du möter är samtidigt en möjlighet att lära dig mer om dig själv och utveckla nya "
                "strategier. Det som känns svårt idag kan bli ett område av styrka imorgon - med rätt verktyg och perspektiv.")

    @staticmethod
    def build_on_existing_capabilities(current_strength: str, desired_growth: str) -> str:
        """
        Show how user can leverage existing strengths to achieve desired growth.
        """
        # This creates a bridge from "what I'm already good at" to "what I want to develop"

        return (f"Du har redan {current_strength} - det är din grund. För att utveckla {desired_growth}, "
                f"kan du använda det du redan kan som språngbräda. Hur kan din befintliga styrka hjälpa "
                f"dig ta första steget mot det nya?")


class GrowthMindset:
    """
    Emphasize malleability of behavior (not fixed traits).
    Celebrate small insights. Encourage experimentation.
    """

    @staticmethod
    def emphasize_malleability(trait_name: str) -> str:
        """
        Clarify that personality traits are relatively stable but behaviors can change.
        """
        return (f"Din position på {trait_name} är relativt stabil över tid - det är din baseline. "
                f"MEN, det betyder inte att du är låst. Du kan utveckla nya beteenden, strategier och "
                f"färdigheter som kompenserar eller arbetar MED dina naturliga tendenser. "
                f"Personlighet är inte öde - det är utgångspunkt.")

    @staticmethod
    def celebrate_insight(insight: str) -> str:
        """
        Positively reinforce user's self-discovery moments.
        """
        celebrations = [
            f"Wow, det där är en kraftfull insikt! {insight}",
            f"Det där är exakt rätt observation. {insight}",
            f"Jag älskar att du såg den kopplingen! {insight}",
            f"Nu kommer vi någonstans! {insight}",
            f"Perfekt självkännedom! {insight}"
        ]

        # Return first one (could be randomized)
        return celebrations[0]

    @staticmethod
    def encourage_experimentation(area: str) -> str:
        """
        Frame personal development as experimentation, not failure/success.
        """
        return (f"Tänk på {area} som ett experiment. Det finns inget 'misslyckas' här - bara data. "
                f"Prova en strategi i en vecka. Om det fungerar, behåll den. Om inte, justera och prova "
                f"igen. Varje försök ger dig information om vad som funkar för just DIG. "
                f"Det är så self-knowledge byggs - genom nyfiken utforskning, inte genom att följa en mall.")

    @staticmethod
    def growth_oriented_language(fixed_statement: str) -> str:
        """
        Convert fixed mindset language to growth mindset language.
        """
        conversions = {
            "jag är dålig på": "jag utvecklar min förmåga att",
            "jag kan inte": "jag har inte lärt mig än hur jag ska",
            "det är för svårt": "det här utmanar mig att växa",
            "jag är inte typ": "jag har inte varit typ",
            "jag klarar inte": "jag behöver nya strategier för att",
            "det är såhär jag är": "det är såhär jag varit - men jag kan välja annorlunda",
        }

        statement_lower = fixed_statement.lower()
        for fixed, growth in conversions.items():
            if fixed in statement_lower:
                converted = statement_lower.replace(fixed, growth)
                return (f"Jag hör lite fixed mindset där. Vad händer om vi omformulerar: "
                        f"Istället för '{fixed_statement}', prova '{converted}'? "
                        f"Känner du skillnaden? Det är inte bara ord - det öppnar för möjlighet.")

        return "Kom ihåg: Du är inte färdig. Du utvecklas hela tiden."


def generate_insight(
    user_profile: Dict[str, float],
    user_message: str,
    conversation_history: List[str] = None
) -> Optional[str]:
    """
    Main function to generate insights based on user's profile and statements.

    Args:
        user_profile: Big Five scores
        user_message: Current message
        conversation_history: Previous user statements

    Returns:
        Generated insight or None
    """
    # Try pattern recognition first
    if conversation_history:
        patterns = PatternRecognition.identify_trait_patterns(user_profile, conversation_history + [user_message])
        if patterns:
            return patterns[0]  # Return most relevant pattern

    # Try connecting specific behavior to traits
    pattern_insight = PatternRecognition.generate_pattern_insight(user_profile, user_message)
    if pattern_insight:
        return pattern_insight

    # If discussing challenges, frame as opportunity
    if any(word in user_message.lower() for word in ['problem', 'svårt', 'utmaning', 'kämpar']):
        return StrengthsBasedApproach.frame_challenge_as_opportunity(user_message, user_profile)

    return None
