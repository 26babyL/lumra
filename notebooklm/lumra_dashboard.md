/* ══════════════════════════════════════════════════════════════
   LUMRA DASHBOARD — lumra_dashboard.css
   Emerald Odyssey Blueprint v1.2
   ══════════════════════════════════════════════════════════════ */

/* ══════════════════════════════════════════════════════════════
   §1. GLASS EFFECTS — Dashboard Components
   ══════════════════════════════════════════════════════════════ */
.chart-card,
.side-card,
.metric-strip,
.quick-stats-bar {
  background     : var(--glass-bg, rgba(255,255,255,0.85));
  backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
  -webkit-backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
  border         : 1px solid var(--glass-border, rgba(255,255,255,0.25));
  border-radius  : 18px;
  box-shadow     : var(--glass-shadow,
                       0 2px 16px rgba(0,0,0,0.06),
                       0 0 0 0.5px rgba(0,0,0,0.04));
}

/* ══════════════════════════════════════════════════════════════
   §2. ANIMATIONS
   ══════════════════════════════════════════════════════════════ */
@keyframes drift {
  from { transform: translate(0,0) scale(1); }
  to   { transform: translate(20px,28px) scale(1.06); }
}

@keyframes toastIn  { from { opacity:0; transform:translateX(24px); } to { opacity:1; transform:none; } }
@keyframes toastOut { from { opacity:1; } to { opacity:0; pointer-events:none; } }

/* ══════════════════════════════════════════════════════════════
   §3. COMPONENT STYLES
   ══════════════════════════════════════════════════════════════ */
.perf-strip {
  background   : linear-gradient(135deg,var(--color-emerald-950) 0%,var(--color-emerald-800) 50%,var(--color-emerald-700) 100%);
  border-radius: 18px;
  box-shadow   : 0 4px 20px var(--color-emerald-700-a022, rgba(4,120,87,0.22));
}

.metric-icon {
  width        : 32px;
  height       : 32px;
  border-radius: 8px;
  background   : var(--color-emerald-600-a010, rgba(5,150,105,0.10));
  display      : flex;
  align-items  : center;
  justify-content: center;
  color        : var(--color-emerald-600);
  font-size    : 13px;
  flex-shrink  : 0;
}

.prod-row {
  display     : flex;
  align-items : center;
  gap         : 10px;
  padding     : 9px 0;
  border-bottom: 1px solid var(--glass-border, rgba(255,255,255,0.18));
  transition  : background .12s;
}

.prod-row:last-child { border-bottom: none; }

.rank-badge {
  width        : 22px;
  height       : 22px;
  border-radius: 6px;
  background   : var(--color-emerald-600-a008, rgba(5,150,105,0.08));
  color        : var(--color-emerald-700);
  font-size    : 11px;
  font-weight  : 700;
  display      : flex;
  align-items  : center;
  justify-content: center;
  flex-shrink  : 0;
}

.rank-badge.top { background: var(--color-emerald-600-a015, rgba(5,150,105,0.15)); color:var(--color-emerald-950); }

.mini-bar-bg {
  background   : rgba(226,232,240,0.40);
  border-radius: 99px;
  height       : 4px;
  overflow     : hidden;
  flex:1;
}

.mini-bar {
  height       : 4px;
  border-radius: 99px;
  background   : linear-gradient(90deg,var(--color-emerald-600),var(--color-emerald-400, #34d399));
  transition   : width .6s ease;
}

/* ══════════════════════════════════════════════════════════════
   §4. TOAST NOTIFICATIONS
   ══════════════════════════════════════════════════════════════ */
.toast {
  background: var(--color-surface-strong);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  animation: toastIn 0.3s ease-out forwards;
}

.toast.out {
  animation: toastOut 0.2s ease-in forwards;
}

/* ══════════════════════════════════════════════════════════════
   §5. RESPONSIVE & UTILITY
   ══════════════════════════════════════════════════════════════ */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ══════════════════════════════════════════════════════════════
   §6. ALPINE.JS CLOAK
   ══════════════════════════════════════════════════════════════ */
[x-cloak] { display: none !important; }