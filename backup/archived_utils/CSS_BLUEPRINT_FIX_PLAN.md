# 🔧 CSS Blueprint Alignment — Fix Plan

**Status**: 10/11 files need updates  
**Priority**: CRITICAL - Settings must match LUMRA_ERP_EMERALD_ODYSSEY.md  
**Date**: April 8, 2026

---

## 📊 Audit Results Summary

| File | Status | Issues | Action |
|------|--------|--------|--------|
| lumra_tokens.css | ⚠️ WARNING | Tailwind color names | Review & clean |
| lumra_base.css | ❌ ERROR | Missing token references | Add import + use var() |
| lumra_components.css | ❌ ERROR | 3 missing colors + no Glass Protocol | Rewrite with blueprint |
| lumra_sidebar.css | ❌ ERROR | 3 missing colors + no Glass Protocol | Rewrite with blueprint |
| lumra_navbar.css | ❌ ERROR | 2 missing colors + no Glass Protocol | Rewrite with blueprint |
| lumra_dashboard.css | ❌ ERROR | 3 missing + old colors | Migrate to Odyssey |
| lumra_design_system.css | ❌ ERROR | Auto-generated (needs review) | Check for bloat |
| lumra_form.css | ❌ ERROR | 3 missing colors | Add tokens + Glass Protocol |
| lumra_typography.css | ❌ ERROR | 2 missing colors | Import lumra_tokens.css |
| lumra_bg_blob.css | ❌ ERROR | 2 missing colors | Add tokens |
| theme_overrides.css | ❌ ERROR | 3 missing colors | Add tokens |

---

## 🎯 Blueprint Specifications (Source of Truth)

### Emerald Odyssey Palette
```css
--color-primary: #00674F;      /* Base Emerald — Sidebar, branding */
--color-secondary: #00A86B;    /* Jade — Success, badges, nav */
--color-accent: #EFBF04;       /* Gold — Premium, ratings, KPI */
--color-neutral: #FDFBD4;      /* Cream — Zebra rows */
--color-contrast: #000080;     /* Navy — Heavy headers, footer */
```

### Glass Protocol (MANDATORY for all components)
```css
background: rgba(0,103,79,.08);  /* Emerald tint */
backdrop-filter: blur(12px);     /* Frosted glass */
border: 0.5px solid rgba(255,255,255,0.10);
border-top-color: rgba(255,255,255,0.25);
border-left-color: rgba(255,255,255,0.20);
box-shadow: 0 1px 3px rgba(0,0,0,.08), 
            0 4px 12px rgba(0,0,0,.06),
            0 8px 24px rgba(0,0,0,.04),
            0 16px 48px rgba(0,0,0,.03);
border-radius: 14px;
transition: transform 200ms ease, box-shadow 200ms ease;
```

### Typography Hierarchy
- **H1**: 28px 600 (Page titles)
- **H2**: 22px 600 (Section titles)
- **H3**: 16px 500 (Card titles)
- **Body**: 14px 400 (Default text)
- **Table/Form**: 13px 400
- **Label/Badge**: 11px 500 (uppercase)
- **KPI Numbers**: 28-36px 600 (monospaced, tabular-nums)

### Spacing (ALL must be 8px multiples)
✅ Valid: 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 240px  
❌ Invalid: 7px, 10px, 12px, 14px, 18px, 20px, 22px

### Components & Classes

**KPI Cards**
```css
.kpi-glass {
  background: rgba(0,103,79,.08);
  backdrop-filter: blur(12px);
  border: 0.5px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,.08), ...;
}
```

**Sidebar**
- Container: `.sidebar-glass` → background: rgba(0,103,79,.08)
- Active item: `.nav-item.active` → border-left: 3px solid #00A86B
- Width: 240px (expanded) / 64px (collapsed)

**Navbar**
- `.nav-glass` → background: rgba(255,255,255,.85), blur(12px)
- Height: 56px (7×8)

**Tables**
- Header: background: #00674F (emerald)
- Zebra odd: rgba(0,103,79,.035)
- Zebra even: white
- Row hover: rgba(0,103,79,.055)

**Status Badges**
- Success: rgba(0,168,107,.15) with border rgba(0,168,107,.3)
- Warning: rgba(239,191,4,.15) with border rgba(239,191,4,.4)
- Critical: gradient(#A32D2D → #000080)
- Info: rgba(0,0,128,.08)

---

## 📝 File-by-File Fix Instructions

### 1. **lumra_tokens.css** (REVIEW & VERIFY)
**Current**: ✅ Has Odyssey colors defined, but has some Tailwind names too  
**Action**: Keep Odyssey colors, remove/consolidate Tailwind references  
**Check**: Verify all 5 primary colors exist in exact format

### 2. **lumra_base.css** (ADD IMPORT + UPDATE)
**MISSING**: `@import '../lumra_tokens.css';` at top  
**ACTION**: 
```css
/* 1. Add at very top (before other imports) */
@import './lumra_tokens.css';

/* 2. Update body color reference */
body { color: var(--color-text); }  /* Use tokens, not hardcoded */

/* 3. Update heading colors */
h1, .h1 { color: var(--color-text); }
```

### 3. **lumra_components.css** (MAJOR REWRITE)
**MISSING**: 
- Import lumra_tokens.css
- No Glass Protocol implementation
- Old colors used

**ACTION**:
```css
@import './lumra_tokens.css';

/* Add .kpi-glass template */
.kpi-glass {
  background: rgba(0,103,79,.08);
  backdrop-filter: blur(12px);
  border: 0.5px solid rgba(255,255,255,0.10);
  box-shadow: 0 1px 3px rgba(0,0,0,.08), ... ;
  border-radius: 14px;
  padding: 16px;
}

/* Replace all emerald-600 with var(--color-primary) */
/* Replace all emerald-700 with var(--color-primary-dark) */
```

### 4. **lumra_sidebar.css** (ADD GLASS PROTOCOL)
**Missing**:
- Glass Protocol styles
- Token references

**ACTION**: 
```css
@import './lumra_tokens.css';

.sidebar-glass {
  background: rgba(0,103,79,.08);
  backdrop-filter: blur(16px);
  border: 0.5px solid rgba(255,255,255,0.10);
  /* Add full Glass Protocol */
}

.nav-item.active {
  background: rgba(0,168,107,.15);  /* Use var(--color-secondary-a15) */
  border-left: 3px solid var(--color-secondary);  /* #00A86B */
  color: var(--color-primary);
}
```

### 5. **lumra_navbar.css** (ADD TOKENS)
**Missing**: Token references, Glass Protocol  
**ACTION**: Same pattern — import tokens, use var() instead of hardcoded

### 6. **lumra_dashboard.css** (MIGRATE COLORS)
**Missing**: Replace emerald-600, emerald-700, #047857, #059669  
**ACTION**: Map to Odyssey palette equivalents

### 7. **lumra_design_system.css** (REVIEW)
**Status**: Auto-generated with many Tailwind tokens  
**ACTION**: Check if this should be kept or simplified

### 8. **lumra_form.css** (ADD IMPORT + COLORS)
**Missing**: Import lumra_tokens.css + color variables  
**ACTION**: Use Odyssey palette for form input focus states

### 9. **lumra_typography.css** (ADD IMPORT)
**Missing**: `@import './lumra_tokens.css';` + use variables  
**ACTION**: Use CSS variables for all color values

### 10. **lumra_bg_blob.css** (ADD TOKENS)
**Missing**: Token references for accent colors  
**ACTION**: Import + replace hardcoded with var()

### 11. **theme_overrides.css** (ADD TOKENS)
**Missing**: Import + token usage  
**ACTION**: Same pattern

---

## ✅ Verification Checklist

After fixing each file:
- [ ] File imports `lumra_tokens.css` (except lumra_tokens.css itself)
- [ ] All primary Odyssey colors defined or referenced as `var(--color-*)`
- [ ] NO hardcoded colors from old Tailwind (#047857, #059669, etc.)
- [ ] Glass Protocol implemented on card/panel components
- [ ] All spacing values are 8px multiples
- [ ] Typography matches blueprint sizes
- [ ] File has no syntax errors (matching braces)
- [ ] File size reasonable (not bloated)

---

## 🚀 Implementation Order

**Phase 1 - Foundation** (2 files)
1. ✅ lumra_tokens.css — Review & verify
2. ✅ lumra_base.css — Add import + update

**Phase 2 - Components** (6 files)
3. lumra_components.css — Add Glass Protocol
4. lumra_sidebar.css — Add Glass Protocol  
5. lumra_navbar.css — Add Glass Protocol
6. lumra_form.css — Add tokens
7. lumra_typography.css — Add import
8. lumra_bg_blob.css — Add tokens

**Phase 3 - Cleanup** (3 files)
9. lumra_dashboard.css — Migrate colors
10. lumra_design_system.css — Review/cleanup
11. theme_overrides.css — Add tokens

---

## 📌 CRITICAL RULES

✅ **DO**:
- Use CSS variables from lumra_tokens.css (`var(--color-primary)`)
- Keep Glass Protocol consistent across all cards
- Maintain 8px grid for all spacing
- Import lumra_tokens.css first in component files

❌ **DON'T**:
- Hardcode colors (except in lumra_tokens.css)
- Use old Tailwind colors (emerald-600, emerald-700, etc.)
- Break Glass Protocol recipe  
- Use non-8px-multiple spacing values
- Add inline styles to HTML (CSS only)

---

**Next Step**: Run the fixes in order and test with `python manage.py tailwind build`
