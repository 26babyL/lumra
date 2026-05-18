/* ============================================================
   LUMRA SIDEBAR — lumra_sidebar.css
   Emerald Odyssey Blueprint v1.2
   ============================================================
   File ini adalah SUPLEMEN untuk §17 Sidebar Glass yang sudah
   ada di lumra_components.css.

   Load order:
     1. lumra_tokens.css       ← :root variables & --sb-* tokens
     2. lumra_base.css         ← reset + typography
     3. lumra_components.css   ← §17 sidebar + §18 navbar
     4. lumra_sidebar.css      ← ini (suplemen sidebar)

   KONSTITUSI FILE:
   · Hanya berisi apa yang TIDAK ADA di lumra_components.css §17
   · Semua nilai via var(--) token
   · Tidak ada hardcoded color
   ============================================================ */


/* ══════════════════════════════════════════════════════════════
   §1. UTILITY GLOBAL
   ══════════════════════════════════════════════════════════════ */

/* Alpine.js cloak — wajib agar elemen tidak flash sebelum Alpine init */
[x-cloak] { display: none !important; }


/* ══════════════════════════════════════════════════════════════
   §2. SIDEBAR HEADER & FOOTER BORDER
   ══════════════════════════════════════════════════════════════ */
.sidebar-glass {
  background  : var(--sb-bg, rgba(5, 10, 24, 0.88));
  /* Garis kaca halus di sisi kanan pemisah Sidebar & Navbar */
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  /* Shadow ini akan jatuh ke atas Navbar, menyatukan ruang dimensi */
  box-shadow  : 4px 0 24px rgba(0, 0, 0, 0.15); 
}

.sb-header-border {
  border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.18));
}

[data-theme="dark"] .sb-header-border {
  border-bottom-color: var(--color-border-subtle);
}

.sb-footer-border {
  border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.18));
}

[data-theme="dark"] .sb-footer-border {
  border-top-color: var(--color-border-subtle);
}


/* ══════════════════════════════════════════════════════════════
   §3. COLLAPSED ICON SIZE FIX
   lumra_components.css §17 membuat .nav-icon-wrap 40×40 saat
   collapsed — ini override balik ke 32×32 agar icon tidak raksasa
   ══════════════════════════════════════════════════════════════ */
.nav-item.collapsed .nav-icon-wrap {
  width : 32px;
  height: 32px;
}


/* ══════════════════════════════════════════════════════════════
   §4. NAV SECTION — collapsed state
   Saat collapsed, section label disembunyikan dengan smooth
   ══════════════════════════════════════════════════════════════ */
.nav-section {
  transition: opacity var(--transition-base),
              max-height var(--transition-base),
              padding var(--transition-base);
  max-height: 40px;
  overflow  : hidden;
}

.nav-section.opacity-0 {
  max-height: 0;
  padding   : 0;
  opacity   : 0;
}


/* ══════════════════════════════════════════════════════════════
   §5. NOTIFICATION BADGE — Odyssey Gold
   Blueprint Bab 04 — Badge System
   ══════════════════════════════════════════════════════════════ */
.lumra-badge-new {
  background   : linear-gradient(135deg, var(--color-accent) 0%, #C9A200 100%);
  color        : #1A0A00;
  font-size    : var(--text-label);
  font-weight  : var(--font-bold);
  padding      : 2px var(--sp-2);
  border-radius: var(--radius-pill);
  line-height  : 1;
  flex-shrink  : 0;
  box-shadow   : 0 1px 4px var(--color-accent-a20);
}


/* ══════════════════════════════════════════════════════════════
   §6. THEME TOGGLE — Footer sidebar
   ══════════════════════════════════════════════════════════════ */
.lumra-theme-toggle {
  display      : flex;
  align-items  : center;
  gap          : var(--sp-2);
  padding      : 6px var(--sp-2);
  border-radius: var(--radius-md);
  border       : 0.5px solid var(--sb-btn-border);
  background   : var(--sb-btn-bg);
  cursor       : pointer;
  transition   : background var(--transition-fast),
                 border-color var(--transition-fast);
  width        : 100%;
  color        : var(--sb-text);
}

.lumra-theme-toggle:hover {
  background  : var(--sb-btn-hover-bg);
  border-color: var(--color-primary);
}

.lumra-theme-toggle-track {
  width        : 28px;
  height       : 16px;
  border-radius: var(--radius-pill);
  background   : var(--color-primary-a15);
  border       : 1px solid var(--color-primary-a25);
  position     : relative;
  flex-shrink  : 0;
  transition   : background var(--transition-base);
}

.lumra-theme-toggle-track::after {
  content      : '';
  position     : absolute;
  top          : 50%;
  left         : 3px;
  transform    : translateY(-50%);
  width        : 10px;
  height       : 10px;
  border-radius: 50%;
  background   : var(--color-primary);
  transition   : transform var(--transition-base),
                 background var(--transition-base);
}

[data-theme="dark"] .lumra-theme-toggle-track::after {
  transform : translate(12px, -50%);
  background: var(--color-secondary);
}

.lumra-theme-toggle-label {
  font-size  : var(--text-label);
  font-weight: var(--font-medium);
  color      : var(--sb-text);
}


/* ══════════════════════════════════════════════════════════════
   §7. MOBILE OVERLAY
   ══════════════════════════════════════════════════════════════ */
.sb-mobile-overlay {
  position       : fixed;
  inset          : 0;
  background     : rgba(0, 0, 0, 0.40);
  backdrop-filter: blur(2px);
  z-index        : calc(var(--z-sidebar) - 1);
  cursor         : pointer;
}


/* ══════════════════════════════════════════════════════════════
   §8. LOGOUT BUTTON — footer user area
   ══════════════════════════════════════════════════════════════ */
.sb-logout-btn {
  display         : flex;
  align-items     : center;
  justify-content : center;
  padding         : var(--sp-2);
  border-radius   : var(--radius-sm);
  color           : var(--color-text-subtle);
  opacity         : 0.65;
  transition      : color var(--transition-fast),
                    background var(--transition-fast),
                    opacity var(--transition-fast);
  flex-shrink     : 0;
  text-decoration : none;
}

.sb-logout-btn:hover {
  color      : var(--color-danger);
  background : var(--color-danger-bg);
  opacity    : 1;
}


/* ══════════════════════════════════════════════════════════════
   §9. USERNAME & ROLE TEXT
   ══════════════════════════════════════════════════════════════ */
.sb-username {
  color: var(--color-text);
}

.sb-role {
  color: var(--color-text-muted);
}


/* ══════════════════════════════════════════════════════════════
   §10. SIDEBAR BLOB — dekoratif layered background
   ══════════════════════════════════════════════════════════════ */
@keyframes sb-blob-drift {
  from { transform: translate(0, 0) scale(1); }
  to   { transform: translate(12px, 18px) scale(1.05); }
}

.sb-blob {
  position      : absolute;
  border-radius : 50%;
  filter        : blur(60px);
  pointer-events: none;
  z-index       : 0;
  animation     : sb-blob-drift 20s ease-in-out infinite alternate;
}

.sb-blob-1 {
  width      : 160px;
  height     : 160px;
  background : var(--color-primary);
  opacity    : 0.06;
  top        : -40px;
  left       : -60px;
}

.sb-blob-2 {
  width           : 120px;
  height          : 120px;
  background      : var(--color-secondary);
  opacity         : 0.05;
  bottom          : 64px;
  left            : -20px;
  animation-delay : -8s;
}

/* Pastikan semua nav content di atas blob */
#sidebar > *:not(.sb-blob) {
  position: relative;
  z-index : 1;
}