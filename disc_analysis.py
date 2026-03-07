"""
DISC Analysis Engine - Scoring and profile identification
Analyzes DISC assessment responses and calculates personality scores
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import statistics


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class DISCScores:
    """DISC dimension scores"""
    dominance: float  # 0-100
    influence: float  # 0-100
    steadiness: float  # 0-100
    conscientiousness: float  # 0-100

    def to_dict(self) -> Dict[str, float]:
        return {
            "dominance": round(self.dominance, 1),
            "influence": round(self.influence, 1),
            "steadiness": round(self.steadiness, 1),
            "conscientiousness": round(self.conscientiousness, 1)
        }


@dataclass
class DISCProfile:
    """Complete DISC profile analysis"""
    scores: DISCScores
    primary_style: str  # "D", "I", "S", or "C"
    secondary_style: Optional[str]  # Optional second dominant trait
    profile_code: str  # "D", "DI", "SC", etc.
    profile_level: Dict[str, str]  # "high", "medium", "low" for each dimension

    def to_dict(self) -> Dict:
        return {
            "scores": self.scores.to_dict(),
            "primary_style": self.primary_style,
            "secondary_style": self.secondary_style,
            "profile_code": self.profile_code,
            "profile_level": self.profile_level
        }


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_dimension(
    questions: List[Dict],
    answers: Dict[int, int],
    dimension: str
) -> float:
    """
    Calculate score for a single DISC dimension (0-100 scale)

    Args:
        questions: List of question dicts with 'id', 'dimension', 'keyed'
        answers: Dict mapping question_id to answer value (1-5)
        dimension: "D", "I", "S", or "C"

    Returns:
        Score from 0-100
    """
    dimension_questions = [q for q in questions if q.get("dimension") == dimension]

    if not dimension_questions:
        return 50.0  # Default to middle if no questions

    scores = []
    for q in dimension_questions:
        q_id = q.get("id")
        raw_value = answers.get(q_id, 3)  # Default to neutral if missing

        # Apply reverse keying if needed
        if q.get("keyed") == "-":
            value = 6 - raw_value  # Reverse 1-5 scale
        else:
            value = raw_value

        scores.append(value)

    # Calculate mean (1-5) and convert to 0-100 scale
    mean_score = statistics.mean(scores)
    percentile_score = ((mean_score - 1) / 4) * 100

    return round(percentile_score, 1)


def calculate_disc_scores(
    questions: List[Dict],
    answers: Dict[int, int]
) -> DISCScores:
    """
    Calculate all DISC dimension scores

    Args:
        questions: List of all DISC questions
        answers: User's answers (question_id -> value)

    Returns:
        DISCScores object with all four dimensions
    """
    return DISCScores(
        dominance=score_dimension(questions, answers, "D"),
        influence=score_dimension(questions, answers, "I"),
        steadiness=score_dimension(questions, answers, "S"),
        conscientiousness=score_dimension(questions, answers, "C")
    )


def get_score_level(score: float) -> str:
    """Categorize score as high/medium/low"""
    if score >= 70:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"


def identify_disc_profile(scores: DISCScores) -> DISCProfile:
    """
    Identify DISC profile from scores

    Determines primary/secondary styles and creates profile code
    (e.g., "D", "DI", "SC")

    Args:
        scores: DISCScores object

    Returns:
        Complete DISCProfile with interpretation
    """
    # Get scores as dict for easier processing
    score_dict = {
        "D": scores.dominance,
        "I": scores.influence,
        "S": scores.steadiness,
        "C": scores.conscientiousness
    }

    # Sort by score (descending)
    sorted_styles = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    # Primary style is highest score
    primary_style = sorted_styles[0][0]
    primary_score = sorted_styles[0][1]

    # Secondary style if score >= 60 and within 20 points of primary
    secondary_style = None
    if len(sorted_styles) > 1:
        second_score = sorted_styles[1][1]
        if second_score >= 60 and (primary_score - second_score) <= 20:
            secondary_style = sorted_styles[1][0]

    # Build profile code
    if secondary_style:
        profile_code = primary_style + secondary_style
    else:
        profile_code = primary_style

    # Determine level for each dimension
    profile_level = {
        "D": get_score_level(scores.dominance),
        "I": get_score_level(scores.influence),
        "S": get_score_level(scores.steadiness),
        "C": get_score_level(scores.conscientiousness)
    }

    return DISCProfile(
        scores=scores,
        primary_style=primary_style,
        secondary_style=secondary_style,
        profile_code=profile_code,
        profile_level=profile_level
    )


# ============================================================================
# INTERPRETATION FUNCTIONS
# ============================================================================

def get_dimension_interpretation(dimension: str, score: float, language: str = "sv") -> Dict[str, str]:
    """
    Get interpretation for a single DISC dimension

    Args:
        dimension: "D", "I", "S", or "C"
        score: Score 0-100
        language: "sv" or "en"

    Returns:
        Dict with 'level', 'label', 'description'
    """
    level = get_score_level(score)

    interpretations = {
        "D": {
            "high": {
                "label_sv": "Hög Dominans",
                "label_en": "High Dominance",
                "desc_sv": "Du är direkt, beslutsam och resultatorienterad. Du tar gärna ledningen och driver projekt framåt med kraft.",
                "desc_en": "You are direct, decisive, and results-oriented. You readily take charge and drive projects forward with force."
            },
            "medium": {
                "label_sv": "Medel Dominans",
                "label_en": "Medium Dominance",
                "desc_sv": "Du balanserar mellan att leda och följa, och anpassar dig efter situationen.",
                "desc_en": "You balance between leading and following, adapting to the situation."
            },
            "low": {
                "label_sv": "Låg Dominans",
                "label_en": "Low Dominance",
                "desc_sv": "Du föredrar att samarbeta framför att konkurrera och undviker konfrontation.",
                "desc_en": "You prefer cooperation over competition and avoid confrontation."
            }
        },
        "I": {
            "high": {
                "label_sv": "Hög Inflytande",
                "label_en": "High Influence",
                "desc_sv": "Du är utåtriktad, entusiastisk och bygger relationer naturligt. Du inspirerar och påverkar andra med din energi.",
                "desc_en": "You are outgoing, enthusiastic, and build relationships naturally. You inspire and influence others with your energy."
            },
            "medium": {
                "label_sv": "Medel Inflytande",
                "label_en": "Medium Influence",
                "desc_sv": "Du är bekväm i sociala sammanhang men uppskattar också ensamtid.",
                "desc_en": "You are comfortable in social settings but also appreciate alone time."
            },
            "low": {
                "label_sv": "Låg Inflytande",
                "label_en": "Low Influence",
                "desc_sv": "Du är mer reserverad och föredrar fakta framför känslor i kommunikation.",
                "desc_en": "You are more reserved and prefer facts over emotions in communication."
            }
        },
        "S": {
            "high": {
                "label_sv": "Hög Stabilitet",
                "label_en": "High Steadiness",
                "desc_sv": "Du är tålmodig, lojal och harmonisökande. Du skapar trygghet och stabilitet i team.",
                "desc_en": "You are patient, loyal, and harmony-seeking. You create security and stability in teams."
            },
            "medium": {
                "label_sv": "Medel Stabilitet",
                "label_en": "Medium Steadiness",
                "desc_sv": "Du hanterar både förändring och stabilitet väl och anpassar dig flexibelt.",
                "desc_en": "You handle both change and stability well, adapting flexibly."
            },
            "low": {
                "label_sv": "Låg Stabilitet",
                "label_en": "Low Steadiness",
                "desc_sv": "Du trivs med förändring och variation och känner dig rastlös i rutiner.",
                "desc_en": "You thrive on change and variety and feel restless in routines."
            }
        },
        "C": {
            "high": {
                "label_sv": "Hög Samvetsgrannhet",
                "label_en": "High Conscientiousness",
                "desc_sv": "Du är analytisk, noggrann och kvalitetsmedveten. Du värdesätter precision och systematik.",
                "desc_en": "You are analytical, precise, and quality-conscious. You value precision and systematic approaches."
            },
            "medium": {
                "label_sv": "Medel Samvetsgrannhet",
                "label_en": "Medium Conscientiousness",
                "desc_sv": "Du är noggrann när det behövs men kan också vara pragmatisk.",
                "desc_en": "You are thorough when needed but can also be pragmatic."
            },
            "low": {
                "label_sv": "Låg Samvetsgrannhet",
                "label_en": "Low Conscientiousness",
                "desc_sv": "Du är spontan och föredrar flexibilitet framför strikta processer.",
                "desc_en": "You are spontaneous and prefer flexibility over strict processes."
            }
        }
    }

    dim_interp = interpretations.get(dimension, {}).get(level, {})
    label_key = "label_sv" if language == "sv" else "label_en"
    desc_key = "desc_sv" if language == "sv" else "desc_en"

    return {
        "level": level,
        "label": dim_interp.get(label_key, ""),
        "description": dim_interp.get(desc_key, "")
    }


def get_strengths_from_profile(profile: DISCProfile, language: str = "sv") -> List[str]:
    """
    Identify key strengths based on DISC profile

    Args:
        profile: DISCProfile object
        language: "sv" or "en"

    Returns:
        List of strength descriptions
    """
    strengths = []
    scores = profile.scores

    # Swedish strengths
    if language == "sv":
        if scores.dominance >= 70:
            strengths.append("Du är handlingskraftig och tar snabba beslut")
            strengths.append("Du driver resultat och uppnår mål effektivt")

        if scores.influence >= 70:
            strengths.append("Du bygger relationer och nätverk naturligt")
            strengths.append("Du inspirerar och motiverar andra med din entusiasm")

        if scores.steadiness >= 70:
            strengths.append("Du skapar stabilitet och trygghet i team")
            strengths.append("Du är en pålitlig och lojal teammedlem")

        if scores.conscientiousness >= 70:
            strengths.append("Du levererar högkvalitativt arbete med precision")
            strengths.append("Du analyserar noggrant innan du fattar beslut")

        # Combination strengths
        if scores.dominance >= 60 and scores.influence >= 60:
            strengths.append("Din kombination av drivkraft och karisma gör dig till en naturlig ledare")

        if scores.steadiness >= 60 and scores.conscientiousness >= 60:
            strengths.append("Du kombinerar kvalitet med pålitlighet på ett unikt sätt")

    # English strengths
    else:
        if scores.dominance >= 70:
            strengths.append("You are action-oriented and make quick decisions")
            strengths.append("You drive results and achieve goals efficiently")

        if scores.influence >= 70:
            strengths.append("You build relationships and networks naturally")
            strengths.append("You inspire and motivate others with your enthusiasm")

        if scores.steadiness >= 70:
            strengths.append("You create stability and security in teams")
            strengths.append("You are a reliable and loyal team member")

        if scores.conscientiousness >= 70:
            strengths.append("You deliver high-quality work with precision")
            strengths.append("You analyze thoroughly before making decisions")

        # Combination strengths
        if scores.dominance >= 60 and scores.influence >= 60:
            strengths.append("Your combination of drive and charisma makes you a natural leader")

        if scores.steadiness >= 60 and scores.conscientiousness >= 60:
            strengths.append("You uniquely combine quality with reliability")

    # Return top 4-5 strengths
    return strengths[:5] if strengths else (
        ["Du har en balanserad DISC-profil"] if language == "sv"
        else ["You have a balanced DISC profile"]
    )


def get_development_areas(profile: DISCProfile, language: str = "sv") -> List[str]:
    """
    Identify development areas based on DISC profile

    Args:
        profile: DISCProfile object
        language: "sv" or "en"

    Returns:
        List of development suggestions
    """
    areas = []
    scores = profile.scores

    # Swedish development areas
    if language == "sv":
        if scores.dominance >= 70:
            areas.append("Öva på tålamod och lyssna på andras perspektiv innan du agerar")
            areas.append("Balansera resultatfokus med hänsyn till teamets känslor")

        if scores.influence >= 70:
            areas.append("Utveckla fokus på uppgifter och detaljer, inte bara relationer")
            areas.append("Öva på att följa upp konkreta åtaganden och deadlines")

        if scores.steadiness >= 70:
            areas.append("Träna på att uttrycka åsikter även när det kan skapa konflikt")
            areas.append("Utveckla förmågan att driva förändring och ta risker")

        if scores.conscientiousness >= 70:
            areas.append("Öva på att fatta beslut med begränsad information")
            areas.append("Balansera perfektionism med pragmatism och tidseffektivitet")

        # Low score development
        if scores.dominance <= 30:
            areas.append("Utveckla självförtroende att ta beslut och leda initiativ")

        if scores.influence <= 30:
            areas.append("Öva på att bygga relationer och nätverka mer aktivt")

        if scores.steadiness <= 30:
            areas.append("Träna på tålamod och att ge andra tid att anpassa sig")

        if scores.conscientiousness <= 30:
            areas.append("Utveckla mer systematik och detaljfokus i ditt arbete")

    # English development areas
    else:
        if scores.dominance >= 70:
            areas.append("Practice patience and listen to others' perspectives before acting")
            areas.append("Balance results focus with consideration for team feelings")

        if scores.influence >= 70:
            areas.append("Develop focus on tasks and details, not just relationships")
            areas.append("Practice following up on concrete commitments and deadlines")

        if scores.steadiness >= 70:
            areas.append("Practice expressing opinions even when it might create conflict")
            areas.append("Develop ability to drive change and take risks")

        if scores.conscientiousness >= 70:
            areas.append("Practice making decisions with limited information")
            areas.append("Balance perfectionism with pragmatism and time efficiency")

        # Low score development
        if scores.dominance <= 30:
            areas.append("Develop confidence to make decisions and lead initiatives")

        if scores.influence <= 30:
            areas.append("Practice building relationships and networking more actively")

        if scores.steadiness <= 30:
            areas.append("Practice patience and giving others time to adapt")

        if scores.conscientiousness <= 30:
            areas.append("Develop more systematic approach and detail focus in your work")

    # Return top 3-4 areas
    return areas[:4]


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_disc_assessment(
    questions: List[Dict],
    answers: Dict[int, int]
) -> DISCProfile:
    """
    Complete DISC assessment analysis

    Args:
        questions: List of all DISC questions
        answers: User's answers (question_id -> value 1-5)

    Returns:
        Complete DISCProfile with scores and interpretation
    """
    # Calculate scores
    scores = calculate_disc_scores(questions, answers)

    # Identify profile
    profile = identify_disc_profile(scores)

    return profile
