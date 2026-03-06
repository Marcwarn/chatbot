/**
 * IPIP Big Five Questions - Swedish Version
 *
 * Source: International Personality Item Pool (IPIP)
 * License: Public Domain
 *
 * Based on IPIP-50 (10 items per factor)
 * Validated psychometric instrument
 *
 * References:
 * - Goldberg, L. R. (1992). The development of markers for the Big-Five factor structure.
 * - Donnellan, M. B., Oswald, F. L., Baird, B. M., & Lucas, R. E. (2006).
 *   The mini-IPIP scales: tiny-yet-effective measures of the Big Five factors of personality.
 */

export interface BigFiveQuestion {
  id: number;
  text: string;
  dimension: 'O' | 'C' | 'E' | 'A' | 'N'; // Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
  keyed: 'plus' | 'minus'; // Plus = higher score means more of trait, Minus = reverse scored
}

/**
 * IPIP-50 Big Five Questionnaire - Swedish Translation
 *
 * 50 items total:
 * - 10 Openness (O)
 * - 10 Conscientiousness (C)
 * - 10 Extraversion (E)
 * - 10 Agreeableness (A)
 * - 10 Neuroticism (N)
 */
export const IPIP_BIG_FIVE_50: BigFiveQuestion[] = [
  // ============================================================================
  // EXTRAVERSION (E) - 10 items
  // ============================================================================
  {
    id: 1,
    text: "Jag är själens levande på festen",
    dimension: 'E',
    keyed: 'plus'
  },
  {
    id: 2,
    text: "Jag pratar inte särskilt mycket",
    dimension: 'E',
    keyed: 'minus'
  },
  {
    id: 3,
    text: "Jag känner mig bekväm med andra människor",
    dimension: 'E',
    keyed: 'plus'
  },
  {
    id: 4,
    text: "Jag håller mig i bakgrunden",
    dimension: 'E',
    keyed: 'minus'
  },
  {
    id: 5,
    text: "Jag startar konversationer",
    dimension: 'E',
    keyed: 'plus'
  },
  {
    id: 6,
    text: "Jag har lite att säga",
    dimension: 'E',
    keyed: 'minus'
  },
  {
    id: 7,
    text: "Jag pratar med många olika personer på fester",
    dimension: 'E',
    keyed: 'plus'
  },
  {
    id: 8,
    text: "Jag gillar inte att dra till mig uppmärksamhet",
    dimension: 'E',
    keyed: 'minus'
  },
  {
    id: 9,
    text: "Jag trivs i folksamlingar",
    dimension: 'E',
    keyed: 'plus'
  },
  {
    id: 10,
    text: "Jag föredrar att vara tyst och lyssna",
    dimension: 'E',
    keyed: 'minus'
  },

  // ============================================================================
  // AGREEABLENESS (A) - 10 items
  // ============================================================================
  {
    id: 11,
    text: "Jag är intresserad av andra människor",
    dimension: 'A',
    keyed: 'plus'
  },
  {
    id: 12,
    text: "Jag förolämpar andra",
    dimension: 'A',
    keyed: 'minus'
  },
  {
    id: 13,
    text: "Jag bryr mig om andras känslor",
    dimension: 'A',
    keyed: 'plus'
  },
  {
    id: 14,
    text: "Jag är inte intresserad av andras problem",
    dimension: 'A',
    keyed: 'minus'
  },
  {
    id: 15,
    text: "Jag har ett varmt hjärta",
    dimension: 'A',
    keyed: 'plus'
  },
  {
    id: 16,
    text: "Jag är kall och likgiltig",
    dimension: 'A',
    keyed: 'minus'
  },
  {
    id: 17,
    text: "Jag tar mig tid för andra",
    dimension: 'A',
    keyed: 'plus'
  },
  {
    id: 18,
    text: "Jag känner lite för andra",
    dimension: 'A',
    keyed: 'minus'
  },
  {
    id: 19,
    text: "Jag gör människor bekväma",
    dimension: 'A',
    keyed: 'plus'
  },
  {
    id: 20,
    text: "Jag är inte riktigt intresserad av andra",
    dimension: 'A',
    keyed: 'minus'
  },

  // ============================================================================
  // CONSCIENTIOUSNESS (C) - 10 items
  // ============================================================================
  {
    id: 21,
    text: "Jag är alltid förberedd",
    dimension: 'C',
    keyed: 'plus'
  },
  {
    id: 22,
    text: "Jag lämnar mina saker överallt",
    dimension: 'C',
    keyed: 'minus'
  },
  {
    id: 23,
    text: "Jag uppmärksammar detaljer",
    dimension: 'C',
    keyed: 'plus'
  },
  {
    id: 24,
    text: "Jag gör en röra av saker",
    dimension: 'C',
    keyed: 'minus'
  },
  {
    id: 25,
    text: "Jag slutför uppgifter direkt",
    dimension: 'C',
    keyed: 'plus'
  },
  {
    id: 26,
    text: "Jag glömmer ofta att lägga tillbaka saker på sin plats",
    dimension: 'C',
    keyed: 'minus'
  },
  {
    id: 27,
    text: "Jag gillar ordning",
    dimension: 'C',
    keyed: 'plus'
  },
  {
    id: 28,
    text: "Jag undviker mina ansvar",
    dimension: 'C',
    keyed: 'minus'
  },
  {
    id: 29,
    text: "Jag följer en planering",
    dimension: 'C',
    keyed: 'plus'
  },
  {
    id: 30,
    text: "Jag lämnar ofta mina uppgifter ogjorda",
    dimension: 'C',
    keyed: 'minus'
  },

  // ============================================================================
  // NEUROTICISM (N) - 10 items
  // ============================================================================
  {
    id: 31,
    text: "Jag blir lätt upprörd",
    dimension: 'N',
    keyed: 'plus'
  },
  {
    id: 32,
    text: "Jag är avslappnad större delen av tiden",
    dimension: 'N',
    keyed: 'minus'
  },
  {
    id: 33,
    text: "Jag oroar mig för saker",
    dimension: 'N',
    keyed: 'plus'
  },
  {
    id: 34,
    text: "Jag blir sällan stressad",
    dimension: 'N',
    keyed: 'minus'
  },
  {
    id: 35,
    text: "Jag blir lätt irriterad",
    dimension: 'N',
    keyed: 'plus'
  },
  {
    id: 36,
    text: "Jag hanterar stress bra",
    dimension: 'N',
    keyed: 'minus'
  },
  {
    id: 37,
    text: "Mina humörsvängningar är stora",
    dimension: 'N',
    keyed: 'plus'
  },
  {
    id: 38,
    text: "Jag är sällan nedstämd",
    dimension: 'N',
    keyed: 'minus'
  },
  {
    id: 39,
    text: "Jag blir ofta arg",
    dimension: 'N',
    keyed: 'plus'
  },
  {
    id: 40,
    text: "Jag har bra kontroll över mina känslor",
    dimension: 'N',
    keyed: 'minus'
  },

  // ============================================================================
  // OPENNESS (O) - 10 items
  // ============================================================================
  {
    id: 41,
    text: "Jag har en livlig fantasi",
    dimension: 'O',
    keyed: 'plus'
  },
  {
    id: 42,
    text: "Jag har svårt att förstå abstrakta idéer",
    dimension: 'O',
    keyed: 'minus'
  },
  {
    id: 43,
    text: "Jag har utmärkta idéer",
    dimension: 'O',
    keyed: 'plus'
  },
  {
    id: 44,
    text: "Jag har inte särskilt bra fantasi",
    dimension: 'O',
    keyed: 'minus'
  },
  {
    id: 45,
    text: "Jag är snabb på att förstå saker",
    dimension: 'O',
    keyed: 'plus'
  },
  {
    id: 46,
    text: "Jag undviker filosofiska diskussioner",
    dimension: 'O',
    keyed: 'minus'
  },
  {
    id: 47,
    text: "Jag gillar att tänka på nya sätt",
    dimension: 'O',
    keyed: 'plus'
  },
  {
    id: 48,
    text: "Jag är inte intresserad av abstrakta idéer",
    dimension: 'O',
    keyed: 'minus'
  },
  {
    id: 49,
    text: "Jag har brett ordförråd",
    dimension: 'O',
    keyed: 'plus'
  },
  {
    id: 50,
    text: "Jag har svårigheter med komplexa tankar",
    dimension: 'O',
    keyed: 'minus'
  }
];

/**
 * Likert Scale Options (Swedish)
 */
export const LIKERT_OPTIONS = [
  { value: 1, label: "Stämmer inte alls" },
  { value: 2, label: "Stämmer dåligt" },
  { value: 3, label: "Neutral / Osäker" },
  { value: 4, label: "Stämmer ganska bra" },
  { value: 5, label: "Stämmer helt" }
];

/**
 * Big Five Dimension Names & Descriptions (Swedish)
 */
export const BIG_FIVE_DIMENSIONS = {
  E: {
    name: "Extraversion",
    shortName: "Extraversion",
    description: "Utåtriktad, social, energisk",
    lowDescription: "Introvert, reserverad, självständig",
    highDescription: "Extravert, utåtriktad, pratsam",
    color: "#EF4444" // Red
  },
  A: {
    name: "Agreeableness",
    shortName: "Vänlighet",
    description: "Samarbetsvillig, empatisk, omtänksam",
    lowDescription: "Skeptisk, kritisk, konkurrensinriktad",
    highDescription: "Samarbetsvillig, tillitsfull, hjälpsam",
    color: "#10B981" // Green
  },
  C: {
    name: "Conscientiousness",
    shortName: "Samvetsgrannhet",
    description: "Organiserad, pålitlig, målinriktad",
    lowDescription: "Spontan, flexibel, avslappnad",
    highDescription: "Organiserad, pålitlig, disciplinerad",
    color: "#6366F1" // Indigo
  },
  N: {
    name: "Neuroticism",
    shortName: "Emotionell Stabilitet",
    description: "Emotionell reaktivitet och stresshantering",
    lowDescription: "Stabil, lugn, stresstålig",
    highDescription: "Känslig, orolig, stressbenägen",
    color: "#F59E0B" // Amber
  },
  O: {
    name: "Openness",
    shortName: "Öppenhet",
    description: "Kreativ, nyfiken, fantasifull",
    lowDescription: "Praktisk, traditionell, konkret",
    highDescription: "Kreativ, nyfiken, intellektuell",
    color: "#EC4899" // Pink
  }
};

/**
 * Randomize question order (for test-retest reliability)
 */
export function randomizeQuestions(questions: BigFiveQuestion[]): BigFiveQuestion[] {
  const shuffled = [...questions];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

/**
 * Get questions by dimension
 */
export function getQuestionsByDimension(dimension: 'O' | 'C' | 'E' | 'A' | 'N'): BigFiveQuestion[] {
  return IPIP_BIG_FIVE_50.filter(q => q.dimension === dimension);
}
