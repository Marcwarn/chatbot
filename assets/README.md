# Visual Assets Directory
## Landing Page - Personality Assessment Platform

This directory contains all visual assets, icons, images, and related resources for the landing page.

---

## 📁 Directory Structure

```
assets/
├── icons/                      # SVG icons and badges
│   ├── big-five.svg           # Big Five assessment icon
│   ├── disc.svg               # DISC assessment icon
│   └── badges.svg             # Trust/security badges
├── images/                     # Raster images (to be added)
│   ├── hero/                  # Hero section images
│   ├── methods/               # Assessment method images
│   └── benefits/              # Benefit/feature images
├── placeholders.css           # CSS placeholders for missing images
├── IMAGE_OPTIMIZATION_GUIDE.md # Complete optimization guide
└── README.md                  # This file
```

---

## 🎨 Available Icons

### Assessment Method Icons

| Icon | File | Usage | Dimensions |
|------|------|-------|------------|
| Big Five | `icons/big-five.svg` | Five-Factor Model representation | 64×64px |
| DISC | `icons/disc.svg` | DISC quadrant model | 64×64px |

### Trust Badges

Located in `icons/badges.svg` as SVG symbols:

| Badge | Symbol ID | Purpose |
|-------|-----------|---------|
| GDPR Compliant | `badge-gdpr` | Data protection compliance |
| SSL Secure | `badge-secure` | Encrypted connection |
| Science Validated | `badge-validated` | Research-backed |
| Privacy Protected | `badge-privacy` | Privacy guarantee |

**Usage Example:**

```html
<!-- Include badge definitions -->
<svg style="display: none;">
    <use href="assets/icons/badges.svg"/>
</svg>

<!-- Use a specific badge -->
<svg width="100" height="100">
    <use href="#badge-gdpr"/>
</svg>
```

---

## 🖼️ Image Placeholders

While waiting for final images, use CSS placeholders from `placeholders.css`:

### Hero Section

```html
<link rel="stylesheet" href="assets/placeholders.css">

<div class="hero-placeholder">
    <div class="hero-content">
        <h1>Discover Your True Self</h1>
        <p>Science-backed personality assessments</p>
    </div>
</div>
```

### Method Cards

```html
<div class="method-image-placeholder method-image-placeholder--big-five"
     data-icon="🧠">
</div>

<div class="method-image-placeholder method-image-placeholder--disc"
     data-icon="DISC">
</div>
```

### Benefit Icons

```html
<div class="benefit-icon-placeholder benefit-icon-placeholder--career">
    💼
</div>

<div class="benefit-icon-placeholder benefit-icon-placeholder--growth">
    📈
</div>
```

---

## 📋 Quick Start

### 1. Using SVG Icons

```html
<!-- Inline SVG (best performance) -->
<svg class="icon-big-five" width="64" height="64">
    <use href="assets/icons/big-five.svg"/>
</svg>

<!-- Or include directly -->
<img src="assets/icons/big-five.svg"
     alt="Big Five personality assessment"
     width="64"
     height="64">
```

### 2. Adding New Images

Before adding images, read the [Image Optimization Guide](IMAGE_OPTIMIZATION_GUIDE.md).

**Quick checklist:**
1. Resize to exact dimensions needed
2. Compress with [TinyPNG](https://tinypng.com)
3. Convert to WebP
4. Create JPEG fallback
5. Use semantic naming: `section-description-variant.ext`
6. Add descriptive alt text

### 3. Using Placeholders

```html
<link rel="stylesheet" href="assets/placeholders.css">

<!-- Hero placeholder -->
<div class="hero-placeholder"></div>

<!-- With loading skeleton -->
<div class="skeleton skeleton-image"></div>

<!-- With pattern background -->
<div class="pattern-dots">
    Your content here
</div>
```

---

## 🎯 Brand Guidelines

### Colors

See `brand-colors.css` for complete palette.

**Primary:**
- Primary: `#667eea`
- Secondary: `#764ba2`
- Gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

**DISC:**
- D (Dominance): `#FF4444`
- I (Influence): `#FFD700`
- S (Steadiness): `#44AA44`
- C (Conscientiousness): `#4444FF`

**Big Five:**
- Openness: `#8b5cf6`
- Conscientiousness: `#3b82f6`
- Extraversion: `#f59e0b`
- Agreeableness: `#10b981`
- Neuroticism: `#ef4444`

### Typography

**Font:** Inter (Google Fonts)
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Usage:**
```css
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

---

## 📊 Performance Budget

| Asset Type | Budget | Notes |
|------------|--------|-------|
| Hero Image | 150KB | WebP format |
| Method Images | 80KB each | 3 images total |
| Icons | 5KB each | Use SVG |
| **Total Images** | **440KB** | - |
| **Total Page** | **1.5MB** | Including CSS, JS |

**Monitor with Lighthouse:**
```bash
npm install -g lighthouse
lighthouse https://your-domain.com --view
```

---

## ♿ Accessibility

### Alt Text Requirements

**Always provide descriptive alt text:**

```html
<!-- ✅ Good -->
<img src="hero.webp"
     alt="Woman reflecting on her personality assessment results with a smile">

<!-- ❌ Bad -->
<img src="hero.webp" alt="Image">
```

### Decorative Images

```html
<!-- Mark decorative images -->
<img src="pattern.svg" alt="" role="presentation">
```

### Icon Labels

```html
<!-- Screen reader friendly icons -->
<svg role="img" aria-label="Security lock indicating data protection">
    <title>Security</title>
    <!-- icon path -->
</svg>
```

---

## 🚀 Optimization Workflow

### Adding a New Image

1. **Prepare**
   ```bash
   # Resize image
   convert input.jpg -resize 1920x1080 output.jpg

   # Convert to WebP
   cwebp -q 80 output.jpg -o output.webp
   ```

2. **Compress**
   - Use [TinyPNG](https://tinypng.com) for JPEG/PNG
   - Use [Squoosh](https://squoosh.app) for WebP
   - Target: < budget limits

3. **Add to Project**
   ```html
   <picture>
       <source srcset="assets/images/output.webp" type="image/webp">
       <img src="assets/images/output.jpg"
            alt="Descriptive alt text"
            loading="lazy"
            width="1920"
            height="1080">
   </picture>
   ```

4. **Test**
   - Chrome DevTools (Network tab)
   - Lighthouse performance audit
   - Test on 3G connection
   - Screen reader testing

---

## 🛠️ Tools & Resources

### Compression Tools

**Online:**
- [TinyPNG](https://tinypng.com) - PNG/JPEG compression
- [Squoosh](https://squoosh.app) - Modern formats (WebP, AVIF)
- [SVGOMG](https://jakearchibald.github.io/svgomg/) - SVG optimization

**Desktop:**
- [ImageOptim](https://imageoptim.com) (Mac)
- [FileOptimizer](https://sourceforge.net/projects/nikkhokkho/) (Windows)

### Icon Resources

**Free SVG Icons:**
- [Heroicons](https://heroicons.com)
- [Feather Icons](https://feathericons.com)
- [Lucide](https://lucide.dev)

**Illustrations:**
- [unDraw](https://undraw.co)
- [Storyset](https://storyset.com)
- [Blush](https://blush.design)

### Stock Images

**Free:**
- [Unsplash](https://unsplash.com)
- [Pexels](https://pexels.com)
- [Pixabay](https://pixabay.com)

---

## 📝 File Naming Conventions

### Format

```
[section]-[description]-[variant].[ext]

Examples:
hero-personality-discovery.webp
hero-personality-discovery@2x.webp
hero-personality-discovery.jpg
method-big-five-illustration.webp
method-disc-quadrants.webp
benefit-career-growth.svg
icon-security-badge.svg
```

### Rules

- Use lowercase
- Use hyphens (not underscores or spaces)
- Be descriptive but concise
- Include section/context
- Add variant (@2x, -mobile, -tablet)
- Use correct extension

**✅ Good:**
- `hero-self-discovery.webp`
- `method-big-five-chart@2x.webp`
- `icon-privacy-shield.svg`

**❌ Bad:**
- `Image1.jpg`
- `final_FINAL_v3.png`
- `IMG_2834.JPG`

---

## 🔄 Maintenance

### Regular Tasks

**Monthly:**
- [ ] Review image performance metrics
- [ ] Check for unused images
- [ ] Update outdated screenshots
- [ ] Test lazy loading

**Quarterly:**
- [ ] Audit total page weight
- [ ] Review new image formats (AVIF, etc.)
- [ ] Update optimization tools
- [ ] Refresh hero image (seasonal?)

**Annually:**
- [ ] Major visual refresh
- [ ] Update brand guidelines
- [ ] Review accessibility compliance
- [ ] Performance benchmark

### Monitoring

```javascript
// Check total image weight
const images = document.querySelectorAll('img');
let total = 0;

images.forEach(img => {
    fetch(img.src)
        .then(r => r.blob())
        .then(blob => {
            console.log(`${img.alt}: ${(blob.size/1024).toFixed(2)}KB`);
            total += blob.size;
        });
});

setTimeout(() => {
    console.log(`Total: ${(total/1024).toFixed(2)}KB`);
}, 2000);
```

---

## 🎨 Design Tokens

All design tokens are available in `brand-colors.css`:

```css
@import url('../brand-colors.css');

.hero {
    background: var(--gradient-primary);
    color: var(--color-white);
}

.button-primary {
    background: var(--color-primary);
    color: var(--color-white);
    border-radius: var(--radius-lg);
    padding: var(--space-4) var(--space-6);
}
```

### Available Variables

- Colors: `--color-primary`, `--color-secondary`, etc.
- Spacing: `--space-1` to `--space-32`
- Typography: `--text-xs` to `--text-7xl`
- Shadows: `--shadow-sm` to `--shadow-2xl`
- Radius: `--radius-sm` to `--radius-full`

---

## 📚 Related Documentation

- [VISUAL_ASSETS_SPEC.md](../VISUAL_ASSETS_SPEC.md) - Complete visual specifications
- [IMAGE_OPTIMIZATION_GUIDE.md](IMAGE_OPTIMIZATION_GUIDE.md) - Detailed optimization guide
- [brand-colors.css](../brand-colors.css) - Design tokens and color palette
- [icon-library.html](../icon-library.html) - Visual icon showcase

---

## ❓ FAQ

### Q: Should I use SVG or PNG for icons?

**A:** Always use SVG for icons, logos, and simple graphics. They're scalable, smaller, and work on any screen resolution.

### Q: What's the difference between WebP and JPEG?

**A:** WebP provides 25-35% better compression than JPEG with same quality. Always provide both (WebP as primary, JPEG as fallback).

### Q: How do I test image accessibility?

**A:** Use a screen reader (VoiceOver on Mac, NVDA on Windows) or automated tools like axe DevTools. Every image needs descriptive alt text.

### Q: Can I use placeholder images in production?

**A:** No. Placeholders in `placeholders.css` are temporary. Replace with optimized real images before launch.

### Q: What if my image exceeds the budget?

**A:**
1. Reduce dimensions (do you need 4K?)
2. Increase compression (try 70-75% quality)
3. Convert to WebP (30-50% smaller)
4. Consider using CSS gradients instead

### Q: How do I handle retina displays?

**A:** Provide @2x versions using srcset:
```html
<img src="image.jpg"
     srcset="image@2x.jpg 2x"
     alt="...">
```

---

## 🆘 Support

**Questions?** Contact:
- Design Team: design@example.com
- Technical Issues: File a GitHub issue
- Documentation: Update this README

---

**Version:** 1.0
**Last Updated:** March 7, 2026
**Maintainer:** Design Team
