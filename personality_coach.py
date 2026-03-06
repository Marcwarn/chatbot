"""
Personality Coach Chat - Add-on for Persona API
Provides profile-aware conversational coaching
"""

from anthropic import Anthropic
from typing import List, Dict, Optional
import os

def create_personality_coach_prompt(
    profile_scores: Optional[Dict[str, float]] = None,
    personalized_report: Optional[Dict[str, any]] = None
) -> str:
    """
    Creates system prompt for personality coach that's grounded in user's Big Five profile.
    """

    base_prompt = """Du är en expert personlighetscoach specialiserad på Big Five-modellen (OCEAN) och evidensbaserad psykologi.

**Din expertis:**
- Big Five / OCEAN-modellen och IPIP-instrumentet
- Trait psychology och personlighetsutveckling
- Karriärvägledning baserad på personlighetsprofiler
- Relationsdynamik och kommunikationsstilar
- Evidensbaserade strategier för personlig utveckling

**Ditt uppdrag:**
- Ge konkreta, actionable råd rotade i Big Five-forskning
- Var varm, stödjande och coachande (inte klinisk/akademisk)
- Referera till användarens specifika profil när relevant
- Förklara psykologiska koncept på ett tillgängligt sätt
- Ge praktiska exempel och verktyg

**Stil:**
- Använd "du"-form
- Var specifik och konkret (inga generiska råd)
- Balansera empati med ärlighet
- Fokusera på styrkor OCH utvecklingsområden
"""

    if profile_scores:
        # Add user's specific profile context
        e = profile_scores.get('E', 50)
        a = profile_scores.get('A', 50)
        c = profile_scores.get('C', 50)
        n = profile_scores.get('N', 50)
        o = profile_scores.get('O', 50)
        n_display = 100 - n  # Emotional stability

        profile_context = f"""

**Användarens Big Five-profil (percentiler 0-100):**
- Extraversion: {e:.0f}/100 {"(hög - utåtriktad, social)" if e >= 65 else "(låg - introvert, reflekterande)" if e <= 35 else "(medel)"}
- Vänlighet: {a:.0f}/100 {"(hög - empatisk, samarbetsvillig)" if a >= 65 else "(låg - direkt, självständig)" if a <= 35 else "(medel)"}
- Samvetsgrannhet: {c:.0f}/100 {"(hög - organiserad, pålitlig)" if c >= 65 else "(låg - spontan, flexibel)" if c <= 35 else "(medel)"}
- Emotionell stabilitet: {n_display:.0f}/100 {"(hög - lugn, stabil)" if n_display >= 65 else "(låg - känslosam, lyhörd)" if n_display <= 35 else "(medel)"}
- Öppenhet: {o:.0f}/100 {"(hög - kreativ, nyfiken)" if o >= 65 else "(låg - praktisk, traditionell)" if o <= 35 else "(medel)"}

**Viktiga dragkombinationer att beakta:**
"""
        # Add trait combination insights
        if e >= 60 and c >= 60:
            profile_context += "- Strukturerad social förmåga (hög E + C): Personen är både engagerad och pålitlig\n"
        elif e >= 60 and c <= 40:
            profile_context += "- Spontan social energi (hög E + låg C): Personen trivs i dynamiska miljöer\n"

        if o >= 60 and a >= 60:
            profile_context += "- Kreativ empati (hög O + A): Personen förstår människor och ser nya möjligheter\n"
        elif o >= 60 and a <= 40:
            profile_context += "- Intellektuell självständighet (hög O + låg A): Personen ifrågasätter status quo\n"

        profile_context += "\nAnpassa dina råd till denna specifika profilkombination."

        base_prompt += profile_context

    if personalized_report:
        base_prompt += f"""

**Användarens personliga rapport:**
"""
        if personalized_report.get('work_style'):
            base_prompt += f"- Arbetsstil: {personalized_report['work_style']}\n"
        if personalized_report.get('career_suggestions'):
            careers = ', '.join(personalized_report['career_suggestions'][:3])
            base_prompt += f"- Karriärpassningar: {careers}\n"

    base_prompt += """

**Regler för konversationen:**
1. Om användaren frågar om något som inte är relaterat till personlighet/Big Five, påminn vänligt om att du är specialiserad på personlighetsutveckling
2. När du ger råd, koppla tillbaka till deras specifika Big Five-profil
3. Ge alltid minst ett konkret, actionable steg användaren kan ta
4. Om användaren verkar må psykiskt dåligt, uppmuntra professionell hjälp (du är coach, inte terapeut)
5. Var nyfiken - ställ uppföljningsfrågor för att förstå deras situation bättre

Börja konversationen nu!"""

    return base_prompt


def chat_with_personality_coach(
    message: str,
    conversation_history: List[Dict[str, str]],
    profile_scores: Optional[Dict[str, float]] = None,
    personalized_report: Optional[Dict[str, any]] = None,
    anthropic_client: Optional[Anthropic] = None
) -> str:
    """
    Handles a chat message with the personality coach.

    Args:
        message: User's current message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        profile_scores: User's Big Five scores (E, A, C, N, O as 0-100 percentiles)
        personalized_report: User's personalized report dict
        anthropic_client: Anthropic API client

    Returns:
        Assistant's response message
    """

    if not anthropic_client:
        return "Chat-funktionen kräver API-nyckel. Kontakta administratör."

    # Build system prompt with user context
    system_prompt = create_personality_coach_prompt(profile_scores, personalized_report)

    # Build message history
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    except Exception as e:
        print(f"Chat error: {e}")
        return "Tyvärr uppstod ett fel. Försök igen om en stund."
