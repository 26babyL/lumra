# 🎨 LUMRA Design System Reference v3.0
**Untuk memastikan semua HTML templates konsisten dengan Emerald Odyssey theme**

---

## 📋 Quick Summary
- **Theme**: Emerald Odyssey v3.0 (Glass Morphism)
- **Framework**: Django + Tailwind + Alpine.js
- **Status**: ✅ Base templates (base.html, navbar, sidebar) sudah di-update

---

## 🎨 Color Palette (CSS Tokens)

### Primary Colors
```css
--em: #00674F;           /* Primary Emerald */
--jade: #00A86B;         /* Secondary Jade */
--gold: #EFBF04;         /* Accent Gold */
--cream: #FDFBD4;        /* Neutral Cream */
--navy: #000080;         /* Contrast Navy */
```

### Semantic Colors
```css
--em-08: rgba(0, 103, 79, 0.08);     /* Light emerald bg */
--em-12: rgba(0, 103, 79, 0.12);     /* Medium emerald bg */
--em-15: rgba(0, 103, 79, 0.15);     /* Dark emerald bg */
--em-20: rgba(0, 103, 79, 0.20);     /* Border emerald */
--em-25: rgba(0, 103, 79, 0.25);     /* Strong border */

--jade-05: rgba(0, 168, 107, 0.05);  /* Extra-soft hover */
--jade-08: rgba(0, 168, 107, 0.08);  /* Light jade bg */
--jade-12: rgba(0, 168, 107, 0.12);  /* Medium jade bg */
--jade-15: rgba(0, 168, 107, 0.15);  /* Dark jade bg */
--jade-25: rgba(0, 168, 107, 0.25);  /* Medium border */
--jade-35: rgba(0, 168, 107, 0.35);  /* Logo shadow */

--gold-08: rgba(239, 191, 4, 0.08);  /* Light gold */
--gold-12: rgba(239, 191, 4, 0.12);  /* Medium gold */
--gold-15: rgba(239, 191, 4, 0.15);  /* Dark gold */

--slate-300: #cbd5e1;   /* Section labels */
--slate-400: #94a3b8;   /* Sub-items text */
--slate-600: #6b8a7a;   /* Nav items text */
```

---

## 🔷 Glass Morphism System

### Core Glass Effect
```css
.glass-base {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 0.5px solid rgba(0, 103, 79, 0.1);
  box-shadow: 0 1px 3px rgba(0,0,0,.08), 
              0 4px 12px rgba(0,0,0,.06);
}
```

### Components Using Glass
✅ `.nav-glass` - Navbar (56px height)
✅ `.sidebar-glass` - Sidebar navigation
✅ `.lumra-glass` - General glass cards
✅ `.lumra-kpi-glass` - KPI cards
✅ `.content-grid-section` - Content sections

---

## 📐 Spacing & Sizing

### Border Radius
```css
--r4: 4px;
--r6: 6px;
--r8: 8px;
--r10: 10px;
--r12: 12px;
--r14: 14px;
--rpill: 100px
```

### Shadows
```css
--shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06);
--shadow-h: 0 4px 16px rgba(0, 103, 79, .16), 0 8px 24px rgba(0,0,0,.06);
--shadow-glow: 0 0 8px rgba(0, 168, 107, 0.5);
```

### Transitions
```css
--transition-fast: 0.12s;
--transition-base: 0.2s;
--transition-slow: 0.3s;
--transition-ease: cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 🎯 Component Patterns

### KPI Cards
```html
<div class="lumra-kpi-glass">
  <div class="relative z-10 flex justify-between items-start gap-4">
    <div class="flex-1">
      <span class="text-10px font-700 text-slate-600 uppercase">{{ title }}</span>
      <div class="text-22px font-700 text-slate-800">{{ value }}</div>
    </div>
    {% if change_pct %}
    <span class="inline-flex px-2 py-1 rounded-rpill text-10px font-600"
          style="background: rgba(0, 168, 107, 0.15); color: #00674F;">
      ↑ {{ change_pct }}
    </span>
    {% endif %}
  </div>
</div>
```

### Grid/Section Containers
```html
<section class="content-grid-section px-6 py-5">
  <!-- Card background: rgba(255, 255, 255, 0.88) -->
  <!-- Border: 0.5px solid rgba(0, 103, 79, 0.08) -->
  <!-- Border-radius: 12px -->
</section>
```

### Navigation Items
```html
<a href="#" class="nav-item" :class="[active ? 'active' : '']">
  <div class="nav-icon-wrap"><i class="nav-icon"></i></div>
  <span x-show="open">{{ label }}</span>
</a>
```

---

## 🔧 Layout Structure

### Unified Layout
```
┌─────────────────────────────────────┐
│ SIDEBAR │   NAVBAR (seamless)       │
├─────────┼──────────────────────────┤
│         │  MAIN CONTENT             │
│ Border  │  - Grid sections          │
│ right   │  - Each has border        │
│         │─────────────────────────  │
└─────────────────────────────────────┘
```

- **Sidebar**: `w-[64px]` (collapsed) / `w-[240px]` (expanded)
- **Navbar**: `56px` height, sticky top
- **Content**: Full-width, with `px-4 py-6 sm:px-6 lg:px-8`
- **Sections**: Bordered cards with consistent spacing

---

## ✨ Typography

### Font
```css
font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
```

### Sizes
- Heading: `text-2xl` (32px) → `font-bold`
- Section title: `text-sm` (14px) → `font-black`
- Label/caption: `text-10px` → `font-700 uppercase`
- Body: `text-13px` → `font-500`

---

## 🎨 Hover & Active States

### Navigation Item Active
```css
.nav-item.active {
  background: rgba(0, 168, 107, 0.12);  /* Jade bg */
  color: #00674F;                        /* Emerald text */
  font-weight: 600;
}
.nav-item.active::before {
  width: 3px;
  background: #00A86B;  /* Jade glow */
  box-shadow: 0 0 8px rgba(0, 168, 107, 0.5);
}
```

### Card Hover
```css
.lumra-glass:hover,
.content-grid-section:hover {
  box-shadow: 0 4px 16px rgba(0, 103, 79, .16);
  transform: translateY(-2px);
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 767px) {
  .sidebar { position: fixed; z-index: 30; }
  .navbar { margin-left: 0; }
}

/* Tablet & Desktop */
@media (min-width: 768px) {
  .navbar { margin-left: 64px; transition: margin-left 0.3s ease; }
  .sidebar { width: 64px; }
}

/* Sidebar Open Desktop */
body.sidebar-open {
  .navbar { margin-left: 240px; }
  .content { margin-left: 240px; }
}
```

---

## ✅ Checklist untuk Setiap File HTML (IMPORTANT!)

Sebelum generate ke Claude, pastikan file memiliki:

- [ ] `{% load tailwind_tags %}` di atas
- [ ] `{% extends 'base/base.html' %}` jika page content
- [ ] KPI/card sections pakai `.lumra-kpi-glass` atau `.lumra-glass`
- [ ] Grid sections pakai `.content-grid-section`
- [ ] Borders: `0.5px solid rgba(0, 103, 79, 0.1)` atau `0.08`
- [ ] Warna teks: emerald `#00674F`, jade `#00A86B`, slate-600 `#6b8a7a`
- [ ] Hover effects: `box-shadow` + `translateY(-2px)`
- [ ] Responsive: `grid-cols-1 sm:grid-cols-2 xl:grid-cols-4` pattern
- [ ] Alpine.js directives: `x-data`, `x-show`, `@click`, etc.
- [ ] Icons: Font Awesome `.fas` dengan warna dari theme
- [ ] Mobile: hamburger pada `md:hidden`
- [ ] Z-index: navbar `z-30`, dropdown `z-50`

---

## 📚 File Status

### ✅ UPDATED (Reference untuk consistency)
- `base.html` - Design tokens + layout
- `navbar.html` - Glass morphism, seamless border
- `sidebar.html` - Nav styling, glass base
- `kpi_card.html` - Glass card pattern
- `dashboard.html` - Content structure

### ⏳ PERLU DI-UPDATE (following same pattern)
- `/auth/` pages (login, register)
- `/inventory/` pages (products, stock, etc.)
- `/master_data/` pages (categories, vendors, etc.)
- `/reports/` pages (sales, inventory, etc.)
- `/settings/` pages (profile, business, etc.)

---

## 🔗 Usage Instructions

Ketika ingin update file HTML baru:

1. **Reference file**: Lihat `base.html`, `navbar.html`, atau `dashboard.html`
2. **Apply pattern**: Copy glass morphism pattern yang sama
3. **Check colors**: Gunakan CSS tokens, bukan hardcode warna
4. **Mobile first**: Design untuk mobile, expand ke desktop
5. **Validation**: Pastikan semua checklist di atas terpenuhi

---

## 💡 Problem-Solving

### Q: Warna tidak sesuai
**A**: Gunakan CSS tokens (--em, --jade, --gold) atau rgba values. Jangan hardcode warna.

### Q: Border tidak konsisten
**A**: Konsisten pakai: `0.5px solid rgba(0, 103, 79, 0.1)` untuk emerald frosted

### Q: Layout tidak seamless
**A**: Pastikan wrapper punya background + backdropfilter, gunakan `content-grid-section`

### Q: Hover effects tidak smooth
**A**: Pakai `transition: box-shadow var(--transition-base), transform var(--transition-base)`

---

**Last Updated**: April 9, 2026  
**Theme**: Emerald Odyssey v3.0  
**Status**: 🟢 Consistent across base templates
