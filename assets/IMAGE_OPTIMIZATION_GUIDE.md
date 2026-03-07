# Image Optimization Guide
## Landing Page Visual Assets

**Purpose:** Ensure all images are optimized for performance, accessibility, and user experience.

---

## Pre-Upload Checklist

Before adding any image to the landing page:

- [ ] **Resize to exact dimensions needed**
  - Hero: 1920×1080px (plus @2x: 3840×2160px)
  - Method cards: 600×400px
  - Icons: Use SVG (scalable)
  - Thumbnails: 300×200px

- [ ] **Compress images**
  - Use [TinyPNG](https://tinypng.com) or [ImageOptim](https://imageoptim.com)
  - Target: Hero < 150KB, Others < 80KB

- [ ] **Convert to modern formats**
  - Primary: WebP
  - Fallback: JPEG (always provide)
  - Never use PNG for photos (only for graphics with transparency)

- [ ] **Create responsive versions**
  - Mobile: 640px wide
  - Tablet: 1024px wide
  - Desktop: 1920px wide
  - Retina: @2x versions where needed

- [ ] **Write descriptive alt text**
  - Be specific and descriptive
  - Explain what the image shows, not just "image" or "photo"
  - Include context relevant to personality assessment

- [ ] **Test on slow connection**
  - Use Chrome DevTools Network throttling
  - Simulate 3G connection
  - Verify lazy loading works

---

## File Naming Convention

Use clear, semantic naming:

```
Format: [section]-[description]-[variant].[ext]

✅ Good:
hero-personality-discovery.webp
hero-personality-discovery@2x.webp
hero-personality-discovery.jpg (fallback)
method-big-five-illustration.webp
method-disc-quadrants.webp
icon-security-badge.svg
benefit-career-growth.svg

❌ Bad:
image1.jpg
photo.png
final-FINAL-v3.jpg
IMG_2834.JPG
```

---

## Image Specifications

### Hero Image

```
Dimensions: 1920×1080px (16:9)
Format: WebP + JPEG fallback
Size: < 150KB (WebP), < 200KB (JPEG)
Retina: 3840×2160px @2x (< 300KB)

Quality Settings:
- WebP: 80-85%
- JPEG: 75-80%
```

### Method Card Images

```
Dimensions: 600×400px (3:2)
Format: WebP + JPEG fallback
Size: < 80KB each
Retina: 1200×800px @2x (< 150KB)

Quality Settings:
- WebP: 80%
- JPEG: 75%
```

### Feature Icons

```
Format: SVG (preferred) or WebP
Size: 64×64px or 24×24px
File size: < 5KB (SVG should be optimized)

SVG Optimization:
- Remove unnecessary metadata
- Simplify paths
- Use SVGOMG tool
```

### Background Patterns

```
Format: SVG or CSS gradients (preferred)
Fallback: WebP (< 30KB)

Prefer CSS over images:
- Gradients: Use CSS linear-gradient
- Dots/Grid: Use CSS background-image
- Waves: Inline SVG
```

---

## Responsive Image Implementation

### Basic Picture Element

```html
<picture>
    <!-- WebP sources for modern browsers -->
    <source
        srcset="assets/images/hero-large.webp 1x,
                assets/images/hero-large@2x.webp 2x"
        media="(min-width: 1024px)"
        type="image/webp">

    <!-- JPEG fallback for older browsers -->
    <source
        srcset="assets/images/hero-large.jpg 1x,
                assets/images/hero-large@2x.jpg 2x"
        media="(min-width: 1024px)"
        type="image/jpeg">

    <!-- Tablet -->
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

    <!-- Mobile fallback -->
    <img
        src="assets/images/hero-small.jpg"
        srcset="assets/images/hero-small.webp 1x,
                assets/images/hero-small@2x.webp 2x"
        alt="Person experiencing moment of self-discovery and personal insight"
        loading="lazy"
        width="1920"
        height="1080"
        class="hero-image">
</picture>
```

### Simple Image with WebP

```html
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="Descriptive alt text" loading="lazy">
</picture>
```

### Background Image with Lazy Loading

```html
<div class="lazy-background"
     data-bg="url('assets/images/pattern.webp')"
     role="img"
     aria-label="Decorative background pattern">
</div>

<script>
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.backgroundImage = entry.target.dataset.bg;
            observer.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('.lazy-background').forEach(el => {
    observer.observe(el);
});
</script>
```

---

## Lazy Loading Strategy

### Critical Images (Above Fold)

**DO NOT lazy load:**
- Hero image
- Logo
- First viewport content

```html
<img src="hero.webp" alt="..." loading="eager">
```

### Below-Fold Images

**DO lazy load:**
- Method card images
- Benefit icons (if images)
- Testimonial photos
- Footer content

```html
<img src="benefit.webp" alt="..." loading="lazy">
```

### Native Lazy Loading Support

```html
<!-- Modern browsers -->
<img src="image.webp" alt="..." loading="lazy">

<!-- With fallback for older browsers -->
<img src="image.webp"
     alt="..."
     loading="lazy"
     class="lazyload"
     data-src="image.webp">
```

---

## Accessibility Requirements

### Alt Text Best Practices

**✅ Good Alt Text:**

```html
<img src="hero.webp"
     alt="Woman looking thoughtful while reviewing her personality assessment results on a tablet, surrounded by notes about self-discovery">

<img src="big-five-icon.svg"
     alt="Big Five personality assessment icon showing five interconnected circles representing openness, conscientiousness, extraversion, agreeableness, and neuroticism">

<img src="security-badge.svg"
     alt="GDPR compliant badge indicating data protection and privacy compliance">
```

**❌ Bad Alt Text:**

```html
<img src="hero.webp" alt="Image">
<img src="big-five-icon.svg" alt="Icon">
<img src="security-badge.svg" alt="Badge">
```

### Decorative Images

Images that don't convey information:

```html
<!-- Use empty alt and role="presentation" -->
<img src="decorative-pattern.svg" alt="" role="presentation">

<!-- Or aria-hidden -->
<img src="decorative.svg" alt="" aria-hidden="true">
```

### Complex Images

Images that need detailed descriptions:

```html
<figure>
    <img src="personality-chart.webp"
         alt="Bar chart showing Big Five personality trait scores"
         aria-describedby="chart-description">
    <figcaption id="chart-description">
        Detailed description: The chart shows five bars representing
        personality traits. Openness: 75%, Conscientiousness: 82%,
        Extraversion: 45%, Agreeableness: 68%, Neuroticism: 32%.
    </figcaption>
</figure>
```

---

## Performance Budget

### Total Page Budget

| Asset Type | Budget | Individual Limit |
|------------|--------|------------------|
| Hero Image | 150KB | 150KB |
| Method Images (3) | 240KB | 80KB each |
| Icons (SVG) | 30KB | 5KB each |
| Badges (SVG) | 20KB | 5KB each |
| **Total Images** | **440KB** | - |
| **Total Page** | **1.5MB** | - |

### Monitoring Performance

```javascript
// Check image sizes in DevTools Console
const images = document.querySelectorAll('img');
let totalSize = 0;

images.forEach(img => {
    fetch(img.src)
        .then(response => response.blob())
        .then(blob => {
            console.log(`${img.src}: ${(blob.size / 1024).toFixed(2)} KB`);
            totalSize += blob.size;
        });
});

setTimeout(() => {
    console.log(`Total image size: ${(totalSize / 1024).toFixed(2)} KB`);
}, 3000);
```

---

## Tools & Resources

### Compression Tools

**Online:**
- [TinyPNG](https://tinypng.com) - PNG & JPEG compression
- [Squoosh](https://squoosh.app) - Modern image compression (WebP, AVIF)
- [SVGOMG](https://jakearchibald.github.io/svgomg/) - SVG optimization
- [Compress JPEG](https://compressjpeg.com) - Batch JPEG compression

**Desktop:**
- [ImageOptim](https://imageoptim.com) - Mac batch optimizer
- [FileOptimizer](https://sourceforge.net/projects/nikkhokkho/) - Windows optimizer
- [GIMP](https://www.gimp.org) - Free image editor

**Command Line:**
```bash
# WebP conversion
cwebp -q 80 input.jpg -o output.webp

# JPEG optimization
jpegoptim --max=80 --strip-all image.jpg

# PNG optimization
pngquant --quality=65-80 image.png

# SVG optimization
svgo input.svg -o output.svg
```

### Testing Tools

**Performance:**
- [WebPageTest](https://webpagetest.org) - Real-world performance testing
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Chrome DevTools audit
- [GTmetrix](https://gtmetrix.com) - Performance analysis

**Accessibility:**
- [WAVE](https://wave.webaim.org) - Web accessibility checker
- [axe DevTools](https://www.deque.com/axe/devtools/) - Accessibility testing
- Screen readers: VoiceOver (Mac), NVDA (Windows)

### Stock Image Resources

**Free (Attribution Required):**
- [Unsplash](https://unsplash.com) - High-quality photos
- [Pexels](https://pexels.com) - Free stock photos
- [Pixabay](https://pixabay.com) - Photos and illustrations

**Illustrations:**
- [unDraw](https://undraw.co) - Open-source illustrations
- [Storyset](https://storyset.com) - Customizable illustrations
- [Blush](https://blush.design) - Illustration library

**Icons:**
- [Heroicons](https://heroicons.com) - Beautiful SVG icons
- [Feather Icons](https://feathericons.com) - Minimal icons
- [Lucide](https://lucide.dev) - Icon library

---

## Workflow Checklist

### Adding a New Image

1. **Source/Create Image**
   - [ ] Use appropriate source (stock, custom design)
   - [ ] Ensure licensing allows commercial use
   - [ ] Get highest quality source file

2. **Prepare Image**
   - [ ] Crop/resize to exact dimensions
   - [ ] Remove unnecessary elements
   - [ ] Adjust colors to match brand palette
   - [ ] Export at 100% quality initially

3. **Optimize Image**
   - [ ] Compress with TinyPNG/Squoosh
   - [ ] Create WebP version (80-85% quality)
   - [ ] Create JPEG fallback (75-80% quality)
   - [ ] Create @2x retina version if needed
   - [ ] Verify file size < budget

4. **Create Responsive Versions**
   - [ ] Mobile: 640px wide
   - [ ] Tablet: 1024px wide
   - [ ] Desktop: 1920px wide
   - [ ] Compress each version

5. **Add to Project**
   - [ ] Upload to assets/images/ folder
   - [ ] Use semantic file naming
   - [ ] Update HTML with <picture> element
   - [ ] Add descriptive alt text
   - [ ] Add width/height attributes

6. **Test**
   - [ ] Test on Chrome, Firefox, Safari
   - [ ] Test on mobile devices
   - [ ] Test with slow 3G connection
   - [ ] Test with screen reader
   - [ ] Run Lighthouse audit
   - [ ] Verify lazy loading works

7. **Deploy**
   - [ ] Commit to git with descriptive message
   - [ ] Push to staging environment
   - [ ] QA review
   - [ ] Deploy to production

---

## Common Issues & Solutions

### Issue: Images Too Large

**Solution:**
- Reduce image dimensions (do you need 4K?)
- Increase compression (try 70-75% quality)
- Convert to WebP (30-50% smaller than JPEG)
- Consider using CSS gradients instead

### Issue: Images Look Blurry on Retina

**Solution:**
- Provide @2x versions using srcset
- Use SVG for logos/icons (infinite scaling)
- Ensure 2x image is exactly 2× dimensions

### Issue: Slow Loading

**Solution:**
- Enable lazy loading for below-fold images
- Use CDN for image delivery
- Implement progressive JPEG loading
- Consider blur-up placeholder technique

### Issue: Images Not Accessible

**Solution:**
- Add descriptive alt text
- Use aria-label for background images
- Mark decorative images with alt=""
- Test with screen reader

### Issue: Layout Shift (CLS)

**Solution:**
- Always specify width and height attributes
- Use aspect-ratio CSS property
- Reserve space with placeholder
- Use blur-up technique

```html
<img src="image.webp"
     alt="..."
     width="1920"
     height="1080"
     style="aspect-ratio: 16/9;">
```

---

## Advanced Techniques

### Blur-Up Placeholder

```html
<div class="blur-up">
    <!-- Tiny 20px preview (< 1KB) -->
    <img src="preview-tiny.jpg"
         class="blur-up-preview"
         alt="">

    <!-- Full quality image -->
    <img src="image.webp"
         class="blur-up-full"
         alt="Descriptive alt text"
         onload="this.classList.add('loaded')">
</div>

<style>
.blur-up { position: relative; }
.blur-up-preview {
    filter: blur(10px);
    transform: scale(1.1);
}
.blur-up-full {
    position: absolute;
    top: 0;
    opacity: 0;
    transition: opacity 0.3s;
}
.blur-up-full.loaded {
    opacity: 1;
}
</style>
```

### Progressive JPEG

Export JPEGs as "progressive" in Photoshop or:

```bash
jpegtran -progressive -copy none input.jpg > output.jpg
```

### Art Direction

Different crops for different viewports:

```html
<picture>
    <!-- Desktop: Landscape -->
    <source media="(min-width: 1024px)"
            srcset="hero-landscape.webp">

    <!-- Tablet: Square -->
    <source media="(min-width: 768px)"
            srcset="hero-square.webp">

    <!-- Mobile: Portrait -->
    <img src="hero-portrait.webp" alt="...">
</picture>
```

---

## Future Considerations

### Next-Gen Formats

**AVIF:** Even better compression than WebP
```html
<picture>
    <source srcset="image.avif" type="image/avif">
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="...">
</picture>
```

### Image CDN

Consider using an image CDN like:
- Cloudinary
- Imgix
- Cloudflare Images

Benefits:
- Automatic format conversion
- On-the-fly resizing
- Global CDN delivery
- URL-based transformations

---

**Maintained by:** Design Team
**Last Updated:** March 7, 2026
**Questions?** Contact the design team or file an issue
