# Visual Assets Specification
## Landing Page Design System

**Version:** 1.0
**Last Updated:** March 7, 2026
**Purpose:** Define visual standards for the personality assessment landing page

---

## 1. Hero Image Requirements

### Primary Hero Image

**Purpose:** Establish trust, show human element, inspire self-discovery

**Specifications:**
- **Dimensions:** 1920×1080px (16:9 aspect ratio)
- **Format:** WebP with JPEG fallback
- **File Size:** < 150KB (optimized)
- **Retina Version:** 3840×2160px @2x (< 300KB)
- **Color Palette:** Blues (#667eea), Purples (#764ba2), warm accents
- **Mood:** Inspiring, hopeful, professional, warm
- **Style:** Modern, clean, illustrative (not photographic)

**Subject Options:**

1. **Abstract Personality Visualization** (Recommended)
   - Network of interconnected nodes representing personality traits
   - Glowing connections showing relationships between traits
   - Gradient colors from blue to purple
   - Subtle animation potential (for video/animated version)

2. **Person with Insight Moment**
   - Individual experiencing "aha!" moment
   - Light bulb or glowing aura around head
   - Diverse representation (rotate hero images)
   - Natural, confident posture
   - Modern, minimal illustration style

3. **Brain/Mind Representation**
   - Stylized brain with personality dimensions highlighted
   - Five sections for Big Five traits
   - Clean, scientific but accessible design
   - Avoid medical/clinical appearance

4. **Peaceful Reflection**
   - Person in contemplative state
   - Sunrise/growth metaphor
   - Upward trajectory, positive direction
   - Warm, inviting color palette

**Avoid:**
- Stock photo clichés (people pointing at charts)
- Overly corporate imagery (suits, boardrooms)
- Clinical/medical aesthetics
- Cold, impersonal visuals
- Intimidating or complex imagery

**File Naming:**
```
hero-personality-discovery.webp
hero-personality-discovery.jpg (fallback)
hero-personality-discovery@2x.webp (retina)
```

---

## 2. Method Icons

### Big Five Icon

**Purpose:** Represent the Five-Factor Model visually

**Specifications:**
- **Format:** SVG (scalable, inline)
- **Canvas Size:** 64×64px viewBox
- **Style:** Five interconnected circles
- **Colors:** Blue to purple gradient (#667eea → #764ba2)
- **Design:** Harmonious, balanced, professional

**Visual Concept:**
```
    O           Openness
O       O       Conscientiousness - Extraversion
  O   O         Agreeableness - Neuroticism
```

**Symbolism:**
- Five distinct circles representing five traits
- Interconnections showing trait relationships
- Gradient showing spectrum/continuity
- Balanced layout (not hierarchical)

### DISC Icon

**Purpose:** Represent the DISC assessment model

**Specifications:**
- **Format:** SVG (scalable, inline)
- **Canvas Size:** 64×64px viewBox
- **Style:** Circle divided into four quadrants
- **Colors:**
  - D (Dominance): #FF4444 (Red)
  - I (Influence): #FFD700 (Yellow)
  - S (Steadiness): #44AA44 (Green)
  - C (Conscientiousness): #4444FF (Blue)

**Visual Concept:**
```
    D | I
    -----
    C | S
```

**Design Notes:**
- Clean quadrant divisions
- Bold, distinct colors
- Circular boundary (unity)
- Equal sections (no hierarchy)

### Feature Icons (24×24px SVG)

**Purpose:** Illustrate key benefits and features

| Feature | Icon | Symbol | Color |
|---------|------|--------|-------|
| Self-Insight | 🎯 | Target/Bullseye | #667eea |
| Career Growth | 💼 | Briefcase | #764ba2 |
| Relationships | 🤝 | Handshake | #10b981 |
| Personal Growth | 📈 | Upward Chart | #3b82f6 |
| Science-Based | 🔬 | Microscope | #8b5cf6 |
| Security | 🔒 | Lock | #059669 |
| Privacy | 🛡️ | Shield | #0891b2 |
| Trust | ✓ | Checkmark | #10b981 |

**Icon Style Guidelines:**
- Rounded, friendly edges
- 2px stroke weight
- Consistent visual style
- Accessible (works in monochrome)
- Scales well from 16px to 64px

---

## 3. Background Patterns & Gradients

### Hero Background Gradient

```css
.hero {
    background: linear-gradient(135deg,
        #667eea 0%,
        #764ba2 100%);
}

/* With overlay pattern */
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(
        circle,
        rgba(255, 255, 255, 0.1) 1px,
        transparent 1px
    );
    background-size: 20px 20px;
    opacity: 0.4;
}
```

### Section Dividers

**Wave Separator:**
```html
<svg class="wave-separator" viewBox="0 0 1200 120" preserveAspectRatio="none">
    <path d="M0,0 C300,100 900,100 1200,0 L1200,120 L0,120 Z"
          fill="#f9fafb"/>
</svg>
```

**Gradient Fade:**
```css
.section-divider {
    height: 120px;
    background: linear-gradient(to bottom,
        rgba(249, 250, 251, 0),
        rgba(249, 250, 251, 1));
}
```

### Dot Pattern Background

```css
.dot-pattern {
    background-image: radial-gradient(
        circle,
        rgba(102, 126, 234, 0.1) 1px,
        transparent 1px
    );
    background-size: 24px 24px;
    background-position: 0 0;
}
```

---

## 4. Brand Colors

### Primary Palette

```css
:root {
    /* Primary Brand Colors */
    --color-primary: #667eea;
    --color-primary-dark: #5568d3;
    --color-primary-light: #818cf8;
    --color-secondary: #764ba2;
    --color-secondary-dark: #6b3fa0;
    --color-secondary-light: #9333ea;

    /* Brand Gradient */
    --gradient-primary: linear-gradient(135deg,
        var(--color-primary) 0%,
        var(--color-secondary) 100%);
}
```

### DISC Assessment Colors

```css
:root {
    /* DISC Model Colors */
    --color-disc-d: #FF4444;           /* Dominance - Red */
    --color-disc-d-light: #ff6b6b;
    --color-disc-i: #FFD700;           /* Influence - Yellow */
    --color-disc-i-light: #ffe066;
    --color-disc-s: #44AA44;           /* Steadiness - Green */
    --color-disc-s-light: #66bb6a;
    --color-disc-c: #4444FF;           /* Conscientiousness - Blue */
    --color-disc-c-light: #6b6bff;
}
```

### Big Five Trait Colors

```css
:root {
    /* Big Five Trait Colors */
    --color-openness: #8b5cf6;         /* Purple */
    --color-conscientiousness: #3b82f6; /* Blue */
    --color-extraversion: #f59e0b;     /* Orange */
    --color-agreeableness: #10b981;    /* Green */
    --color-neuroticism: #ef4444;      /* Red */

    /* Big Five Gradient */
    --gradient-big-five: linear-gradient(135deg,
        #667eea 0%,
        #764ba2 100%);
}
```

### UI & Semantic Colors

```css
:root {
    /* Semantic Colors */
    --color-success: #10b981;
    --color-success-light: #34d399;
    --color-warning: #f59e0b;
    --color-warning-light: #fbbf24;
    --color-error: #ef4444;
    --color-error-light: #f87171;
    --color-info: #3b82f6;
    --color-info-light: #60a5fa;

    /* Neutral Grays */
    --color-gray-50: #f9fafb;
    --color-gray-100: #f3f4f6;
    --color-gray-200: #e5e7eb;
    --color-gray-300: #d1d5db;
    --color-gray-400: #9ca3af;
    --color-gray-500: #6b7280;
    --color-gray-600: #4b5563;
    --color-gray-700: #374151;
    --color-gray-800: #1f2937;
    --color-gray-900: #111827;

    /* Background Colors */
    --color-bg-primary: #ffffff;
    --color-bg-secondary: #f9fafb;
    --color-bg-tertiary: #f3f4f6;
}
```

---

## 5. Typography System

### Font Family

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont,
                    'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu',
                    sans-serif;
    --font-mono: 'Menlo', 'Monaco', 'Courier New', monospace;
}

body {
    font-family: var(--font-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
```

### Type Scale

```css
:root {
    /* Font Sizes */
    --text-xs: 0.75rem;      /* 12px */
    --text-sm: 0.875rem;     /* 14px */
    --text-base: 1rem;       /* 16px */
    --text-lg: 1.125rem;     /* 18px */
    --text-xl: 1.25rem;      /* 20px */
    --text-2xl: 1.5rem;      /* 24px */
    --text-3xl: 1.875rem;    /* 30px */
    --text-4xl: 2.25rem;     /* 36px */
    --text-5xl: 3rem;        /* 48px */
    --text-6xl: 3.75rem;     /* 60px */

    /* Line Heights */
    --leading-tight: 1.25;
    --leading-snug: 1.375;
    --leading-normal: 1.5;
    --leading-relaxed: 1.625;
    --leading-loose: 2;
}
```

### Heading Styles

```css
h1, .h1 {
    font-size: var(--text-5xl);
    font-weight: 700;
    line-height: var(--leading-tight);
    letter-spacing: -0.02em;
    color: var(--color-gray-900);
}

h2, .h2 {
    font-size: var(--text-4xl);
    font-weight: 600;
    line-height: var(--leading-snug);
    letter-spacing: -0.01em;
    color: var(--color-gray-900);
}

h3, .h3 {
    font-size: var(--text-2xl);
    font-weight: 600;
    line-height: var(--leading-normal);
    color: var(--color-gray-900);
}

h4, .h4 {
    font-size: var(--text-xl);
    font-weight: 600;
    line-height: var(--leading-normal);
    color: var(--color-gray-900);
}
```

### Body Text Styles

```css
p, .body-text {
    font-size: var(--text-lg);
    line-height: var(--leading-relaxed);
    color: var(--color-gray-600);
}

.lead {
    font-size: var(--text-xl);
    line-height: var(--leading-relaxed);
    color: var(--color-gray-700);
}

.small {
    font-size: var(--text-sm);
    line-height: var(--leading-normal);
}

.tagline {
    font-size: var(--text-xl);
    font-weight: 400;
    line-height: var(--leading-relaxed);
    opacity: 0.9;
}
```

---

## 6. Illustration Style Guide

### Visual Style

**Characteristics:**
- Modern, minimal, friendly
- Rounded edges (not sharp/aggressive)
- 2-3 colors max per illustration
- Consistent line weight (2-3px)
- Approachable, not intimidating
- Flat design with subtle shadows

**Mood:**
- Professional but warm
- Inspiring but realistic
- Scientific but accessible
- Trustworthy but friendly

### Subject Guidelines

**✅ DO Use:**
- Abstract personality representations
- Diverse people in natural poses
- Connection/network metaphors
- Light bulb/insight moments
- Growth/development imagery
- Upward trajectories
- Harmonious compositions
- Nature metaphors (trees, growth)

**❌ AVOID:**
- Clinical/medical imagery
- Stock photo clichés
- Overly corporate settings
- Aggressive/sharp visuals
- Complex diagrams
- Text-heavy graphics
- Stereotypes
- Intimidating imagery

### Illustration Examples

**For "Self-Discovery" Concept:**
- Person looking at reflection showing multiple facets
- Mirror revealing inner traits
- Puzzle pieces coming together
- Path leading to destination

**For "Science-Based" Concept:**
- Clean data visualization
- Balanced scales
- Validated checkmark badge
- Research/study metaphor

**For "Personal Growth" Concept:**
- Ascending stairs/path
- Growing plant/tree
- Expanding circles
- Opening door to light

---

## 7. Badge & Trust Indicators

### Security Badges

**GDPR Compliant Badge:**
```svg
<svg viewBox="0 0 120 120" class="badge-gdpr">
    <circle cx="60" cy="60" r="55" fill="#10b981"/>
    <path d="M60,25 L70,35 L60,45 L50,35 Z" fill="white"/>
    <text x="60" y="75" text-anchor="middle" fill="white"
          font-size="14" font-weight="600">GDPR</text>
    <text x="60" y="92" text-anchor="middle" fill="white"
          font-size="10">Compliant</text>
</svg>
```

**SSL/Security Badge:**
```svg
<svg viewBox="0 0 100 100" class="badge-secure">
    <rect x="30" y="40" width="40" height="40" rx="4" fill="#059669"/>
    <path d="M50,25 C50,25 60,30 60,40" stroke="#059669"
          stroke-width="3" fill="none"/>
    <path d="M50,25 C50,25 40,30 40,40" stroke="#059669"
          stroke-width="3" fill="none"/>
    <path d="M45,55 L48,60 L55,50" stroke="white"
          stroke-width="3" fill="none"/>
</svg>
```

**Science-Based Badge:**
```svg
<svg viewBox="0 0 100 100" class="badge-science">
    <circle cx="50" cy="50" r="45" fill="#3b82f6"/>
    <path d="M50,30 L50,50 L65,65" stroke="white"
          stroke-width="3" fill="none"/>
    <circle cx="50" cy="50" r="3" fill="white"/>
    <circle cx="65" cy="65" r="3" fill="white"/>
    <text x="50" y="90" text-anchor="middle" fill="white"
          font-size="12">VALIDATED</text>
</svg>
```

---

## 8. Image Optimization Guide

### Pre-Upload Checklist

```markdown
## Before Upload:
- [ ] Resize to exact dimensions needed
- [ ] Compress with TinyPNG or ImageOptim
- [ ] Convert to WebP format
- [ ] Create JPEG fallback
- [ ] Create @2x retina version if needed
- [ ] Add descriptive alt text
- [ ] Test on slow connection (3G)
- [ ] Verify aspect ratio on mobile

## Target Sizes:
- Hero image: < 150KB (WebP), < 200KB (JPEG)
- Method images: < 80KB each
- Icons: SVG (inline preferred)
- Thumbnails: < 30KB
- Background patterns: CSS or SVG
```

### File Naming Convention

```
Format: [section]-[description]-[variant].[ext]

Examples:
hero-personality-discovery.webp
hero-personality-discovery.jpg
hero-personality-discovery@2x.webp
method-big-five-illustration.webp
method-disc-quadrants.webp
icon-security-badge.svg
icon-privacy-shield.svg
benefit-career-growth.svg
```

### Responsive Image Implementation

```html
<!-- Hero Image with Multiple Sources -->
<picture>
    <source
        srcset="assets/images/hero-large.webp 1x,
                assets/images/hero-large@2x.webp 2x"
        media="(min-width: 1024px)"
        type="image/webp">
    <source
        srcset="assets/images/hero-large.jpg 1x,
                assets/images/hero-large@2x.jpg 2x"
        media="(min-width: 1024px)"
        type="image/jpeg">

    <source
        srcset="assets/images/hero-medium.webp 1x,
                assets/images/hero-medium@2x.webp 2x"
        media="(min-width: 768px)"
        type="image/webp">
    <source
        srcset="assets/images/hero-medium.jpg 1x,
                assets/images/hero-medium@2x.jpg 2x"
        media="(min-width: 768px)"
        type="image/jpeg">

    <img
        src="assets/images/hero-small.jpg"
        srcset="assets/images/hero-small.webp 1x,
                assets/images/hero-small@2x.webp 2x"
        alt="Person experiencing moment of self-discovery and insight"
        loading="lazy"
        width="1920"
        height="1080">
</picture>
```

### Lazy Loading Strategy

```html
<!-- Critical images (above fold) - eager loading -->
<img src="hero.webp" alt="..." loading="eager">

<!-- Below-fold images - lazy loading -->
<img src="benefit.webp" alt="..." loading="lazy">

<!-- Background images via CSS -->
<div class="lazy-background" data-bg="url('pattern.webp')"></div>

<script>
// Lazy load backgrounds
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.backgroundImage =
                entry.target.dataset.bg;
        }
    });
});
document.querySelectorAll('.lazy-background')
    .forEach(el => observer.observe(el));
</script>
```

---

## 9. CSS Placeholder System

### Hero Placeholder

```css
.hero-placeholder {
    width: 100%;
    height: 500px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero-placeholder::before {
    content: "🧠";
    font-size: 120px;
    opacity: 0.3;
    position: absolute;
    animation: float 6s ease-in-out infinite;
}

.hero-placeholder::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(
        circle,
        rgba(255, 255, 255, 0.1) 1px,
        transparent 1px
    );
    background-size: 20px 20px;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}
```

### Method Card Placeholders

```css
.method-image-placeholder {
    width: 100%;
    height: 200px;
    background: linear-gradient(to bottom, #f3f4f6, #e5e7eb);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.method-image-placeholder--big-five {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.method-image-placeholder--disc {
    background: conic-gradient(
        from 0deg,
        #FF4444 0deg 90deg,
        #FFD700 90deg 180deg,
        #44AA44 180deg 270deg,
        #4444FF 270deg 360deg
    );
    opacity: 0.2;
}

.method-image-placeholder::before {
    content: attr(data-icon);
    font-size: 64px;
    opacity: 0.4;
}
```

---

## 10. Accessibility Requirements

### Alt Text Guidelines

**Hero Images:**
```
Good: "Person experiencing moment of self-discovery with glowing insight visualization"
Bad: "Person smiling"
```

**Method Icons:**
```
Good: "Big Five personality assessment icon showing five interconnected traits"
Bad: "Five circles icon"
```

**Decorative Images:**
```html
<img src="decoration.svg" alt="" role="presentation">
```

### Color Contrast

All text must meet WCAG AA standards:
- Normal text: 4.5:1 minimum contrast
- Large text (18pt+): 3:1 minimum contrast
- Interactive elements: 3:1 minimum contrast

**Test Your Colors:**
```css
/* ✅ Good contrast */
.button-primary {
    background: #667eea;
    color: #ffffff; /* 4.52:1 ratio */
}

/* ❌ Poor contrast */
.text-light-on-light {
    background: #f3f4f6;
    color: #d1d5db; /* Only 1.5:1 - fails WCAG */
}
```

### Focus Indicators

```css
:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
}

.button:focus-visible {
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}
```

---

## 11. Animation Guidelines

### Subtle Micro-interactions

```css
/* Button hover */
.button {
    transition: all 0.2s ease;
}

.button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Card hover */
.card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Icon pulse */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.icon-animated {
    animation: pulse 2s ease-in-out infinite;
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## 12. Performance Budget

### Image Budget

| Page Section | Max Total Size | Individual Max |
|--------------|----------------|----------------|
| Hero | 150KB | 150KB |
| Methods (3 images) | 240KB | 80KB each |
| Benefits icons | 30KB | SVG inline |
| Trust badges | 20KB | SVG inline |
| **Total** | **440KB** | - |

### Loading Priority

1. **Critical (eager):** Hero image, logo
2. **High (lazy):** Method images, trust badges
3. **Low (lazy):** Decorative backgrounds, patterns

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Create assets folder structure
- [ ] Set up brand color CSS variables
- [ ] Import web fonts (Inter)
- [ ] Create SVG icon library
- [ ] Build CSS placeholders

### Phase 2: Assets
- [ ] Design/source hero image
- [ ] Create Big Five icon
- [ ] Create DISC icon
- [ ] Design feature icons (8 total)
- [ ] Create trust badges (3 total)

### Phase 3: Optimization
- [ ] Optimize all images < budget
- [ ] Create WebP versions
- [ ] Generate @2x retina versions
- [ ] Write descriptive alt text
- [ ] Test lazy loading

### Phase 4: Testing
- [ ] Test on slow connection (3G)
- [ ] Verify responsive breakpoints
- [ ] Check color contrast (WCAG AA)
- [ ] Test with screen reader
- [ ] Validate focus indicators

---

## Resources & Tools

### Design Tools
- **Figma:** UI design and prototyping
- **Adobe Illustrator:** Vector icon creation
- **Affinity Designer:** Alternative vector tool

### Optimization Tools
- **TinyPNG:** Image compression
- **Squoosh:** WebP conversion
- **SVGOMG:** SVG optimization
- **ImageOptim:** Batch optimization (Mac)

### Testing Tools
- **WebPageTest:** Performance testing
- **Lighthouse:** Accessibility & performance
- **Contrast Checker:** WCAG compliance
- **Screen Reader:** VoiceOver (Mac), NVDA (Windows)

### Stock Resources
- **Unsplash:** High-quality photos
- **Undraw:** Illustration library
- **Heroicons:** SVG icon set
- **Feather Icons:** Minimal icon set

---

## Maintenance

### Quarterly Review
- Review image performance metrics
- Update hero image for freshness
- Test new image formats (AVIF, etc.)
- Audit accessibility compliance

### When to Update
- New brand guidelines
- Performance budget exceeded
- User feedback on visuals
- A/B test results
- Platform updates (new image formats)

---

**Document Owner:** Design Team
**Last Review:** March 7, 2026
**Next Review:** June 7, 2026
