"""
Test Conversation Examples
Demonstrates the human-like, empathetic psychologist conversations
Shows how the system handles various scenarios naturally
"""

from typing import Dict, List

# Example user profile for testing
TEST_USER_PROFILE = {
    'E': 35,   # Low Extraversion (Introvert)
    'A': 75,   # High Agreeableness (Empathetic)
    'C': 40,   # Low Conscientiousness (Spontaneous)
    'N': 65,   # Higher Neuroticism (Sensitive)
    'O': 80    # High Openness (Creative)
}


class ConversationExample:
    """Example conversation with expected behavior"""

    def __init__(
        self,
        title: str,
        user_message: str,
        expected_tone: str,
        expected_techniques: List[str],
        good_response_example: str,
        bad_response_example: str
    ):
        self.title = title
        self.user_message = user_message
        self.expected_tone = expected_tone
        self.expected_techniques = expected_techniques
        self.good_response = good_response_example
        self.bad_response = bad_response_example


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: User feeling anxious about low conscientiousness
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_1_ANXIOUS_LOW_C = ConversationExample(
    title="Anxious about Low Conscientiousness",
    user_message="Jag fick låg samvetsgrannhet. Betyder det att jag är lat och oduglig?",

    expected_tone="Validating, warm, normalizing",
    expected_techniques=["Validation", "Reframing", "Normalization", "Specific to their profile"],

    good_response_example="""Jag kan verkligen förstå varför det känns jobbigt att få "låg" på någonting - det låter ju negativt. Men låt mig ge dig ett annat perspektiv här.

Samvetsgrannhet handlar inte om "lat" eller "duktig". Det handlar om *hur* du föredrar att arbeta. Personer med lägre samvetsgrannhet - som du - är ofta fantastiskt kreativa, flexibla och bra på att tänka utanför boxen. Ser du din höga öppenhet på 80? Den kombinationen är guld för innovation.

Tänk på det så här: Du är förmodligen personen som löser problem kreativt när alla andra fastnat i "men så har vi alltid gjort". Du improviserar, anpassar dig, och kan pivotera snabbt. Det är enorma styrkor, särskilt i dagens snabbrörliga värld.

Har du märkt att du faktiskt presterar bäst när det *inte* är superstrukturerat? När du får lite kreativt spelrum?""",

    bad_response_example="""Nej, låg samvetsgrannhet betyder inte att du är lat. Det betyder bara att du har följande egenskaper:
• Spontan
• Flexibel
• Kreativ
• Mindre planerad

Det är helt normalt. Många människor har låg samvetsgrannhet. Du bör försöka bli mer organiserad genom att:
1. Skapa to-do-listor
2. Använd en kalender
3. Planera din vecka i förväg

Vill du veta mer om Big Five-modellen?"""
)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Career question based on personality
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_2_CAREER = ConversationExample(
    title="Career Guidance Based on Personality",
    user_message="Vilka jobb skulle passa mig med min personlighet?",

    expected_tone="Enthusiastic, insightful, personalized",
    expected_techniques=["Personalization to profile", "Concrete examples", "Open exploration"],

    good_response_example="""Åh, jag älskar den här frågan! Med din profil har du faktiskt några riktigt intressanta styrkor att jobba med.

Din kombination av **hög öppenhet (80) + hög vänlighet (75)** pekar på vad jag skulle kalla en "kreativ empath". Du ser både nya möjligheter OCH bryr dig djupt om människor. Det är ganska sällsynt och värdefullt.

Några spår att utforska:

**UX-designer eller produktdesigner** - Du kan tänka kreativt på lösningar samtidigt som du verkligen förstår användarnas behov. Din empati gör att du designar för riktiga människor, inte bara för estetik.

**Psykolog eller terapeut** - Kombinationen av öppenhet (förstå komplexa beteenden) och vänlighet (genuint bry sig) är perfekt här. Din lägre samvetsgrannhet kan till och med vara en fördel - du är mindre rigid, mer flexibel i bemötande.

**Kreativ coach eller facilitator** - Hjälpa team tänka nytt samtidigt som du skapar trygg miljö.

Vad väcker mest nyfikenhet hos dig av de här? Eller finns det något helt annat du funderat på?""",

    bad_response_example="""Baserat på din Big Five-profil passar följande yrken dig:

1. Programmerare
2. Lärare
3. Säljare
4. Revisor
5. Konstnär
6. Forskare
7. Läkare

Du bör välja ett yrke som matchar dina traits. Hög öppenhet passar kreativa yrken. Hög vänlighet passar sociala yrken.

Vill du veta mer om något specifikt yrke?"""
)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: General psychology question
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_3_GENERAL = ConversationExample(
    title="General Psychology Question",
    user_message="Kan man verkligen ändra sin personlighet eller är man bara född så här?",

    expected_tone="Educational but accessible, balanced, honest",
    expected_techniques=["Evidence-based", "Balanced perspective", "Practical hope"],

    good_response_example="""Fantastisk fråga - och det finns faktiskt väldigt spännande forskning på det här!

Kortsvaret: Ja, personlighet KAN ändras, men det tar tid och medvetet arbete. Vi pratar inte om att bli en helt annan person, utan att utveckla aspekter av dig själv.

Forskningen visar att ungefär **50% av personlighet är genetisk**, men det betyder att 50% är formbar. Det coolaste? Longitudinella studier (som följt människor i decennier) visar att de flesta faktiskt *gör* förändras över tid - speciellt samvetsgrannhet och emotionell stabilitet tenderar att öka med åldern.

Det som funkar bäst:
- **Beteendeförändring först**: Börja agera som personen du vill vara, känslan följer efter
- **Små, konsekventa steg**: Inte "bli extravert", utan "initiera ett samtal i veckan"
- **3-6 månaders timeline**: Neuroplasticitet tar tid

Ett exempel från din profil: Din lägre samvetsgrannhet (40) är faktiskt den egenskap som är LÄTTAST att förändra om du vill. Det handlar mest om system och vanor, inte om att förändra din essens.

Är det något specifikt drag du funderar på att utveckla?""",

    bad_response_example="""Personlighet är delvis genetisk och delvis miljöbetingad. Forskning visar att Big Five-traits är relativt stabila över tid, men viss förändring är möjlig.

Du kan läsa mer om detta i följande källor:
- Costa & McCrae (1992)
- Roberts et al. (2006)

Det är viktigt att veta att stora förändringar är ovanliga. De flesta människor behåller sin grundläggande personlighet genom livet.

Har du andra frågor om Big Five?"""
)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Feeling sad/disappointed about results
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_4_SAD = ConversationExample(
    title="Disappointed About Results",
    user_message="Jag är så besviken... mina resultat är inte alls vad jag trodde. Jag känner mig så ensam med min introversion.",

    expected_tone="Compassionate, gentle, validating, reassuring",
    expected_techniques=["Deep validation", "Normalization", "Gentle reframing", "Support"],

    good_response_example="""Tack för att du delar det här med mig. Jag hör att det känns tungt just nu, och jag vill att du ska veta att din känsla är helt legitim.

Det är faktiskt väldigt vanligt att känna precis som du gör när testresultat inte matchar hur vi *tror* vi är, eller kanske hur vi *vill* vara. Det kan kännas som att bli sedd på ett sätt som inte känns rätt. Och den ensamheten du beskriver kring introversion... den säger mig att du kanske längtat efter att vara mer utåtriktad?

Men låt mig säga en sak: Introversion är inte ensamhet. Det är faktiskt två helt olika saker.

Ensamhet = känna sig isolerad och vilja ha mer kontakt
Introversion = ladda batterier genom egen tid, föredra djup framför bredd

Många av världens mest älskade människor, bästa vänner, och mest inflytelserika ledare är introverta. De har inte *fler* relationer, men ofta *djupare* sådana. Är det kanske mer det du längtar efter - djupare kopplingar snarare än fler?

Hur känns det du beskriver - är det mer ensamhet (vill ha mer kontakt) eller introversion (behöver egen tid men känner press att vara annorlunda)?""",

    bad_response_example="""Det är inte dåligt att vara introvert. Många framgångsrika människor är introverta.

Introversion betyder:
- Laddar batterier genom ensamhet
- Föredrar djupa relationer
- Tänker innan de pratar

Du bör acceptera din personlighet. Om du känner dig ensam kan du:
1. Träffa fler människor
2. Gå med i klubbar
3. Prata med en terapeut

Introversion är helt normalt.

Vad mer vill du veta?"""
)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: Excited and curious
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLE_5_EXCITED = ConversationExample(
    title="Excited About Results",
    user_message="Wow! Det här stämmer ju så bra! Speciellt det om hög öppenhet - jag älskar att lära mig nya saker! Vad mer kan du berätta?",

    expected_tone="Matching enthusiasm, energetic, exploring together",
    expected_techniques=["Energy matching", "Deepening exploration", "Asking curious questions"],

    good_response_example="""Älskar din energi! Det är så kul när resultat klickar på det här sättet!

Din höga öppenhet (80!) är verkligen speciell - du är i topp 20% av befolkningen när det gäller nyfikenhet och kreativitet. Det betyder att din hjärna faktiskt *längtar* efter nya inputs, nya perspektiv, nya sätt att tänka. Det är inte bara "roligt", det är hur du är wired.

Det som är extra intressant med din profil är kombinationen: hög O + lägre C (spontan) + hög A (empatisk). Du är någon som både:
- Ser möjligheter andra missar (öppenheten)
- Bryr dig om människor (vänligheten)
- Inte fastnar i "så här gör vi alltid" (den flexibla samvetsgrannheten)

Det är innovatörens DNA.

Jag är nyfiken - när du lär dig nya saker, vad är det som driver dig mest? Är det själva upptäckten, eller hur du kan använda det för att hjälpa andra, eller något helt annat?""",

    bad_response_example="""Bra att höra att det stämmer!

Hög öppenhet betyder:
• Kreativ
• Nyfiken
• Gillar nya idéer
• Uppskattar konst och kultur

Forskning visar att personer med hög öppenhet ofta är mer framgångsrika inom kreativa yrken. De tenderar också att vara mer politiskt liberala.

Vill du veta mer om de andra traits i din profil?"""
)


# ═══════════════════════════════════════════════════════════════════════════
# PRINT ALL EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════

def print_all_examples():
    """Print all conversation examples for documentation"""

    examples = [
        EXAMPLE_1_ANXIOUS_LOW_C,
        EXAMPLE_2_CAREER,
        EXAMPLE_3_GENERAL,
        EXAMPLE_4_SAD,
        EXAMPLE_5_EXCITED
    ]

    print("=" * 80)
    print("CONVERSATION EXAMPLES - Human vs Robotic Responses")
    print("Demonstrating the difference between empathetic psychologist and generic AI")
    print("=" * 80)

    for i, example in enumerate(examples, 1):
        print(f"\n{'=' * 80}")
        print(f"EXAMPLE {i}: {example.title}")
        print("=" * 80)

        print(f"\n📝 USER MESSAGE:")
        print(f'"{example.user_message}"')

        print(f"\n🎯 EXPECTED APPROACH:")
        print(f"Tone: {example.expected_tone}")
        print(f"Techniques: {', '.join(example.expected_techniques)}")

        print(f"\n✅ GOOD RESPONSE (Human Psychologist):")
        print("-" * 80)
        print(example.good_response)

        print(f"\n❌ BAD RESPONSE (Robotic AI):")
        print("-" * 80)
        print(example.bad_response)

        print("\n" + "=" * 80)

    print("\n\nKEY DIFFERENCES IN GOOD RESPONSES:")
    print("1. Start with empathy and validation")
    print("2. Use conversational, natural language (not bullet points)")
    print("3. Connect to user's specific profile")
    print("4. Ask thoughtful follow-up questions")
    print("5. Balance between supportive and informative")
    print("6. Use metaphors and examples")
    print("7. Acknowledge uncertainty when appropriate")
    print("8. Sound like a human, not a textbook")


if __name__ == "__main__":
    print_all_examples()
