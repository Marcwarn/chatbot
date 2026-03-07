"""
Report Explainer - Personal Report Q&A System
Answers questions about user's specific Big Five and DISC scores
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# TRAIT EXPLANATIONS
# ============================================================================

BIG_FIVE_EXPLANATIONS = {
    "E": {
        "name_sv": "Extraversion",
        "name_en": "Extraversion",
        "high_description_sv": """
Du är utåtriktad och får energi av sociala situationer. Du trivs i grupp,
tar gärna initiativ till kontakt och känner dig bekväm i centrum av uppmärksamheten.
        """,
        "low_description_sv": """
Du är introvert och får energi av tid för dig själv. Du föredrar djupare samtal
med färre personer och behöver återhämtningstid efter sociala aktiviteter.
        """,
        "medium_description_sv": """
Du är ambivert - balanserad mellan inåt- och utåtriktad. Du kan njuta både av
sociala situationer och ensam tid, beroende på sammanhang och humör.
        """,
        "career_high_sv": "Försäljning, kundservice, event, undervisning, ledning",
        "career_low_sv": "Forskning, skrivande, IT, design, analys",
        "growth_high_sv": "Lär dig lyssna mer, ge andra utrymme, balansera social tid",
        "growth_low_sv": "Öva på att ta initiativ, bygga nätverk, visa dig själv"
    },
    "A": {
        "name_sv": "Vänlighet (Agreeableness)",
        "name_en": "Agreeableness",
        "high_description_sv": """
Du är empatisk, omtänksam och samarbetsvillig. Du värdesätter harmoni,
förstår andras perspektiv och är ofta den som håller fred i gruppen.
        """,
        "low_description_sv": """
Du är direkt, självständig och objektiv. Du säger vad du tycker, ifrågasätter
status quo och prioriterar sanning framför harmoni.
        """,
        "medium_description_sv": """
Du balanserar empati med ärlighet. Du kan vara omtänksam när situationen kräver
det, men också stå på dig och vara direkt när det behövs.
        """,
        "career_high_sv": "Vård, socialt arbete, HR, terapi, kundrelationer",
        "career_low_sv": "Juridik, revision, vetenskaplig kritik, förhandling",
        "growth_high_sv": "Öva på att sätta gränser, säga nej, prioritera dig själv",
        "growth_low_sv": "Träna empati, lyssna aktivt, kompromissa ibland"
    },
    "C": {
        "name_sv": "Samvetsgrannhet (Conscientiousness)",
        "name_en": "Conscientiousness",
        "high_description_sv": """
Du är organiserad, pålitlig och målinriktad. Du planerar noggrant, håller deadlines
och har höga standarder för dig själv och ditt arbete.
        """,
        "low_description_sv": """
Du är spontan, flexibel och anpassningsbar. Du trivs med förändring, improviserar
gärna och låter inte detaljer hindra dig från att ta tag i nya saker.
        """,
        "medium_description_sv": """
Du balanserar planering med spontanitet. Du kan vara organiserad när det behövs,
men också flexibel och anpassningsbar i dynamiska situationer.
        """,
        "career_high_sv": "Projektledning, ekonomi, administration, kvalitetssäkring",
        "career_low_sv": "Kreativa yrken, startup, konsultverksamhet, Event",
        "growth_high_sv": "Öva på flexibilitet, släpp perfektionism, var spontan",
        "growth_low_sv": "Skapa rutiner, sätt mål, förbättra tidsplanering"
    },
    "N": {
        "name_sv": "Neuroticism (emotionell känslighet)",
        "name_en": "Neuroticism",
        "high_description_sv": """
Du är känslosam och lyhörd för omgivningen. Du känner djupt, reflekterar mycket
och är medveten om risker och problem - vilket kan vara både styrka och utmaning.
        """,
        "low_description_sv": """
Du är emotionellt stabil och lugn under press. Du låter dig inte störas av stress,
återhämtar dig snabbt från motgångar och behåller perspektiv i svåra situationer.
        """,
        "medium_description_sv": """
Du har balanserad emotionell känslighet. Du kan känna stress och oro, men har
verktyg för att hantera det och återfå balans relativt snabbt.
        """,
        "career_high_sv": "Kreativa yrken, konstnärligt arbete, skrivande (men tänk på stresshantering)",
        "career_low_sv": "Krishantering, akutvård, militär, polisarbete, ledning",
        "growth_high_sv": "Mindfulness, stresshantering, kognitiv omstrukturering, motion",
        "growth_low_sv": "Träna emotionell medvetenhet, empati för andras stress"
    },
    "O": {
        "name_sv": "Öppenhet (Openness)",
        "name_en": "Openness",
        "high_description_sv": """
Du är kreativ, nyfiken och öppen för nya idéer. Du njuter av intellektuella
utmaningar, abstrakt tänkande och att utforska olika perspektiv och möjligheter.
        """,
        "low_description_sv": """
Du är praktisk, jordnära och värderar beprövade metoder. Du föredrar konkreta
svar, struktur och stabilitet framför abstraktion och förändring.
        """,
        "medium_description_sv": """
Du balanserar nyfikenhet med pragmatism. Du kan uppskatta nya idéer när de är
relevanta, men föredrar praktiska tillämpningar framför abstrakt filosoferande.
        """,
        "career_high_sv": "Forskning, design, konst, innovation, strategi, rådgivning",
        "career_low_sv": "Administration, produktion, kvalitetskontroll, implementering",
        "growth_high_sv": "Fokusera på genomförande, färdigställ projekt, var praktisk",
        "growth_low_sv": "Utforska nya idéer, läs brett, utmana dina antaganden"
    }
}

DISC_EXPLANATIONS = {
    "D": {
        "name_sv": "Dominance (Dominans)",
        "high_description_sv": """
Du är resultatorienterad, beslutsam och direkt. Du tar gärna ledningen,
fattar snabba beslut och fokuserar på att uppnå mål effektivt.
        """,
        "low_description_sv": """
Du är samarbetsinriktad och föredrar att arbeta med andra. Du tar dig tid
att överväga beslut och undviker att dominera situationer.
        """,
        "strengths_high_sv": "Ledarskap, problemlösning, drivenhet, mod",
        "challenges_high_sv": "Kan verka otålig, dominant, okänslig för andras känslor",
        "tips_high_sv": "Lyssna mer, var tålmodig, involvera andra i beslut"
    },
    "I": {
        "name_sv": "Influence (Inflytande)",
        "high_description_sv": """
Du är utåtriktad, entusiastisk och övertygande. Du trivs i sociala sammanhang,
inspirerar andra och skapar positiv energi runt dig.
        """,
        "low_description_sv": """
Du är mer reserverad och faktaorienterad. Du föredrar sakliga argument
framför entusiasm och arbetar metodiskt snarare än spontant.
        """,
        "strengths_high_sv": "Kommunikation, motivation, teamwork, kreativitet",
        "challenges_high_sv": "Kan sakna fokus på detaljer, vara för optimistisk",
        "tips_high_sv": "Följ upp detaljer, var realistisk, lyssna aktivt"
    },
    "S": {
        "name_sv": "Steadiness (Stabilitet)",
        "high_description_sv": """
Du är stabil, pålitlig och tålmodig. Du värdesätter harmoni och stabilitet,
arbetar metodiskt och är lojal mot team och organisation.
        """,
        "low_description_sv": """
Du trivs med förändring och variation. Du är dynamisk, flexibel och
blir lätt uttråkad av monotona rutiner.
        """,
        "strengths_high_sv": "Pålitlighet, tålamod, lagarbete, empati",
        "challenges_high_sv": "Kan vara motståndskraftig mot förändring, undvika konflikter",
        "tips_high_sv": "Acceptera förändring, var mer öppen för nya metoder"
    },
    "C": {
        "name_sv": "Conscientiousness (Noggrannhet)",
        "high_description_sv": """
Du är analytisk, detaljorienterad och kvalitetsmedveten. Du följer regler,
uppskattar struktur och strävar efter perfektion i ditt arbete.
        """,
        "low_description_sv": """
Du är mer intuitiv och pragmatisk. Du fokuserar på helhet snarare än
detaljer och är bekväm med ungefärliga lösningar.
        """,
        "strengths_high_sv": "Precision, kvalitet, analys, systematik",
        "challenges_high_sv": "Kan vara perfektionistisk, långsam, kritisk",
        "tips_high_sv": "Balansera perfektion med pragmatism, delegera mer"
    }
}


# ============================================================================
# TRAIT COMPARISON INSIGHTS
# ============================================================================

def get_trait_interaction(trait1: str, score1: float, trait2: str, score2: float, language: str = "sv") -> str:
    """
    Get insights about how two traits interact

    Args:
        trait1: First trait (E, A, C, N, O)
        score1: Score for first trait
        trait2: Second trait
        score2: Score for second trait
        language: Language code

    Returns:
        Interaction description
    """
    # Determine levels
    level1 = "high" if score1 >= 65 else "low" if score1 <= 35 else "medium"
    level2 = "high" if score2 >= 65 else "low" if score2 <= 35 else "medium"

    if language == "sv":
        interactions = {
            ("E", "high", "C", "high"): "Strukturerad social förmåga - du är både engagerande och pålitlig, vilket gör dig till en effektiv teamledare.",
            ("E", "high", "C", "low"): "Spontan social energi - du trivs i dynamiska miljöer och improviserar gärna i sociala sammanhang.",
            ("E", "low", "C", "high"): "Lugn precision - du arbetar metodiskt och fokuserat, och trivs med djupgående uppgifter.",
            ("E", "low", "O", "high"): "Reflekterande kreativitet - du utforskar idéer djupt och självständigt.",

            ("O", "high", "A", "high"): "Kreativ empati - du förstår människor och ser nya möjligheter i relationsdynamik.",
            ("O", "high", "A", "low"): "Intellektuell självständighet - du ifrågasätter status quo och tänker kritiskt.",
            ("O", "high", "C", "low"): "Visionär spontanitet - du genererar många idéer men kan ha svårt att genomföra.",
            ("O", "high", "C", "high"): "Strukturerad innovation - du kan både komma på kreativa lösningar och implementera dem.",

            ("A", "high", "N", "high"): "Empatisk känslighet - du är mycket lyhörd för andra men kan påverkas starkt av konflikter.",
            ("A", "low", "N", "low"): "Objektiv stabilitet - du fattar rationella beslut utan att påverkas av känslor.",
            ("C", "high", "N", "low"): "Pålitlig lugn - du levererar konsekvent hög kvalitet även under press.",
            ("C", "low", "N", "high"): "Kreativ oro - du kan känna stress över ostruktur men också vara flexibel.",
        }

        key = (trait1, level1, trait2, level2)
        reverse_key = (trait2, level2, trait1, level1)

        return interactions.get(key) or interactions.get(reverse_key) or ""

    return ""


# ============================================================================
# PERCENTILE EXPLANATIONS
# ============================================================================

def explain_percentile(score: float, language: str = "sv") -> str:
    """
    Explain what a percentile score means in layman's terms

    Args:
        score: Percentile score 0-100
        language: Language code

    Returns:
        Explanation string
    """
    if language == "sv":
        if score >= 90:
            return f"Mycket hög (topp 10%) - du scorar högre än {int(score)}% av befolkningen"
        elif score >= 75:
            return f"Hög ({int(score)}:e percentilen) - högre än {int(score)}% av människor"
        elif score >= 60:
            return f"Över medel ({int(score)}:e percentilen) - något högre än genomsnittet"
        elif score >= 40:
            return f"Medel ({int(score)}:e percentilen) - runt genomsnittet"
        elif score >= 25:
            return f"Under medel ({int(score)}:e percentilen) - något lägre än genomsnittet"
        elif score >= 10:
            return f"Låg ({int(score)}:e percentilen) - lägre än {100-int(score)}% av människor"
        else:
            return f"Mycket låg (botten 10%) - lägre än {100-int(score)}% av befolkningen"
    else:
        return f"{int(score)}th percentile"


# ============================================================================
# REPORT EXPLAINER CLASS
# ============================================================================

class ReportExplainer:
    """
    Explains user's personality assessment results
    """

    def __init__(self, language: str = "sv"):
        self.language = language

    def explain_single_trait(
        self,
        trait: str,
        score: float,
        assessment_type: str = "big_five"
    ) -> Dict[str, str]:
        """
        Explain a single trait score

        Args:
            trait: Trait code (E, A, C, N, O for Big Five; D, I, S, C for DISC)
            score: Score 0-100
            assessment_type: "big_five" or "disc"

        Returns:
            Dict with explanation components
        """
        level = "high" if score >= 65 else "low" if score <= 35 else "medium"

        if assessment_type == "big_five":
            explanations = BIG_FIVE_EXPLANATIONS.get(trait, {})
        else:
            explanations = DISC_EXPLANATIONS.get(trait, {})

        name = explanations.get(f"name_{self.language}", trait)
        description = explanations.get(f"{level}_description_{self.language}", "").strip()
        percentile_explanation = explain_percentile(score, self.language)

        result = {
            "trait": trait,
            "trait_name": name,
            "score": score,
            "level": level,
            "percentile_explanation": percentile_explanation,
            "description": description
        }

        # Add career suggestions if available
        if assessment_type == "big_five":
            career_key = f"career_{level}_{self.language}"
            if career_key in explanations:
                result["career_suggestions"] = explanations[career_key]

            growth_key = f"growth_{level}_{self.language}"
            if growth_key in explanations:
                result["growth_tips"] = explanations[growth_key]
        else:
            # DISC
            if level == "high":
                result["strengths"] = explanations.get(f"strengths_{level}_{self.language}", "")
                result["challenges"] = explanations.get(f"challenges_{level}_{self.language}", "")
                result["tips"] = explanations.get(f"tips_{level}_{self.language}", "")

        return result

    def compare_traits(
        self,
        trait1: str,
        score1: float,
        trait2: str,
        score2: float
    ) -> str:
        """
        Compare and explain the interaction between two traits

        Args:
            trait1: First trait code
            score1: First trait score
            trait2: Second trait code
            score2: Second trait score

        Returns:
            Comparison explanation
        """
        interaction = get_trait_interaction(trait1, score1, trait2, score2, self.language)

        if interaction:
            return interaction

        # Generic comparison
        level1 = "hög" if score1 >= 65 else "låg" if score1 <= 35 else "medel"
        level2 = "hög" if score2 >= 65 else "låg" if score2 <= 35 else "medel"

        name1 = BIG_FIVE_EXPLANATIONS.get(trait1, {}).get(f"name_{self.language}", trait1)
        name2 = BIG_FIVE_EXPLANATIONS.get(trait2, {}).get(f"name_{self.language}", trait2)

        return f"Du har {level1} {name1} och {level2} {name2}. Denna kombination ger dig en unik personlighetsprofil."

    def explain_full_profile(
        self,
        scores: Dict[str, float],
        assessment_type: str = "big_five"
    ) -> Dict[str, any]:
        """
        Explain complete personality profile

        Args:
            scores: Dict mapping trait codes to scores
            assessment_type: "big_five" or "disc"

        Returns:
            Complete profile explanation
        """
        explanations = {}
        high_traits = []
        low_traits = []

        for trait, score in scores.items():
            explanation = self.explain_single_trait(trait, score, assessment_type)
            explanations[trait] = explanation

            if score >= 65:
                high_traits.append(explanation["trait_name"])
            elif score <= 35:
                low_traits.append(explanation["trait_name"])

        # Generate summary
        summary_parts = []
        if high_traits:
            summary_parts.append(f"Dina starkaste drag är {', '.join(high_traits)}")
        if low_traits:
            summary_parts.append(f"Du är lägre i {', '.join(low_traits)}")

        summary = ". ".join(summary_parts) if summary_parts else "Din profil visar en balanserad personlighet."

        return {
            "summary": summary,
            "trait_explanations": explanations,
            "high_traits": high_traits,
            "low_traits": low_traits
        }

    def answer_why_score(
        self,
        trait: str,
        score: float,
        assessment_type: str = "big_five"
    ) -> str:
        """
        Answer "Why did I get this score?" question

        Args:
            trait: Trait code
            score: Score received
            assessment_type: Assessment type

        Returns:
            Empathetic explanation
        """
        level = "hög" if score >= 65 else "låg" if score <= 35 else "medel"
        explanation = self.explain_single_trait(trait, score, assessment_type)

        if self.language == "sv":
            response = f"""
Din {level}a score i {explanation['trait_name']} ({int(score)}:e percentilen) reflekterar hur du svarade på frågorna om detta drag.

{explanation['description']}

Kom ihåg: Det finns inget "bra" eller "dåligt" score. Varje personlighetsprofil har sina styrkor.
            """.strip()

            # Add normalization
            if level == "låg":
                response += f"\n\nAtt vara {level} i {explanation['trait_name']} är helt normalt - {100-int(score)}% av befolkningen scorar lägre än dig!"
            elif level == "hög":
                response += f"\n\nAtt vara {level} i {explanation['trait_name']} är helt normalt - du scorar högre än {int(score)}% av befolkningen!"

            return response

        return f"Your score in {explanation['trait_name']} is {int(score)}th percentile."


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_personalized_examples(
    trait: str,
    score: float,
    context: str = "work",
    language: str = "sv"
) -> List[str]:
    """
    Generate personalized examples based on trait and score

    Args:
        trait: Trait code
        score: Score value
        context: Context (work, relationships, etc.)
        language: Language code

    Returns:
        List of concrete examples
    """
    level = "high" if score >= 65 else "low" if score <= 35 else "medium"

    if language != "sv":
        return []

    examples = {
        ("E", "high", "work"): [
            "Du får energi av gruppmöten och brainstorming-sessioner",
            "Du trivs i öppna kontorslandskap och söker ofta social interaktion",
            "Du är ofta den som tar initiativ till after work och teamaktiviteter"
        ],
        ("E", "low", "work"): [
            "Du föredrar eget kontor eller hörlurar i öppet landskap",
            "Du laddar batterier genom lunch ensam ibland",
            "Du trivs med djupfokusarbete utan många möten"
        ],
        ("C", "high", "work"): [
            "Du har alltid koll på deadlines och levererar i tid",
            "Ditt skrivbord och digital filstruktur är välorganiserad",
            "Du gillar att planera veckan på söndagskvällen"
        ],
        ("C", "low", "work"): [
            "Du trivs med last-minute-projekt och deadlines",
            "Du improviserar lösningar och är flexibel när planer ändras",
            "Du blir lätt uttråkad av detaljerad planering"
        ],
        ("O", "high", "work"): [
            "Du älskar att lära dig nya verktyg och metoder",
            "Du kommer ofta med kreativa lösningar på problem",
            "Du njuter av strategiska diskussioner och möjlighetsanalys"
        ],
        ("O", "low", "work"): [
            "Du föredrar beprövade metoder som fungerar",
            "Du uppskattar tydliga instruktioner och konkreta mål",
            "Du är praktisk och 'hands-on' i ditt arbete"
        ]
    }

    key = (trait, level, context)
    return examples.get(key, [])


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("REPORT EXPLAINER TEST")
    print("=" * 80)

    explainer = ReportExplainer(language="sv")

    # Test single trait explanation
    print("\n1. SINGLE TRAIT EXPLANATION (Low Conscientiousness):")
    print("-" * 80)
    result = explainer.explain_single_trait("C", 30, "big_five")
    print(f"Trait: {result['trait_name']}")
    print(f"Score: {result['score']} ({result['level']})")
    print(f"Percentile: {result['percentile_explanation']}")
    print(f"Description: {result['description']}")
    if 'career_suggestions' in result:
        print(f"Career fit: {result['career_suggestions']}")

    # Test full profile
    print("\n2. FULL PROFILE EXPLANATION:")
    print("-" * 80)
    test_scores = {"E": 75, "A": 45, "C": 30, "N": 60, "O": 85}
    profile = explainer.explain_full_profile(test_scores)
    print(f"Summary: {profile['summary']}")
    print(f"High traits: {', '.join(profile['high_traits'])}")
    print(f"Low traits: {', '.join(profile['low_traits'])}")

    # Test "why" question
    print("\n3. 'WHY DID I GET THIS SCORE?' ANSWER:")
    print("-" * 80)
    why_answer = explainer.answer_why_score("C", 30)
    print(why_answer)

    # Test trait comparison
    print("\n4. TRAIT COMPARISON:")
    print("-" * 80)
    comparison = explainer.compare_traits("E", 75, "C", 30)
    print(comparison)

    # Test personalized examples
    print("\n5. PERSONALIZED EXAMPLES:")
    print("-" * 80)
    examples = generate_personalized_examples("C", 30, "work", "sv")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex}")

    print("\n" + "=" * 80)
    print("✅ Report Explainer test completed!")
