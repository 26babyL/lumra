# ⚡ QUICK REFERENCE - Emerald Odyssey for Claude
**Copy-paste ini langsung ke Claude ketika request generate HTML templates**

---

## 🚀 READY-TO-USE PROMPT TEMPLATE

```
@claude

Perbarui/buat file HTML template dengan Emerald Odyssey Design System 3.0

REFERENCE DOCUMENTS (dalam project):
- LUMRA_DESIGN_SYSTEM_REFERENCE.md
- CLAUDE_GENERATION_CHECKLIST.md

COLOR PALETTE (gunakan variabel):
--em: #00674F           (Emerald - primary)
--jade: #00A86B         (Secondary)
--gold: #EFBF04         (Accent)
--slate-600: #6b8a7a    (Text)
--slate-400: #94a3b8    (Label)
--slate-300: #cbd5e1    (Muted)

GLASS MORPHISM (semua cards):
- Background: rgba(255, 255, 255, 0.92)
- Backdrop: blur(12px) saturate(180%)
- Border: 0.5px solid rgba(0, 103, 79, 0.1)
- Radius: 8px (r8) atau 14px (r14)

PATTERN YANG SELALU DIPAKAI:
✓ Section wrapper: class="content-grid-section px-6 py-5"
✓ Cards dalam grid: class="lumra-glass p-4"
✓ KPI cards: class="lumra-kpi-glass"
✓ Form input: class="glass-base"
✓ Buttons: bg-em (Emerald) atau bg-jade (Jade)

RESPONSIVE GRID:
- Mobile: grid-cols-1
- Tablet: sm:grid-cols-2 atau md:grid-cols-2
- Desktop: lg:grid-cols-3 atau xl:grid-cols-4

TYPOGRAPHY:
- Font: Plus Jakarta Sans (dari base.html)
- Heading: text-20px font-700
- Body: text-13px font-500
- Label: text-10px font-700 uppercase

HOVER EFFECTS:
- Cards: hover:shadow-h transition
- Texts: hover:text-jade transition
- Buttons: hover:bg-opacity-90

VALIDATION CHECKLIST sebelum approve:
☑ Warna dari CSS tokens (--em, --jade, --gold, --slate-*)
☑ Glass effect pada semua cards/sections
☑ Responsive: mobile (cols-1) → desktop (cols-3/4)
☑ Spacing grid: 4/6/8/12/16/24px saja
☑ Font: Plus Jakarta Sans (tidak mix fonts)
☑ Borders: 0.5px solid rgba(0, 103, 79, 0.1) konsisten
☑ Hover states smooth dengan transition
☑ Form: input dengan glass-base, focus:ring-2 focus:ring-jade
☑ Accessibility: semantic HTML, aria-label, alt text
☑ Alpine.js: x-data, @click, x-show jika needed

FILE STRUKTUR:
{% load tailwind_tags %}
{% extends 'base/base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
<section class="content-grid-section px-6 py-5">
  <!-- content here -->
</section>
{% endblock %}

[TASK HERE]
```

---

## 🎨 CSS CLASSES (Copy-Paste Ready)

### Background/Glass
```
.glass-base                 → rgba(255,255,255,0.92) + blur(12px)
.lumra-glass                → Glass card default
.lumra-kpi-glass            → Glass card for metrics
.nav-glass                  → Navbar styling
.sidebar-glass              → Sidebar styling
.content-grid-section       → Section wrapper (px-6 py-5)
```

### Text Colors
```
text-em                     → #00674F (Emerald)
text-jade                   → #00A86B (Jade)
text-gold                   → #EFBF04 (Gold)
text-slate-800              → Heading text
text-slate-600              → Body text
text-slate-400              → Label text
```

### Backgrounds
```
bg-em                       → Emerald button
bg-jade                     → Jade accent
bg-gold                     → Gold highlight
bg-slate-100                → Light background
```

### Hover/Interactive
```
hover:shadow-h              → Card elevation
hover:text-jade             → Text color on hover
hover:bg-opacity-90         → Button fade
focus:ring-2 focus:ring-jade → Input focus
```

### Sizing
```
w-full                      → Full width
max-w-7xl                   → Container limit
min-h-screen                → Full viewport height
h-[52px]                    → Navbar height
w-[64px]                    → Sidebar collapsed
w-[240px]                   → Sidebar expanded
```

### Spacing (Grid 4/6/8/12/16/24px)
```
px-4 py-2.5                 → Button/input default
px-6 py-5                   → Section/card default
gap-4                       → Grid/flex gap
mb-4 / mt-4                 → Vertical spacing
```

### Grid/Flex
```
grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4
flex items-center justify-between
flex-col gap-2 sm:flex-row sm:justify-between
```

### Borders/Radius
```
rounded-r8                  → 8px (default card)
rounded-r12                 → 12px (larger)
rounded-r14                 → 14px (KPI cards)
rounded-rpill               → 100px (pill shape)
border-b border-t border-l border-r       → Individual borders
border-0.5 [rgba(0,103,79,0.1)]           → Emerald frost border
```

---

## 📋 COMPONENT SNIPPETS

### KPI Card
```html
<div class="lumra-kpi-glass">
  <div class="relative z-10 flex justify-between items-start gap-4">
    <div class="flex-1">
      <span class="text-10px font-700 text-slate-600 uppercase">Label</span>
      <div class="text-22px font-700 text-slate-800">{{ value }}</div>
    </div>
    {% if change_pct %}
    <span class="inline-flex px-2 py-1 rounded-rpill text-10px font-600 
                 bg-jade-12 text-em">
      ↑ {{ change_pct }}%
    </span>
    {% endif %}
  </div>
</div>
```

### Section Header
```html
<div class="flex items-center justify-between mb-6">
  <h2 class="text-20px font-700 text-slate-800">Section Title</h2>
  <a href="#" class="text-13px text-jade font-600 hover:underline">View all</a>
</div>
```

### Emerald Button
```html
<button class="inline-flex items-center px-4 py-2 rounded-r8 gap-2 
               bg-em text-cream hover:shadow-h transition font-600">
  <i class="fas fa-icon"></i> Button Text
</button>
```

### Form Input Group
```html
<div>
  <label class="block text-13px font-600 text-slate-800 mb-2">Field Label</label>
  <input type="text" 
         class="w-full px-4 py-2.5 rounded-r8 glass-base 
                text-13px focus:outline-none 
                focus:ring-2 focus:ring-jade transition"
         placeholder="Enter value">
</div>
```

### Grid Container
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {% for item in items %}
  <div class="lumra-glass p-4">
    <h3 class="text-13px font-600 text-slate-800">{{ item.name }}</h3>
    <p class="text-13px text-slate-600">{{ item.description }}</p>
  </div>
  {% endfor %}
</div>
```

### Table Header
```html
<table class="w-full">
  <thead>
    <tr class="border-b border-0.5 border-em-10">
      <th class="px-4 py-3 text-left text-10px font-700 text-slate-600 uppercase">
        Column 1
      </th>
      <th class="px-4 py-3 text-left text-10px font-700 text-slate-600 uppercase">
        Column 2
      </th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr class="border-b border-0.5 border-em-08 hover:bg-em-08 transition">
      <td class="px-4 py-3 text-13px text-slate-800">{{ row.col1 }}</td>
      <td class="px-4 py-3 text-13px text-slate-600">{{ row.col2 }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
```

### Mobile Responsive
```html
<!-- Hamburger pada mobile -->
<button class="md:hidden" @click="open = !open">
  <i class="fas fa-bars"></i>
</button>

<!-- Content shift -->
<div class="md:ml-64">
  <!-- Content dengan sidebar open di desktop -->
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {% for item in items %}<div>...</div>{% endfor %}
</div>
```

---

## ❌ ANTI-PATTERNS (Jangan lakukan ini!)

```
❌ Hardcoded warna
   style="background-color: #ffffff"
✅ Gunakan CSS tokens
   class="glass-base"

❌ Inline style everywhere
   <div style="padding: 16px; margin: 8px;">
✅ Gunakan Tailwind classes
   <div class="p-4 m-2">

❌ Custom CSS di file
   <style>.my-custom { color: #abc; }</style>
✅ Semua styling di base.html atau Tailwind config

❌ Inconsistent spacing
   <div style="padding: 5px 10px 7px 15px;">
✅ Grid spacing: 4/6/8/12/16/24px saja
   <div class="px-4 py-2">

❌ Different fonts
   font-family: Arial, Roboto, 'Comic Sans'
✅ Selalu Plus Jakarta Sans
   (sudah di base.html)

❌ No responsive
   <div class="w-[400px]">
✅ Mobile-first responsive
   <div class="w-full md:w-1/2 lg:w-1/3">

❌ Inconsistent colors
   <span class="text-green-500">
✅ Gunakan theme palette
   <span class="text-jade">

❌ No hover states
   <button class="bg-blue-500">
✅ Proper interactions
   <button class="bg-em hover:shadow-h transition">
```

---

## 🔍 DEBUGGING QUICK FIXES

| Problem | Solution |
|---------|----------|
| Warna tidak Emerald | Class `text-em` atau inline `style="color: var(--em)"` |
| Card tidak glass | Class `glass-base` atau `lumra-glass` |
| Terlalu besar spacing | Kurangi: `px-8 py-4` → `px-4 py-2.5` |
| Mobile cramped | Add `flex-col gap-2 sm:flex-row` |
| Border tebal/salah | Use `border-0.5 border-em-10` |
| Hover tidak smooth | Add `transition` atau `transition-all` |
| Form input blur | Add `focus:ring-2 focus:ring-jade focus:outline-none` |
| Grid tidak responsive | Add `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` |
| Font berbeda | Remove custom fonts, base.html sudah Plus Jakarta Sans |
| Shadow terlalu besar | Use `shadow` atau `hover:shadow-h` saja |

---

## 📊 VALIDATION BEFORE SUBMITTING

```javascript
// Checklist items (copy to Claude)
✓ npm run build / python manage.py tailwind build (no errors)
✓ Responsive tested (mobile 360px, tablet 768px, desktop 1920px)
✓ All colors are CSS tokens (no #123abc)
✓ All spacing is 4/6/8/12/16/24px grid
✓ No inline styles except data attributes
✓ No custom CSS files
✓ Hover states smooth with transition
✓ Form fields have focus:ring states
✓ Buttons are emerald or jade
✓ Tables have alternating row hover
✓ Mobile navigation functional
✓ Accessibility: aria-label, semantic HTML
✓ No console errors/warnings
✓ Load time under 3s
```

---

## 🎯 EXAMPLE FULL PROMPT FOR CLAUDE

```
@claude

Update dashboard.html to match Emerald Odyssey Design System.

REFERENCE:
- Design System: d:\APPS\Project\lumra\LUMRA_DESIGN_SYSTEM_REFERENCE.md
- Checklist: d:\APPS\Project\lumra\CLAUDE_GENERATION_CHECKLIST.md

KEY REQUIREMENTS:
1. All KPI cards use .lumra-kpi-glass class
2. Sections wrapped in .content-grid-section
3. Grid responsive: grid-cols-1 sm:grid-cols-2 lg:grid-cols-4
4. Colors: Use --em (Emerald), --jade, --gold tokens only
5. No inline styles, only Tailwind classes
6. Glass effect: blur(12px) saturate(180%)
7. Borders: 0.5px solid rgba(0, 103, 79, 0.1)
8. Hover: hover:shadow-h transition
9. Focus: focus:ring-2 focus:ring-jade
10. Mobile responsive

VALIDATION REQUIRED:
☐ No hardcoded colors
☐ All sections have .content-grid-section
☐ KPI cards have change % badge
☐ Grid responsive (1 col mobile, 2 tablet, 4 desktop)
☐ Buttons are bg-em or bg-jade
☐ Forms use glass-base inputs
☐ Hover states smooth
☐ Mobile navigation hidden (md:hidden)

[CONTENT TO UPDATE]
```

---

## 📞 SUPPORT COMMANDS

**When you get CSS errors:**
```
Run: python manage.py tailwind build
Should see: ✓ Built successfully
If error, check: base.html for :root tokens
```

**When layout breaks:**
```
Check: grid classes (grid-cols-1 sm:grid-cols--2 etc)
Check: sidebar width (w-64 or w-[240px])
Check: navbar height (h-[56px])
Check: content padding (px-6 py-5)
```

**When colors wrong:**
```
Check: Using CSS tokens (--em, --jade, --gold)
Check: No hardcoded colors #123abc
Fix: Replace hex colors with class names
```

---

**Last Updated**: April 9, 2026  
**For**: Claude HTML Template Generation  
**Status**: ✅ Ready to Use  
**Next**: Copy appropriate section and send to Claude!
