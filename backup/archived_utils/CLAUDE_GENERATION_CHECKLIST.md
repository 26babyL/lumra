# 📋 CLAUDE HTML Template Generation Checklist
**Panduan untuk generate/update semua HTML templates dengan konsisten**

---

## 🎯 SEBELUM GENERATE KE CLAUDE

### Step 1: Reference Documents Ready
- [ ] `LUMRA_DESIGN_SYSTEM_REFERENCE.md` sudah dibaca
- [ ] Color palette tokens sudah dipahami
- [ ] Glass morphism pattern sudah jelas
- [ ] Layout structure sudah dipahami

### Step 2: Context Disiapkan
```
Instruksi untuk Claude:

"Perbarui/buat HTML template sesuai **Emerald Odyssey Design System**:
- Reference: LUMRA_DESIGN_SYSTEM_REFERENCE.md
- Warna: Gunakan CSS tokens (--em, --jade, --gold, dll)
- Glass effect: backdrop-filter blur(12px) + saturate(180%)
- Layout: Seamless navbar + sidebar + content
- Spacing: Gunakan increments 4/6/8/12/16/24px
- Typography: Plus Jakarta Sans dengan semantic weights
- Mobile first: @media (max-width: 767px) untuk mobile
- Responsive: Grid columns: 1 sm:2 md:3 lg:4 xl:6
- Border: 0.5px solid rgba(0, 103, 79, 0.1) untuk sections
- Hover: box-shadow + translateY(-2px)
- Checklist: [lihat section TEMPLATE_STRUCTURE di bawah]"
```

---

## 🏗️ TEMPLATE STRUCTURE (copy-paste untuk Claude)

Setiap HTML template harus memiliki struktur ini:

### Header/Meta
```html
{% load tailwind_tags %}
{% extends 'base/base.html' %}

{% block title %}Page Title{% endblock %}
{% block description %}Brief description{% endblock %}
{% block content %}
```

### Section Pattern
```html
<section class="content-grid-section px-6 py-5">
  <!-- Header Row -->
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-20px font-700 text-slate-800">Section Title</h2>
    <button class="inline-flex px-4 py-2 rounded-r10 gap-2 glass-base hover:shadow-h transition">
      <i class="fas fa-plus text-em"></i> Action
    </button>
  </div>
  
  <!-- Content -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {% for item in items %}
    <div class="lumra-glass p-4">
      <!-- Card content -->
    </div>
    {% endfor %}
  </div>
</section>
```

### KPI Card Pattern
```html
<div class="lumra-kpi-glass">
  <div class="relative z-10 flex justify-between items-start gap-4">
    <div class="flex-1">
      <span class="text-10px font-700 text-slate-600 uppercase">Label</span>
      <div class="text-22px font-700 text-slate-800">{{ value }}</div>
    </div>
    {% if change_pct %}
    <span class="inline-flex px-2 py-1 rounded-rpill text-10px font-600 bg-jade-12 text-em">
      ↑ {{ change_pct }}%
    </span>
    {% endif %}
  </div>
</section>
```

### Form Pattern
```html
<form class="space-y-4 p-6">
  <div>
    <label class="block text-13px font-600 text-slate-800 mb-2">Field Label</label>
    <input type="text" 
           class="w-full px-4 py-2.5 rounded-r8 glass-base text-13px
                  focus:outline-none focus:ring-2 focus:ring-jade
                  placeholder:text-slate-400"
           placeholder="Enter value">
  </div>
  
  <button type="submit" 
          class="w-full px-4 py-2.5 bg-em text-cream rounded-r8 
                 font-600 hover:shadow-glow transition">
    Submit
  </button>
</form>
```

---

## ✅ VALIDATION CHECKLIST

Setiap section harus lolos checklist ini:

### Color & Styling
- [ ] ✓ Semua warna dari CSS tokens (--em, --jade, --gold, --slate-*)
- [ ] ✓ Jangan hardcode warna #123abc
- [ ] ✓ Background cards: rgba(255,255,255,0.92) atau `glass-base` class
- [ ] ✓ Borders: `0.5px solid rgba(0, 103, 79, 0.1)` untuk konsistensi
- [ ] ✓ Text color: `text-slate-800` (heading), `text-slate-600` (body)
- [ ] ✓ Secondary color: `text-em` atau `text-jade` untuk emphasis

### Typography
- [ ] ✓ Font: Plus Jakarta Sans (sudah di base.html)
- [ ] ✓ Heading: `text-20px font-700` atau `text-22px font-800`
- [ ] ✓ Body: `text-13px font-500`
- [ ] ✓ Label: `text-10px font-700 uppercase`
- [ ] ✓ Jangan mix font families

### Spacing & Layout
- [ ] ✓ Padding/margin: 4, 6, 8, 12, 16, 24, 32 px (grid increments)
- [ ] ✓ Gap antara items: `gap-4` atau `gap-6`
- [ ] ✓ Sections: `px-6 py-5` minimal
- [ ] ✓ Cards dalam grid: responsive columns

### Responsive Design
- [ ] ✓ Mobile: `grid-cols-1` (single column)
- [ ] ✓ Tablet: `sm:grid-cols-2` atau `md:grid-cols-2`
- [ ] ✓ Desktop: `lg:grid-cols-3` atau `xl:grid-cols-4`
- [ ] ✓ Mobile navigation: sidebar hidden, hamburger visible
- [ ] ✓ Max-width container: `max-w-7xl` jika needed

### Interactions & Animations
- [ ] ✓ Hover: `hover:shadow-h` untuk cards
- [ ] ✓ Hover text: `hover:text-jade` untuk links
- [ ] ✓ Button hover: `hover:bg-opacity-90` atau shadow upgrade
- [ ] ✓ Focus states: `focus:outline-none focus:ring-2 focus:ring-jade`
- [ ] ✓ Transitions: `transition` atau `transition-all` untuk smoothness

### Accessibility & Semantics
- [ ] ✓ Semantic HTML: `<section>`, `<article>`, `<header>`, `<button>`
- [ ] ✓ ARIA labels: `aria-label` untuk buttons tanpa text
- [ ] ✓ Form labels: `<label for="id">` connected ke input
- [ ] ✓ Alt text: Images punya `alt` attribute
- [ ] ✓ Keyboard navigation: Tab order reasonable

### Alpine.js Integration (jika needed)
- [ ] ✓ `x-data` untuk state management
- [ ] ✓ `@click` untuk interactions
- [ ] ✓ `x-show` atau `x-if` untuk conditional rendering
- [ ] ✓ Event handlers: `@submit.prevent`, `@blur`, etc.

---

## 📝 COPY-PASTE SNIPPETS

### Emerald Button
```html
<button class="inline-flex items-center px-4 py-2 rounded-r8 gap-2 
               bg-em text-cream hover:shadow-h transition font-600">
  <i class="fas fa-icon"></i> Button Text
</button>
```

### Glass Card
```html
<div class="glass-base p-6 rounded-r12 hover:shadow-h transition">
  <!-- content -->
</div>
```

### Section Header
```html
<div class="flex items-center justify-between mb-6">
  <h2 class="text-20px font-700 text-slate-800">Header</h2>
  <a href="#" class="text-13px text-jade font-600 hover:underline">View all</a>
</div>
```

### Grid Container
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {% for item in items %}
  <div class="lumra-glass p-4"><!-- content --></div>
  {% endfor %}
</div>
```

### Form Input
```html
<input type="text" 
       class="w-full px-4 py-2.5 rounded-r8 glass-base 
              text-13px border-0 focus:outline-none 
              focus:ring-2 focus:ring-jade transition"
       placeholder="Placeholder text">
```

---

## 🚀 GENERATE WORKFLOW

### Workflow Step 1: Siapkan Prompt
```
Context yang perlu diberikan ke Claude:

1. Reference: "Lihat LUMRA_DESIGN_SYSTEM_REFERENCE.md"
2. Template: "Gunakan section pattern di bawah"
3. Checklist: "Pastikan semua items di ✓ VALIDATION CHECKLIST"
4. File: "[Paste template file content atau describe changes]"
5. Constraint: "Hanya CSS Tailwind + inline glass-base class, jangan inline style"
```

### Workflow Step 2: Send ke Claude
```
@claude 
Perbarui/buat file: [filename]
Gunakan design system: LUMRA_DESIGN_SYSTEM_REFERENCE.md
Pattern: [paste relevant section pattern]
Checklist requirement: [paste validation checklist]

[Content to generate/update]
```

### Workflow Step 3: Validate Output
- [ ] ✓ Semua checklist items tercapai?
- [ ] ✓ Colors sesuai tokens?
- [ ] ✓ Responsive pada mobile/tablet/desktop?
- [ ] ✓ Spacing konsisten?
- [ ] ✓ Hover effects smooth?

### Workflow Step 4: Review & Merge
- [ ] ✓ Copy file to templates/
- [ ] ✓ Test di browser (mobile + desktop)
- [ ] ✓ Check console: no errors/warnings
- [ ] ✓ Verify links working

---

## 🎯 PRIORITY MODULES (untuk di-update)

### HIGH PRIORITY (banyak users lihat)
1. `/lumra_pages/sales_insight/` - Dashboard, sales report
2. `/lumra_pages/inventory/` - Product list, stock
3. `/lumra_pages/reports/` - All reports pages

### MEDIUM PRIORITY
4. `/lumra_pages/master_data/` - Categories, vendors, settings
5. `/lumra_pages/settings/` - Profile, business, users

### LOW PRIORITY
6. `/lumra_pages/auth/` - Login, register (sudah standard)
7. `/lumra_pages/messages/` - Chat/messaging pages
8. `/lumra_pages/marketing/` - Promo, campaigns
9. `/lumra_pages/production/` - Prod planning pages

---

## 🔍 QUICK DEBUGGING

### Problem: Warna tidak Emerald
```
❌ style="color: #00674F"
✅ class="text-em" atau inline jika needed: style="color: var(--em)"
```

### Problem: Card tidak glass effect
```
❌ class="bg-white border border-gray-300"
✅ class="glass-base"
```

### Problem: Button terlalu besar/kecil
```
❌ class="px-8 py-4"
✅ class="px-4 py-2.5" (mobile first) + "md:px-6 md:py-3" (desktop)
```

### Problem: Text alignment kacau mobile
```
❌ class="flex justify-between" (cramped on mobile)
✅ class="flex flex-col gap-2 sm:flex-row sm:justify-between"
```

---

## 📚 Related Documents
- **Design System**: `LUMRA_DESIGN_SYSTEM_REFERENCE.md`
- **Status Report**: `LUMRA_TEMPLATES_AUDIT_STATUS.md`
- **Base Files**: `/lumra_config/templates/base/` (reference implementations)

---

**Last Updated**: April 9, 2026  
**Version**: 3.0  
**Status**: 🟢 Ready for Claude generation
