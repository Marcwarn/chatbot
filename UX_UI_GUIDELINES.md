# UX/UI Guidelines for Personality Assessment Landing Page

## Table of Contents
1. [Visual Hierarchy](#visual-hierarchy)
2. [Color Psychology](#color-psychology)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Interactive Elements](#interactive-elements)
6. [User Journey Optimization](#user-journey-optimization)
7. [Conversion Optimization](#conversion-optimization)
8. [Accessibility Standards](#accessibility-standards)
9. [Mobile Optimization](#mobile-optimization)
10. [Performance Guidelines](#performance-guidelines)
11. [Micro-interactions](#micro-interactions)
12. [Trust Signals](#trust-signals)

---

## Visual Hierarchy

### Principle: Guide the Eye Through Clear Priority Levels

#### Hero Section (Highest Priority)
```
Priority Level 1: Brand Identity & Value Proposition
├── Logo/Icon: 96px × 96px, gradient background
├── Headline: 3.5rem (56px), bold, gradient text
├── Subheadline: 1.25rem (20px), medium weight
└── Supporting text: 0.875rem (14px), light weight

Visual Weight Distribution:
- Brand Icon: 20% visual attention
- Headline: 40% visual attention
- Subheadline: 25% visual attention
- Supporting text: 15% visual attention
```

**Implementation:**
```css
.hero-icon {
    width: 96px;
    height: 96px;
    background: linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899);
    border-radius: 1.5rem;
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
}

.hero-headline {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1.1;
    background: linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.hero-subheadline {
    font-size: 1.25rem;
    font-weight: 500;
    color: #6B7280;
    line-height: 1.6;
}
```

#### Assessment Cards (Primary Content)
```
Visual Hierarchy Within Cards:
├── Icon (14px × 14px) + Title (24px, bold) [Top Row]
├── Type Badge (14px, semibold) [Secondary identifier]
├── Description (14px, regular) [Body text]
├── Dimension Showcase [Visual highlight box]
├── Feature Bullets [Supporting details]
└── CTA Button [Action trigger]

Prominence Techniques:
- Border on hover: 2px solid brand color
- Elevation: transform: translateY(-4px)
- Shadow depth: box-shadow: 0 12px 24px rgba(0,0,0,0.12)
```

#### Comparison Section (Supporting Content)
```
Layout Strategy:
- Equal weight cards for Big Five vs DISC
- Background colors differentiate sections
- Border emphasis (2px) for visual containment
- Icon + heading alignment for scannability
```

#### Features Section (Trust Building)
```
Three-Column Grid:
- Icon-first design (draws eye)
- Gradient backgrounds for visual interest
- Centered alignment for balance
- Concise copy (max 2 lines per feature)
```

### Visual Flow Path
```
User Eye Movement Pattern (F-Pattern):
1. Top horizontal: Logo → Brand name
2. Vertical left: Icon → Title → Description
3. Second horizontal: Feature bullets
4. Action: CTA button
5. Repeat for second card
6. Bottom: Comparison → Features → Footer
```

---

## Color Psychology

### Primary Color Palette

#### Brand Colors (Trust & Premium)
```css
:root {
    /* Primary: Indigo - Trust, Intelligence, Professionalism */
    --primary-600: #6366F1;
    --primary-50: #EEF2FF;

    /* Secondary: Purple - Creativity, Premium, Innovation */
    --secondary-600: #8B5CF6;
    --secondary-50: #F5F3FF;

    /* Accent: Pink - Energy, Empathy, Connection */
    --accent-600: #EC4899;
    --accent-50: #FDF2F8;
}
```

**Psychology Behind Choices:**
- **Indigo (#6366F1)**: Conveys trust, stability, and intelligence. Used for Big Five assessment to emphasize scientific validity.
- **Purple (#8B5CF6)**: Suggests creativity and premium quality. Used in gradients for brand distinction.
- **Pink (#EC4899)**: Adds warmth and approachability. Balances the cool tones.

#### Assessment-Specific Colors

**Big Five Palette**
```css
.big-five-theme {
    --bf-primary: #6366F1;      /* Indigo - Trust */
    --bf-secondary: #8B5CF6;    /* Purple - Depth */
    --bf-openness: #8B5CF6;     /* Purple - Creativity */
    --bf-conscientiousness: #F59E0B; /* Amber - Focus */
    --bf-extraversion: #6366F1;  /* Indigo - Social */
    --bf-agreeableness: #10B981; /* Green - Harmony */
    --bf-neuroticism: #EF4444;   /* Red - Emotion */
}
```

**DISC Palette**
```css
.disc-theme {
    --disc-primary: #FF4444;     /* Red - Energy */
    --disc-secondary: #FFD700;   /* Gold - Warmth */
    --disc-dominance: #FF4444;   /* Red - Power */
    --disc-influence: #FFD700;   /* Gold - Enthusiasm */
    --disc-steadiness: #44AA44;  /* Green - Stability */
    --disc-compliance: #4444FF;  /* Blue - Precision */
}
```

#### Functional Colors
```css
.functional-colors {
    /* Success - Positive actions, completion */
    --success-600: #10B981;
    --success-50: #ECFDF5;

    /* Warning - Attention, important info */
    --warning-600: #F59E0B;
    --warning-50: #FFFBEB;

    /* Error - Problems, critical actions */
    --error-600: #EF4444;
    --error-50: #FEF2F2;

    /* Neutral - Text, borders, backgrounds */
    --gray-900: #111827;  /* Headings */
    --gray-700: #374151;  /* Body text */
    --gray-500: #6B7280;  /* Secondary text */
    --gray-200: #E5E7EB;  /* Borders */
    --gray-50: #F9FAFB;   /* Backgrounds */
}
```

### Color Application Guidelines

#### Contrast Ratios (WCAG AA Minimum)
```
Text Contrast Requirements:
- Body text (16px+): 4.5:1 minimum
- Large text (24px+ or 18px+ bold): 3:1 minimum
- Interactive elements: 3:1 minimum

Current Compliance:
✓ Gray-900 on white: 16.1:1
✓ Gray-700 on white: 11.2:1
✓ Primary-600 on white: 7.4:1
✓ Success-600 on white: 4.8:1
✗ Warning-600 on white: 2.9:1 (use darker shade for text)
```

#### Gradient Usage
```css
/* Brand Gradient - Hero, CTAs, Premium Elements */
.gradient-primary {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
}

/* Big Five Gradient */
.gradient-big-five {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
}

/* DISC Gradient */
.gradient-disc {
    background: linear-gradient(135deg, #FF4444 0%, #FFD700 100%);
}

/* Background Gradient - Subtle, calming */
.gradient-background {
    background: linear-gradient(160deg, #EEF2FF 0%, #FFF5F5 40%, #FFFEF0 70%, #F0FFF4 100%);
}
```

#### Color Accessibility
```css
/* Never use color alone to convey information */
/* ✗ Bad: Red border only for errors */
.error-bad {
    border: 2px solid #EF4444;
}

/* ✓ Good: Red border + icon + text for errors */
.error-good {
    border: 2px solid #EF4444;
}
.error-good::before {
    content: "⚠";
    margin-right: 0.5rem;
}
```

---

## Typography

### Font Stack

#### Primary Font Family
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
                 'Helvetica Neue', Arial, sans-serif;
    font-feature-settings: 'kern' 1, 'liga' 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
```

**Rationale:** System fonts provide:
- Instant loading (no font download)
- Native OS appearance (familiar to users)
- Excellent readability across devices
- Perfect Swedish character support (å, ä, ö)

### Type Scale

#### Desktop Scale
```css
/* Display - Hero headlines */
.text-display {
    font-size: 3.5rem;      /* 56px */
    line-height: 1.1;
    font-weight: 900;
    letter-spacing: -0.02em;
}

/* Heading 1 - Page titles */
.text-h1 {
    font-size: 2.5rem;      /* 40px */
    line-height: 1.2;
    font-weight: 800;
    letter-spacing: -0.01em;
}

/* Heading 2 - Section titles */
.text-h2 {
    font-size: 1.5rem;      /* 24px */
    line-height: 1.3;
    font-weight: 700;
}

/* Heading 3 - Card titles */
.text-h3 {
    font-size: 1.25rem;     /* 20px */
    line-height: 1.4;
    font-weight: 600;
}

/* Body Large - Subheadings */
.text-body-lg {
    font-size: 1.125rem;    /* 18px */
    line-height: 1.6;
    font-weight: 500;
}

/* Body - Primary text */
.text-body {
    font-size: 1rem;        /* 16px */
    line-height: 1.6;
    font-weight: 400;
}

/* Body Small - Secondary text */
.text-body-sm {
    font-size: 0.875rem;    /* 14px */
    line-height: 1.5;
    font-weight: 400;
}

/* Caption - Labels, metadata */
.text-caption {
    font-size: 0.75rem;     /* 12px */
    line-height: 1.4;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
```

#### Mobile Scale (Adjusted for smaller screens)
```css
@media (max-width: 768px) {
    .text-display {
        font-size: 2.5rem;  /* 40px */
    }

    .text-h1 {
        font-size: 2rem;    /* 32px */
    }

    .text-h2 {
        font-size: 1.25rem; /* 20px */
    }

    /* Body sizes remain the same for readability */
    .text-body {
        font-size: 1rem;    /* Never below 16px on mobile */
    }
}
```

### Typography Best Practices

#### Line Height for Readability
```css
/* Short lines (headings): 1.1 - 1.3 */
h1, h2, h3 {
    line-height: 1.2;
}

/* Medium lines (body): 1.5 - 1.8 */
p, li, div {
    line-height: 1.6;
}

/* Optimal line length: 50-75 characters */
.content-wrapper {
    max-width: 65ch;  /* characters */
}
```

#### Swedish Character Support
```css
/* All fonts must support: å, ä, ö, Å, Ä, Ö */
/* Test string: "Öppen för Ändring - Påverkan" */

/* System fonts provide excellent support */
/* If using custom fonts, verify unicode coverage:
   U+00C5 (Å), U+00C4 (Ä), U+00D6 (Ö)
   U+00E5 (å), U+00E4 (ä), U+00F6 (ö) */
```

#### Hierarchy Implementation
```html
<!-- Example: Assessment Card -->
<div class="assessment-card">
    <!-- Icon + Title: Highest hierarchy -->
    <h2 class="text-h2 text-gray-900">Big Five</h2>

    <!-- Type badge: Secondary identifier -->
    <span class="text-caption text-indigo-600">Personlighetstest</span>

    <!-- Description: Body text -->
    <p class="text-body-sm text-gray-700">
        Utforska dina grundläggande personlighetsdrag...
    </p>

    <!-- Feature bullets: Supporting details -->
    <ul class="text-body-sm text-gray-600">
        <li>50 validerade frågor</li>
    </ul>

    <!-- CTA: Action emphasis -->
    <button class="text-body font-bold">
        Starta Big Five-test →
    </button>
</div>
```

---

## Spacing & Layout

### Spacing System

#### Base Unit: 4px
```css
:root {
    --space-1: 0.25rem;   /* 4px */
    --space-2: 0.5rem;    /* 8px */
    --space-3: 0.75rem;   /* 12px */
    --space-4: 1rem;      /* 16px */
    --space-5: 1.25rem;   /* 20px */
    --space-6: 1.5rem;    /* 24px */
    --space-8: 2rem;      /* 32px */
    --space-10: 2.5rem;   /* 40px */
    --space-12: 3rem;     /* 48px */
    --space-16: 4rem;     /* 64px */
    --space-20: 5rem;     /* 80px */
    --space-24: 6rem;     /* 96px */
    --space-32: 8rem;     /* 128px */
}
```

### Layout Grid

#### Container Widths
```css
/* Maximum content width for readability */
.container-max {
    max-width: 1200px;
    margin: 0 auto;
}

/* Landing page optimal width */
.landing-container {
    max-width: 1024px;  /* 4-column max width */
    margin: 0 auto;
    padding: 0 1rem;
}

/* Mobile padding */
@media (max-width: 768px) {
    .landing-container {
        padding: 0 1rem;  /* 16px sides */
    }
}

/* Desktop padding */
@media (min-width: 1024px) {
    .landing-container {
        padding: 0 2rem;  /* 32px sides */
    }
}
```

#### Section Spacing
```css
/* Vertical rhythm between sections */
.section {
    margin-bottom: var(--space-20);  /* 80px */
}

@media (min-width: 768px) {
    .section {
        margin-bottom: var(--space-24);  /* 96px */
    }
}

@media (min-width: 1024px) {
    .section {
        margin-bottom: var(--space-32);  /* 128px */
    }
}
```

#### Card Spacing
```css
.card {
    /* Internal padding */
    padding: var(--space-6);  /* 24px */

    /* Spacing between cards */
    margin-bottom: var(--space-6);  /* 24px */

    /* Border radius for friendly appearance */
    border-radius: 24px;
}

/* Card grid */
.card-grid {
    display: grid;
    gap: var(--space-6);  /* 24px */
}

@media (min-width: 768px) {
    .card-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: var(--space-6);  /* 24px */
    }
}
```

### Whitespace Philosophy

#### Generous Whitespace = Reduced Cognitive Load
```css
/* Bad: Cramped spacing */
.cramped {
    padding: 8px;
    margin-bottom: 8px;
}

/* Good: Breathing room */
.spacious {
    padding: 24px;
    margin-bottom: 24px;
}

/* Better: Responsive breathing room */
.optimal {
    padding: clamp(16px, 4vw, 32px);
    margin-bottom: clamp(24px, 5vw, 48px);
}
```

#### Element-Specific Spacing

**Text Blocks**
```css
/* Paragraph spacing */
p + p {
    margin-top: 1rem;  /* 16px between paragraphs */
}

/* List spacing */
li + li {
    margin-top: 0.5rem;  /* 8px between items */
}

/* Section spacing */
section + section {
    margin-top: 5rem;  /* 80px between sections */
}
```

**Component Spacing**
```css
/* Icon + Text alignment */
.icon-text {
    display: flex;
    align-items: center;
    gap: 0.875rem;  /* 14px */
}

/* Button group spacing */
.button-group {
    display: flex;
    gap: 1rem;  /* 16px */
}

/* Feature grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;  /* 32px */
}
```

### Responsive Layout Patterns

#### Mobile-First Grid
```css
/* Start with single column */
.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
    .grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
    }
}
```

#### Flexbox Patterns
```css
/* Center content vertically and horizontally */
.flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Space between elements */
.flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Responsive flex direction */
.flex-responsive {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

@media (min-width: 768px) {
    .flex-responsive {
        flex-direction: row;
        align-items: center;
    }
}
```

---

## Interactive Elements

### Buttons

#### Button Hierarchy
```css
/* Primary CTA - Highest emphasis */
.btn-primary {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white;
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    transition: all 0.2s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.btn-primary:active {
    transform: scale(0.98);
}

/* Secondary Button - Medium emphasis */
.btn-secondary {
    background: white;
    color: #6366F1;
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 600;
    border: 2px solid #6366F1;
    transition: all 0.2s ease;
}

.btn-secondary:hover {
    background: #EEF2FF;
}

/* Ghost Button - Low emphasis */
.btn-ghost {
    background: transparent;
    color: #6B7280;
    padding: 14px 24px;
    border: none;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-ghost:hover {
    color: #6366F1;
    background: #F9FAFB;
}
```

#### Button States
```css
/* Default state defined above */

/* Hover state */
.btn:hover {
    cursor: pointer;
}

/* Focus state (keyboard navigation) */
.btn:focus {
    outline: 3px solid #6366F1;
    outline-offset: 2px;
}

/* Active/Pressed state */
.btn:active {
    transform: scale(0.98);
}

/* Disabled state */
.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

/* Loading state */
.btn.loading {
    position: relative;
    color: transparent;
}

.btn.loading::after {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spinner 0.6s linear infinite;
}

@keyframes spinner {
    to { transform: rotate(360deg); }
}
```

#### Touch-Friendly Sizing
```css
/* Minimum touch target: 44px × 44px (Apple guideline) */
.btn {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 24px;
}

/* Icon buttons */
.btn-icon {
    width: 44px;
    height: 44px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

### Cards

#### Card Hover Effects
```css
.card {
    background: white;
    border-radius: 24px;
    padding: 24px;
    border: 2px solid transparent;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;
}

.card:hover {
    border-color: #6366F1;
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.card:active {
    transform: scale(0.98);
}
```

#### Card Active State (Selected)
```css
.card.selected {
    border-color: #6366F1;
    background: #EEF2FF;
    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
}

.card.selected::before {
    content: "✓";
    position: absolute;
    top: 12px;
    right: 12px;
    width: 24px;
    height: 24px;
    background: #6366F1;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}
```

### Forms

#### Input Fields
```css
.input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.2s ease;
}

/* Focus state */
.input:focus {
    outline: none;
    border-color: #6366F1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Error state */
.input.error {
    border-color: #EF4444;
}

.input.error:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.input.success {
    border-color: #10B981;
}
```

#### Checkboxes & Radio Buttons
```css
/* Custom checkbox */
input[type="checkbox"] {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    accent-color: #6366F1;
    cursor: pointer;
}

/* Checkbox label */
.checkbox-label {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    user-select: none;
}

.checkbox-label:hover {
    color: #6366F1;
}
```

### Links

#### Link Styles
```css
/* Default link */
a {
    color: #6366F1;
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: #8B5CF6;
    text-decoration: underline;
}

a:focus {
    outline: 2px solid #6366F1;
    outline-offset: 2px;
}

/* Subtle link (within body text) */
.link-subtle {
    color: inherit;
    border-bottom: 1px solid currentColor;
}

.link-subtle:hover {
    color: #6366F1;
}
```

---

## User Journey Optimization

### Visitor Flow Map

```
ENTRY POINT: Landing Page
├── First Impression (0-3 seconds)
│   ├── Visual Impact: Brand icon + gradient headline
│   ├── Value Clarity: "Vetenskapliga personlighets- och beteendetester"
│   └── Relevance Check: "Does this solve my need?"
│
├── Exploration (3-30 seconds)
│   ├── Method Comparison: Big Five vs DISC cards
│   ├── Feature Scanning: Icons + bullet points
│   └── Trust Building: Scientific validation, GDPR badges
│
├── Decision (30-90 seconds)
│   ├── Deep Dive: "Vilken ska jag välja?" section
│   ├── Value Assessment: Time commitment, question count
│   └── Risk Evaluation: Privacy, cost, commitment
│
└── Action (90+ seconds)
    ├── CTA Click: "Starta Big Five-test" or "Starta DISC-analys"
    ├── Assessment Start: Consent → Questions
    └── Completion: Results → Coach → (Optional) Purchase
```

### Decision Points & Friction Reduction

#### Decision Point 1: "Does This Solve My Need?"
**Location:** Hero section (above the fold)

**User Questions:**
- What is this?
- Is it for me?
- Can I trust it?

**Optimization:**
```html
<div class="hero">
    <!-- Clear identity -->
    <h1>Persona - Vetenskapliga Personlighetstester</h1>

    <!-- Value proposition -->
    <p>Upptäck din personlighet och beteendestil med validerade assessments</p>

    <!-- Trust signal -->
    <div class="trust-badge">
        <span>10,000+ nöjda användare</span>
        <span>⭐⭐⭐⭐⭐ 4.8/5</span>
    </div>

    <!-- Low-friction CTA -->
    <button>Kom Igång Gratis</button>
</div>
```

#### Decision Point 2: "Which Assessment Fits Me?"
**Location:** Assessment cards

**Friction:** Too many options, unclear differences

**Solution:**
```html
<!-- Add "Most Popular" badge -->
<div class="card big-five">
    <span class="badge-popular">Mest Populär</span>
    <h2>Big Five</h2>
    <!-- ... -->
</div>

<!-- Add clear use case differentiation -->
<div class="comparison">
    <div class="use-case">
        <h3>Välj Big Five om du vill:</h3>
        <ul>
            <li>✓ Förstå din grundläggande personlighet</li>
            <li>✓ Utvecklas personligt</li>
        </ul>
    </div>
    <div class="use-case">
        <h3>Välj DISC om du vill:</h3>
        <ul>
            <li>✓ Förbättra arbetsprestation</li>
            <li>✓ Utveckla ledarskap</li>
        </ul>
    </div>
</div>
```

#### Decision Point 3: "Is This Worth It?"
**Location:** Below cards, pricing (if added)

**Friction:** Unclear value, price concerns

**Solution:**
```html
<!-- Emphasize free trial -->
<div class="value-prop">
    <h3>Börja Gratis</h3>
    <ul>
        <li>✓ Fullständigt assessment (ingen betalning krävs)</li>
        <li>✓ Detaljerad rapport</li>
        <li>✓ AI-driven coach (3 frågor gratis)</li>
        <li>✓ Ingen kreditkort krävs</li>
    </ul>
</div>

<!-- Show value comparison -->
<div class="value-comparison">
    <div>Traditionell coaching: 1,500 kr/session</div>
    <div>Persona: Gratis start + 49 kr för obegränsad coach</div>
</div>
```

#### Decision Point 4: "Can I Trust This?"
**Location:** Features section, footer

**Friction:** Privacy concerns, data security

**Solution:**
```html
<div class="trust-signals">
    <!-- Scientific validation -->
    <div class="trust-item">
        <img src="shield-check.svg" alt="Vetenskapligt validerat">
        <h4>Vetenskapligt Validerat</h4>
        <p>Baserat på IPIP-50 och officiell DISC-modell</p>
    </div>

    <!-- GDPR compliance -->
    <div class="trust-item">
        <img src="lock.svg" alt="GDPR-säkert">
        <h4>GDPR-Säkert</h4>
        <p>Dina data är krypterade och kan raderas när som helst</p>
    </div>

    <!-- AI transparency -->
    <div class="trust-item">
        <img src="sparkles.svg" alt="AI-driven">
        <h4>AI-Driven Analys</h4>
        <p>Claude 3.5 Sonnet för personliga insikter</p>
    </div>
</div>

<!-- Privacy policy link -->
<footer>
    <a href="/privacy">Integritetspolicy (GDPR)</a>
    <a href="/security">Datasäkerhet</a>
</footer>
```

#### Decision Point 5: "How Do I Start?"
**Location:** CTA buttons

**Friction:** Complex onboarding, too many steps

**Solution:**
```html
<!-- Clear, simple CTA -->
<button class="btn-primary">
    Starta Big Five-test →
    <span class="btn-subtitle">Gratis, 10 minuter, inga kort krävs</span>
</button>

<!-- One-click start (no signup required initially) -->
<!-- Collect email only after showing value (after assessment) -->
```

### Scroll Triggers & Progressive Disclosure

#### Sticky CTA (After Hero Scroll)
```javascript
// Show floating CTA when user scrolls past hero
const hero = document.querySelector('.hero');
const floatingCta = document.querySelector('.floating-cta');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            floatingCta.classList.add('visible');
        } else {
            floatingCta.classList.remove('visible');
        }
    });
}, { threshold: 0.1 });

observer.observe(hero);
```

```css
.floating-cta {
    position: fixed;
    bottom: 20px;
    right: 20px;
    opacity: 0;
    transform: translateY(100px);
    transition: all 0.3s ease;
    z-index: 1000;
}

.floating-cta.visible {
    opacity: 1;
    transform: translateY(0);
}
```

#### Fade-In Animations
```javascript
// Fade in sections as they enter viewport
const sections = document.querySelectorAll('.fade-in-section');

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
        }
    });
}, { threshold: 0.1 });

sections.forEach(section => sectionObserver.observe(section));
```

```css
.fade-in-section {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}

.fade-in-section.revealed {
    opacity: 1;
    transform: translateY(0);
}
```

---

## Conversion Optimization

### Above the Fold (Critical First 3 Seconds)

#### The 3-Second Rule
Users decide within 3 seconds whether to stay or leave. Above the fold must answer:
1. **What is this?** → Clear headline
2. **Why should I care?** → Value proposition
3. **What do I do?** → Clear CTA
4. **Can I trust this?** → Trust signal

#### Optimal Above-the-Fold Structure
```html
<div class="hero-fold">
    <!-- 1. WHAT IS THIS? -->
    <div class="brand-identity">
        <img src="icon.svg" alt="Persona">
        <h1>Persona - Vetenskapliga Personlighetstester</h1>
    </div>

    <!-- 2. WHY CARE? -->
    <p class="value-proposition">
        Upptäck din personlighet och beteendestil med AI-driven analys.
        Vetenskapligt validerade assessments för självinsikt och utveckling.
    </p>

    <!-- 3. WHAT TO DO? -->
    <div class="cta-primary">
        <button class="btn-large btn-primary">
            Kom Igång Gratis
        </button>
        <p class="cta-subtitle">10 minuter · Inga kort krävs · GDPR-säkert</p>
    </div>

    <!-- 4. CAN I TRUST? -->
    <div class="trust-inline">
        <div class="trust-stat">
            <strong>10,000+</strong> användare
        </div>
        <div class="trust-rating">
            ⭐⭐⭐⭐⭐ <strong>4.8/5</strong>
        </div>
        <div class="trust-badge">
            <img src="gdpr-badge.svg" alt="GDPR">
        </div>
    </div>
</div>
```

### CTA Optimization

#### Primary CTA Best Practices
```css
/* Size: Large and prominent */
.cta-primary {
    min-height: 56px;
    padding: 16px 32px;
    font-size: 1.125rem;
    font-weight: 700;
}

/* Color: High contrast */
.cta-primary {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Position: Prominent, easy to find */
.cta-primary {
    display: block;
    margin: 2rem auto;
    max-width: 320px;
}

/* Copy: Action-oriented, benefit-focused */
/* ✗ "Submit" | ✓ "Kom Igång Gratis" */
/* ✗ "Click Here" | ✓ "Starta Big Five-test →" */
```

#### CTA Button Copy Guidelines
```
Action Verbs (Start with these):
- Starta (Start)
- Kom igång (Get started)
- Upptäck (Discover)
- Ta testet (Take the test)
- Börja (Begin)

Value Addition (Add benefit):
- Starta Gratis
- Kom Igång Idag
- Upptäck Din Personlighet
- Ta Testet (10 min)

Avoid:
- Generic: "Klicka här", "Submit", "OK"
- Passive: "Learn more" (unless secondary CTA)
- Jargon: "Initiate assessment protocol"
```

#### Multiple CTAs (Hierarchy)
```html
<!-- Primary CTA: Highest emphasis -->
<button class="btn-primary btn-large">
    Starta Big Five-test Gratis →
</button>

<!-- Secondary CTA: Medium emphasis -->
<button class="btn-secondary">
    Se Exempel på Rapport
</button>

<!-- Tertiary CTA: Low emphasis (link style) -->
<a href="/learn-more" class="link">
    Läs mer om vetenskapen bakom Big Five
</a>
```

### Form Optimization

#### Minimal Fields Strategy
```html
<!-- ✗ Bad: Too many fields upfront -->
<form class="signup-bad">
    <input type="text" placeholder="Förnamn" required>
    <input type="text" placeholder="Efternamn" required>
    <input type="email" placeholder="E-post" required>
    <input type="password" placeholder="Lösenord" required>
    <input type="password" placeholder="Bekräfta lösenord" required>
    <input type="tel" placeholder="Telefon">
    <select>Kön</select>
    <input type="date" placeholder="Födelsedatum">
    <button>Registrera</button>
</form>

<!-- ✓ Good: Start assessment immediately, collect email later -->
<div class="signup-good">
    <!-- Step 1: Start immediately (no signup) -->
    <button class="btn-primary">Starta Testet Nu</button>
    <p class="note">Inget konto krävs för att börja</p>

    <!-- Step 2: After assessment, before results -->
    <form class="email-capture">
        <h3>Se Dina Resultat</h3>
        <p>Ange din e-post för att få din fullständiga rapport:</p>
        <input type="email" placeholder="din@email.com" required>
        <button>Visa Mina Resultat →</button>
    </form>
</div>
```

#### Inline Validation
```html
<input
    type="email"
    id="email"
    class="input"
    aria-describedby="email-error"
    aria-invalid="false"
>
<span id="email-error" class="error-message hidden">
    Ange en giltig e-postadress
</span>

<script>
const emailInput = document.getElementById('email');
const errorMessage = document.getElementById('email-error');

emailInput.addEventListener('blur', () => {
    const isValid = emailInput.validity.valid;

    if (!isValid) {
        emailInput.classList.add('error');
        emailInput.setAttribute('aria-invalid', 'true');
        errorMessage.classList.remove('hidden');
    } else {
        emailInput.classList.remove('error');
        emailInput.setAttribute('aria-invalid', 'false');
        errorMessage.classList.add('hidden');
    }
});
</script>
```

#### Clear Error Messages
```html
<!-- ✗ Bad: Technical error -->
<span class="error">Invalid input</span>

<!-- ✓ Good: Helpful error -->
<span class="error">
    E-postadressen måste innehålla @ och en domän (t.ex. exempel@email.com)
</span>
```

#### Success Feedback
```html
<!-- Visual feedback on successful form submission -->
<div class="success-message">
    <div class="success-icon">✓</div>
    <h3>Tack! Din e-post är bekräftad.</h3>
    <p>Dina resultat visas om ett ögonblick...</p>
</div>

<style>
.success-message {
    background: #ECFDF5;
    border: 2px solid #10B981;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    animation: slideInUp 0.4s ease;
}

.success-icon {
    width: 48px;
    height: 48px;
    background: #10B981;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin: 0 auto 16px;
}
</style>
```

### Social Proof

#### Types of Social Proof
```html
<!-- 1. User Count -->
<div class="social-proof">
    <strong>10,000+</strong> personer har upptäckt sin personlighet med Persona
</div>

<!-- 2. Testimonials -->
<blockquote class="testimonial">
    <p>"Fantastisk insikt i min personlighet. Hjälpte mig förstå mina styrkor och utvecklingsområden."</p>
    <cite>
        <img src="avatar.jpg" alt="">
        <div>
            <strong>Anna Andersson</strong>
            <span>HR-chef, Stockholm</span>
        </div>
    </cite>
</blockquote>

<!-- 3. Ratings -->
<div class="rating">
    <div class="stars">⭐⭐⭐⭐⭐</div>
    <strong>4.8/5</strong>
    <span>(2,341 recensioner)</span>
</div>

<!-- 4. Trust Badges -->
<div class="badges">
    <img src="gdpr-compliant.svg" alt="GDPR Compliant">
    <img src="ssl-secure.svg" alt="SSL Encrypted">
    <img src="science-backed.svg" alt="Vetenskapligt Validerat">
</div>

<!-- 5. Live Activity -->
<div class="live-activity">
    <span class="pulse"></span>
    <span>Johan från Göteborg slutförde Big Five-testet för 2 minuter sedan</span>
</div>
```

### Urgency & Scarcity (Use Sparingly & Honestly)

```html
<!-- ✗ Bad: Fake urgency -->
<div class="urgency-fake">
    ⏰ Endast 3 platser kvar idag! (False scarcity)
</div>

<!-- ✓ Good: Honest time-sensitive offer -->
<div class="urgency-honest">
    🎁 Introducerbjudande: Gratis AI-coach till och med 31 mars
</div>

<!-- ✓ Good: Create value, not pressure -->
<div class="value-reminder">
    💡 Ju tidigare du börjar, desto snabbare får du insikter för din utveckling
</div>
```

---

## Accessibility Standards

### WCAG 2.1 Level AA Compliance

#### Perceivable

**1.1 Text Alternatives**
```html
<!-- All images must have alt text -->
<img src="big-five-icon.svg" alt="Big Five personality assessment icon">

<!-- Decorative images: empty alt -->
<img src="decorative-pattern.svg" alt="">

<!-- Complex images: detailed description -->
<img src="results-chart.png" alt="Bar chart showing Big Five scores: Openness 75%, Conscientiousness 65%, Extraversion 80%, Agreeableness 70%, Neuroticism 40%">
```

**1.3 Adaptable**
```html
<!-- Use semantic HTML -->
<header>
    <nav aria-label="Main navigation">
        <ul>
            <li><a href="/">Hem</a></li>
        </ul>
    </nav>
</header>

<main>
    <section aria-labelledby="hero-heading">
        <h1 id="hero-heading">Persona</h1>
    </section>
</main>

<footer>
    <p>© 2026 Persona</p>
</footer>
```

**1.4 Distinguishable**
```css
/* Color contrast (WCAG AA) */
/* Text: 4.5:1 minimum */
/* Large text (24px+ or 18px+ bold): 3:1 minimum */

/* ✓ Good contrast examples */
.text-primary {
    color: #111827;  /* 16.1:1 on white */
}

.text-secondary {
    color: #374151;  /* 11.2:1 on white */
}

.link {
    color: #6366F1;  /* 7.4:1 on white */
}

/* ✗ Bad contrast */
.text-bad {
    color: #CBD5E0;  /* 2.1:1 - fails WCAG */
}

/* Never convey information by color alone */
/* ✗ Bad */
<span style="color: red;">Error</span>

/* ✓ Good */
<span class="error">
    <span class="icon" aria-hidden="true">⚠</span>
    Error: Invalid email
</span>
```

#### Operable

**2.1 Keyboard Accessible**
```html
<!-- All interactive elements must be keyboard accessible -->
<!-- Native elements are automatically accessible -->
<button>Click me</button>
<a href="/page">Link</a>

<!-- Custom elements need tabindex and keyboard handlers -->
<div
    role="button"
    tabindex="0"
    onclick="handleClick()"
    onkeydown="handleKeyDown(event)"
>
    Custom button
</div>

<script>
function handleKeyDown(event) {
    // Activate on Enter or Space
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handleClick();
    }
}
</script>
```

**2.2 Enough Time**
```javascript
// No time limits on reading content
// If needed, provide options to extend time

// ✓ Good: Pauseable animations
<button onclick="toggleAnimation()">
    Pause Animation
</button>
```

**2.3 Seizures**
```css
/* No flashing content more than 3 times per second */
/* Avoid rapid color changes */

/* ✗ Bad */
@keyframes flash {
    0%, 100% { background: white; }
    50% { background: red; }
}

/* ✓ Good: Gentle fade */
@keyframes gentle-fade {
    0% { opacity: 0.8; }
    50% { opacity: 1; }
    100% { opacity: 0.8; }
}
```

**2.4 Navigable**
```html
<!-- Skip to main content link -->
<a href="#main-content" class="skip-link">
    Hoppa till huvudinnehåll
</a>

<style>
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #6366F1;
    color: white;
    padding: 8px 16px;
    text-decoration: none;
    z-index: 100;
}

.skip-link:focus {
    top: 0;
}
</style>

<!-- Clear page titles -->
<title>Big Five Personlighetstest - Persona</title>

<!-- Descriptive headings -->
<h1>Persona - Vetenskapliga Personlighetstester</h1>
<h2>Välj Din Assessment</h2>
<h3>Big Five Personlighetstest</h3>

<!-- Logical heading hierarchy (don't skip levels) -->
<!-- ✓ h1 → h2 → h3 -->
<!-- ✗ h1 → h3 (skipped h2) -->

<!-- Focus indicators -->
<style>
*:focus {
    outline: 3px solid #6366F1;
    outline-offset: 2px;
}

/* Never remove focus outline without replacement */
/* ✗ Bad */
*:focus {
    outline: none;
}
</style>
```

#### Understandable

**3.1 Readable**
```html
<!-- Language attribute -->
<html lang="sv">

<!-- Language changes -->
<p>Baserat på <span lang="en">Big Five</span> modellen</p>

<!-- Plain language -->
<!-- ✗ Complex: "Utilize the psychometric instrument to ascertain personality dimensions" -->
<!-- ✓ Simple: "Ta testet för att upptäcka din personlighet" -->
```

**3.2 Predictable**
```html
<!-- Consistent navigation -->
<nav aria-label="Main navigation">
    <ul>
        <li><a href="/">Hem</a></li>
        <li><a href="/assessments">Tester</a></li>
        <li><a href="/about">Om Oss</a></li>
    </ul>
</nav>

<!-- No automatic context changes -->
<!-- ✗ Bad: Select that auto-submits on change -->
<select onchange="this.form.submit()">

<!-- ✓ Good: Explicit submit button -->
<select id="language">
    <option>Svenska</option>
    <option>English</option>
</select>
<button type="submit">Byt språk</button>
```

**3.3 Input Assistance**
```html
<!-- Clear labels -->
<label for="email">E-postadress</label>
<input
    type="email"
    id="email"
    name="email"
    autocomplete="email"
    aria-required="true"
    aria-describedby="email-hint email-error"
>
<span id="email-hint" class="hint">
    Vi skickar din rapport till denna adress
</span>
<span id="email-error" class="error hidden">
    Ange en giltig e-postadress
</span>

<!-- Error identification -->
<form onsubmit="return validateForm()">
    <!-- If error, show summary -->
    <div class="error-summary" role="alert" aria-live="assertive">
        <h3>Det finns 2 fel i formuläret:</h3>
        <ul>
            <li><a href="#email">E-postadress saknas</a></li>
            <li><a href="#consent">Du måste godkänna villkoren</a></li>
        </ul>
    </div>
</form>

<!-- Error suggestions -->
<span class="error">
    Ogiltigt format. Använd: förnamn.efternamn@företag.se
</span>
```

#### Robust

**4.1 Compatible**
```html
<!-- Valid HTML -->
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persona</title>
</head>
<body>
    <!-- Unique IDs -->
    <div id="main-content">
        <!-- No duplicate IDs in the page -->
    </div>
</body>
</html>

<!-- ARIA roles and attributes -->
<button
    aria-label="Stäng modal"
    aria-expanded="true"
    aria-controls="modal-content"
>
    <span aria-hidden="true">×</span>
</button>

<div
    id="modal-content"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
>
    <h2 id="modal-title">Välkommen</h2>
</div>
```

### Screen Reader Optimization

```html
<!-- Visually hidden but screen reader accessible -->
<style>
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
</style>

<button>
    <span class="sr-only">Starta Big Five personlighetstest</span>
    <span aria-hidden="true">→</span>
</button>

<!-- ARIA live regions for dynamic content -->
<div aria-live="polite" aria-atomic="true">
    <p>Laddning: 25%</p>
</div>

<!-- ARIA labels for context -->
<nav aria-label="Main navigation"></nav>
<nav aria-label="Footer navigation"></nav>

<!-- Icon buttons -->
<button aria-label="Stäng">
    <svg aria-hidden="true"><!-- X icon --></svg>
</button>
```

---

## Mobile Optimization

### Mobile-First Approach

#### Viewport Configuration
```html
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"
>

<!-- Don't disable zoom -->
<!-- ✗ Bad: maximum-scale=1.0, user-scalable=no -->
<!-- ✓ Good: Allow zoom for accessibility -->
```

#### Touch Target Sizing
```css
/* Minimum: 44px × 44px (Apple guideline) */
/* Recommended: 48px × 48px (Material Design) */

.btn, .link-touch {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 24px;
}

/* Spacing between touch targets */
.btn + .btn {
    margin-top: 12px;  /* At least 8px gap */
}
```

#### Typography for Mobile
```css
/* Never use font-size below 16px on inputs */
/* iOS zooms page if input font-size < 16px */
input, select, textarea {
    font-size: 16px;  /* Minimum to prevent zoom */
}

/* Body text: 16px minimum for readability */
body {
    font-size: 16px;
    line-height: 1.6;
}

/* Headings: Scale down on mobile */
h1 {
    font-size: clamp(2rem, 5vw, 3.5rem);
}
```

### Responsive Layout

#### Breakpoints
```css
/* Mobile-first breakpoints */
:root {
    --breakpoint-sm: 640px;   /* Small tablets */
    --breakpoint-md: 768px;   /* Tablets */
    --breakpoint-lg: 1024px;  /* Desktops */
    --breakpoint-xl: 1280px;  /* Large desktops */
}

/* Mobile-first media queries */
/* Base styles are for mobile */
.container {
    padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
    .container {
        padding: 2rem;
    }
}

/* Desktop and up */
@media (min-width: 1024px) {
    .container {
        padding: 3rem;
    }
}
```

#### Responsive Grid
```css
/* Single column on mobile */
.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}

/* 2 columns on tablet */
@media (min-width: 768px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* 3 columns on desktop */
@media (min-width: 1024px) {
    .grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
    }
}
```

#### Stack on Mobile
```css
/* Flex row on desktop, column on mobile */
.flex-responsive {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

@media (min-width: 768px) {
    .flex-responsive {
        flex-direction: row;
        align-items: center;
    }
}
```

### Mobile Interactions

#### Touch-Friendly Buttons
```css
/* Larger padding for easier tapping */
.btn-mobile {
    padding: 16px 24px;
    font-size: 1.125rem;
}

/* Full-width buttons on mobile */
@media (max-width: 768px) {
    .btn-primary {
        width: 100%;
        display: block;
    }
}

/* Remove hover effects on touch devices */
@media (hover: none) {
    .btn:hover {
        transform: none;
    }

    .btn:active {
        transform: scale(0.98);
    }
}
```

#### Prevent Tap Highlight Flash
```css
/* Remove default tap highlight */
* {
    -webkit-tap-highlight-color: transparent;
}

/* Add custom active state */
.btn:active {
    background-color: darken(currentColor, 10%);
}
```

#### Swipe Gestures (If Applicable)
```javascript
// Basic swipe detection
let touchStartX = 0;
let touchEndX = 0;

element.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

element.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
        // Swipe left
    }
    if (touchEndX > touchStartX + 50) {
        // Swipe right
    }
}
```

### Mobile Performance

#### Optimize Images
```html
<!-- Responsive images -->
<img
    src="image-800.jpg"
    srcset="
        image-400.jpg 400w,
        image-800.jpg 800w,
        image-1200.jpg 1200w
    "
    sizes="
        (max-width: 768px) 100vw,
        (max-width: 1024px) 50vw,
        33vw
    "
    alt="Big Five assessment"
    loading="lazy"
>

<!-- Modern formats with fallback -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <source srcset="image.jpg" type="image/jpeg">
    <img src="image.jpg" alt="Fallback">
</picture>
```

#### Reduce JavaScript
```html
<!-- Defer non-critical JavaScript -->
<script defer src="analytics.js"></script>

<!-- Async for independent scripts -->
<script async src="chat-widget.js"></script>

<!-- Critical CSS inline, rest async -->
<style>
    /* Critical above-the-fold styles */
    body { margin: 0; font-family: system-ui; }
</style>
<link rel="stylesheet" href="styles.css" media="print" onload="this.media='all'">
```

---

## Performance Guidelines

### Core Web Vitals

#### Largest Contentful Paint (LCP) - Target: < 2.5s
```html
<!-- Optimize hero image -->
<link rel="preload" as="image" href="hero-image.jpg">

<img
    src="hero-image.jpg"
    alt="Persona hero"
    fetchpriority="high"
    width="1200"
    height="600"
>

<!-- Inline critical CSS -->
<style>
    /* Critical above-the-fold styles */
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

#### First Input Delay (FID) - Target: < 100ms
```javascript
// Minimize JavaScript execution time
// Break up long tasks

// ✗ Bad: Long blocking task
function processData() {
    for (let i = 0; i < 1000000; i++) {
        // Heavy processing
    }
}

// ✓ Good: Break into chunks
async function processDataInChunks() {
    for (let i = 0; i < 1000; i++) {
        await processChunk(i);
        // Yield to browser
        await new Promise(resolve => setTimeout(resolve, 0));
    }
}
```

#### Cumulative Layout Shift (CLS) - Target: < 0.1
```html
<!-- Always specify image dimensions -->
<img
    src="image.jpg"
    alt="Assessment"
    width="800"
    height="600"
>

<!-- Reserve space for dynamic content -->
<div style="min-height: 400px;">
    <!-- Content loads here -->
</div>

<!-- Use CSS aspect ratio for responsive images -->
<style>
.img-wrapper {
    aspect-ratio: 16 / 9;
    overflow: hidden;
}
</style>
```

### Resource Optimization

#### Minimize HTTP Requests
```html
<!-- Combine CSS files -->
<!-- ✗ Bad: Multiple CSS files -->
<link rel="stylesheet" href="reset.css">
<link rel="stylesheet" href="layout.css">
<link rel="stylesheet" href="components.css">

<!-- ✓ Good: Single combined file -->
<link rel="stylesheet" href="styles.min.css">

<!-- Use CSS instead of images when possible -->
<style>
/* CSS gradient instead of gradient image */
.gradient {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
}
</style>
```

#### Compress Assets
```bash
# Gzip compression on server
# Enable in nginx:
gzip on;
gzip_types text/css application/javascript image/svg+xml;
gzip_min_length 1000;

# Brotli compression (better than gzip)
brotli on;
brotli_types text/css application/javascript;
```

#### Lazy Load Images
```html
<!-- Native lazy loading -->
<img src="image.jpg" loading="lazy" alt="Assessment">

<!-- Intersection Observer for more control -->
<script>
const images = document.querySelectorAll('img[data-src]');

const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));
</script>
```

### Caching Strategy
```html
<!-- Service Worker for offline caching -->
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
}
</script>

<!-- Service Worker (sw.js) -->
<script>
const CACHE_NAME = 'persona-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/styles.css',
    '/script.js',
    '/logo.svg'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
</script>
```

---

## Micro-interactions

### Button Press Feedback
```css
.btn {
    transition: transform 0.1s ease, box-shadow 0.2s ease;
}

.btn:active {
    transform: scale(0.98);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Add subtle animation */
@keyframes press {
    0% { transform: scale(1); }
    50% { transform: scale(0.98); }
    100% { transform: scale(1); }
}

.btn.clicked {
    animation: press 0.2s ease;
}
```

### Card Hover Effect
```css
.card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

/* Smooth border color transition */
.card {
    border: 2px solid transparent;
    transition: border-color 0.3s ease;
}

.card:hover {
    border-color: #6366F1;
}
```

### Scroll Reveal Animations
```javascript
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
        }
    });
}, observerOptions);

document.querySelectorAll('.reveal').forEach(el => {
    observer.observe(el);
});
```

```css
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}

.reveal.revealed {
    opacity: 1;
    transform: translateY(0);
}

/* Stagger animation for multiple elements */
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.2s; }
.reveal:nth-child(3) { transition-delay: 0.3s; }
```

### Loading States
```html
<button class="btn btn-primary" id="submit-btn">
    <span class="btn-text">Skicka</span>
    <span class="btn-loader hidden">
        <svg class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2" />
        </svg>
    </span>
</button>

<style>
.spinner {
    width: 20px;
    height: 20px;
    animation: spin 0.8s linear infinite;
}

.spinner circle {
    fill: none;
    stroke: currentColor;
    stroke-dasharray: 60;
    stroke-dashoffset: 0;
    animation: spin-circle 1.4s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes spin-circle {
    0% { stroke-dashoffset: 60; }
    50% { stroke-dashoffset: 15; }
    100% { stroke-dashoffset: 60; }
}
</style>

<script>
document.getElementById('submit-btn').addEventListener('click', function() {
    this.classList.add('loading');
    this.querySelector('.btn-text').classList.add('hidden');
    this.querySelector('.btn-loader').classList.remove('hidden');
    this.disabled = true;

    // After API call completes:
    // this.classList.remove('loading');
    // this.querySelector('.btn-text').classList.remove('hidden');
    // this.querySelector('.btn-loader').classList.add('hidden');
    // this.disabled = false;
});
</script>
```

### Success Animations
```css
@keyframes success-checkmark {
    0% {
        stroke-dashoffset: 50;
    }
    100% {
        stroke-dashoffset: 0;
    }
}

.checkmark {
    stroke-dasharray: 50;
    animation: success-checkmark 0.6s ease forwards;
}
```

---

## Trust Signals

### Social Proof Elements

#### User Statistics
```html
<div class="stat-grid">
    <div class="stat">
        <div class="stat-number">10,000+</div>
        <div class="stat-label">Nöjda användare</div>
    </div>
    <div class="stat">
        <div class="stat-number">98%</div>
        <div class="stat-label">Rekommenderar oss</div>
    </div>
    <div class="stat">
        <div class="stat-number">4.8/5</div>
        <div class="stat-label">Genomsnittligt betyg</div>
    </div>
</div>

<style>
.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 2rem;
    text-align: center;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    font-size: 0.875rem;
    color: #6B7280;
    margin-top: 0.5rem;
}
</style>
```

#### Testimonials
```html
<div class="testimonial-carousel">
    <blockquote class="testimonial">
        <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
        <p class="testimonial-text">
            "Fantastisk insikt i min personlighet. Hjälpte mig verkligen
            förstå mina styrkor och utvecklingsområden. AI-coachen var
            som att prata med en riktig psykolog!"
        </p>
        <cite class="testimonial-author">
            <img src="avatar-anna.jpg" alt="" class="testimonial-avatar">
            <div>
                <strong>Anna Svensson</strong>
                <span>HR-chef, Stockholm</span>
            </div>
        </cite>
    </blockquote>
</div>

<style>
.testimonial {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.testimonial-stars {
    color: #F59E0B;
    margin-bottom: 1rem;
}

.testimonial-text {
    font-size: 1.125rem;
    line-height: 1.6;
    color: #374151;
    margin-bottom: 1.5rem;
}

.testimonial-author {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-style: normal;
}

.testimonial-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
}
</style>
```

#### Trust Badges
```html
<div class="trust-badges">
    <div class="badge">
        <img src="gdpr-badge.svg" alt="GDPR Compliant">
        <span>GDPR-Säkert</span>
    </div>
    <div class="badge">
        <img src="ssl-badge.svg" alt="SSL Encrypted">
        <span>SSL-Krypterat</span>
    </div>
    <div class="badge">
        <img src="science-badge.svg" alt="Science Based">
        <span>Vetenskapligt</span>
    </div>
</div>

<style>
.trust-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    justify-content: center;
    margin: 2rem 0;
}

.badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: white;
    border-radius: 999px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.badge img {
    width: 24px;
    height: 24px;
}

.badge span {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
}
</style>
```

### Security Indicators

```html
<!-- SSL indicator -->
<div class="security-notice">
    <svg class="lock-icon" viewBox="0 0 24 24">
        <path d="M12 2C9.243 2 7 4.243 7 7v3H6c-1.103 0-2 .897-2 2v8c0 1.103.897 2 2 2h12c1.103 0 2-.897 2-2v-8c0-1.103-.897-2-2-2h-1V7c0-2.757-2.243-5-5-5zm0 2c1.654 0 3 1.346 3 3v3H9V7c0-1.654 1.346-3 3-3z"/>
    </svg>
    <span>Säker anslutning</span>
</div>

<!-- Privacy assurance -->
<div class="privacy-assurance">
    <h4>Din Integritet är Vår Prioritet</h4>
    <ul>
        <li>✓ Dina svar är krypterade</li>
        <li>✓ Vi säljer aldrig din data</li>
        <li>✓ Du kan radera allt när som helst</li>
        <li>✓ GDPR-compliant lagring</li>
    </ul>
    <a href="/privacy">Läs vår integritetspolicy</a>
</div>
```

### Scientific Validation

```html
<div class="scientific-validation">
    <h3>Vetenskapligt Validerade Assessments</h3>
    <div class="validation-grid">
        <div class="validation-item">
            <img src="ipip-logo.svg" alt="IPIP">
            <h4>IPIP-50</h4>
            <p>Big Five baseras på International Personality Item Pool,
               validerat i över 50 länder</p>
        </div>
        <div class="validation-item">
            <img src="disc-logo.svg" alt="DISC">
            <h4>DISC-modellen</h4>
            <p>Använd av Fortune 500-företag i över 40 år</p>
        </div>
        <div class="validation-item">
            <img src="ai-logo.svg" alt="AI">
            <h4>Claude 3.5 Sonnet</h4>
            <p>State-of-the-art AI för djup personlighetsanalys</p>
        </div>
    </div>
</div>
```

---

## Implementation Checklist

### Pre-Launch Checklist

#### Visual Design
- [ ] Consistent color palette across all pages
- [ ] Typography hierarchy is clear
- [ ] All Swedish characters (å, ä, ö) render correctly
- [ ] Gradient backgrounds load smoothly
- [ ] Icons are consistent size and style

#### Accessibility
- [ ] All images have alt text
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible
- [ ] Skip to main content link present
- [ ] ARIA labels on custom components
- [ ] Screen reader tested

#### Mobile
- [ ] Responsive on 320px width (iPhone SE)
- [ ] Touch targets minimum 44px
- [ ] No horizontal scroll on mobile
- [ ] Text is readable without zoom (16px minimum)
- [ ] Buttons are full-width on mobile
- [ ] Forms are easy to fill on mobile

#### Performance
- [ ] Largest Contentful Paint < 2.5s
- [ ] First Input Delay < 100ms
- [ ] Cumulative Layout Shift < 0.1
- [ ] Images are optimized and lazy-loaded
- [ ] CSS and JS are minified
- [ ] Gzip/Brotli compression enabled

#### Conversion
- [ ] CTA buttons are prominent and clear
- [ ] Value proposition is above the fold
- [ ] Trust signals are visible
- [ ] Forms have minimal fields
- [ ] Error messages are helpful
- [ ] Success states are clear

#### Trust
- [ ] GDPR compliance mentioned
- [ ] Privacy policy linked
- [ ] Security badges displayed
- [ ] Testimonials (if applicable)
- [ ] Scientific validation explained

---

## Conclusion

These UX/UI guidelines provide a comprehensive foundation for creating a high-converting, accessible, and performant landing page for Persona personality assessments.

**Key Principles:**
1. **User-Centered Design**: Every decision prioritizes user needs
2. **Accessibility First**: WCAG 2.1 AA compliance is non-negotiable
3. **Mobile-First**: Optimize for smallest screens first
4. **Performance Matters**: Fast loading = better conversions
5. **Trust Building**: Transparency and validation reduce friction
6. **Continuous Improvement**: Test, measure, iterate

**Next Steps:**
1. Implement these guidelines in landing page
2. Conduct user testing
3. Measure conversion rates
4. A/B test variations
5. Iterate based on data

For questions or clarifications on any guideline, refer to the specific section above or consult with the UX/UI specialist.
