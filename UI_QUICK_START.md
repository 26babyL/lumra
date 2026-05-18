# 🎨 Emerald Odyssey UI — Quick Start

**Design System Implementasi dari Figma** ✨

---

## ✅ Apa Yang Sudah Di-Update

### 1. **Greeting Section** — "Hello, [User]! 👋"
- Personalized welcome dengan user name
- Quick stats row (Ready, Stores, Sync, Users)
- Status indicator & location badge
- Professional typography hierarchy

📍 **Lokasi**: `templates/components/greeting_section.html`

### 2. **Metric Cards** — KPI Display Pattern
- Glass morphism effect (blur + transparency)
- Status badges (online/offline/pending)
- Change indicators (up/down trends)
- Progress bars (optional)
- Smooth hover animations

📍 **Lokasi**: `templates/components/metric_card.html`

### 3. **Content Sections** — Organized Containers
- Header dengan icon + title + actions
- Body untuk content free-form
- Footer dengan metadata + action buttons
- Responsive layouts

📍 **Lokasi**: `templates/components/content_section.html`

### 4. **Dashboard Layout** — Master Template
- Greeting + Metrics + Sections integrated
- Responsive grid (mobile-first)
- Primary + Sidebar columns

📍 **Lokasi**: `templates/layouts/dashboard_layout.html`

### 5. **Updated Dashboard** — Sales Insight
- Greeting section di awal dengan welcome message
- Improved KPI cards dengan metric-card styling
- Better spacing & visual hierarchy
- Menu selain tetap sama (store switcher, date picker, etc)

📍 **Lokasi**: `lumra_pages/sales_insight/dashboard.html`

---

## 🚀 How to Use

### **Di Dashboard Existing:**

Greeting section sudah auto-rendered dengan:
- User first name dari Django `user.first_name`
- Status indicators (Active, Ready, Stores count, etc)
- Responsive grid layout

### **Di Page Lain:**

```django
{# Include greeting #}
{% include "components/greeting_section.html" with 
    greeting_message="Your custom message"
    location="Custom Location"
%}

{# Metric card grid #}
<div class="metric-cards-grid">
  {% include "components/metric_card.html" with 
      title="Card Title"
      value="Value"
      change="+5%"
      change_type="up"
  %}
</div>

{# Content section #}
{% include "components/content_section.html" with 
    title="Section Title"
    content=content_html
%}
```

---

## 🎯 Design Features

✨ **Visual Elements:**
- Glass morphism with 12px blur + 180% saturation
- Smooth 0.2s animations with cubic-bezier easing
- Hover effects dengan elevation (+2px translateY)
- Border colors dari Emerald palette (#00674F)

🎨 **Color Palette (Emerald Odyssey):**
- **Primary**: #00674F (Deep Emerald)
- **Secondary**: #00A86B (Jade)
- **Accent**: #EFBF04 (Gold)
- **Text**: #1e293b (Slate-800)
- **Muted**: #94a3b8 (Slate-400)

📦 **Responsive:**
- Mobile (< 640px): Single column
- Tablet (640-1024px): 2 columns
- Desktop (> 1024px): 3-4 columns
- Wide (> 1280px): Full grid

---

## 📂 File Structure

```
lumra_config/templates/
├── base/
│   ├── base.html ────────────── Master layout (design tokens)
│   ├── navbar.html ──────────── Command bar
│   └── sidebar.html ─────────── Navigation
├── components/
│   ├── greeting_section.html ── Welcome card
│   ├── metric_card.html ─────── KPI card
│   └── content_section.html ─── Container
├── layouts/
│   └── dashboard_layout.html ── Master dashboard
└── lumra_pages/sales_insight/
    └── dashboard.html ────────── Example implementation
```

---

## 🔄 Menu/Navigation — Unchanged

Semua menu yang ada tetap preserved:
- ✅ Store switcher
- ✅ Date period picker
- ✅ Live indicator  
- ✅ Hamburger toggle (mobile)
- ✅ All existing functionality

Only **styling** yang improved, structure tetap sama!

---

## 💡 Tips

1. **Greeting stats** — Pass dari context/view untuk dynamic data
2. **Metric cards** — Loop dari data list untuk multiple cards
3. **Content sections** — Gunakan untuk organize report/tables/charts
4. **Keep it simple** — Components sudah handle styling, focus on content
5. **Responsive first** — Semua components mobile-friendly

---

## 📸 Visual Reference

Design pattern mengikuti Figma design:
- **Greeting**: Like "Hello, Liam Gallagher!" dengan user info
- **Metrics**: Like KVA, KWH, KVAR, PF cards dengan values
- **Layout**: Clean sidebar + navbar + main content

---

## 🚦 Current Status

| Component | Status | Location |
|-----------|--------|----------|
| Greeting Section | ✅ Ready | `components/` |
| Metric Cards | ✅ Ready | `components/` |
| Content Section | ✅ Ready | `components/` |
| Dashboard Layout | ✅ Ready | `layouts/` |
| Sales Dashboard | ✅ Updated | `lumra_pages/sales_insight/` |

---

## 🎓 Next Steps

1. **Test on different pages** — Copy patterns ke pages lain
2. **Customize colors** — Gunakan CSS variables di `:root`
3. **Add animations** — Alpine.js transitions sudah siap
4. **Mobile test** — Verify responsive di mobile devices
5. **Integrate data** — Pass context dari Django views

---

## 📚 Full Documentation

Lihat: [`UI_COMPONENTS_REFERENCE.md`](UI_COMPONENTS_REFERENCE.md)

---

**Design System**: Emerald Odyssey v3.0
**Last Updated**: April 13, 2026
**Status**: ✅ Production Ready
