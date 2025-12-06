/**
 * Big Five Scoring Algorithm
 *
 * Based on standard psychometric practices:
 * - Reverse scoring for negatively keyed items
 * - Standardization to 0-100 scale
 * - Percentile calculation based on normal distribution
 *
 * References:
 * - John, O. P., & Srivastava, S. (1999). The Big Five trait taxonomy
 * - Costa, P. T., & McCrae, R. R. (1992). NEO PI-R professional manual
 */

import { BigFiveQuestion, BIG_FIVE_DIMENSIONS } from './ipip-questions';

export interface Answer {
  questionId: number;
  value: number; // 1-5 Likert scale
}

export interface DimensionScore {
  dimension: 'O' | 'C' | 'E' | 'A' | 'N';
  name: string;
  rawScore: number;        // Sum of item scores
  meanScore: number;       // Average per item (1-5)
  standardScore: number;   // 0-100 scale
  percentile: number;      // Compared to population norm
  interpretation: string;
  facets: string[];        // Specific aspects of the dimension
  color: string;
}

export interface BigFiveResult {
  scores: DimensionScore[];
  overallProfile: string;
  strengths: string[];
  developmentAreas: string[];
  careerSuggestions: string[];
  relationshipStyle: string;
}

/**
 * Calculate raw score for a dimension
 */
function calculateRawScore(
  answers: Answer[],
  questions: BigFiveQuestion[],
  dimension: 'O' | 'C' | 'E' | 'A' | 'N'
): { rawScore: number; meanScore: number } {
  const dimQuestions = questions.filter(q => q.dimension === dimension);
  let totalScore = 0;

  for (const question of dimQuestions) {
    const answer = answers.find(a => a.questionId === question.id);
    if (!answer) continue;

    let score = answer.value;

    // Reverse scoring for negatively keyed items
    if (question.keyed === 'minus') {
      score = 6 - score; // 1→5, 2→4, 3→3, 4→2, 5→1
    }

    totalScore += score;
  }

  const meanScore = totalScore / dimQuestions.length;

  return {
    rawScore: totalScore,
    meanScore: meanScore
  };
}

/**
 * Convert mean score (1-5) to standard score (0-100)
 */
function toStandardScore(meanScore: number): number {
  // Linear transformation: (meanScore - 1) / 4 * 100
  return ((meanScore - 1) / 4) * 100;
}

/**
 * Calculate percentile based on normal distribution
 *
 * Approximation using population norms:
 * - Mean = 3.0 (on 1-5 scale) = 50th percentile
 * - SD = 0.6-0.8 (varies by dimension)
 *
 * For simplicity, using SD = 0.7 for all dimensions
 */
function calculatePercentile(meanScore: number): number {
  const populationMean = 3.0;
  const populationSD = 0.7;

  // Z-score
  const z = (meanScore - populationMean) / populationSD;

  // Convert Z-score to percentile (approximation)
  // Using cumulative distribution function approximation
  const percentile = cumulativeNormal(z) * 100;

  return Math.max(1, Math.min(99, Math.round(percentile)));
}

/**
 * Cumulative normal distribution (approximation)
 */
function cumulativeNormal(z: number): number {
  // Abramowitz and Stegun approximation
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp(-z * z / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));

  return z > 0 ? 1 - p : p;
}

/**
 * Generate interpretation text based on score
 */
function getInterpretation(
  dimension: 'O' | 'C' | 'E' | 'A' | 'N',
  percentile: number
): string {
  const dimInfo = BIG_FIVE_DIMENSIONS[dimension];

  if (percentile < 30) {
    return `Låg ${dimInfo.shortName}: ${dimInfo.lowDescription}`;
  } else if (percentile > 70) {
    return `Hög ${dimInfo.shortName}: ${dimInfo.highDescription}`;
  } else {
    return `Medel ${dimInfo.shortName}: Balanserad mellan ${dimInfo.lowDescription.toLowerCase()} och ${dimInfo.highDescription.toLowerCase()}`;
  }
}

/**
 * Get facets (sub-traits) for each dimension
 */
function getFacets(dimension: 'O' | 'C' | 'E' | 'A' | 'N', percentile: number): string[] {
  const facetMap: Record<string, { low: string[]; high: string[] }> = {
    E: {
      low: ['Föredrar ensamhet', 'Lyssnar mer än pratar', 'Tänker innan du agerar'],
      high: ['Energisk i sociala sammanhang', 'Tar initiativ', 'Pratar lätt med nya människor']
    },
    A: {
      low: ['Kritiskt tänkande', 'Står på dig', 'Självständig'],
      high: ['Empatisk', 'Samarbetsvillig', 'Tillitsfull']
    },
    C: {
      low: ['Spontan', 'Flexibel', 'Avslappnad'],
      high: ['Planerar noga', 'Pålitlig', 'Målinriktad']
    },
    N: {
      low: ['Emotionellt stabil', 'Lugn under press', 'Optimistisk'],
      high: ['Känslomässigt medveten', 'Försiktig', 'Reflekterande']
    },
    O: {
      low: ['Praktisk', 'Traditionell', 'Jordnära'],
      high: ['Kreativ', 'Nyfiken', 'Experimenterar gärna']
    }
  };

  return percentile < 50 ? facetMap[dimension].low : facetMap[dimension].high;
}

/**
 * Main scoring function
 */
export function scoreAssessment(
  answers: Answer[],
  questions: BigFiveQuestion[]
): BigFiveResult {
  const dimensions: Array<'O' | 'C' | 'E' | 'A' | 'N'> = ['O', 'C', 'E', 'A', 'N'];

  const scores: DimensionScore[] = dimensions.map(dim => {
    const { rawScore, meanScore } = calculateRawScore(answers, questions, dim);
    const standardScore = toStandardScore(meanScore);
    const percentile = calculatePercentile(meanScore);
    const interpretation = getInterpretation(dim, percentile);
    const facets = getFacets(dim, percentile);

    return {
      dimension: dim,
      name: BIG_FIVE_DIMENSIONS[dim].shortName,
      rawScore,
      meanScore,
      standardScore,
      percentile,
      interpretation,
      facets,
      color: BIG_FIVE_DIMENSIONS[dim].color
    };
  });

  // Generate overall profile
  const overallProfile = generateOverallProfile(scores);

  // Identify strengths (top 2 dimensions)
  const strengths = generateStrengths(scores);

  // Identify development areas (bottom 2 dimensions, if low)
  const developmentAreas = generateDevelopmentAreas(scores);

  // Career suggestions based on profile
  const careerSuggestions = generateCareerSuggestions(scores);

  // Relationship style
  const relationshipStyle = generateRelationshipStyle(scores);

  return {
    scores,
    overallProfile,
    strengths,
    developmentAreas,
    careerSuggestions,
    relationshipStyle
  };
}

/**
 * Generate overall personality profile description
 */
function generateOverallProfile(scores: DimensionScore[]): string {
  const highTraits = scores.filter(s => s.percentile > 65).map(s => s.name);
  const lowTraits = scores.filter(s => s.percentile < 35).map(s => s.name);

  let profile = 'Din personlighetsprofil visar ';

  if (highTraits.length > 0) {
    profile += `hög ${highTraits.join(', ')}`;
  }

  if (lowTraits.length > 0) {
    if (highTraits.length > 0) profile += ' och ';
    profile += `låg ${lowTraits.join(', ')}`;
  }

  if (highTraits.length === 0 && lowTraits.length === 0) {
    profile += 'en balanserad profil över alla dimensioner';
  }

  profile += '. Detta är din unika kombination av egenskaper som formar hur du tänker, känner och agerar.';

  return profile;
}

/**
 * Identify key strengths
 */
function generateStrengths(scores: DimensionScore[]): string[] {
  const sortedScores = [...scores].sort((a, b) => b.percentile - a.percentile);
  const topTwo = sortedScores.slice(0, 2);

  const strengthMap: Record<string, Record<string, string>> = {
    E: {
      high: 'Du bygger lätt relationer och energiserar andra',
      low: 'Du tänker djupt och arbetar bra självständigt'
    },
    A: {
      high: 'Du skapar harmoni och bygger förtroende',
      low: 'Du tar beslut objektivt och står på dig'
    },
    C: {
      high: 'Du är pålitlig och når dina mål',
      low: 'Du anpassar dig snabbt och är spontan'
    },
    N: {
      high: 'Du är medveten om risker och förberedd',
      low: 'Du hanterar stress med lätthet'
    },
    O: {
      high: 'Du ser nya möjligheter och innoverar',
      low: 'Du är praktisk och jordnära'
    }
  };

  return topTwo.map(score => {
    const level = score.percentile > 50 ? 'high' : 'low';
    return strengthMap[score.dimension][level];
  });
}

/**
 * Identify development areas
 */
function generateDevelopmentAreas(scores: DimensionScore[]): string[] {
  // Only suggest development if score is very low (<25th percentile)
  const lowScores = scores.filter(s => s.percentile < 25);

  const developmentMap: Record<string, string> = {
    E: 'Överväg att gradvis utöka ditt sociala nätverk',
    A: 'Arbeta på att se andras perspektiv i konflikter',
    C: 'Utveckla rutiner och struktur för viktiga uppgifter',
    N: 'Utforska stresshanteringstekniker som mindfulness',
    O: 'Utmana dig själv att prova nya upplevelser regelbundet'
  };

  return lowScores.map(score => developmentMap[score.dimension]);
}

/**
 * Generate career suggestions based on Big Five profile
 */
function generateCareerSuggestions(scores: DimensionScore[]): string[] {
  const profile = {
    E: scores.find(s => s.dimension === 'E')!.percentile > 50,
    A: scores.find(s => s.dimension === 'A')!.percentile > 50,
    C: scores.find(s => s.dimension === 'C')!.percentile > 50,
    N: scores.find(s => s.dimension === 'N')!.percentile < 50, // Low N = Stable
    O: scores.find(s => s.dimension === 'O')!.percentile > 50
  };

  const suggestions: string[] = [];

  // High E + High A = People-focused roles
  if (profile.E && profile.A) {
    suggestions.push('Kundrelationer, HR, Coaching');
  }

  // High O + Low N = Creative roles
  if (profile.O && profile.N) {
    suggestions.push('Design, Innovation, Forskning');
  }

  // High C + Low O = Analytical roles
  if (profile.C && !profile.O) {
    suggestions.push('Finans, Administration, Kvalitetssäkring');
  }

  // High E + High O = Entrepreneurial
  if (profile.E && profile.O) {
    suggestions.push('Entreprenörskap, Försäljning, Marknadsföring');
  }

  // Low E + High C = Technical roles
  if (!profile.E && profile.C) {
    suggestions.push('Programmering, Analys, Teknik');
  }

  return suggestions.length > 0 ? suggestions : ['Utforska roller som matchar din balanserade profil'];
}

/**
 * Generate relationship style description
 */
function generateRelationshipStyle(scores: DimensionScore[]): string {
  const E = scores.find(s => s.dimension === 'E')!.percentile;
  const A = scores.find(s => s.dimension === 'A')!.percentile;
  const N = scores.find(s => s.dimension === 'N')!.percentile;

  let style = 'I relationer är du ';

  // Extraversion influence
  if (E > 65) {
    style += 'socialt aktiv och trivs med många kontakter. ';
  } else if (E < 35) {
    style += 'mer selektiv med nära relationer och värdesätter djup. ';
  } else {
    style += 'balanserad mellan socialt umgänge och egen tid. ';
  }

  // Agreeableness influence
  if (A > 65) {
    style += 'Du är omtänksam och strävar efter harmoni. ';
  } else if (A < 35) {
    style += 'Du är direkta och värdesätter ärlighet framför diplomati. ';
  }

  // Neuroticism influence
  if (N > 65) {
    style += 'Du är känslig för relationsdynamik och kan behöva bekräftelse.';
  } else if (N < 35) {
    style += 'Du är trygg och stabil i relationer.';
  }

  return style;
}
