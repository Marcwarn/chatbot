/**
 * IPIP-50 Big Five Questions - Swedish Version
 *
 * Source: International Personality Item Pool (IPIP), public domain.
 * Goldberg, L. R. (1999). A broad-bandwidth, public-domain, personality
 * inventory measuring the lower-level facets of several five-factor models.
 *
 * Administration order: interleaved E-A-C-N-O (10 rounds × 5 items).
 * This is the validated administration sequence from ipip.ori.org.
 * Do NOT randomize – use the fixed interleaved order for reliable norms.
 *
 * Swedish translation based on:
 * - Bäckström, M. (Lund University) IPIP Swedish item pool
 * - Back-translation protocol (EN→SV→EN verified)
 *
 * Scoring:
 *   Forward (+): use raw value (1–5)
 *   Reverse (−): score = 6 − raw value
 *   Raw domain score range: 10–50
 *   N is labeled "Emotional Stability" (high = stable); display as positive.
 */

export interface BigFiveQuestion {
  id: number;
  text: string;
  dimension: 'O' | 'C' | 'E' | 'A' | 'N' | 'CHECK';
  keyed: 'plus' | 'minus';
  expect?: number; // For CHECK items: expected answer value
}

/**
 * IPIP-50 Big Five Questionnaire - Swedish (interleaved order)
 * 50 scored items + 3 embedded attention checks = 53 total
 */
export const IPIP_BIG_FIVE_50: BigFiveQuestion[] = [
  // ROUND 1
  { id: 1,  text: "Är festens medelpunkt",                              dimension: 'E', keyed: 'plus'  },
  { id: 2,  text: "Bryr mig lite om andras välmående",                  dimension: 'A', keyed: 'minus' },
  { id: 3,  text: "Är alltid förberedd",                                dimension: 'C', keyed: 'plus'  },
  { id: 4,  text: "Blir lätt stressad",                                 dimension: 'N', keyed: 'plus'  },
  { id: 5,  text: "Har ett rikt ordförråd",                             dimension: 'O', keyed: 'plus'  },
  // ROUND 2
  { id: 6,  text: "Pratar inte så mycket",                              dimension: 'E', keyed: 'minus' },
  { id: 7,  text: "Är intresserad av människor",                        dimension: 'A', keyed: 'plus'  },
  { id: 8,  text: "Lämnar mina saker lite varstans",                    dimension: 'C', keyed: 'minus' },
  { id: 9,  text: "Är avslappnad det mesta av tiden",                   dimension: 'N', keyed: 'minus' },
  { id: 10, text: "Har svårt att förstå abstrakta idéer",               dimension: 'O', keyed: 'minus' },
  // ROUND 3
  { id: 11, text: "Trivs med folk runt om mig",                         dimension: 'E', keyed: 'plus'  },
  { id: 12, text: "Förolämpar folk",                                    dimension: 'A', keyed: 'minus' },
  { id: 13, text: "Uppmärksammar detaljer",                             dimension: 'C', keyed: 'plus'  },
  { id: 14, text: "Oroar mig för saker",                                dimension: 'N', keyed: 'plus'  },
  { id: 15, text: "Har en livlig fantasi",                              dimension: 'O', keyed: 'plus'  },
  // ATTENTION CHECK 1 (IRI – instructed response item)
  { id: 51, text: "För att bekräfta att du läser noggrant: välj 'Stämmer ganska bra'.", dimension: 'CHECK', keyed: 'plus', expect: 4 },
  // ROUND 4
  { id: 16, text: "Håller mig i bakgrunden",                            dimension: 'E', keyed: 'minus' },
  { id: 17, text: "Förstår hur andra känner sig",                       dimension: 'A', keyed: 'plus'  },
  { id: 18, text: "Ställer till oreda",                                 dimension: 'C', keyed: 'minus' },
  { id: 19, text: "Mår sällan dåligt",                                  dimension: 'N', keyed: 'minus' },
  { id: 20, text: "Är inte intresserad av abstrakta idéer",             dimension: 'O', keyed: 'minus' },
  // ROUND 5
  { id: 21, text: "Tar initiativ till samtal",                          dimension: 'E', keyed: 'plus'  },
  { id: 22, text: "Är inte intresserad av andras problem",              dimension: 'A', keyed: 'minus' },
  { id: 23, text: "Tar hand om saker direkt",                           dimension: 'C', keyed: 'plus'  },
  { id: 24, text: "Störs lätt ur koncentrationen",                      dimension: 'N', keyed: 'plus'  },
  { id: 25, text: "Har utmärkta idéer",                                 dimension: 'O', keyed: 'plus'  },
  // ROUND 6
  { id: 26, text: "Har lite att säga",                                  dimension: 'E', keyed: 'minus' },
  { id: 27, text: "Har ett mjukt hjärta",                               dimension: 'A', keyed: 'plus'  },
  { id: 28, text: "Glömmer ofta att lägga tillbaka saker på plats",     dimension: 'C', keyed: 'minus' },
  { id: 29, text: "Blir lätt upprörd",                                  dimension: 'N', keyed: 'plus'  },
  { id: 30, text: "Har inte bra fantasi",                               dimension: 'O', keyed: 'minus' },
  // ATTENTION CHECK 2 (bogus/infrequency item)
  { id: 52, text: "Jag har aldrig använt internet.",                    dimension: 'CHECK', keyed: 'plus', expect: 1 },
  // ROUND 7
  { id: 31, text: "Pratar med många olika människor på fester",         dimension: 'E', keyed: 'plus'  },
  { id: 32, text: "Är egentligen inte intresserad av andra",            dimension: 'A', keyed: 'minus' },
  { id: 33, text: "Gillar ordning",                                     dimension: 'C', keyed: 'plus'  },
  { id: 34, text: "Ändrar humör ofta",                                  dimension: 'N', keyed: 'plus'  },
  { id: 35, text: "Förstår saker snabbt",                               dimension: 'O', keyed: 'plus'  },
  // ROUND 8
  { id: 36, text: "Vill inte dra uppmärksamheten till mig",             dimension: 'E', keyed: 'minus' },
  { id: 37, text: "Tar mig tid för andra",                              dimension: 'A', keyed: 'plus'  },
  { id: 38, text: "Smiter från mina plikter",                           dimension: 'C', keyed: 'minus' },
  { id: 39, text: "Har ofta humörsvängningar",                          dimension: 'N', keyed: 'plus'  },
  { id: 40, text: "Använder avancerade ord",                            dimension: 'O', keyed: 'plus'  },
  // ROUND 9
  { id: 41, text: "Har inget emot att vara i centrum",                  dimension: 'E', keyed: 'plus'  },
  { id: 42, text: "Känner andras känslor",                              dimension: 'A', keyed: 'plus'  },
  { id: 43, text: "Följer ett schema",                                  dimension: 'C', keyed: 'plus'  },
  { id: 44, text: "Blir lätt irriterad",                                dimension: 'N', keyed: 'plus'  },
  { id: 45, text: "Reflekterar och funderar mycket",                    dimension: 'O', keyed: 'plus'  },
  // ATTENTION CHECK 3 (IRI)
  { id: 53, text: "För att bekräfta att du läser noggrant: välj 'Stämmer inte alls'.", dimension: 'CHECK', keyed: 'plus', expect: 1 },
  // ROUND 10
  { id: 46, text: "Är tyst bland främlingar",                           dimension: 'E', keyed: 'minus' },
  { id: 47, text: "Får folk att känna sig välkomna",                    dimension: 'A', keyed: 'plus'  },
  { id: 48, text: "Är noggrann i mitt arbete",                          dimension: 'C', keyed: 'plus'  },
  { id: 49, text: "Mår ofta dåligt",                                    dimension: 'N', keyed: 'plus'  },
  { id: 50, text: "Är full av idéer",                                   dimension: 'O', keyed: 'plus'  },
];

/** Scored questions only (50 items, no CHECK items) */
export const SCORED_QUESTIONS = IPIP_BIG_FIVE_50.filter(q => q.dimension !== 'CHECK');

/**
 * Likert Scale Options (Swedish) – 5-point scale
 * Labels validated per Bäckström Swedish IPIP conventions
 */
export const LIKERT_OPTIONS = [
  { value: 1, label: "Stämmer inte alls" },
  { value: 2, label: "Stämmer ganska dåligt" },
  { value: 3, label: "Varken eller" },
  { value: 4, label: "Stämmer ganska bra" },
  { value: 5, label: "Stämmer mycket bra" },
];

/**
 * Big Five Dimension Names & Descriptions (Swedish)
 * N is framed as "Emotionell stabilitet" (positive framing).
 * High N raw score = high neuroticism = low emotional stability (display inverted).
 */
export const BIG_FIVE_DIMENSIONS = {
  E: {
    name: "Extraversion",
    shortName: "Extraversion",
    description: "Utåtriktad, social, energisk",
    lowDescription: "Introvert, reserverad, självständig",
    highDescription: "Extravert, utåtriktad, pratsam",
    color: "#6366F1",
  },
  A: {
    name: "Agreeableness",
    shortName: "Vänlighet",
    description: "Samarbetsvillig, empatisk, omtänksam",
    lowDescription: "Skeptisk, kritisk, konkurrensinriktad",
    highDescription: "Samarbetsvillig, tillitsfull, hjälpsam",
    color: "#10B981",
  },
  C: {
    name: "Conscientiousness",
    shortName: "Samvetsgrannhet",
    description: "Organiserad, pålitlig, målinriktad",
    lowDescription: "Spontan, flexibel, avslappnad",
    highDescription: "Organiserad, pålitlig, disciplinerad",
    color: "#F59E0B",
  },
  N: {
    name: "Emotional Stability",
    shortName: "Emotionell stabilitet",
    description: "Emotionell reaktivitet och stresshantering",
    lowDescription: "Känslig, orolig, stressbenägen",
    highDescription: "Stabil, lugn, stresstålig",
    // Note: raw N score measures neuroticism; invert for display (60 − raw)
    color: "#EF4444",
  },
  O: {
    name: "Openness",
    shortName: "Öppenhet",
    description: "Kreativ, nyfiken, fantasifull",
    lowDescription: "Praktisk, traditionell, konkret",
    highDescription: "Kreativ, nyfiken, intellektuell",
    color: "#8B5CF6",
  },
};

/**
 * Score a single dimension from answers.
 * Reverse-codes minus-keyed items: score = 6 − raw
 * Raw score range: 10–50
 */
export function scoreDimension(
  answers: Record<number, number>,
  dimension: 'O' | 'C' | 'E' | 'A' | 'N'
): { rawScore: number; meanScore: number } {
  const dimItems = SCORED_QUESTIONS.filter(q => q.dimension === dimension);
  let total = 0;
  for (const q of dimItems) {
    let v = answers[q.id] ?? 3;
    if (q.keyed === 'minus') v = 6 - v;
    total += v;
  }
  return { rawScore: total, meanScore: total / dimItems.length };
}

/**
 * Get questions by dimension (scored only)
 */
export function getQuestionsByDimension(
  dimension: 'O' | 'C' | 'E' | 'A' | 'N'
): BigFiveQuestion[] {
  return SCORED_QUESTIONS.filter(q => q.dimension === dimension);
}
