/* ============================================================
   LUMRA BASE — lumra_base.css
   ============================================================
   Import font, reset, dan typography global.
   Bergantung pada lumra_tokens.css (harus load dulu).
   ============================================================ */

/* ══════════════════════════════════════════════════════════════
   FONT IMPORT
   ══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500&display=swap');


/* ══════════════════════════════════════════════════════════════
   RESET
   ══════════════════════════════════════════════════════════════ */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
  scroll-behavior: smooth;
  scrollbar-gutter: stable;
}

body {
  font-family            : var(--font-body);
  font-size              : var(--text-body);
  font-weight            : var(--font-regular);
  line-height            : var(--leading-normal);
  color                  : var(--color-text);
  background             : var(--color-bg);
  -webkit-font-smoothing : antialiased;
  -moz-osx-font-smoothing: grayscale;
}


/* ══════════════════════════════════════════════════════════════
   TYPOGRAPHY HIERARCHY — Blueprint: Bab 02
   ══════════════════════════════════════════════════════════════ */

/* H1 — Page Title */
h1, .h1, .text-page-title {
  font-family   : var(--font-heading);
  font-size     : var(--text-page);
  font-weight   : var(--font-semibold);
  line-height   : var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color         : var(--color-text);
}

/* H2 — Section Title */
h2, .h2, .text-section-title {
  font-family   : var(--font-heading);
  font-size     : var(--text-section);
  font-weight   : var(--font-semibold);
  line-height   : var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color         : var(--color-text);
}

/* H3 — Card Title */
h3, .h3, .text-card-title {
  font-family   : var(--font-heading);
  font-size     : var(--text-card-title);
  font-weight   : var(--font-medium);
  line-height   : var(--leading-snug);
  color         : var(--color-text);
}

/* Body text */
p, .text-body {
  font-size  : var(--text-body);
  line-height: var(--leading-normal);
  color      : var(--color-text);
}

/* Table/Form text */
.text-table {
  font-size: var(--text-table);
}

/* Label/Badge text */
.text-label {
  font-size     : var(--text-label);
  font-weight   : var(--font-semibold);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
}

/* KPI Number — monospaced, tabular */
.text-kpi, .kpi-value {
  font-family          : var(--font-mono);
  font-size            : var(--text-kpi);
  font-weight          : var(--font-medium);
  line-height          : 1.15;
  font-variant-numeric : tabular-nums;
  letter-spacing       : -0.01em;
  color                : var(--color-text);
}


/* ══════════════════════════════════════════════════════════════
   UTILITY CLASSES
   ══════════════════════════════════════════════════════════════ */

/* Text colors */
.text-muted              { color: var(--color-text-muted); }
.text-subtle             { color: var(--color-text-subtle); }
.text-primary            { color: var(--color-primary); }
.text-success            { color: var(--color-success-text); }
.text-warning            { color: var(--color-warning-text); }
.text-danger             { color: var(--color-danger-text); }

/* Font weights */
.font-regular            { font-weight: var(--font-regular); }
.font-medium             { font-weight: var(--font-medium); }
.font-semibold           { font-weight: var(--font-semibold); }
.font-bold               { font-weight: var(--font-bold); }

/* Letter spacing */
.tracking-wide           { letter-spacing: var(--tracking-wide); }
.tracking-widest         { letter-spacing: var(--tracking-widest); }


/* ══════════════════════════════════════════════════════════════
   LINKS & SELECTION
   ══════════════════════════════════════════════════════════════ */
a {
  color          : var(--color-primary);
  text-decoration: none;
  transition     : color var(--transition-fast);
}

a:hover {
  color: var(--color-primary-light);
}

::selection {
  background: var(--color-primary-a25);
  color     : var(--color-primary-dark);
}


/* ══════════════════════════════════════════════════════════════
   FOCUS RING — Blueprint: Accessibility
   ══════════════════════════════════════════════════════════════ */
:focus {
  outline: none;
}

:focus-visible {
  outline      : 2px solid var(--color-primary);
  outline-offset: 2px;
}


/* ══════════════════════════════════════════════════════════════
   SCROLLBAR
   ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {
  width : 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background       : var(--color-slate-300);
  border-radius    : var(--radius-pill);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-slate-400);
}

* {
  scrollbar-width: thin;
  scrollbar-color: var(--color-slate-300) transparent;
}