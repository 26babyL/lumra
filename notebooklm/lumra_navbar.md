/* ============================================================
   LUMRA NAVBAR — lumra_navbar.css
   Emerald Odyssey Blueprint v1.2  (FIXED)
   ============================================================
   Load order:
     1. lumra_tokens.css
     2. lumra_base.css
     3. lumra_components.css   ← §18 .nav-glass & .cmd-input
     4. lumra_sidebar.css
     5. lumra_navbar.css       ← ini

   PERBAIKAN vs versi sebelumnya:
   · §1  nav-glass  — hapus height/position/z-index (sudah di §18,
          dobel override bikin sticky tidak bekerja di beberapa browser)
   · §2  cmd-input  — border-radius pakai --radius-lg bukan --radius-pill
          (pill terlalu bulat untuk input search). Tambah fallback eksplisit
          di setiap var() agar tidak transparan saat token belum load.
   · §5  cmd-dropdown — tambah fallback rgba() di semua var() kritis
   · §10 store-pill — font-size hardcoded 13px (bukan var(--text-table)
          yang nilainya bergantung di tokens)
   ============================================================ */


/* ══════════════════════════════════════════════════════════════
   §1. NAV GLASS — CONSISTENT WITH SIDEBAR
   Menggunakan implementasi sidebar untuk konsistensi visual
   ══════════════════════════════════════════════════════════════ */
.nav-glass {
  background  : var(--sb-bg, rgba(5, 10, 24, 0.88));
  backdrop-filter: var(--glass-blur-heavy, blur(24px)) saturate(180%);
  -webkit-backdrop-filter: var(--glass-blur-heavy, blur(24px)) saturate(180%);
  border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.18));
  border-radius: 0; /* Tidak rounded agar selaras dengan sidebar */
  box-shadow  : 0 1px 3px rgba(0, 0, 0, 0.06),
                0 0 0 0.5px rgba(0, 0, 0, 0.04);
}

[data-theme="dark"] .nav-glass {
  background  : var(--sb-bg, rgba(5, 10, 24, 0.88));
  border-bottom-color: var(--color-border-subtle);
  box-shadow  : 0 1px 3px rgba(0, 0, 0, 0.30),
                0 0 0 0.5px rgba(0, 0, 0, 0.20);
}


/* ══════════════════════════════════════════════════════════════
   §2. COMMAND SEARCH INPUT
   FIX: border-radius dari --radius-pill (9999px) → --radius-lg (12px)
   FIX: fallback eksplisit di setiap var() kritis
   ══════════════════════════════════════════════════════════════ */
.cmd-input {
  background   : var(--glass-bg-subtle, rgba(255, 255, 255, 0.60));
  border       : 1px solid var(--border-ui, rgba(203, 213, 225, 0.70));
  border-radius: var(--radius-lg, 12px);
  transition   : background var(--transition-fast, 0.14s),
                 border-color var(--transition-fast, 0.14s),
                 box-shadow var(--transition-fast, 0.14s);
}

.cmd-input:focus {
  outline     : none;
  background  : var(--glass-bg-strong, rgba(255, 255, 255, 0.92));
  border-color: var(--color-secondary, #00A86B);
  box-shadow  : var(--shadow-focus, 0 0 0 3px rgba(0, 168, 107, 0.20));
}

[data-theme="dark"] .cmd-input {
  background: var(--glass-bg-subtle, rgba(255, 255, 255, 0.04));
  border-color: var(--border-ui, rgba(255, 255, 255, 0.10));
}

[data-theme="dark"] .cmd-input:focus {
  background: var(--glass-bg-strong, rgba(255, 255, 255, 0.08));
}


/* ══════════════════════════════════════════════════════════════
   §3. COMMAND TOKEN CHIP
   ══════════════════════════════════════════════════════════════ */
.cmd-token {
  display       : inline-flex;
  align-items   : center;
  gap           : 3px;
  padding       : 1px 6px;
  border-radius : var(--radius-xs, 4px);
  font-size     : 11px;
  font-weight   : var(--font-bold, 700);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  line-height   : 1.7;
  flex-shrink   : 0;
}

.cmd-token-product  { background: #D1FAE5; color: #064E3B; }
.cmd-token-location { background: #DBEAFE; color: #1E3A8A; }
.cmd-token-stock    { background: #FEF3C7; color: #78350F; }
.cmd-token-default  { background: #F1F5F9; color: #475569; }

[data-theme="dark"] .cmd-token-product  { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; }
[data-theme="dark"] .cmd-token-location { background: rgba(59, 130, 246, 0.15);  color: #93C5FD; }
[data-theme="dark"] .cmd-token-stock    { background: rgba(245, 158, 11, 0.15);  color: #FCD34D; }
[data-theme="dark"] .cmd-token-default  { background: rgba(255, 255, 255, 0.08); color: #94A3B8; }


/* ══════════════════════════════════════════════════════════════
   §4. KBD HINT
   ══════════════════════════════════════════════════════════════ */
.kbd {
  display       : inline-flex;
  align-items   : center;
  padding       : 1px 5px;
  border        : 1px solid #E2E8F0;
  border-radius : var(--radius-xs, 4px);
  background    : #F8FAFC;
  font-size     : 11px;
  font-family   : var(--font-mono, ui-monospace, monospace);
  color         : #94A3B8;
  line-height   : 1.6;
  pointer-events: none;
}

[data-theme="dark"] .kbd {
  background  : rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  color       : #64748B;
}


/* ══════════════════════════════════════════════════════════════
   §5. COMMAND DROPDOWN — glass panel
   FIX: fallback rgba() di background & border-color
   ══════════════════════════════════════════════════════════════ */
.cmd-dropdown {
  background             : var(--glass-bg-strong, rgba(255, 255, 255, 0.95));
  backdrop-filter        : var(--glass-blur-heavy, blur(24px)) saturate(180%);
  -webkit-backdrop-filter: var(--glass-blur-heavy, blur(24px)) saturate(180%);
  border                 : 1px solid var(--border-ui, rgba(203, 213, 225, 0.70));
  border-radius          : var(--radius-xl, 16px);
  box-shadow             :
    0 8px 30px rgba(0, 0, 0, 0.09),
    0 2px 8px  rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.60);
  overflow: hidden;
}

[data-theme="dark"] .cmd-dropdown {
  background  : var(--glass-bg-strong, rgba(10, 18, 36, 0.95));
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow  :
    0 8px 30px rgba(0, 0, 0, 0.35),
    0 2px 8px  rgba(0, 0, 0, 0.20),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}


/* ══════════════════════════════════════════════════════════════
   §6. COMMAND RESULT ITEM
   ══════════════════════════════════════════════════════════════ */
.cmd-result-item {
  display        : flex;
  align-items    : center;
  gap            : 10px;
  padding        : 9px 16px;
  cursor         : pointer;
  transition     : background var(--transition-fast, 0.14s);
  border-radius  : 0;
  text-decoration: none;
  width          : 100%;
  text-align     : left;
  border         : none;
  background     : transparent;
  color          : inherit;
}

.cmd-result-item:hover,
.cmd-result-item.active {
  background: rgba(16, 185, 129, 0.06);
}

.cmd-result-item.active {
  border-left: 2px solid var(--color-primary, #10B981);
}

[data-theme="dark"] .cmd-result-item:hover,
[data-theme="dark"] .cmd-result-item.active {
  background: rgba(16, 185, 129, 0.08);
}


/* ══════════════════════════════════════════════════════════════
   §7. SECTION LABEL IN DROPDOWN
   ══════════════════════════════════════════════════════════════ */
.cmd-section-label {
  font-size     : 10px;
  font-weight   : var(--font-bold, 700);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color         : #94A3B8;
  padding       : 8px 16px 4px;
}

[data-theme="dark"] .cmd-section-label {
  color: #475569;
}


/* ══════════════════════════════════════════════════════════════
   §8. SCROLLBAR IN DROPDOWN
   ══════════════════════════════════════════════════════════════ */
.cmd-scroll::-webkit-scrollbar       { width: 4px; }
.cmd-scroll::-webkit-scrollbar-track { background: transparent; }
.cmd-scroll::-webkit-scrollbar-thumb {
  background   : rgba(203, 213, 225, 0.60);
  border-radius: 9999px;
}

[data-theme="dark"] .cmd-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.10);
}


/* ══════════════════════════════════════════════════════════════
   §9. NOTIFICATION DOT
   ══════════════════════════════════════════════════════════════ */
@keyframes notifPulse {
  0%, 100% { transform: scale(1);    opacity: 1; }
  50%      { transform: scale(1.35); opacity: .75; }
}

.notif-dot {
  position     : absolute;
  top          : 7px;
  right        : 7px;
  width        : 7px;
  height       : 7px;
  border-radius: 50%;
  background   : #EF4444;
  border       : 1.5px solid rgba(255, 255, 255, 0.9);
  animation    : notifPulse 2.4s ease-in-out infinite;
}

[data-theme="dark"] .notif-dot {
  border-color: var(--color-bg, #020617);
}


/* ══════════════════════════════════════════════════════════════
   §10. STORE PILL
   FIX: font-size hardcoded 13px (bukan var(--text-table) yang
   nilainya bisa berubah/undefined di token baru)
   ══════════════════════════════════════════════════════════════ */
.store-pill {
  display      : inline-flex;
  align-items  : center;
  gap          : 6px;
  padding      : 4px 10px 4px 7px;
  border       : 1px solid rgba(16, 185, 129, 0.20);
  border-radius: 9999px;
  background   : rgba(16, 185, 129, 0.06);
  font-size    : 13px;
  font-weight  : var(--font-semibold, 600);
  color        : #064E3B;
  cursor       : pointer;
  transition   : background var(--transition-fast, 0.14s),
                 border-color var(--transition-fast, 0.14s);
  white-space  : nowrap;
  max-width    : 180px;
}

.store-pill:hover {
  background  : rgba(16, 185, 129, 0.10);
  border-color: rgba(16, 185, 129, 0.35);
}

[data-theme="dark"] .store-pill {
  color       : #A7F3D0;
  background  : rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.18);
}

[data-theme="dark"] .store-pill:hover {
  background  : rgba(16, 185, 129, 0.13);
  border-color: rgba(16, 185, 129, 0.28);
}


/* ══════════════════════════════════════════════════════════════
   §11. AVATAR RING
   ══════════════════════════════════════════════════════════════ */
.avatar-ring {
  border       : 1.5px solid var(--border-ui, rgba(203, 213, 225, 0.70));
  border-radius: 50%;
  object-fit   : cover;
}

.avatar-ring:hover {
  border-color: rgba(16, 185, 129, 0.40);
}