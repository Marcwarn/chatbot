"""
DISC Report Generator - Comprehensive personality reports
Generates detailed DISC reports with career recommendations and insights
Supports Swedish and English
"""

from typing import Dict, List, Optional
from anthropic import Anthropic
import json

from disc_analysis import DISCProfile, DISCScores, get_strengths_from_profile, get_development_areas, get_dimension_interpretation
from disc_prompts import get_profile_name, get_profile_traits


# ============================================================================
# REPORT DATA MODELS
# ============================================================================

class DISCReport:
    """Complete DISC assessment report"""

    def __init__(
        self,
        profile: DISCProfile,
        language: str = "sv",
        personalized_insights: Optional[Dict] = None
    ):
        self.profile = profile
        self.language = language
        self.personalized_insights = personalized_insights

    def to_dict(self) -> Dict:
        """Export report as dictionary"""
        return {
            "profile_code": self.profile.profile_code,
            "profile_name": get_profile_name(self.profile.profile_code, self.language),
            "profile_traits": get_profile_traits(self.profile.profile_code, self.language),
            "scores": self.profile.scores.to_dict(),
            "dimension_interpretations": self.get_dimension_interpretations(),
            "summary": self.get_summary(),
            "strengths": self.get_strengths(),
            "development_areas": self.get_development_areas(),
            "work_style": self.get_work_style(),
            "communication_style": self.get_communication_style(),
            "career_recommendations": self.get_career_recommendations(),
            "team_dynamics": self.get_team_dynamics(),
            "personalized_insights": self.personalized_insights
        }

    def get_dimension_interpretations(self) -> List[Dict]:
        """Get interpretations for all four DISC dimensions"""
        dimensions = ["D", "I", "S", "C"]
        scores = {
            "D": self.profile.scores.dominance,
            "I": self.profile.scores.influence,
            "S": self.profile.scores.steadiness,
            "C": self.profile.scores.conscientiousness
        }

        interpretations = []
        for dim in dimensions:
            interp = get_dimension_interpretation(dim, scores[dim], self.language)
            interpretations.append({
                "dimension": dim,
                "score": scores[dim],
                **interp
            })

        return interpretations

    def get_summary(self) -> str:
        """Get overall profile summary"""
        profile_name = get_profile_name(self.profile.profile_code, self.language)

        if self.language == "sv":
            return f"Du har en {profile_name}-profil. {get_profile_traits(self.profile.profile_code, self.language)}. Din primära stil är {self.profile.primary_style}, vilket betyder att du naturligt dras till {self._get_primary_behavior()}."
        else:
            return f"You have a {profile_name} profile. {get_profile_traits(self.profile.profile_code, self.language)}. Your primary style is {self.profile.primary_style}, which means you are naturally drawn to {self._get_primary_behavior()}."

    def _get_primary_behavior(self) -> str:
        """Get primary behavioral tendency description"""
        behaviors = {
            "D": {
                "sv": "resultat, utmaningar och snabba beslut",
                "en": "results, challenges, and quick decisions"
            },
            "I": {
                "sv": "relationer, samarbete och socialt inflytande",
                "en": "relationships, collaboration, and social influence"
            },
            "S": {
                "sv": "stabilitet, harmoni och pålitligt lagarbete",
                "en": "stability, harmony, and reliable teamwork"
            },
            "C": {
                "sv": "kvalitet, precision och systematisk analys",
                "en": "quality, precision, and systematic analysis"
            }
        }
        lang = "sv" if self.language == "sv" else "en"
        return behaviors.get(self.profile.primary_style, {}).get(lang, "")

    def get_strengths(self) -> List[str]:
        """Get list of key strengths"""
        return get_strengths_from_profile(self.profile, self.language)

    def get_development_areas(self) -> List[str]:
        """Get list of development areas"""
        return get_development_areas(self.profile, self.language)

    def get_work_style(self) -> str:
        """Get work style description based on DISC profile"""
        profile_code = self.profile.profile_code

        work_styles = {
            "D": {
                "sv": "Du trivs i tempofyllda miljöer där du kan ta beslut och driva resultat. Du uppskattar autonomi och utmaningar. Du arbetar bäst med tydliga mål och minimal övervakning. Undvik mikro-management och alltför långsamma processer.",
                "en": "You thrive in fast-paced environments where you can make decisions and drive results. You appreciate autonomy and challenges. You work best with clear goals and minimal supervision. Avoid micro-management and overly slow processes."
            },
            "I": {
                "sv": "Du blomstrar i samarbetsintensiva miljöer med mycket människokontakt. Du uppskattar teamwork, brainstorming och socialt samspel. Du arbetar bäst när du kan påverka andra och bygga relationer. Undvik isolerat arbete och rigid struktur.",
                "en": "You flourish in collaborative environments with lots of people contact. You appreciate teamwork, brainstorming, and social interaction. You work best when you can influence others and build relationships. Avoid isolated work and rigid structure."
            },
            "S": {
                "sv": "Du trivs i stabila, förutsägbara miljöer där du kan bygga långsiktiga relationer. Du uppskattar tydliga rutiner och laganda. Du arbetar bäst när du känner dig värdefull för teamet och har tid att anpassa dig till förändringar. Undvik plötsliga omorganisationer och konflikter.",
                "en": "You thrive in stable, predictable environments where you can build long-term relationships. You appreciate clear routines and team spirit. You work best when you feel valued by the team and have time to adapt to changes. Avoid sudden reorganizations and conflicts."
            },
            "C": {
                "sv": "Du trivs i strukturerade miljöer med höga kvalitetskrav. Du uppskattar tydliga processer, data och tid för analys. Du arbetar bäst när du får granska detaljer och säkerställa precision. Undvik brådska och otydliga krav.",
                "en": "You thrive in structured environments with high quality standards. You appreciate clear processes, data, and time for analysis. You work best when you can review details and ensure precision. Avoid rush and unclear requirements."
            },
            "DI": {
                "sv": "Du kombinerar drivkraft med karisma och trivs som ledare i dynamiska team. Du vill uppnå resultat samtidigt som du inspirerar andra. Du arbetar bäst med både målstyrning och människokontakt.",
                "en": "You combine drive with charisma and thrive as a leader in dynamic teams. You want to achieve results while inspiring others. You work best with both goal direction and people contact."
            },
            "DC": {
                "sv": "Du kombinerar handlingskraft med noggrannhet och trivs i roller som kräver både tempo och kvalitet. Du vill driva resultat med precision. Du arbetar bäst när du kan vara både effektiv och grundlig.",
                "en": "You combine action with precision and thrive in roles requiring both pace and quality. You want to drive results with precision. You work best when you can be both efficient and thorough."
            },
            "DS": {
                "sv": "Du balanserar resultatfokus med teamharmoni och trivs som stabil ledare. Du vill uppnå mål utan att offra relationerna. Du arbetar bäst när du kan leda med både styrka och empati.",
                "en": "You balance results focus with team harmony and thrive as a stable leader. You want to achieve goals without sacrificing relationships. You work best when you can lead with both strength and empathy."
            },
            "IS": {
                "sv": "Du kombinerar social energi med stabilitet och trivs som lagspelare och supporter. Du bygger starka team genom entusiasm och lojalitet. Du arbetar bäst i positiva, trygga miljöer.",
                "en": "You combine social energy with stability and thrive as a team player and supporter. You build strong teams through enthusiasm and loyalty. You work best in positive, secure environments."
            },
            "IC": {
                "sv": "Du balanserar kreativitet med analys och trivs i roller som kräver både innovation och precision. Du vill tänka nytt samtidigt som du säkerställer kvalitet.",
                "en": "You balance creativity with analysis and thrive in roles requiring both innovation and precision. You want to think creatively while ensuring quality."
            },
            "SC": {
                "sv": "Du kombinerar stabilitet med kvalitet och trivs som pålitlig specialist. Du levererar konsekvent hög standard genom systematik och noggrannhet. Du arbetar bäst i lugn och ordning.",
                "en": "You combine stability with quality and thrive as a reliable specialist. You consistently deliver high standards through systematic and thorough work. You work best in calm and order."
            }
        }

        lang = "sv" if self.language == "sv" else "en"
        return work_styles.get(profile_code, work_styles.get(self.profile.primary_style, {})).get(lang, "")

    def get_communication_style(self) -> str:
        """Get communication style description"""
        profile_code = self.profile.profile_code

        comm_styles = {
            "D": {
                "sv": "Du kommunicerar direkt, kortfattat och resultatfokuserat. Du uppskattar när andra är konkreta och kommer till poängen snabbt. Ge andra tid att tänka och var medveten om att din direkthet kan upplevas som hård. Träna på att lyssna mer och lägga till empati i din kommunikation.",
                "en": "You communicate directly, concisely, and results-focused. You appreciate when others are concrete and get to the point quickly. Give others time to think and be aware that your directness can be perceived as harsh. Practice listening more and adding empathy to your communication."
            },
            "I": {
                "sv": "Du kommunicerar entusiastiskt, öppet och relationsorienterat. Du delar gärna idéer och känslor. Var medveten om att strukturera dina budskap och följ upp konkreta åtaganden. Träna på att vara mer koncis och fokuserad när situationen kräver det.",
                "en": "You communicate enthusiastically, openly, and relationship-oriented. You readily share ideas and feelings. Be mindful of structuring your messages and following up on concrete commitments. Practice being more concise and focused when the situation requires it."
            },
            "S": {
                "sv": "Du kommunicerar lugnt, lyssnande och diplomatiskt. Du undviker konflikt och söker konsensus. Träna på att uttrycka åsikter även när de kan skapa spänningar. Var tydligare med dina behov och gränser. Din lyhördhet är en styrka - använd den aktivt.",
                "en": "You communicate calmly, listening, and diplomatically. You avoid conflict and seek consensus. Practice expressing opinions even when they might create tension. Be clearer about your needs and boundaries. Your responsiveness is a strength - use it actively."
            },
            "C": {
                "sv": "Du kommunicerar analytiskt, strukturerat och fakta-baserat. Du föredrar skriftlig kommunikation och väl förberedda möten. Träna på att vara mer spontan och personlig i din kommunikation. Balansera data med relationer och visa mer av dig själv.",
                "en": "You communicate analytically, structured, and fact-based. You prefer written communication and well-prepared meetings. Practice being more spontaneous and personal in your communication. Balance data with relationships and show more of yourself."
            },
            "DI": {
                "sv": "Du kommunicerar med energi och tydlighet. Du är både resultatfokuserad och relationsskapande. Balansera din direkthet med lyssnade och ge andra utrymme att bidra.",
                "en": "You communicate with energy and clarity. You are both results-focused and relationship-building. Balance your directness with listening and give others space to contribute."
            },
            "DC": {
                "sv": "Du kommunicerar tydligt och faktabaserat. Du kombinerar effektivitet med noggrannhet. Träna på att vara mer personlig och empatisk i din kommunikation.",
                "en": "You communicate clearly and fact-based. You combine efficiency with precision. Practice being more personal and empathetic in your communication."
            },
            "DS": {
                "sv": "Du kommunicerar med auktoritet men också omtanke. Du balanserar styrka med empati. Fortsätt utveckla denna unika kombination.",
                "en": "You communicate with authority but also care. You balance strength with empathy. Continue developing this unique combination."
            },
            "IS": {
                "sv": "Du kommunicerar varmt och inkluderande. Du skapar trygghet genom både entusiasm och stabilitet. Träna på att vara mer direkt när situationen kräver det.",
                "en": "You communicate warmly and inclusively. You create security through both enthusiasm and stability. Practice being more direct when the situation requires it."
            },
            "IC": {
                "sv": "Du kommunicerar kreativt men strukturerat. Du balanserar innovation med precision. Var medveten om att inte övervälma andra med detaljer.",
                "en": "You communicate creatively but structured. You balance innovation with precision. Be mindful not to overwhelm others with details."
            },
            "SC": {
                "sv": "Du kommunicerar systematiskt och tillförlitligt. Du skapar förtroende genom både stabilitet och kvalitet. Träna på att vara mer proaktiv i din kommunikation.",
                "en": "You communicate systematically and reliably. You build trust through both stability and quality. Practice being more proactive in your communication."
            }
        }

        lang = "sv" if self.language == "sv" else "en"
        return comm_styles.get(profile_code, comm_styles.get(self.profile.primary_style, {})).get(lang, "")

    def get_career_recommendations(self) -> List[str]:
        """Get career recommendations based on DISC profile"""
        profile_code = self.profile.profile_code

        careers = {
            "D": {
                "sv": [
                    "VD/Företagsledare - Din drivkraft och beslutsamhet passar perfekt för ledande positioner",
                    "Entreprenör - Du tar risker och driver igenom visioner",
                    "Säljchef - Din målmedvetenhet ger resultat",
                    "Projektledare (snabba projekt) - Du levererar under press",
                    "Managementkonsult - Du löser problem effektivt"
                ],
                "en": [
                    "CEO/Executive - Your drive and decisiveness fit perfectly for leadership positions",
                    "Entrepreneur - You take risks and drive visions forward",
                    "Sales Director - Your goal-orientation delivers results",
                    "Project Manager (fast projects) - You deliver under pressure",
                    "Management Consultant - You solve problems efficiently"
                ]
            },
            "I": {
                "sv": [
                    "Försäljare/Account Manager - Du bygger relationer naturligt",
                    "HR-specialist/Rekryterare - Din empatiska förmåga är ovärderlig",
                    "Marknadsföringschef - Du kommunicerar budskap engagerande",
                    "Event Manager - Du skapar energi och sammanhållning",
                    "Coach/Tränare - Du inspirerar och motiverar andra"
                ],
                "en": [
                    "Sales/Account Manager - You build relationships naturally",
                    "HR Specialist/Recruiter - Your empathetic ability is invaluable",
                    "Marketing Director - You communicate messages engagingly",
                    "Event Manager - You create energy and cohesion",
                    "Coach/Trainer - You inspire and motivate others"
                ]
            },
            "S": {
                "sv": [
                    "HR-generalist - Du skapar trygghet för medarbetare",
                    "Kundtjänstchef - Din tålamod och empati är perfekt",
                    "Projektkoordinator - Du håller ihop teamet",
                    "Socialsekreterare/Kurator - Du stöttar människor genom svårigheter",
                    "Teamledare - Du leder genom förtroende och stabilitet"
                ],
                "en": [
                    "HR Generalist - You create security for employees",
                    "Customer Service Manager - Your patience and empathy are perfect",
                    "Project Coordinator - You hold the team together",
                    "Social Worker/Counselor - You support people through difficulties",
                    "Team Leader - You lead through trust and stability"
                ]
            },
            "C": {
                "sv": [
                    "Revisor/Controller - Din noggrannhet och systematik är avgörande",
                    "Kvalitetsansvarig - Du säkerställer höga standarder",
                    "Data Analyst - Du älskar att dyka djupt i siffror",
                    "Systemutvecklare - Din precision skapar felfri kod",
                    "Forskare - Du granskar data metodiskt"
                ],
                "en": [
                    "Auditor/Controller - Your precision and systematic approach are crucial",
                    "Quality Manager - You ensure high standards",
                    "Data Analyst - You love diving deep into numbers",
                    "Systems Developer - Your precision creates flawless code",
                    "Researcher - You examine data methodically"
                ]
            },
            "DI": {
                "sv": [
                    "Sales Director - Du kombinerar resultat med relationer",
                    "Startup-grundare - Din energi och drivkraft skapar företag",
                    "Politisk ledare - Du inspirerar och driver förändring",
                    "Management Consultant - Du influerar och löser problem"
                ],
                "en": [
                    "Sales Director - You combine results with relationships",
                    "Startup Founder - Your energy and drive create companies",
                    "Political Leader - You inspire and drive change",
                    "Management Consultant - You influence and solve problems"
                ]
            },
            "DC": {
                "sv": [
                    "COO/Operations Director - Du driver kvalitet och resultat",
                    "IT-projektledare - Du kombinerar tempo med precision",
                    "Teknisk chef - Du leder med expertis och handlingskraft"
                ],
                "en": [
                    "COO/Operations Director - You drive quality and results",
                    "IT Project Manager - You combine pace with precision",
                    "Technical Director - You lead with expertise and action"
                ]
            },
            "DS": {
                "sv": [
                    "HR-direktör - Du balanserar affärsbeslut med medarbetaromsorg",
                    "Verksamhetschef (vård/skola) - Du leder med både styrka och empati"
                ],
                "en": [
                    "HR Director - You balance business decisions with employee care",
                    "Operations Manager (healthcare/education) - You lead with both strength and empathy"
                ]
            },
            "IS": {
                "sv": [
                    "Teamledare/Scrum Master - Du bygger starka, harmoniska team",
                    "Customer Success Manager - Du skapar långsiktiga relationer",
                    "Lärare - Du inspirerar och stöttar"
                ],
                "en": [
                    "Team Leader/Scrum Master - You build strong, harmonious teams",
                    "Customer Success Manager - You create long-term relationships",
                    "Teacher - You inspire and support"
                ]
            },
            "IC": {
                "sv": [
                    "UX Designer - Du kombinerar kreativitet med användarforskning",
                    "Produktchef - Du innoverar baserat på data",
                    "Kreativ strateg - Du tänker nytt med precision"
                ],
                "en": [
                    "UX Designer - You combine creativity with user research",
                    "Product Manager - You innovate based on data",
                    "Creative Strategist - You think creatively with precision"
                ]
            },
            "SC": {
                "sv": [
                    "Kvalitetsingenjör - Du kombinerar pålitlighet med precision",
                    "Compliance Officer - Du säkerställer standarder metodiskt",
                    "Bibliotekar/Arkivarie - Du organiserar och bevarar"
                ],
                "en": [
                    "Quality Engineer - You combine reliability with precision",
                    "Compliance Officer - You ensure standards methodically",
                    "Librarian/Archivist - You organize and preserve"
                ]
            }
        }

        lang = "sv" if self.language == "sv" else "en"
        return careers.get(profile_code, careers.get(self.profile.primary_style, {})).get(lang, [])[:5]

    def get_team_dynamics(self) -> str:
        """Get team dynamics and collaboration advice"""
        if self.language == "sv":
            return f"""**Samarbete med andra DISC-stilar:**

- **Med D-typer**: Var direkt, fokusera på resultat, undvik långsam process
- **Med I-typer**: Var positiv och social, ge utrymme för idéer och relation
- **Med S-typer**: Var tålmodig, ge tid för anpassning, värdera stabilitet
- **Med C-typer**: Var förberedd med fakta, ge tid för analys, respektera processer

**Din roll i team**: {self._get_team_role()}

**Tips för effektivt samarbete**: Anpassa din kommunikationsstil efter teammedlemmars DISC-profiler för bästa resultat."""
        else:
            return f"""**Collaboration with other DISC styles:**

- **With D-types**: Be direct, focus on results, avoid slow process
- **With I-types**: Be positive and social, give room for ideas and relationship
- **With S-types**: Be patient, give time for adaptation, value stability
- **With C-types**: Be prepared with facts, give time for analysis, respect processes

**Your role in teams**: {self._get_team_role()}

**Tips for effective collaboration**: Adapt your communication style to team members' DISC profiles for best results."""

    def _get_team_role(self) -> str:
        """Get team role description"""
        roles = {
            "D": {
                "sv": "Du är den naturliga ledaren som driver teamet framåt och fattar snabba beslut",
                "en": "You are the natural leader who drives the team forward and makes quick decisions"
            },
            "I": {
                "sv": "Du är teamets energikälla och relationsskapare som skapar positiv atmosfär",
                "en": "You are the team's energy source and relationship builder who creates positive atmosphere"
            },
            "S": {
                "sv": "Du är teamets stabilisator och supporter som skapar harmoni och trygghet",
                "en": "You are the team's stabilizer and supporter who creates harmony and security"
            },
            "C": {
                "sv": "Du är teamets kvalitetssäkrare som säkerställer precision och noggrannhet",
                "en": "You are the team's quality assurer who ensures precision and accuracy"
            }
        }
        lang = "sv" if self.language == "sv" else "en"
        return roles.get(self.profile.primary_style, {}).get(lang, "")


# ============================================================================
# AI-POWERED PERSONALIZED INSIGHTS
# ============================================================================

def generate_personalized_disc_insights(
    profile: DISCProfile,
    language: str = "sv",
    anthropic_client: Optional[Anthropic] = None
) -> Optional[Dict]:
    """
    Generate AI-powered personalized insights using Claude

    Args:
        profile: DISCProfile object
        language: "sv" or "en"
        anthropic_client: Anthropic API client

    Returns:
        Dict with personalized insights or None if not available
    """
    if not anthropic_client:
        return None

    scores = profile.scores.to_dict()
    profile_code = profile.profile_code

    prompt = f"""Du är en expert DISC-coach med 20+ års erfarenhet. Skapa en DJUPT personlig DISC-rapport på {"svenska" if language == "sv" else "English"}.

**DISC-profil:**
- Dominance: {scores['dominance']:.1f}/100
- Influence: {scores['influence']:.1f}/100
- Steadiness: {scores['steadiness']:.1f}/100
- Conscientiousness: {scores['conscientiousness']:.1f}/100
- Profilkod: {profile_code}

**Uppgift:** Skapa exceptionellt djupa, personliga insikter som går LÅNGT BORTOM generiska DISC-beskrivningar.

**Format (JSON):**
```json
{{
  "unique_combination": "3-4 meningar om vad som är UNIKT med just denna DISC-kombination. Ge KONKRETA exempel på hur dragen samverkar i verkliga situationer.",

  "leadership_style": "4-5 meningar om exakt hur personen leder bäst. Inkludera: beslutsfattande-stil, hur de motiverar team, konflikthantering, delegering. GE ACTIONABLE TIPS.",

  "stress_response": "3-4 meningar om hur personen reagerar under stress baserat på DISC-profilen, vad som utlöser stress, och KONKRETA strategier för att hantera det.",

  "ideal_environment": "3-4 meningar om den perfekta arbetsmiljön för denna profil. Konkret: kontor eller hemma? Team eller solo? Struktur eller frihet? Tempo?",

  "blind_spots": ["2-3 utvecklingsområden med MYCKET KONKRETA, STEG-FÖR-STEG råd baserat på DISC-profilen"],

  "communication_tips": ["3-4 konkreta kommunikationstips för hur personen kan kommunicera mer effektivt med andra DISC-stilar"]
}}
```

**KRAV:**
1. DJUP analys av DISC-interaktioner
2. KONKRETA exempel och scenarios
3. ACTIONABLE råd
4. PERSONLIGT och VARMT
5. Fokus på UNIKA kombinationen av DISC-drag

Generera rapporten nu:"""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(response_text)
        return data

    except Exception as e:
        print(f"AI insights generation failed: {e}")
        return None


# ============================================================================
# MAIN REPORT GENERATION FUNCTION
# ============================================================================

def generate_disc_report(
    profile: DISCProfile,
    language: str = "sv",
    anthropic_client: Optional[Anthropic] = None,
    include_ai_insights: bool = True
) -> Dict:
    """
    Generate complete DISC report

    Args:
        profile: DISCProfile object
        language: "sv" or "en"
        anthropic_client: Anthropic API client (optional)
        include_ai_insights: Whether to generate AI insights

    Returns:
        Complete report dictionary
    """
    # Generate AI insights if available
    personalized_insights = None
    if include_ai_insights and anthropic_client:
        personalized_insights = generate_personalized_disc_insights(
            profile, language, anthropic_client
        )

    # Create report
    report = DISCReport(profile, language, personalized_insights)

    return report.to_dict()
