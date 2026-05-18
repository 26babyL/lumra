/* ============================================================
   LUMRA DESIGN TOKENS — lumra_tokens.css
   Emerald Odyssey Blueprint v1.1
   ============================================================
   KONSTITUSI FILE:
   · HANYA berisi :root dan [data-theme="dark"] declarations
   · TIDAK ADA styling class di sini — murni token/variabel
   · Single Source of Truth untuk semua nilai desain
   · Semua spacing HARUS kelipatan 4px (Blueprint: Bab 09)

   Blueprint Reference: Bab 07 — CSS Token Reference
   ============================================================ */


/* ════════════════════════════════════════════════════════════
   EMERALD ODYSSEY PALETTE — 5 Warna Utama
   Blueprint: Bab 02 — Fondasi Warna
   ════════════════════════════════════════════════════════════ */
:root {

  /* ── Primary: Base Emerald — Sidebar, branding, identity mark ── */
  --color-primary         : #00674F;
  --color-primary-light   : #2E8C69;
  --color-primary-dark    : #003D2C;
  --color-primary-glow    : #5DA88A;

  /* Emerald scale */
  --color-emerald-50      : #E6F2EE;
  --color-emerald-100     : #C0DFCF;
  --color-emerald-200     : #90C4AC;
  --color-emerald-300     : #5DA88A;
  --color-emerald-400     : #34D399;
  --color-emerald-500     : #00674F;
  --color-emerald-600     : #005A44;
  --color-emerald-700     : #004D39;
  --color-emerald-800     : #003D2C;
  --color-emerald-900     : #002D1F;
  --color-emerald-950     : #001A12;

  /* ── Secondary: Jade Accent — Success, tombol aktif, badge ── */
  --color-secondary       : #00A86B;

  /* ── Accent: Odyssey Gold — Premium, rating, KPI highlight ── */
  --color-accent          : #EFBF04;

  /* ── Neutral: Ivory Cream — Zebra row odd, off-white bg ── */
  --color-neutral         : #FDFBD4;

  /* ── Contrast: Deep Navy — Heavy heading, footer, authority ── */
  --color-contrast        : #000080;

  /* ── Extended UI accents — digunakan di KPI card corner tints ── */
  --color-violet          : #8B5CF6;
  --color-danger-dark     : #7F1D1D;
  --color-border-print    : #E2E8F0;


  /* ════════════════════════════════════════════════════════════
     ALPHA VARIANTS — Digunakan untuk glass tint & overlays
     ════════════════════════════════════════════════════════════ */

  /* Primary alpha */
  --color-primary-a03     : rgba(0, 103, 79, 0.03);
  --color-primary-a05     : rgba(0, 103, 79, 0.05);
  --color-primary-a06     : rgba(0, 103, 79, 0.06);
  --color-primary-a08     : rgba(0, 103, 79, 0.08);
  --color-primary-a10     : rgba(0, 103, 79, 0.10);
  --color-primary-a12     : rgba(0, 103, 79, 0.12);
  --color-primary-a15     : rgba(0, 103, 79, 0.15);
  --color-primary-a20     : rgba(0, 103, 79, 0.20);
  --color-primary-a25     : rgba(0, 103, 79, 0.25);
  --color-primary-a30     : rgba(0, 103, 79, 0.30);
  --color-primary-a40     : rgba(0, 103, 79, 0.40);
  --color-primary-a50     : rgba(0, 103, 79, 0.50);

  /* Secondary alpha */
  --color-secondary-a12   : rgba(0, 168, 107, 0.12);
  --color-secondary-a15   : rgba(0, 168, 107, 0.15);
  --color-secondary-a20   : rgba(0, 168, 107, 0.20);
  --color-secondary-a25   : rgba(0, 168, 107, 0.25);

  /* Accent (Gold) alpha */
  --color-accent-a10      : rgba(239, 191, 4, 0.10);
  --color-accent-a15      : rgba(239, 191, 4, 0.15);
  --color-accent-a20      : rgba(239, 191, 4, 0.20);

  /* Contrast (Navy) alpha */
  --color-contrast-a06    : rgba(0, 0, 128, 0.06);
  --color-contrast-a08    : rgba(0, 0, 128, 0.08);
  --color-contrast-a10    : rgba(0, 0, 128, 0.10);
  --color-contrast-a15    : rgba(0, 0, 128, 0.15);

  /* Black alpha — untuk overlay dan subtle utility */
  --color-black-a002      : rgba(0, 0, 0, 0.02);
  --color-black-a004      : rgba(0, 0, 0, 0.04);
  --color-black-a006      : rgba(0, 0, 0, 0.06);
  --color-black-a008      : rgba(0, 0, 0, 0.08);


  /* ════════════════════════════════════════════════════════════
     SEMANTIC COLORS — Status (Odyssey-aligned)
     Blueprint: Bab 02 — Warna Semantik
     ════════════════════════════════════════════════════════════ */

  /* Sukses — Emerald-aligned */
  --color-success         : #00674F;
  --color-success-bg      : rgba(0, 168, 107, 0.10);
  --color-success-border  : rgba(0, 168, 107, 0.25);
  --color-success-text    : #003D2C;

  /* Warning — Gold-aligned */
  --color-warning         : #B88A00;
  --color-warning-bg      : rgba(239, 191, 4, 0.12);
  --color-warning-border  : rgba(239, 191, 4, 0.30);
  --color-warning-text    : #635200;

  /* Danger/Kritis — Red → Navy gradient (JANGAN merah polos) */
  --color-danger          : #A32D2D;
  --color-danger-bg       : rgba(163, 45, 45, 0.08);
  --color-danger-border   : rgba(163, 45, 45, 0.20);
  --color-danger-text     : #7F1D1D;
  --color-danger-odyssey  : linear-gradient(135deg, #A32D2D, #000080);

  /* Info — Navy-aligned */
  --color-info            : #000080;
  --color-info-bg         : rgba(0, 0, 128, 0.07);
  --color-info-border     : rgba(0, 0, 128, 0.15);
  --color-info-text       : #000080;


  /* ════════════════════════════════════════════════════════════
     SLATE SCALE — Neutral grays
     ════════════════════════════════════════════════════════════ */
  --color-slate-50        : #F8FAFC;
  --color-slate-100       : #F1F5F9;
  --color-slate-200       : #E2E8F0;
  --color-slate-300       : #CBD5E1;
  --color-slate-400       : #94A3B8;
  --color-slate-500       : #64748B;
  --color-slate-600       : #475569;
  --color-slate-700       : #334155;
  --color-slate-800       : #1E293B;
  --color-slate-900       : #0F172A;
  --color-slate-950       : #020617;


  /* ════════════════════════════════════════════════════════════
     SURFACE & TEXT — Light mode defaults
     ════════════════════════════════════════════════════════════ */
  --color-bg              : #F2F6F4;
  --color-surface         : rgba(255, 255, 255, 0.92);
  --color-surface-strong  : rgba(255, 255, 255, 0.99);
  --color-surface-subtle  : rgba(255, 255, 255, 0.60);

  --color-border          : rgba(203, 213, 225, 0.70);
  --color-border-subtle   : rgba(203, 213, 225, 0.40);
  --color-border-strong   : rgba(148, 163, 184, 0.60);
  --color-border-focus    : #00674F;

  --color-text            : #0F172A;
  --color-text-muted      : #475569;
  --color-text-subtle     : #94A3B8;
  --color-text-inverse    : #FFFFFF;


  /* ════════════════════════════════════════════════════════════
     GLASS PROTOCOL — Blueprint: Bab 02 & Bab 04
     Resep wajib: blur + frosted-edge border + 4-layer shadow
     ════════════════════════════════════════════════════════════ */

  /* Blur levels */
  --glass-blur            : blur(14px) saturate(180%);
  --glass-blur-light      : blur(8px)  saturate(160%);
  --glass-blur-heavy      : blur(20px) saturate(200%);
  --glass-dark-blur       : blur(8px);

  /* Background tints */
  --glass-bg              : rgba(255, 255, 255, 0.72);
  --glass-bg-strong       : rgba(255, 255, 255, 0.94);
  --glass-bg-subtle       : rgba(255, 255, 255, 0.48);
  --glass-bg-emerald      : rgba(0, 103, 79, 0.08);
  --glass-bg-gold         : rgba(239, 191, 4, 0.07);
  --glass-bg-navy         : rgba(0, 0, 128, 0.06);

  /* Frosted Edge — mensimulasikan pantulan cahaya dari atas & kiri */
  --glass-border          : 0.5px solid rgba(255, 255, 255, 0.10);
  --glass-border-top      : rgba(255, 255, 255, 0.25);
  --glass-border-left     : rgba(255, 255, 255, 0.20);

  /* Border untuk UI di atas background putih */
  --border-ui             : rgba(203, 213, 225, 0.80);
  --border-ui-subtle      : rgba(203, 213, 225, 0.40);
  --border-ui-strong      : rgba(148, 163, 184, 0.60);


  /* ════════════════════════════════════════════════════════════
     SHADOW SYSTEM — Natural Shadow 4 Layers
     Blueprint: Bab 02 — The Glass Protocol
     ════════════════════════════════════════════════════════════ */

  /* Natural Shadow — 4 lapis makin memudar */
  --shadow-natural        :
    0 1px 3px  rgba(0, 0, 0, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.06),
    0 8px 24px rgba(0, 0, 0, 0.04),
    0 16px 48px rgba(0, 0, 0, 0.03);

  /* Hover — emerald tint */
  --shadow-hover          :
    0 4px 16px rgba(0, 103, 79, 0.16),
    0 8px 24px rgba(0, 0, 0, 0.06),
    0 16px 40px rgba(0, 0, 0, 0.04);

  /* Alias untuk backward compatibility */
  --shadow-natural-hover  : var(--shadow-hover);

  /* Focus ring */
  --shadow-focus          : 0 0 0 3px rgba(0, 168, 107, 0.25);

  /* Glow emerald */
  --shadow-glow           : 0 0 28px rgba(0, 103, 79, 0.22);

  /* Modal — lebih dalam */
  --shadow-modal          :
    0 8px 32px rgba(0, 0, 0, 0.16),
    0 16px 56px rgba(0, 0, 0, 0.12),
    0 24px 80px rgba(0, 0, 0, 0.08);

  /* Extra small — untuk card tipis */
  --shadow-xs             :
    0 1px 2px rgba(0, 0, 0, 0.06),
    0 2px 6px rgba(0, 0, 0, 0.04);


  /* ════════════════════════════════════════════════════════════
     SPACING — 8PX GRID
     Blueprint: Bab 02, Bab 09 — The Invisible Grid
     Semua nilai adalah kelipatan 4px
     ════════════════════════════════════════════════════════════ */
  --sp-1                  : 4px;   /* Micro-gap internal, gap label & nilai badge */
  --sp-2                  : 8px;   /* Padding kecil, padding badge, icon margin */
  --sp-3                  : 12px;  /* Gap antar elemen dalam card */
  --sp-4                  : 16px;  /* Padding card standar */
  --sp-5                  : 20px;  /* Card header padding */
  --sp-6                  : 24px;  /* Padding section, margin antar card */
  --sp-8                  : 32px;  /* Gap antar section besar */
  --sp-10                 : 40px;  /* Section breathing room */
  --sp-12                 : 48px;  /* Top padding halaman */
  --sp-16                 : 64px;  /* Page-level spacing */


  /* ════════════════════════════════════════════════════════════
     BORDER RADIUS
     Blueprint: Bab 09 — Audit Grid Checklist
     ════════════════════════════════════════════════════════════ */
  --radius-xs             : 4px;
  --radius-sm             : 6px;
  --radius-md             : 8px;
  --radius-lg             : 10px;
  --radius-xl             : 14px;
  --radius-2xl            : 20px;
  --radius-pill           : 100px;


  /* ════════════════════════════════════════════════════════════
     TYPOGRAPHY — Plus Jakarta Sans
     Blueprint: Bab 02 — Tipografi & Hierarki
     ════════════════════════════════════════════════════════════ */

  /* Font family */
  --font-body             : 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --font-heading          : 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --font-display          : 'DM Sans', 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-mono             : 'JetBrains Mono', 'Fira Code', monospace;

  /* Font size — hierarki ketat, tidak boleh ada nilai di luar ini */
  --text-label            : 11px;  /* Badge, label uppercase */
  --text-table            : 13px;  /* Sel tabel, input form, meta */
  --text-body             : 14px;  /* Body / description */
  --text-card-title       : 16px;  /* H3 / Card title */
  --text-card             : 16px;  /* Alias */
  --text-section          : 22px;  /* H2 / Section title */
  --text-page             : 28px;  /* H1 / Page title */
  --text-kpi              : 28px;  /* KPI number standard */
  --text-kpi-lg           : 36px;  /* KPI number large */

  /* Font weight */
  --font-regular          : 400;
  --font-medium           : 500;
  --font-semibold         : 600;
  --font-bold             : 700;

  /* Line height */
  --leading-tight         : 1.2;
  --leading-snug          : 1.35;
  --leading-normal        : 1.6;

  /* Letter spacing */
  --tracking-tight        : -0.02em;
  --tracking-normal       : 0;
  --tracking-wide         : 0.04em;
  --tracking-widest       : 0.12em;


  /* ════════════════════════════════════════════════════════════
     TRANSITIONS — Blueprint: Bab 06
     ════════════════════════════════════════════════════════════ */
  --ease-out              : cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out           : cubic-bezier(0.45, 0, 0.55, 1);
  --ease-bounce           : cubic-bezier(0.34, 1.56, 0.64, 1);

  --transition-fast       : 150ms var(--ease-out);
  --transition-base       : 200ms var(--ease-out);
  --transition-slow       : 300ms var(--ease-out);
  --transition-modal      : 250ms var(--ease-bounce);
  --transition-drawer     : 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-sidebar    : 300ms var(--ease-out);


  /* ════════════════════════════════════════════════════════════
     Z-INDEX SCALE
     ════════════════════════════════════════════════════════════ */
  --z-base                : 0;
  --z-dropdown            : 100;
  --z-sticky              : 200;
  --z-navbar              : 300;
  --z-sidebar             : 350;
  --z-modal               : 400;
  --z-toast               : 500;
  --z-tooltip             : 600;


  /* ════════════════════════════════════════════════════════════
     LAYOUT CONSTANTS
     ════════════════════════════════════════════════════════════ */
  --sidebar-width         : 240px;   /* 30 × 8px */
  --sidebar-collapsed     : 64px;    /* 8 × 8px */
  --navbar-height         : 56px;    /* 7 × 8px */
  --content-max-width     : 1280px;


  /* ════════════════════════════════════════════════════════════
     TIER BADGE TOKENS — Blueprint: Bab 04 Badge System
     ════════════════════════════════════════════════════════════ */
  --tier-platinum-bg      : #000080;
  --tier-platinum-text    : #EFBF04;
  --tier-gold-bg          : #EFBF04;
  --tier-gold-text        : #000000;
  --tier-silver-bg        : #888888;
  --tier-silver-text      : #FFFFFF;
  --tier-verified-bg      : #00674F;
  --tier-verified-text    : #FDFBD4;


  /* ════════════════════════════════════════════════════════════
     SIDEBAR TOKENS — Light Mode
     Blueprint: Bab 04 — Sidebar & Navbar Protocol
     ════════════════════════════════════════════════════════════ */
  --sb-width              : 240px;
  --sb-width-collapsed    : 64px;

  --sb-bg                 : rgba(248, 250, 252, 0.82);
  --sb-text               : var(--color-slate-500);
  --sb-text-active        : var(--color-emerald-950);
  --sb-icon-color         : var(--color-slate-500);

  --sb-hover-bg           : var(--color-primary-a06);
  --sb-hover-text         : var(--color-emerald-950);
  --sb-active-bg          : linear-gradient(90deg, var(--color-primary-a10) 0%, var(--color-primary-a03) 100%);
  --sb-active-text        : var(--color-emerald-950);
  --sb-parent-bg          : var(--color-primary-a06);
  --sb-sub-text           : var(--color-text-subtle);
  --sb-sub-hover-bg       : var(--color-primary-a05);
  --sb-section-color      : var(--color-slate-400);

  --sb-tooltip-bg         : var(--color-slate-800);
  --sb-tooltip-text       : var(--color-slate-100);
  --sb-tooltip-border     : var(--color-slate-700);
  --sb-btn-bg             : rgba(255, 255, 255, 0.60);
  --sb-btn-border         : rgba(203, 213, 225, 0.60);
  --sb-btn-hover-bg       : rgba(255, 255, 255, 0.90);
  --sb-logo-text          : var(--color-slate-800);
}


/* ════════════════════════════════════════════════════════════
   DARK MODE OVERRIDES
   ════════════════════════════════════════════════════════════ */
[data-theme="dark"],
.dark {
  /* Surface & background */
  --color-bg              : #0B1120;
  --color-surface         : rgba(20, 30, 50, 0.92);
  --color-surface-strong  : rgba(20, 30, 50, 0.98);
  --color-surface-subtle  : rgba(20, 30, 50, 0.60);

  /* Border */
  --color-border          : rgba(255, 255, 255, 0.10);
  --color-border-subtle   : rgba(255, 255, 255, 0.06);
  --color-border-strong   : rgba(255, 255, 255, 0.16);

  --border-ui             : rgba(255, 255, 255, 0.10);
  --border-ui-subtle      : rgba(255, 255, 255, 0.06);
  --border-ui-strong      : rgba(255, 255, 255, 0.16);

  /* Text */
  --color-text            : #F0F6F3;
  --color-text-muted      : #94A3B8;
  --color-text-subtle     : #475569;

  /* Glass */
  --glass-bg              : rgba(20, 30, 50, 0.72);
  --glass-bg-strong       : rgba(20, 30, 50, 0.94);
  --glass-bg-subtle       : rgba(20, 30, 50, 0.48);
  --glass-bg-emerald      : rgba(0, 103, 79, 0.14);

  /* Shadows deeper in dark */
  --shadow-natural        :
    0 1px 3px  rgba(0, 0, 0, 0.24),
    0 4px 12px rgba(0, 0, 0, 0.18),
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 16px 48px rgba(0, 0, 0, 0.08);

  --shadow-hover          :
    0 4px 16px rgba(0, 103, 79, 0.28),
    0 8px 24px rgba(0, 0, 0, 0.20),
    0 16px 40px rgba(0, 0, 0, 0.14);

  /* Sidebar — dark */
  --sb-bg                 : rgba(5, 10, 24, 0.88);
  --sb-text               : var(--color-slate-400);
  --sb-text-active        : var(--color-emerald-300);
  --sb-icon-color         : var(--color-slate-500);

  --sb-hover-bg           : rgba(0, 168, 107, 0.08);
  --sb-hover-text         : var(--color-emerald-50);
  --sb-active-bg          : linear-gradient(90deg, rgba(0, 168, 107, 0.14) 0%, rgba(0, 168, 107, 0.04) 100%);
  --sb-active-text        : var(--color-emerald-300);
  --sb-parent-bg          : rgba(0, 168, 107, 0.07);
  --sb-sub-text           : var(--color-slate-500);
  --sb-sub-hover-bg       : rgba(0, 168, 107, 0.06);
  --sb-section-color      : var(--color-slate-600);

  --sb-tooltip-bg         : var(--color-slate-100);
  --sb-tooltip-text       : var(--color-slate-800);
  --sb-tooltip-border     : var(--color-slate-200);
  --sb-btn-bg             : rgba(255, 255, 255, 0.04);
  --sb-btn-border         : rgba(255, 255, 255, 0.08);
  --sb-btn-hover-bg       : rgba(0, 168, 107, 0.10);
  --sb-logo-text          : var(--color-emerald-100);
}