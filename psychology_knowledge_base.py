"""
Psychology Knowledge Base
Expert knowledge about Big Five, DISC, career guidance, relationships,
and personal development - all research-backed and accessible
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class CareerMatch:
    """Career recommendation with reasoning"""
    career: str
    fit_score: float  # 0.0 to 1.0
    reasoning: str
    required_traits: Dict[str, str]  # trait -> level needed


@dataclass
class RelationshipInsight:
    """Relationship dynamic based on personality"""
    dynamic_type: str
    description: str
    strengths: List[str]
    challenges: List[str]
    advice: List[str]


class PsychologyKnowledgeBase:
    """
    Comprehensive psychology knowledge base for personality coaching
    Includes Big Five, DISC, career guidance, relationships, and development
    """

    def __init__(self, language: str = "sv"):
        self.language = language

    # ═══════════════════════════════════════════════════════════════════════
    # BIG FIVE DEEP KNOWLEDGE
    # ═══════════════════════════════════════════════════════════════════════

    def get_trait_explanation(self, trait: str, score: float, language: str = "sv") -> Dict[str, str]:
        """
        Get comprehensive explanation of a Big Five trait
        Includes: definition, facets, research findings, real-world impact
        """

        if language == "sv":
            return self._get_trait_explanation_swedish(trait, score)
        else:
            return self._get_trait_explanation_english(trait, score)

    def _get_trait_explanation_swedish(self, trait: str, score: float) -> Dict[str, str]:
        """Swedish trait explanations"""

        explanations = {
            'E': {
                'name': 'Extraversion',
                'definition': 'Extraversion handlar om var du får din energi och hur du föredrar att interagera med världen.',
                'high_description': """
Personer med hög extraversion laddar sina batterier i sociala sammanhang. Du trivs förmodligen i grupper,
tar gärna initiativ till samtal och känner dig energisk efter att ha träffat folk. Du tänker ofta genom
att prata högt och gillar att vara där saker händer.

**Forskning visar:**
- Extraverta personer tenderar att ha fler sociala kontakter och större nätverk
- Ofta högre nivåer av positiva känslor i vardagen
- Trivs i yrken med mycket social interaktion
- Kan vara mer benägna att ta risker
- Oftare ledarroller i grupper

**I praktiken:**
- Du gillar brainstorming-möten och spontana diskussioner
- Känner dig ensam eller uttråkad av för mycket ensamhet
- Presterar ofta bättre i team än solo
- Kan ha svårt med jobb som kräver mycket isolerat arbete
                """,
                'low_description': """
Personer med låg extraversion (introversion) får energi från att vara för sig själva. Du föredrar förmodligen
djupare one-on-one samtal framför stora fester, tänker ofta innan du pratar, och behöver tid ensam för att
ladda batterierna efter sociala aktiviteter.

**Forskning visar:**
- Introverta personer har ofta djupare (men färre) vänskaper
- Bättre på fokuserat, självständigt arbete
- Tänker mer innan de agerar (vilket minskar impulsiva misstag)
- Ofta högre akademisk prestation
- Trivs i yrken som kräver koncentration och djuptänkande

**I praktiken:**
- Du föredrar skriftlig kommunikation eller förberedda presentationer framför spontant småprat
- Känner dig utmattad efter långa sociala sammanhang
- Presterar bäst när du får arbeta ostört
- Kan uppfattas som "tyst" men har ofta djupa tankar
                """,
                'mid_description': """
Du har en balanserad extraversion, vilket innebär att du kan anpassa dig till både sociala och ensamma situationer.
Du är vad som kallas "ambivert" - någonstans mitt emellan extravert och introvert.

**Forskning visar:**
- Ambiverta personer kan vara mest framgångsrika i många yrken eftersom de har flexibiliteten att
  anpassa sig till olika situationer
- Kan vara sociala när det behövs, men också njuta av ensamhet
- Ofta bra förhandlare och säljare

**I praktiken:**
- Du kan både leda möten och arbeta självständigt
- Behöver balans mellan socialt och ensam tid
- Kan anpassa kommunikationsstil efter situation
                """,
                'facets': ['Vänskaplig', 'Grupporienterad', 'Självsäker', 'Aktiv', 'Spänningssökande', 'Positiva känslor'],
                'swedish_term': 'Extraversion / Utåtriktadhet'
            },
            'A': {
                'name': 'Agreeableness',
                'definition': 'Vänlighet handlar om hur du förhåller dig till andra - samarbete vs konkurrens, empati vs objektivitet.',
                'high_description': """
Personer med hög vänlighet (agreeableness) är empatiska, samarbetsvilliga och värdesätter harmoni.
Du litar förmodligen på andra, undviker konflikter när möjligt, och bryr dig genuint om andras välmående.

**Forskning visar:**
- Högre vänlighet = bättre relationer och längre äktenskap
- Mer benägna att hjälpa andra (även på egen bekostnad)
- Lägre risk för antisocialt beteende
- Ofta väljer "hjälpande" yrken (lärare, vårdpersonal, terapeuter)
- Kan ha svårare att förhandla om lön (säger inte nej lika lätt)

**I praktiken:**
- Du kompromissar hellre än konfronterar
- Sätter andras behov före dina egna (ibland för mycket)
- Är lojal och pålitlig i relationer
- Kan bli utnyttjad av mer själviska personer
- Skapar harmoniska team-miljöer
                """,
                'low_description': """
Personer med låg vänlighet är mer direkta, oberoende och skeptiska. Du är förmodligen ärlig även när
det är obehagligt, ifrågasätter auktoritet, och prioriterar fakta över känslor.

**Forskning visar:**
- Lägre vänlighet = bättre förhandlare och högre löner
- Mer benägna att utmana status quo och driva innovation
- Ofta i ledarpositioner (särskilt i konkurrensutsatta branscher)
- Bättre på att sätta gränser och säga nej
- Kan uppfattas som "svåra" men också respekterade

**I praktiken:**
- Du säger vad du tycker rakt ut
- Tar inte saker personligt lika lätt
- Bra i yrken som kräver tuffa beslut (CEO, advokat, kirurg)
- Kan behöva träna på diplomatiskt språk
- Värderar kompetens över att vara omtyckt
                """,
                'mid_description': """
Du har balanserad vänlighet, vilket innebär att du kan vara både empatisk och direkt beroende på situation.
Du kan samarbeta när det behövs, men också stå upp för dig själv.

**I praktiken:**
- Du kan vara både lyhörd och beslutsam
- Anpassar nivå av direkthet efter kontext
- Balanserar egna och andras behov
                """,
                'facets': ['Förtroende', 'Uppriktighet', 'Altruism', 'Samarbetsvilja', 'Ödmjukhet', 'Sympati'],
                'swedish_term': 'Vänlighet / Agreeableness'
            },
            'C': {
                'name': 'Conscientiousness',
                'definition': 'Samvetsgrannhet handlar om självdisciplin, organisation och målmedvetenhet.',
                'high_description': """
Personer med hög samvetsgrannhet är organiserade, pålitliga och målmedvetna. Du planerar förmodligen
framåt, håller deadlines, och tycker om struktur och ordning.

**Forskning visar:**
- Högsta predictor för jobbprestanda (viktigare än IQ i många yrken!)
- Längre livslängd (bättre hälsovanor, mindre risktagande)
- Högre akademisk framgång
- Bättre ekonomi (sparar mer, planerar bättre)
- Lägre risk för missbruk och kriminalitet

**I praktiken:**
- Du kommer i tid, håller löften, följer upp
- Gillar to-do-listor, kalendrar, system
- Kan vara perfektionist (ibland för mycket)
- Kan ha svårt att slappna av eller vara spontan
- Andra litar på dig för viktiga uppdrag
                """,
                'low_description': """
Personer med låg samvetsgrannhet är spontana, flexibla och improviserar gärna. Du trivs förmodligen
med att hålla dörrar öppna, tar saker som de kommer, och känner dig begränsad av för mycket struktur.

**Forskning visar:**
- Lägre samvetsgrannhet = högre kreativitet och innovation
- Mer flexibla och anpassningsbara vid förändringar
- Ofta entreprenörer och konstnärer
- Kan vara briljanta problemlösare när planer fallerar
- Trivs i kaos där andra fastnar

**I praktiken:**
- Du gillar inte detaljerad planering
- Bäst på "flow" och improvisation
- Kan ha svårt med administrativa uppgifter
- Behöver deadline-press för att prestera (prokrastinerar)
- Trivs i dynamiska, oförutsägbara miljöer
                """,
                'mid_description': """
Du har balanserad samvetsgrannhet, vilket innebär att du kan både planera och improvisera.
Du har tillräckligt med struktur för att få saker gjorda, men också flexibilitet.

**I praktiken:**
- Du kan både följa planer och anpassa dig
- Organiserad när det behövs, spontan när det passar
- Balanserar struktur och frihet
                """,
                'facets': ['Kompetens', 'Ordning', 'Plikttrogenhet', 'Prestationssträvan', 'Självdisciplin', 'Försiktighet'],
                'swedish_term': 'Samvetsgrannhet / Conscientiousness'
            },
            'N': {
                'name': 'Neuroticism',
                'definition': 'Neuroticism (emotionell stabilitet) handlar om känslomässig reaktivitet och stresstolerans.',
                'high_description': """
Personer med hög neuroticism (låg emotionell stabilitet) känner djupt och reagerar starkt på stress och
negativa händelser. Du är förmodligen empatisk, lyhörd för nyanser, och processerar känslor intensivt.

**Forskning visar:**
- Högre neuroticism = mer kreativitet (känslor ger material)
- Bättre på att upptäcka risker och problem (evolutionär fördel!)
- Ofta djup emotionell intelligens
- Kan driva prestation genom oro ("jag måste förbereda mig extra")
- Högre risk för ångest och depression (men inte oundvikligt!)

**I praktiken:**
- Du oroar dig mer än andra (men fångar också problem tidigt)
- Känslor är intensiva - både positiva och negativa
- Kan ha svårt att släppa tankar på kvällen
- Behöver strategier för stresshantering
- Ofta empatisk och förstående för andras känslor
                """,
                'low_description': """
Personer med låg neuroticism (hög emotionell stabilitet) är lugna, stabila och hanterar stress väl.
Du är förmodligen jämn i humöret, släpper saker lätt, och oroar dig sällan.

**Forskning visar:**
- Lägre neuroticism = bättre fysisk hälsa
- Högre livstillfredsställelse
- Bättre ledarskap (lugn under press)
- Ofta i högrisk-yrken (polis, brandman, pilot, kirurg)
- Återhämtar sig snabbare från motgångar

**I praktiken:**
- Du är teamets lugna klippa i kriser
- Tar inte saker personligt
- Kan verka "känsloläst" för andra (men är oftast bara stabil)
- Kan ibland missa viktiga varningssignaler (oroar sig för lite)
                """,
                'mid_description': """
Du har balanserad emotionell stabilitet, vilket innebär att du reagerar normalt på stress -
varken överdrivet eller underdrivet.

**I praktiken:**
- Känslomässigt responsiv men inte överväldigad
- Hanterar stress genomsnittligt
- Balans mellan känslighet och stabilitet
                """,
                'facets': ['Ångest', 'Ilska', 'Depression', 'Självmedvetenhet', 'Impulsivitet', 'Sårbarhet'],
                'swedish_term': 'Neuroticism / Emotionell stabilitet'
            },
            'O': {
                'name': 'Openness',
                'definition': 'Öppenhet handlar om nyfikenhet, kreativitet och intresse för nya upplevelser och idéer.',
                'high_description': """
Personer med hög öppenhet är nyfikna, kreativa och älskar nya idéer. Du trivs förmodligen med
abstrakt tänkande, gillar konst och filosofi, och vill utforska ovanliga perspektiv.

**Forskning visar:**
- Högre öppenhet = mer kreativitet och innovation
- Bättre på att lära sig nya saker (neuroplasticitet)
- Ofta högre utbildning och bredare intressen
- Mer politiskt liberala (öppna för förändring)
- Trivs i komplexa, intellektuellt stimulerande jobb

**I praktiken:**
- Du läser brett, utforskar nya idéer, gillar debatt
- Kan tänka "outside the box" lätt
- Trivs i kreativa, strategiska eller forskande yrken
- Kan bli uttråkad av repetitivt arbete
- Ofta kulturnörd (musik, konst, litteratur, filosofi)
                """,
                'low_description': """
Personer med låg öppenhet är praktiska, konkreta och föredrar beprövade metoder. Du värdesätter
förmodligen tradition, fokuserar på det konkreta snarare än abstrakta, och gillar rutiner.

**Forskning visar:**
- Lägre öppenhet = bättre på att följa processer och rutiner
- Mer politiskt konservativa (värnar tradition)
- Trivs i strukturerade, väldefinierade yrken
- Ofta högre lojalitet till organisationer
- Bra på detaljarbete och kvalitetskontroll

**I praktiken:**
- Du föredrar "vad som fungerar" framför experiment
- Trivs med tydliga ramar och processer
- Kan vara skeptisk till nya metoder
- Ofta pålitlig i roller som kräver konsekvens
- Gillar konkreta, praktiska lösningar
                """,
                'mid_description': """
Du har balanserad öppenhet, vilket innebär att du kan både uppskatta nya idéer och värdera tradition.
Du är öppen men inte orealistisk, praktisk men inte stelbent.

**I praktiken:**
- Balans mellan innovation och proven methods
- Kan både tänka kreativt och praktiskt
- Öppen för nya idéer om de verkar vettiga
                """,
                'facets': ['Fantasi', 'Estetik', 'Känslor', 'Handlingar', 'Idéer', 'Värderingar'],
                'swedish_term': 'Öppenhet / Openness'
            }
        }

        trait_data = explanations.get(trait, {})
        if not trait_data:
            return {}

        # Select appropriate description based on score
        if score >= 65:
            description = trait_data.get('high_description', '')
        elif score <= 35:
            description = trait_data.get('low_description', '')
        else:
            description = trait_data.get('mid_description', '')

        return {
            'name': trait_data.get('name', ''),
            'swedish_term': trait_data.get('swedish_term', ''),
            'definition': trait_data.get('definition', ''),
            'description': description,
            'facets': trait_data.get('facets', [])
        }

    # ═══════════════════════════════════════════════════════════════════════
    # CAREER GUIDANCE
    # ═══════════════════════════════════════════════════════════════════════

    def get_career_recommendations(
        self,
        scores: Dict[str, float],
        language: str = "sv"
    ) -> List[CareerMatch]:
        """
        Get personalized career recommendations based on Big Five profile
        Returns top career matches with reasoning
        """

        if language == "sv":
            return self._get_career_recommendations_swedish(scores)
        else:
            return self._get_career_recommendations_english(scores)

    def _get_career_recommendations_swedish(self, scores: Dict[str, float]) -> List[CareerMatch]:
        """Swedish career recommendations"""

        e = scores.get('E', 50)
        a = scores.get('A', 50)
        c = scores.get('C', 50)
        n = scores.get('N', 50)
        o = scores.get('O', 50)

        matches = []

        # Software Developer / Programmerare
        if c >= 55 and o >= 55:
            fit = ((c - 50) / 50 + (o - 50) / 50) / 2
            matches.append(CareerMatch(
                career="Programmerare / Mjukvaruutvecklare",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Din kombination av samvetsgrannhet och öppenhet passar perfekt för programmering. Samvetsgrannheten hjälper dig skriva ren, debuggad kod, medan öppenheten gör att du lätt lär dig nya språk och ramverk.",
                required_traits={'C': 'medel-hög', 'O': 'medel-hög', 'E': 'flexibel'}
            ))

        # Psykolog / Terapeut
        if a >= 60 and o >= 55:
            fit = ((a - 50) / 50 + (o - 50) / 50) / 2
            matches.append(CareerMatch(
                career="Psykolog / Terapeut",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Hög vänlighet gör dig empatisk och lyhörd, medan öppenheten hjälper dig förstå komplexa mänskliga beteenden och nya teorier. Du bryr dig genuint om andras välmående.",
                required_traits={'A': 'hög', 'O': 'medel-hög', 'N': 'medel (känslomässig stabilitet)'}
            ))

        # Entrepreneur / Entreprenör
        if e >= 55 and c <= 60 and o >= 60:
            fit = ((e - 50) / 50 + (o - 50) / 50 + (60 - c) / 50) / 3
            matches.append(CareerMatch(
                career="Entreprenör / Startup-grundare",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Hög extraversion hjälper dig nätverka och pitcha, öppenhet driver innovation, och flexibel samvetsgrannhet gör att du kan pivotera snabbt när marknaden förändras.",
                required_traits={'E': 'medel-hög', 'O': 'hög', 'C': 'flexibel (ej för hög)'}
            ))

        # Accountant / Revisor
        if c >= 70 and a <= 55:
            fit = ((c - 50) / 50 + (55 - a) / 50) / 2
            matches.append(CareerMatch(
                career="Revisor / Controller",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Extremt hög samvetsgrannhet = perfekt för detaljerad, noggrann ekonomihantering. Lägre vänlighet hjälper dig vara objektiv och säga nej när siffror inte stämmer.",
                required_traits={'C': 'mycket hög', 'A': 'låg-medel', 'E': 'flexibel'}
            ))

        # Teacher / Lärare
        if a >= 60 and e >= 55:
            fit = ((a - 50) / 50 + (e - 50) / 50) / 2
            matches.append(CareerMatch(
                career="Lärare / Pedagog",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Vänlighet gör dig tålmodig och empatisk med elever, extraversion ger dig energi att stå framför klassen varje dag. Du bryr dig om deras utveckling.",
                required_traits={'A': 'medel-hög', 'E': 'medel-hög', 'C': 'medel (struktur behövs)'}
            ))

        # Researcher / Forskare
        if o >= 70 and c >= 60:
            fit = ((o - 50) / 50 + (c - 50) / 50) / 2
            matches.append(CareerMatch(
                career="Forskare / Akademiker",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Extremt hög öppenhet driver din nyfikenhet och abstrakt tänkande, samvetsgrannheten gör att du kan genomföra rigorösa studier. Perfekt för att utforska nya idéer systematiskt.",
                required_traits={'O': 'mycket hög', 'C': 'medel-hög', 'E': 'låg-medel (ensamt arbete)'}
            ))

        # Sales / Säljare
        if e >= 65 and a <= 50:
            fit = ((e - 50) / 50 + (50 - a) / 50) / 2
            matches.append(CareerMatch(
                career="Säljare / Account Manager",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Hög extraversion gör att du gillar att träffa nya kunder och pitcha, lägre vänlighet hjälper dig förhandla hårt och stå emot nej. Du är driven att vinna.",
                required_traits={'E': 'hög', 'A': 'låg-medel', 'C': 'medel (måste följa upp)'}
            ))

        # Artist / Konstnär
        if o >= 70 and c <= 45:
            fit = ((o - 50) / 50 + (50 - c) / 50) / 2
            matches.append(CareerMatch(
                career="Konstnär / Kreativ yrkesutövare",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Extremt hög öppenhet = kreativ vision och vilja att experimentera. Lägre samvetsgrannhet gör att du inte fastnar i regler utan kan bryta ny mark. Du skapar istället för att följa.",
                required_traits={'O': 'mycket hög', 'C': 'låg-medel (för mycket struktur hämmar)', 'E': 'flexibel'}
            ))

        # Project Manager / Projektledare
        if c >= 65 and e >= 60 and a >= 55:
            fit = ((c - 50) / 50 + (e - 50) / 50 + (a - 50) / 50) / 3
            matches.append(CareerMatch(
                career="Projektledare",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Samvetsgrannhet = strukturerad planering, extraversion = leda möten och team, vänlighet = bygga relationer och lösa konflikter. Du är den som håller ihop alltihopa.",
                required_traits={'C': 'hög', 'E': 'medel-hög', 'A': 'medel-hög'}
            ))

        # Data Analyst
        if c >= 60 and o >= 60 and e <= 50:
            fit = ((c - 50) / 50 + (o - 50) / 50 + (50 - e) / 50) / 3
            matches.append(CareerMatch(
                career="Dataanalytiker / Data Scientist",
                fit_score=min(1.0, max(0.0, 0.5 + fit / 2)),
                reasoning="Samvetsgrannhet = noggrannhet med data, öppenhet = nyfiken på mönster och nya metoder, introversion = fokus på djupanalys utan distraktion.",
                required_traits={'C': 'medel-hög', 'O': 'medel-hög', 'E': 'låg-medel'}
            ))

        # Sort by fit score
        matches.sort(key=lambda x: x.fit_score, reverse=True)

        return matches[:5]  # Top 5

    # ═══════════════════════════════════════════════════════════════════════
    # RELATIONSHIP DYNAMICS
    # ═══════════════════════════════════════════════════════════════════════

    def get_relationship_insights(
        self,
        user_scores: Dict[str, float],
        partner_scores: Optional[Dict[str, float]] = None,
        language: str = "sv"
    ) -> RelationshipInsight:
        """
        Get relationship insights based on personality
        If partner scores provided, analyzes dynamic between them
        """

        if language == "sv":
            return self._get_relationship_insights_swedish(user_scores, partner_scores)
        else:
            return self._get_relationship_insights_english(user_scores, partner_scores)

    def _get_relationship_insights_swedish(
        self,
        user_scores: Dict[str, float],
        partner_scores: Optional[Dict[str, float]]
    ) -> RelationshipInsight:
        """Swedish relationship insights"""

        e = user_scores.get('E', 50)
        a = user_scores.get('A', 50)
        c = user_scores.get('C', 50)
        n = user_scores.get('N', 50)
        o = user_scores.get('O', 50)

        if not partner_scores:
            # General relationship style based on user's traits
            strengths = []
            challenges = []
            advice = []

            if a >= 60:
                strengths.append("Empatisk och stöttande partner")
                strengths.append("Bra på kompromisser och konfliktlösning")
                challenges.append("Kan sätta partners behov före egna (för mycket)")
                advice.append("Öva på att sätta gränser och kommunicera dina egna behov")

            if a <= 40:
                strengths.append("Ärlig och direkt kommunikation")
                strengths.append("Klarar av svåra samtal")
                challenges.append("Kan uppfattas som hård eller okänslig ibland")
                advice.append("Träna på mjukare formuleringar när partner är sårbar")

            if e >= 60:
                strengths.append("Skapar social energi i relationen")
                strengths.append("Tar initiativ till aktiviteter tillsammans")
                challenges.append("Kan behöva mer socialt än introvert partner orkar")
                advice.append("Respektera partners behov av nedtid")

            if e <= 40:
                strengths.append("Djup och reflekterande i samtal")
                strengths.append("Behöver inte konstant stimulans")
                challenges.append("Kan behöva ensam tid som partner tolkar som distans")
                advice.append("Kommunicera tydligt när du behöver ladda batterier")

            if c >= 60:
                strengths.append("Pålitlig och stabil partner")
                strengths.append("Planerar framåt för relationens framtid")
                challenges.append("Kan bli frustrerad av partners spontanitet")
                advice.append("Öva på att släppa planer ibland och flyta med")

            if n >= 60:
                strengths.append("Djup emotionell koppling")
                strengths.append("Känslig för partners känslor")
                challenges.append("Kan bli överväldigad av relationskonflikter")
                advice.append("Träna på mindfulness och kommunicera känslor tidigt")

            if o >= 60:
                strengths.append("Öppen för nya upplevelser tillsammans")
                strengths.append("Intellektuellt stimulerande samtal")
                challenges.append("Kan bli uttråkad i rutiner")
                advice.append("Hitta balans mellan äventyr och stabilitet")

            return RelationshipInsight(
                dynamic_type="Din relationsstil",
                description=f"Baserat på din Big Five-profil har du både styrkor och utmaningar i relationer.",
                strengths=strengths if strengths else ["Balanserad relationsstil"],
                challenges=challenges if challenges else ["Inga tydliga utmaningar"],
                advice=advice if advice else ["Fortsätt kommunicera öppet"]
            )

        # If partner scores provided, analyze dynamic
        else:
            # Compare traits
            e_diff = abs(e - partner_scores.get('E', 50))
            a_diff = abs(a - partner_scores.get('A', 50))

            if e_diff >= 30:
                return RelationshipInsight(
                    dynamic_type="Introvert-Extravert dynamik",
                    description="Ni har mycket olika energinivåer och sociala behov.",
                    strengths=[
                        "Ni balanserar varandra - en driver socialt, en bromsar",
                        "Kan lära av varandras perspektiv",
                        "Bredare socialt spektrum tillsammans"
                    ],
                    challenges=[
                        "Konflikter om hur mycket socialt vs hemma-tid",
                        "Risk att den extraverta känner sig begränsad",
                        "Risk att den introverta känner sig utmattad"
                    ],
                    advice=[
                        "Kommunicera tydligt om energinivåer",
                        "Skapa win-win: extraverta umgås solo ibland, introverta följer med ibland",
                        "Respektera att ni laddar på olika sätt"
                    ]
                )

    # ═══════════════════════════════════════════════════════════════════════
    # PERSONAL DEVELOPMENT
    # ═══════════════════════════════════════════════════════════════════════

    def get_development_strategies(
        self,
        trait: str,
        current_score: float,
        desired_direction: str,  # "increase" or "decrease"
        language: str = "sv"
    ) -> Dict[str, List[str]]:
        """
        Get evidence-based strategies for personality development

        Note: Personality IS changeable but requires sustained effort!
        Research shows ~20-30% change is possible over years
        """

        if language == "sv":
            return self._get_development_strategies_swedish(trait, current_score, desired_direction)
        else:
            return {}

    def _get_development_strategies_swedish(
        self,
        trait: str,
        current_score: float,
        desired_direction: str
    ) -> Dict[str, List[str]]:
        """Swedish development strategies"""

        strategies = {
            'E_increase': {
                'understanding': [
                    "Forskning visar att extraversion KAN ökas, men det tar tid och övning.",
                    "Du behöver inte bli extremt extravert - små förändringar kan ge stor effekt.",
                    "Målet är inte att ändra vem du är, utan att utöka din komfortzon."
                ],
                'practical_steps': [
                    "Börja smått: Säg hej till en främling i veckan",
                    "Gå med i en klubb/grupp kring ett intresse",
                    "Öva på small talk i lågrisk-situationer (kassan, hissen)",
                    "Sätt mål: Initiera 1 samtal per dag",
                    "Efter sociala events: Notera vad som gick bra (inte bara vad som kändes jobbigt)"
                ],
                'mindset': [
                    "Betrakta sociala situationer som träning, inte test",
                    "Påminn dig: De flesta är för upptagna med sig själva för att döma dig",
                    "Extraversion = lärd färdighet, inte medfödd begåvning"
                ],
                'realistic_timeline': "3-6 månader av konsekvent övning för märkbar förändring"
            },
            'C_increase': {
                'understanding': [
                    "Samvetsgrannhet är det drag som LÄTTAST att ändra (forskning bekräftar).",
                    "Det handlar om att bygga system och vanor, inte vilja.",
                    "Du kommer alltid vara mer spontan än super-organiserade, men kan hitta din struktur."
                ],
                'practical_steps': [
                    "Börja med EN vana: Gör sängen varje morgon (bygger momentum)",
                    "Använd externa system: Kalender-alerts, to-do-appar, automatisering",
                    "Implementation intentions: 'När klockan är 9, då gör jag X'",
                    "Börja planera kvällen före (bara 5 min)",
                    "Belöna dig när du följer planen (positiv förstärkning)"
                ],
                'mindset': [
                    "Du bygger inte perfektionism, utan tillförlitlighet",
                    "Struktur = frihet (mindre mental energi på att hålla koll)",
                    "Missa inte två dagar i rad (en miss = ok, två = ny vana)"
                ],
                'realistic_timeline': "2-3 månader för nya vanor att kännas naturliga"
            },
            'A_increase': {
                'understanding': [
                    "Vänlighet kan tränas genom medkänsla-meditation (metta).",
                    "Ofta handlar det mer om uttryck än känslor - du kanske KÄNNER empati men visar det inte.",
                    "Målet är inte att bli mjuk, utan att vara taktfull när det spelar roll."
                ],
                'practical_steps': [
                    "Öva aktiv lyssning: Upprepa vad personen sa innan du svarar",
                    "Fråga 'Hur mår du?' och lyssna faktiskt på svaret",
                    "När du är kritisk: Lägg till något positivt också",
                    "Träna på 'mjuka starts' i konflikter: 'Jag känner mig...' istället för 'Du gör aldrig...'",
                    "Loving-kindness meditation 5 min/dag (applikationer finns)"
                ],
                'mindset': [
                    "Vänlighet ≠ svaghet, det är strategiskt i relationer",
                    "Du kan vara både direkt OCH empatisk",
                    "Människor hör kritik bättre när de känner sig sedda först"
                ],
                'realistic_timeline': "Märkbar skillnad inom 1-2 månader av övning"
            },
            'N_decrease': {
                'understanding': [
                    "Neuroticism kan minskas (mest forskningsstöd för KBT och mindfulness).",
                    "Det handlar inte om att sluta känna, utan att hantera känslor bättre.",
                    "Din känslighet kan vara styrka - målet är kontroll, inte avdöva."
                ],
                'practical_steps': [
                    "Daglig mindfulness: 10 min meditation (Headspace, Calm)",
                    "Journaling: Skriv ner oro, lägg ifrån dig på papper",
                    "Kognitiv omstrukturering: Utmana katastrofala tankar ('Vad är worst case? Hur sannolikt?')",
                    "Sömn + motion + kost (biologisk grund för stabilitet)",
                    "Professionell terapi om det påverkar livet kraftigt"
                ],
                'mindset': [
                    "Känslor är data, inte direktiv",
                    "Tankar är inte fakta",
                    "Du kan känna ångest OCH agera modig"
                ],
                'realistic_timeline': "3-6 månader av KBT/mindfulness för märkbar effekt"
            }
        }

        key = f"{trait}_{desired_direction}"
        return strategies.get(key, {
            'understanding': ["Denna riktning kräver mer specifik kontext."],
            'practical_steps': ["Kontakta en professionell coach för skräddarsydda råd."],
            'mindset': [],
            'realistic_timeline': "Varierande"
        })

    # ═══════════════════════════════════════════════════════════════════════
    # DISC KNOWLEDGE (brief, for integration)
    # ═══════════════════════════════════════════════════════════════════════

    def get_disc_explanation(self, language: str = "sv") -> Dict[str, str]:
        """Quick DISC model explanation"""

        if language == "sv":
            return {
                'D': "Dominance: Direkthet, resultatfokus, beslutsfattande. Drivs av kontroll och utmaningar.",
                'I': "Influence: Social, entusiastisk, optimistisk. Drivs av erkännande och relationer.",
                'S': "Steadiness: Stabil, lojal, tålmodig. Drivs av harmoni och trygghet.",
                'C': "Conscientiousness: Analytisk, noggrann, systematisk. Drivs av kvalitet och exakthet."
            }
        else:
            return {
                'D': "Dominance: Direct, results-focused, decisive. Driven by control and challenges.",
                'I': "Influence: Social, enthusiastic, optimistic. Driven by recognition and relationships.",
                'S': "Steadiness: Stable, loyal, patient. Driven by harmony and security.",
                'C': "Conscientiousness: Analytical, precise, systematic. Driven by quality and accuracy."
            }


# Example usage
if __name__ == "__main__":
    kb = PsychologyKnowledgeBase(language="sv")

    # Test trait explanation
    print("=== TRAIT EXPLANATION ===")
    explanation = kb.get_trait_explanation('E', 35, "sv")
    print(f"{explanation['name']}: {explanation['swedish_term']}")
    print(explanation['description'][:500] + "...")

    print("\n=== CAREER RECOMMENDATIONS ===")
    test_scores = {'E': 35, 'A': 75, 'C': 45, 'N': 65, 'O': 80}
    careers = kb.get_career_recommendations(test_scores, "sv")
    for career in careers[:3]:
        print(f"\n{career.career} (fit: {career.fit_score:.2f})")
        print(f"  {career.reasoning}")

    print("\n=== DEVELOPMENT STRATEGY ===")
    strategy = kb.get_development_strategies('C', 35, 'increase', "sv")
    print("Praktiska steg:")
    for step in strategy.get('practical_steps', [])[:3]:
        print(f"  - {step}")
