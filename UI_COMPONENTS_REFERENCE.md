# UI Components Reference — Emerald Odyssey Design System

Dokumentasi penggunaan components UI baru yang implementasi design pattern dari Figma.

## 📦 Components Available

### 1. **Greeting Section** (`components/greeting_section.html`)
Personalized welcome section dengan user greeting + quick stats.

```django
{% include "components/greeting_section.html" with 
    greeting_time="Good Morning"
    greeting_message="Welcome back to your dashboard"
    location="Dashboard"
    greeting_stats=greeting_stats_list
%}
```

**Context variables yang diperlukan:**
- `user` — Django user object
- `greeting_time` — Waktu (morning/afternoon/evening)
- `greeting_message` — Custom welcome message
- `location` — Current location/store
- `greeting_stats` — List of stat dicts

**Stat dict format:**
```python
{
    'label': 'Revenue',
    'value': '$12,450',
    'change': '+5.2%',
    'trend': 'positive',  # positive, negative
    'icon': 'arrow-up'
}
```

---

### 2. **Metric Cards** (`components/metric_card.html`)
Reusable KPI card component untuk display metrics.

```django
{% include "components/metric_card.html" with 
    title="Today's Sales"
    value="Rp 2.500.000"
    unit="IDR"
    status="online"
    change="+5.2%"
    change_type="up"
    subtitle="Last 30 days"
    progress_value=65
%}
```

**Available attributes:**
- `title` — Card title/label
- `value` — Main metric value
- `unit` — Unit (e.g., "IDR", "kWh")
- `subtitle` — Secondary info
- `status` — Status badge (online/offline/pending)
- `change` — Change indicator text
- `change_type` — up/down/neutral
- `progress_value` — Progress bar % (0-100)
- `badge` — Badge type (success/danger/warning)
- `badge_icon` — Icon for badge

**Multiple cards di grid:**
```html
<div class="metric-cards-grid">
  {% for card in metric_cards %}
    {% include "components/metric_card.html" with card=card %}
  {% endfor %}
</div>
```

---

### 3. **Content Section** (`components/content_section.html`)
Container untuk content sections dengan header, body, footer.

```django
{% include "components/content_section.html" with 
    title="Recent Transactions"
    description="Last 30 days"
    icon="receipt"
    icon_type="success"
    show_header=True
    show_footer=True
    footer_meta="Updated 2 minutes ago"
    content=content_html
%}
```

**Available attributes:**
- `title` — Section title
- `description` — Section subtitle
- `section_label` — Label tag
- `icon` — FontAwesome icon name
- `icon_type` — primary/success/warning/danger
- `show_header` — Show section header
- `show_footer` — Show section footer
- `content` — Inner HTML content
- `footer_meta` — Footer metadata text
- `action_label` — CTA button label
- `action_link` — CTA button link
- `footer_actions` — Show "View All" button

---

### 4. **Dashboard Layout** (`layouts/dashboard_layout.html`)
Master layout yang combine greeting + metrics + sections.

```django
{% extends "layouts/dashboard_layout.html" %}

{% block dashboard_primary %}
  {# Main content column #}
{% endblock %}

{% block dashboard_sidebar %}
  {# Sidebar content #}
{% endblock %}
```

**Context untuk layout:**
```python
context = {
    'show_greeting': True,
    'greeting_time': 'Good Morning',
    'greeting_message': 'Welcome back',
    'location': 'Jakarta HQ',
    'greeting_stats': [...],
    
    'metrics_title': 'Key Metrics',
    'metrics_label': 'OVERVIEW',
    'metric_cards': [
        {'title': '...', 'value': '...', ...},
    ],
}
```

---

## 🎨 CSS Organization

Semua styles sudah ter-define di:
- **Base theme**: `base.html` — Color variables, typography, glass effects
- **Navbar**: `navbar.html` — Command bar styling
- **Sidebar**: `sidebar.html` — Navigation styling
- **Dashboard**: `lumra_pages/sales_insight/dashboard.html` — Metric card styles

### Color Tokens (dari Emerald Odyssey):
```css
--em: #00674F;              /* Primary Emerald */
--jade: #00A86B;            /* Secondary Jade */
--gold: #EFBF04;            /* Accent Gold */
--cream: #FDFBD4;           /* Neutral Cream */
--navy: #000080;            /* Contrast Navy */
```

---

## 📐 Responsive Grid

Semua components responsive:
- **Mobile**: 1 column
- **Tablet (md)**: 2 columns
- **Desktop (lg)**: 3-4 columns
- **Wide (xl)**: Full grid

---

## 🔌 JavaScript/Alpine Integration

Components use Alpine.js for interactivity:

```javascript
// Greeting data
x-data="greetingData()" 
x-text="userName"
x-text="activeLocation"

// Animations
x-transition:enter="..."
x-transition:leave="..."
```

---

## 🚀 Implementation Example

**Dashboard dengan greeting + metrics + content:**

```django
{% extends "base/base.html" %}

{% block extra_css %}
  {# Component styles #}
{% endblock %}

{% block content %}
  <!-- Greeting -->
  {% include "components/greeting_section.html" with ... %}
  
  <!-- Metrics Grid -->
  <section>
    <div class="metric-cards-grid">
      {% for card in metric_cards %}
        {% include "components/metric_card.html" with ... %}
      {% endfor %}
    </div>
  </section>
  
  <!-- Content Sections Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Primary -->
    <div class="lg:col-span-2">
      {% include "components/content_section.html" with ... %}
    </div>
    
    <!-- Sidebar -->
    <div>
      {% include "components/content_section.html" with ... %}
    </div>
  </div>
{% endblock %}
```

---

## ✨ Features

✅ Glass morphism effects dengan blur & transparency
✅ Smooth animations & transitions (0.2s cubic-bezier)
✅ Responsive design (mobile-first)
✅ Accessible (ARIA labels, semantic HTML)
✅ Dark mode ready (CSS variables)
✅ Interactive status indicators & badges
✅ Progress bars & mini charts support
✅ Hover effects & elevation changes

---

## 📝 Tips & Best Practices

1. **Always pass Django context variables** — Jangan hardcode values
2. **Use semantic icons** — FontAwesome icons di `icon` attribute
3. **Consistent spacing** — Gunakan grid system yang sudah ada
4. **Progressive enhancement** — Components work tanpa JavaScript
5. **Accessibility** — Semua components punya ARIA labels

---

## 🔄 Migration Guide

**Dari old dashboard ke new components:**

```django
<!-- OLD -->
<article class="kpi-card today-sales kpi-glass ...">
  <p>{{ kpis.today_sales }}</p>
</article>

<!-- NEW -->
{% include "components/metric_card.html" with 
    title="Today's Sales"
    value=kpis.today_sales
    status="online"
%}
```

---

## 📞 Questions?

Refer ke:
- **Figma design**: https://syrup-text-13395340.figma.site/
- **Base template**: `templates/base/base.html`
- **Example dashboard**: `lumra_pages/sales_insight/dashboard.html`

---

Last Updated: April 13, 2026
Design System: Emerald Odyssey v3.0
