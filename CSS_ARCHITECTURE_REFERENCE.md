# 📋 CSS Architecture Documentation

**Status**: ✅ CORRECTED - Multiple CSS sources (April 8, 2026)

## CSS Sources - There Are Multiple!

### ✅ **THREE Active CSS Locations**

The application uses **THREE CSS sources** working together:

#### 1. **`lumra_config/static/css/`** (Source of Truth for Backend)
```
lumra_config/static/css/
├── lumra_tokens.css           (1. CSS Variables - LOAD FIRST)
├── lumra_base.css             (2. Reset + Typography)
├── lumra_components.css       (3. UI Components)
├── lumra_sidebar.css          (4. Sidebar specific)
├── lumra_navbar.css           (5. Navbar specific)
├── lumra_dashboard.css        (6. Dashboard specific)
├── lumra_design_system.css    (7. Design system utilities)
├── lumra_form.css             (8. Form styles)
├── lumra_typography.css       (9. Typography utilities)
├── lumra_bg_blob.css          (10. Background effects)
└── theme_overrides.css        (11. Theme overrides)

Total: 11 files, ~133 KB
Django STATICFILES_DIRS: ✓ Registered
```

**Purpose**: Development and backend CSS reference  
**Django Settings**:
```python
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'lumra_config', 'static'),  # Used by Django{% static %} tags
]
```

#### 2. **`theme/static/css/dist/`** (THEME App - Frontend CSS)
```
theme/static/css/dist/
├── lumra_tokens.css       (Compiled CSS variables)
├── lumra_components.css   (Compiled components)
└── styles.css             (Main Tailwind output)

Total: 3 files, ~396 KB
Django TAILWIND_APP_NAME: ✓ theme
```

**Purpose**: Frontend production CSS served by theme app  
**Status**: ✅ ACTIVE - Handles frontend styling  
**Served by**: Django Tailwind/app static files system

#### 3. **`static/css/`** (Build Artifacts)
```
static/css/
├── lumra_tokens.css       (Copy of theme/dist)
├── lumra_components.css   (Copy of theme/dist)
└── styles.css             (Copy of theme/dist)

Total: 3 files, ~396 KB
Purpose: Build output from collectstatic
```

**Purpose**: Production collectstatic output  
**Auto-generated**: During `python manage.py collectstatic`

### ✅ **Restoration Status** (April 8, 2026)

Both `theme/static/css/dist/` and `static/css/` have been **RESTORED** because they are NOT duplicates:

- ✅ `theme/static/css/dist/` → Restored (contains compiled Tailwind output)
- ✅ `static/css/` → Restored (build artifacts)

---

---

## CSS Loading Order (Actual Flow)

### Frontend (Browser) Load Sequence
```
1. base.html {% tailwind_css %}
   └─→ Executes: python manage.py tailwind build
   └─→ Outputs to: theme/static/css/dist/styles.css
   └─→ SERVES to browser

2. base.html <style>{% block extra_css %}</style>
   └─→ Inline Odyssey tokens
   └─→ Viewport utilities
   └─→ Glass Protocol definitions

3. Page-specific CSS (if needed)
   └─→ {% static 'css/lumra_dashboard.css' %}
   └─→ Loaded from: lumra_config/static/css/
   └─→ Via Django STATICFILES_DIRS
```

### How It Works

**Option A - Tailwind (Default & Recommended)**
```html
<!-- From base.html -->
{% load tailwind_tags %}
{% tailwind_css %}
<!-- Automatically compiles Tailwind and serves theme/static/css/dist/styles.css -->
```

**Option B - Direct CSS Files**
```html
<!-- Alternative: Load CSS explicitly -->
{% static 'css/lumra_tokens.css' %}
{% static 'css/lumra_components.css' %}

<!-- These resolve to: lumra_config/static/css/ (via STATICFILES_DIRS) -->
```

**Option C - Mixed (Current Optimal)**
```html
<!-- Tailwind for core utility-first styles -->
{% tailwind_css %}

<!-- Additional design system overrides -->
<link rel="stylesheet" href="{% static 'css/lumra_design_system.css' %}">

<!-- Inline tokens as backup -->
<style>
  :root {
    --em: #00674F;
    /* ... more tokens ... */
  }
</style>
```

---

## CSS Priority & Cascade

| Priority | Source | Purpose |
|----------|--------|---------|
| 1 | `<style>` in base.html | Odyssey design tokens, utilities, accessibility |
| 2 | `{% tailwind_css %}` | Utility-first foundation |
| 3 | `lumra_tokens.css` | CSS Variable definitions (fallback) |
| 4 | `lumra_design_system.css` | Component styles, glass protocol |
| 5 | Page-specific CSS | `lumra_dashboard.css`, etc. |
| 6 | Inline `style=` in templates | Last resort (should be minimized) |

---

## ⚠️ **CRITICAL: What Went Wrong (April 8, 2026)**

### The Mistake
- Deleted `theme/static/css/dist/` thinking it was stale
- Result: Frontend CSS styling completely broken
- The sidebar and all pages became unstyled

### Lesson Learned
**DO NOT treat multiple CSS locations as pure duplicates**

Each location serves a purpose:
- `lumra_config/static/css/` → Django backend reference
- `theme/static/css/dist/` → **ACTIVE Frontend CSS** (needed for browser)
- `static/css/` → Build artifacts

### Restoration
- ✅ `theme/static/css/dist/` RESTORED
- ✅ `static/css/` RESTORED
- ✅ Frontend styling now working again

---

## Odyssey Design System Reference

All CSS follows the **Emerald Odyssey v3.0** specification documented in [LUMRA_ERP_EMERALD_ODYSSEY.md](LUMRA_ERP_EMERALD_ODYSSEY.md):

### Core Tokens (in `:root`)
```css
--em: #00674F;           /* Primary Emerald */
--jade: #00A86B;         /* Secondary Jade */
--gold: #EFBF04;         /* Accent Gold */
--cream: #FDFBD4;        /* Neutral Cream */
--navy: #000080;         /* Contrast Navy */
```

### Glass Protocol (Mandatory)
```css
.lumra-glass {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px) saturate(180%);
  border: 0.5px solid rgba(0, 103, 79, 0.1);
  box-shadow: 0 1px 3px rgba(0,0,0,.08), 
              0 4px 12px rgba(0,0,0,.06);
}
```

---

## Deployment Checklist

- ✅ **Both sources verified**: `lumra_config/static/css/` (11 files) + `theme/static/css/dist/` (3 files)
- ✅ **Tailwind build working**: `python manage.py tailwind build`
- ✅ **Django config correct**: STATICFILES_DIRS + TAILWIND_APP_NAME set correctly
- ✅ **Frontend styling active**: `theme/static/css/dist/styles.css` loaded
- ✅ **Design system active**: All Odyssey tokens loaded and tested
- ✅ **Responsive breakpoints**: Tailwind + Glass Protocol verified
- ✅ **NO deleted CSS locations**: All folders restored and protected

---

## Maintenance Rules

### ✅ DO
- Edit **source files** in `lumra_config/static/css/`
- Run `python manage.py tailwind build` after CSS changes
- Keep `theme/static/css/dist/` (frontend production CSS)
- Commit both `lumra_config/static/css/` AND `theme/static/css/dist/` to git
- Test CSS changes via browser DevTools
- Keep lumra_tokens.css as first load
- Maintain Glass Protocol in all card components

### ❌ DON'T
- **NEVER delete** `theme/static/css/dist/` (breaks frontend styling)
- **NEVER delete** `static/css/` (breaks collectstatic)
- Treat multiple CSS locations as pure duplicates
- Edit files in archived backup folders
- Manually edit `static/css/` or `theme/static/css/dist/` (they're generated)
- Break the CSS cascade order
- Add inline styles to templates (use design system instead)

---

**Last Updated**: April 8, 2026  
**Status**: ✅ Production Ready  
**Odyssey Version**: 3.0
