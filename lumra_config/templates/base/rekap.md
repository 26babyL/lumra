sidebar.html
{% load static %}
<style>
  [x-cloak] { display: none !important; }

  :root {
    --emerald-300: #6ee7b7;
    --emerald-400: #34d399;
    --emerald-500: #10b981;
    --emerald-600: #059669;
    --emerald-700: #047857;
    --sidebar-bg: #063d2f;
    --sidebar-surface: rgba(255,255,255,0.05);
    --sidebar-border: rgba(52,211,153,0.12);
    --sidebar-hover: rgba(255,255,255,0.07);
    --sidebar-active-bg: rgba(16,185,129,0.18);
    --sidebar-active-glow: rgba(16,185,129,0.08);
    --text-main: #ecfdf5;
    --text-muted: #6ee7b7;
    --text-dim: rgba(110,231,183,0.45);
    --text-faint: rgba(110,231,183,0.25);
    --danger: #f87171;
    --danger-bg: rgba(248,113,113,0.08);
  }

  /* ── Base ── */
  .sb {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    box-shadow: 2px 0 32px rgba(0,0,0,0.35);
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    border-radius: 0 20px 20px 0;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 60;
    bottom: 0;
    left: 0;
    height: 100vh;

    z-index: 40;
    transition: width 0.28s cubic-bezier(0.4,0,0.2,1);
    will-change: width;
    overflow: hidden;
  }

  /* ── Header ── */
  .sb-header {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 14px;
    border-bottom: 1px solid var(--sidebar-border);
    flex-shrink: 0;
    gap: 10px;
    position: sticky;
    top: 0;
    z-index: 3;
    background: var(--sidebar-bg);
  }

  .sb-logo {
    width: 34px; height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--emerald-400), var(--emerald-700));
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 16px rgba(16,185,129,0.35);
  }

  .sb-logo-text {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.3px;
    white-space: nowrap;
    overflow: hidden;
    transition: opacity 0.2s ease, max-width 0.28s ease;
    max-width: 140px;
  }

  .sb-logo-text.hidden { opacity: 0; max-width: 0; }

  .sb-collapse-btn {
    margin-left: auto;
    width: 26px; height: 26px;
    border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    color: var(--text-muted);
    transition: all 0.15s ease;
    flex-shrink: 0;
  }
  .sb-collapse-btn:hover {
    border-color: var(--emerald-400);
    color: var(--emerald-400);
    background: rgba(16,185,129,0.1);
  }

  /* ── Scroll area ── */
  .sb-nav {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 12px 10px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-height: 0;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .sb-nav::-webkit-scrollbar { display: none; }

  .sb-scroll-region {
    min-height: 0;
  }

  /* ── Section labels ── */
  .sb-section {
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
    padding: 14px 6px 5px;
    white-space: nowrap;
    overflow: hidden;
    transition: opacity 0.2s ease, max-height 0.25s ease, padding 0.25s ease;
  }
  .sb-section.collapsed-hide { opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0; }

  /* ── Divider ── */
  .sb-divider {
    height: 1px;
    background: var(--sidebar-border);
    margin: 6px 4px;
    transition: opacity 0.2s ease;
  }

  /* ── Nav item base ── */
  .sb-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 9px 10px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(110,231,183,0.65);
    text-decoration: none;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
    border: none;
    background: transparent;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
  }

  .sb-item:hover {
    background: var(--sidebar-hover);
    color: var(--text-main);
  }

  .sb-item.active {
    background: var(--sidebar-active-bg);
    color: var(--emerald-400);
    font-weight: 600;
    box-shadow: inset 0 0 0 1px rgba(52,211,153,0.15);
  }

  .sb-item.active::before {
    content: '';
    position: absolute;
    left: 0; top: 22%; bottom: 22%;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: var(--emerald-400);
    box-shadow: 0 0 8px var(--emerald-500);
  }

  .sb-item.parent-active {
    color: var(--text-main);
  }

  /* Collapsed: center icon */
  .sb-item.sb-collapsed-center {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  /* ── Icon ── */
  .sb-icon {
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }

  .sb-icon svg {
    width: 17px; height: 17px;
    stroke-width: 1.8;
    opacity: 0.65;
    transition: opacity 0.15s ease, transform 0.15s ease;
  }

  .sb-item:hover .sb-icon svg,
  .sb-item.active .sb-icon svg,
  .sb-item.parent-active .sb-icon svg {
    opacity: 1;
  }

  .sb-item:hover .sb-icon svg { transform: scale(1.08); }

  /* ── Label ── */
  .sb-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: opacity 0.15s ease, max-width 0.28s ease;
    max-width: 160px;
  }
  .sb-label.hidden { opacity: 0; max-width: 0; }

  /* ── Chevron ── */
  .sb-chevron {
    width: 14px; height: 14px;
    color: var(--text-dim);
    transition: transform 0.25s ease, opacity 0.15s ease;
    flex-shrink: 0;
  }
  .sb-chevron.open { transform: rotate(180deg); color: var(--emerald-400); }
  .sb-chevron.hidden { opacity: 0; max-width: 0; overflow: hidden; }

  /* ── Submenu ── */
  .sb-submenu {
    overflow: hidden;
    padding-left: 14px;
  }

  .sb-submenu[style*='overflow-y:auto'] {
    scrollbar-width: none;
    -ms-overflow-style: none;
    padding-right: 4px;
  }

  .sb-submenu[style*='overflow-y:auto']::-webkit-scrollbar {
    display: none;
  }

  .sb-sub-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px 7px 8px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    color: rgba(110,231,183,0.5);
    text-decoration: none;
    transition: all 0.12s ease;
    white-space: nowrap;
    border-left: 1px solid var(--sidebar-border);
    margin-left: 4px;
  }

  .sb-sub-item::before {
    content: '';
    width: 4px; height: 4px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.4;
    flex-shrink: 0;
    transition: all 0.15s ease;
  }

  .sb-sub-item:hover {
    background: var(--sidebar-hover);
    color: var(--text-main);
    padding-left: 12px;
  }
  .sb-sub-item:hover::before { opacity: 1; background: var(--emerald-400); }

  .sb-sub-item.active {
    color: var(--emerald-400);
    background: rgba(16,185,129,0.08);
    font-weight: 600;
  }
  .sb-sub-item.active::before { background: var(--emerald-400); opacity: 1; }

  /* ── Badge / count ── */
  .sb-badge {
    font-size: 10px;
    font-weight: 700;
    background: rgba(239,68,68,0.18);
    color: var(--danger);
    padding: 1px 6px;
    border-radius: 99px;
    border: 1px solid rgba(239,68,68,0.25);
    flex-shrink: 0;
    transition: opacity 0.2s;
  }
  .sb-badge.hidden { opacity: 0; }

  /* ── Tooltip (collapsed mode) ── */
  .sb-tooltip {
    position: absolute;
    left: calc(100% + 10px);
    top: 50%;
    transform: translateY(-50%) translateX(-4px);
    background: #fff;
    color: #063d2f;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 7px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transition: all 0.18s cubic-bezier(0.16,1,0.3,1);
    z-index: 99;
  }
  .sb-tooltip::before {
    content: '';
    position: absolute;
    right: 100%; top: 50%;
    transform: translateY(-50%);
    border: 5px solid transparent;
    border-right-color: #fff;
  }
  .sb-item:hover .sb-tooltip { opacity: 1; transform: translateY(-50%) translateX(0); }

  /* ── Quick access section ── */
  .sb-quick-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    padding: 4px 0 6px;
    transition: opacity 0.2s ease;
  }

  .sb-quick-grid.hidden { display: none; }

  .sb-quick-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    padding: 10px 6px;
    border-radius: 10px;
    background: var(--sidebar-surface);
    border: 1px solid rgba(255,255,255,0.06);
    color: rgba(110,231,183,0.6);
    font-size: 10.5px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.15s ease;
    cursor: pointer;
    text-align: center;
  }
  .sb-quick-btn:hover {
    background: rgba(255,255,255,0.09);
    color: var(--text-main);
    border-color: rgba(52,211,153,0.25);
  }
  .sb-quick-btn.active {
    background: var(--sidebar-active-bg);
    color: var(--emerald-400);
    border-color: rgba(52,211,153,0.3);
  }
  .sb-quick-btn svg {
    width: 18px; height: 18px;
    stroke-width: 1.7;
    opacity: 0.85;
  }

  /* ── Footer ── */
  .sb-footer {
    margin-top: auto;
    flex-shrink: 0;
    border-top: 1px solid var(--sidebar-border);
    padding: 14px 10px 16px;
    background: linear-gradient(180deg, rgba(6,61,47,0.96), var(--sidebar-bg));
    box-shadow: 0 -10px 30px rgba(0,0,0,0.12);
    position: sticky;
    bottom: 0;
    z-index: 3;
  }

  .sb-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    border-radius: 10px;
    transition: background 0.15s ease;
    cursor: pointer;
    text-decoration: none;
  }
  .sb-user:hover { background: var(--sidebar-hover); }

  .sb-avatar {
    position: relative;
    width: 32px; height: 32px;
    flex-shrink: 0;
  }
  .sb-avatar img {
    width: 32px; height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 1.5px solid rgba(52,211,153,0.4);
  }
  .sb-avatar-dot {
    position: absolute;
    bottom: 0; right: 0;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--emerald-400);
    border: 2px solid var(--sidebar-bg);
  }

  .sb-user-info {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    transition: opacity 0.2s ease, max-width 0.28s ease;
    max-width: 140px;
  }
  .sb-user-info.hidden { opacity: 0; max-width: 0; }

  .sb-user-name {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-main);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sb-user-role {
    font-size: 10.5px;
    color: var(--text-dim);
    white-space: nowrap;
  }

  .sb-logout {
    width: 28px; height: 28px;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-dim);
    transition: all 0.15s ease;
    flex-shrink: 0;
    background: transparent;
    border: none;
    cursor: pointer;
  }
  .sb-logout:hover {
    color: var(--danger);
    background: var(--danger-bg);
  }
  .sb-logout svg { width: 15px; height: 15px; stroke-width: 2; }

  /* ── Logout confirm dialog ── */
  .sb-confirm {
    position: absolute;
    bottom: 70px;
    left: 10px; right: 10px;
    background: #0d4a37;
    border: 1px solid var(--sidebar-border);
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    z-index: 50;
  }
  .sb-confirm p {
    font-size: 12px;
    color: rgba(110,231,183,0.8);
    margin: 0 0 10px;
  }
  .sb-confirm-btns {
    display: flex;
    gap: 6px;
  }
  .sb-confirm-btns button {
    flex: 1;
    padding: 6px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    border: 1px solid transparent;
  }
  .sb-btn-cancel {
    background: rgba(255,255,255,0.06);
    color: rgba(110,231,183,0.7);
    border-color: rgba(255,255,255,0.08) !important;
  }
  .sb-btn-cancel:hover { background: rgba(255,255,255,0.1); color: var(--text-main); }
  .sb-btn-logout {
    background: rgba(248,113,113,0.15);
    color: var(--danger);
    border-color: rgba(248,113,113,0.25) !important;
  }
  .sb-btn-logout:hover { background: rgba(248,113,113,0.25); }

  /* ── Mobile overlay ── */
  .sb-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(3px);
    z-index: 29;
  }
</style>

<aside
  id="sidebar"
  class="sb"
  x-data="sidebarApp()"
  x-init="init()"
  x-cloak
  :style="open ? 'width:260px' : 'width:72px; transform: translateX(0)'"
  :class="{ '-translate-x-full md:translate-x-0': !open && mobile }"
  role="navigation"
  aria-label="Sidebar Navigasi">

  <!-- ── HEADER ── -->
  <div class="sb-header">
    <a href="{% url 'dashboard' %}" class="sb-logo" aria-label="Dashboard">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
        <path d="M2 21v-2h2V3h14v2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2v6h2v2H2zm4-2h8V5H6v14zm10-6h2V7h-2v6z"/>
      </svg>
    </a>

    <span class="sb-logo-text" :class="{ hidden: !open }">CoffeeShop</span>

    <button @click="open = !open"
            class="sb-collapse-btn"
            :aria-label="open ? 'Ciutkan sidebar' : 'Buka sidebar'">
      <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round"
              :d="open ? 'M15 19l-7-7 7-7' : 'M9 5l7 7-7 7'"/>
      </svg>
    </button>
  </div>

  <!-- ── NAV SCROLL ── -->
  <nav class="sb-nav sb-scroll-region" role="menu">

    <!-- ── QUICK ACCESS (collapsed: icon-only grid hidden, show icons stacked) ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Akses Cepat</p>

    <!-- Expanded: 2-col grid -->
    <div class="sb-quick-grid" :class="{ hidden: !open }">
      <a href="{% url 'dashboard' %}"
         class="sb-quick-btn"
         :class="{ active: isActive('/dashboard/') }">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
        </svg>
        Dashboard
      </a>
      <a href="{% url 'pos' %}"
         class="sb-quick-btn"
         :class="{ active: isActive('/pos/') }">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
        Point of Sale
      </a>
      <a href="{% url 'sales_order_list' %}"
         class="sb-quick-btn"
         :class="{ active: isActive('/sales/') }">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Sales
      </a>
      <a href="{% url 'products' %}"
         class="sb-quick-btn"
         :class="{ active: isActive('/inventory/') }">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0v10l-8 4m0-14L4 17m8-10v14"/>
        </svg>
        Inventory
      </a>
    </div>

    <!-- Collapsed: quick access sebagai icon row -->
    <template x-if="!open">
      <div style="display:flex; flex-direction:column; gap:2px;">
        <a href="{% url 'dashboard' %}" class="sb-item sb-collapsed-center" :class="{ active: isActive('/dashboard/') }" role="menuitem">
          <div class="sb-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          </div>
          <span class="sb-tooltip">Dashboard</span>
        </a>
        <a href="{% url 'pos' %}" class="sb-item sb-collapsed-center" :class="{ active: isActive('/pos/') }" role="menuitem">
          <div class="sb-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
          </div>
          <span class="sb-tooltip">Point of Sale</span>
        </a>
      </div>
    </template>

    <div class="sb-divider"></div>

    <!-- ── OPERATIONS ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Operations</p>

    <!-- Sales accordion (max 2 level) -->
    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/sales/','/quotation/','/invoice/','/retur/','/payment/'])">
      <button @click="sub = !sub; $root.activeMenu = sub ? 'sales' : null"
              class="sb-item"
              :class="[isChildActive(['/sales/','/invoice/','/retur/','/payment/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()"
              role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Sales</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Sales</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'sales_order_list' %}" class="sb-sub-item" :class="{ active: isActive('/sales/order') }">Sales Orders</a>
        <a href="{% url 'quotation_list' %}" class="sb-sub-item" :class="{ active: isActive('/sales/quotation') }">Quotations</a>
        <a href="{% url 'invoice_list' %}" class="sb-sub-item" :class="{ active: isActive('/sales/invoice') }">Invoices</a>
        <a href="{% url 'payment_list' %}" class="sb-sub-item" :class="{ active: isActive('/sales/payment') }">Payments</a>
        <a href="{% url 'retur_list' %}" class="sb-sub-item" :class="{ active: isActive('/sales/retur') }">Returns</a>
      </div>
    </div>

    <!-- Inventory accordion -->
    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/inventory/','/products/','/stock-planning/','/stock-movement/','/batch/','/requisition/'])">
      <button @click="sub = !sub; $root.activeMenu = sub ? 'inventory' : null"
              class="sb-item"
              :class="[isChildActive(['/inventory/','/products/','/stock-planning/','/stock-movement/','/batch/','/requisition/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()"
              role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0v10l-8 4m0-14L4 17m8-10v14"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Inventory</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Inventory</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'products' %}" class="sb-sub-item" :class="{ active: isActive('/inventory/products') }">Stock Overview</a>
        <a href="{% url 'stock_planning' %}" class="sb-sub-item" :class="{ active: isActive('/inventory/planning') }">Planning</a>
        <a href="{% url 'stock_movement' %}" class="sb-sub-item" :class="{ active: isActive('/inventory/movement') }">Movements</a>
        <a href="{% url 'batch_list' %}" class="sb-sub-item" :class="{ active: isActive('/inventory/batch') }">Batch Ops</a>
        <a href="{% url 'requisition_list' %}" class="sb-sub-item" :class="{ active: isActive('/inventory/requisition') }">Requisitions</a>
      </div>
    </div>

    <!-- Production accordion -->
    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/production/'])">
      <button @click="sub = !sub; $root.activeMenu = sub ? 'production' : null"
              class="sb-item"
              :class="[isChildActive(['/production/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()"
              role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Production</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Production</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'bom_list' %}" class="sb-sub-item" :class="{ active: isActive('/production/bom') }">Bills of Material</a>
        <a href="{% url 'production_order_list' %}" class="sb-sub-item" :class="{ active: isActive('/production/order') }">Production Orders</a>
        <a href="{% url 'production_scheduling' %}" class="sb-sub-item" :class="{ active: isActive('/production/scheduling') }">Scheduling</a>
        <a href="{% url 'material_consumption' %}" class="sb-sub-item" :class="{ active: isActive('/production/consumption') }">Material Consumption</a>
        <a href="{% url 'finished_goods_receipt' %}" class="sb-sub-item" :class="{ active: isActive('/production/finished') }">Finished Goods</a>
      </div>
    </div>

    <div class="sb-divider"></div>

    <!-- ── ACCOUNTING ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Accounting</p>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/accounting/'])">
      <button @click="sub = !sub"
              class="sb-item"
              :class="[isChildActive(['/accounting/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()"
              role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Accounting</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Accounting</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu" style="max-height:280px;overflow-y:auto;">
        <a href="{% url 'chart_of_accounts' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/coa') }">Chart of Accounts</a>
        <a href="{% url 'general_ledger' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/ledger') }">General Ledger</a>
        <a href="{% url 'journal_entry_list' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/journal') }">Journal Entries</a>
        <a href="{% url 'payment_voucher_form' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/voucher') }">Payment Voucher</a>
        <a href="{% url 'trial_balance' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/trial') }">Trial Balance</a>
        <a href="{% url 'balance_sheet' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/balance') }">Balance Sheet</a>
        <a href="{% url 'profit_loss_statement' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/income') }">Income Statement</a>
        <a href="{% url 'cash_flow_statement' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/cashflow') }">Cash Flow</a>
        <a href="{% url 'accounts_receivable' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/ar') }">Accounts Receivable</a>
        <a href="{% url 'accounts_payable' %}" class="sb-sub-item" :class="{ active: isActive('/accounting/ap') }">Accounts Payable</a>
      </div>
    </div>

    <div class="sb-divider"></div>

    <!-- ── LOGISTICS & MORE ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Logistics</p>

    <a href="{% url 'locations' %}" class="sb-item" :class="[isActive('/locations/') ? 'active' : '', !open ? 'sb-collapsed-center' : '']" role="menuitem">
      <div class="sb-icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      </div>
      <span class="sb-label" :class="{ hidden: !open }">Locations</span>
      <span class="sb-tooltip">Locations</span>
    </a>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/purchasing/','/warehouse/'])">
      <button @click="sub = !sub"
              class="sb-item"
              :class="[isChildActive(['/purchasing/','/warehouse/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()"
              role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Procurement</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Procurement</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'purchasing' %}" class="sb-sub-item" :class="{ active: isActive('/purchasing/') }">Purchase Orders</a>
        <a href="{% url 'supplier_price_list' %}" class="sb-sub-item" :class="{ active: isActive('/supplier-price-list/') }">Supplier Prices</a>
        <a href="{% url 'warehouse_zones' %}" class="sb-sub-item" :class="{ active: isActive('/warehouse/') }">Warehouse Zones</a>
      </div>
    </div>

    <div class="sb-divider"></div>

    <!-- ── OTHER SECTIONS ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Marketing & Data</p>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/marketing/'])">
      <button @click="sub = !sub" class="sb-item"
              :class="[isChildActive(['/marketing/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()" role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Marketing</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Marketing</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'campaign_list' %}" class="sb-sub-item" :class="{ active: isActive('/marketing/campaign') }">Campaigns</a>
        <a href="{% url 'discount_list' %}" class="sb-sub-item" :class="{ active: isActive('/marketing/discount') }">Discounts</a>
        <a href="{% url 'voucher_list' %}" class="sb-sub-item" :class="{ active: isActive('/marketing/voucher') }">Vouchers</a>
        <a href="{% url 'loyalty_members' %}" class="sb-sub-item" :class="{ active: isActive('/marketing/loyalty') }">Loyalty Program</a>
        <a href="{% url 'promotion_calendar' %}" class="sb-sub-item" :class="{ active: isActive('/marketing/promotions') }">Promotions</a>
      </div>
    </div>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/master/'])">
      <button @click="sub = !sub" class="sb-item"
              :class="[isChildActive(['/master/','/bank-accounts/','/payment-terms/','/taxes/','/tags/','/categories/','/units/','/vendors/','/customers/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()" role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Master Data</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Master Data</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu" style="max-height:240px;overflow-y:auto;">
        <a href="{% url 'customer_list' %}" class="sb-sub-item" :class="{ active: isActive('/master/customers') }">Customers</a>
        <a href="{% url 'vendors_list' %}" class="sb-sub-item" :class="{ active: isActive('/master/vendors') }">Vendors</a>
        <a href="{% url 'categories_list' %}" class="sb-sub-item" :class="{ active: isActive('/master/categories') }">Categories</a>
        <a href="{% url 'units_list' %}" class="sb-sub-item" :class="{ active: isActive('/master/units') }">Units</a>
        <a href="{% url 'bank_accounts' %}" class="sb-sub-item" :class="{ active: isActive('/bank-accounts/') }">Bank Accounts</a>
        <a href="{% url 'payment_terms_list' %}" class="sb-sub-item" :class="{ active: isActive('/payment-terms/') }">Payment Terms</a>
        <a href="{% url 'tax_list' %}" class="sb-sub-item" :class="{ active: isActive('/taxes/') }">Taxes</a>
        <a href="{% url 'tags_list' %}" class="sb-sub-item" :class="{ active: isActive('/tags/') }">Tags</a>
      </div>
    </div>

    <div class="sb-divider"></div>

    <!-- ── REPORTS & SETTINGS ── -->
    <p class="sb-section" :class="{ 'collapsed-hide': !open }">Reports & Settings</p>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/reports/'])">
      <button @click="sub = !sub" class="sb-item"
              :class="[isChildActive(['/reports/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()" role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Reports</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Reports</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu">
        <a href="{% url 'sales_report' %}" class="sb-sub-item" :class="{ active: isActive('/reports/sales') }">Sales Report</a>
        <a href="{% url 'report_expiry' %}" class="sb-sub-item" :class="{ active: isActive('/reports/expiry') }">Expiry Report</a>
        <a href="{% url 'report_inventory_age' %}" class="sb-sub-item" :class="{ active: isActive('/reports/inventory-age') }">Inventory Age</a>
        <a href="{% url 'report_production' %}" class="sb-sub-item" :class="{ active: isActive('/reports/production') }">Production</a>
        <a href="{% url 'report_staff_performance' %}" class="sb-sub-item" :class="{ active: isActive('/reports/staff') }">Staff Performance</a>
        <a href="{% url 'report_customer_lifetime' %}" class="sb-sub-item" :class="{ active: isActive('/reports/customer-lifetime') }">Customer Lifetime</a>
      </div>
    </div>

    <!-- Notifications — bukan di Settings lagi -->
    <a href="{% url 'notification' %}"
       class="sb-item"
       :class="[isActive('/notifications/') ? 'active' : '', !open ? 'sb-collapsed-center' : '']"
       role="menuitem">
      <div class="sb-icon" style="position:relative;">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 00-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
        {% if notifications_count %}
        <span style="position:absolute;top:2px;right:2px;width:8px;height:8px;background:#ef4444;border-radius:50%;border:2px solid var(--sidebar-bg);"></span>
        {% endif %}
      </div>
      <span class="sb-label" :class="{ hidden: !open }">Notifications</span>
      {% if notifications_count %}
      <span class="sb-badge" :class="{ hidden: !open }">{{ notifications_count }}</span>
      {% endif %}
      <span class="sb-tooltip">Notifications{% if notifications_count %} ({{ notifications_count }}){% endif %}</span>
    </a>

    <div x-data="{ sub: false }" x-init="sub = isChildActive(['/settings/'])">
      <button @click="sub = !sub" class="sb-item"
              :class="[isChildActive(['/settings/']) ? 'parent-active' : '', !open ? 'sb-collapsed-center' : '']"
              :aria-expanded="sub.toString()" role="menuitem">
        <div class="sb-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </div>
        <span class="sb-label" :class="{ hidden: !open }">Settings</span>
        <svg class="sb-chevron" :class="{ open: sub, hidden: !open }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        <span class="sb-tooltip">Settings</span>
      </button>
      <div x-show="sub && open" x-collapse class="sb-submenu" style="max-height:260px;overflow-y:auto;">
        <a href="{% url 'users_list' %}" class="sb-sub-item" :class="{ active: isActive('/settings/users') }">Users & Roles</a>
        <a href="{% url 'permission_matrix' %}" class="sb-sub-item" :class="{ active: isActive('/settings/permissions') }">Permissions</a>
        <a href="{% url 'business_profile' %}" class="sb-sub-item" :class="{ active: isActive('/settings/business') }">Business Profile</a>
        <a href="{% url 'email_settings' %}" class="sb-sub-item" :class="{ active: isActive('/settings/email') }">Email</a>
        <a href="{% url 'numbering_settings' %}" class="sb-sub-item" :class="{ active: isActive('/settings/numbering') }">Numbering</a>
        <a href="{% url 'backup_restore' %}" class="sb-sub-item" :class="{ active: isActive('/settings/backup') }">Backup & Restore</a>
        <a href="{% url 'api_keys' %}" class="sb-sub-item" :class="{ active: isActive('/settings/api') }">API Keys</a>
        <a href="{% url 'system_status' %}" class="sb-sub-item" :class="{ active: isActive('/settings/system') }">System Status</a>
        <a href="{% url 'about' %}" class="sb-sub-item" :class="{ active: isActive('/settings/about') }">About</a>
      </div>
    </div>

  </nav>

  <!-- ── FOOTER ── -->
  <div class="sb-footer" style="position:relative;">

    <!-- Logout confirmation dialog -->
    <div class="sb-confirm" x-show="confirmLogout" x-cloak x-transition>
      <p>Yakin mau keluar dari sesi ini?</p>
      <div class="sb-confirm-btns">
        <button class="sb-btn-cancel" @click="confirmLogout = false">Batal</button>
        <a href="{% url 'logout' %}" class="sb-btn-logout" style="display:flex;align-items:center;justify-content:center;text-decoration:none;">Keluar</a>
      </div>
    </div>

    <div class="flex items-center" :class="open ? 'gap-2' : 'justify-center'">
      <!-- Avatar -->
      <div style="position:relative;flex-shrink:0;">
        <a href="{% url 'profile' %}">
          <img src="{{ user.profile.avatar.url|default:'/static/img/default-avatar.png' }}"
               style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:1.5px solid rgba(52,211,153,0.4);display:block;"
               alt="{{ user.get_full_name|default:user.username }}"
               onerror="this.src='/static/img/default-avatar.png'">
        </a>
        <span class="sb-avatar-dot"></span>
        <!-- tooltip for collapsed -->
        <span class="sb-tooltip" x-show="!open" x-cloak>{{ user.get_full_name|default:user.username }}</span>
      </div>

      <!-- User info -->
      <div class="sb-user-info" :class="{ hidden: !open }">
        <a href="{% url 'profile' %}" class="sb-user-name" style="display:block;text-decoration:none;transition:color 0.15s;" onmouseover="this.style.color='#6ee7b7'" onmouseout="this.style.color=''">
          {{ user.get_full_name|default:user.username }}
        </a>
        <p class="sb-user-role">{{ user.profile.role|default:"Admin" }}</p>
      </div>

      <!-- Logout btn -->
      <button class="sb-logout"
              x-show="open"
              @click="confirmLogout = true"
              title="Keluar"
              aria-label="Keluar dari sistem">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile overlay -->
  <div class="sb-overlay"
       x-show="open && mobile"
       x-cloak
       x-transition:enter="transition-opacity duration-200"
       x-transition:enter-start="opacity-0"
       x-transition:enter-end="opacity-100"
       x-transition:leave="transition-opacity duration-150"
       x-transition:leave-end="opacity-0"
       @click="open = false"
       aria-hidden="true">
  </div>

</aside>

<script>
function sidebarApp() {
  return {
    open: (JSON.parse(localStorage.getItem('sidebarOpen') || 'true')) && window.innerWidth >= 768,
    mobile: window.innerWidth < 768,
    activeMenu: null,
    confirmLogout: false,

    init() {
      this.$watch('open', v => {
        localStorage.setItem('sidebarOpen', v);
        document.body.classList.toggle('sidebar-open', v);
        window.dispatchEvent(new CustomEvent('sidebar-toggled', { detail: { open: v } }));
      });
      document.body.classList.toggle('sidebar-open', this.open);

      let t;
      window.addEventListener('resize', () => {
        clearTimeout(t);
        t = setTimeout(() => {
          this.mobile = window.innerWidth < 768;
          if (this.mobile) this.open = false;
          else this.open = JSON.parse(localStorage.getItem('sidebarOpen') || 'true');
        }, 100);
      });

      window.addEventListener('toggle-sidebar', () => { this.open = !this.open; });

      window.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
          e.preventDefault(); this.open = !this.open;
        }
        if (e.key === 'Escape') {
          if (this.confirmLogout) this.confirmLogout = false;
          else if (this.mobile) this.open = false;
        }
      });
    },

    isActive(path) {
      const cur = window.location.pathname;
      return cur === path || (path.endsWith('/') && cur.startsWith(path)) || cur.startsWith(path + '/');
    },

    isChildActive(routes) {
      return routes.some(p => this.isActive(p));
    },
  };
}
</script>

navbar.html
{% load static %}
<style>
  [x-cloak] { display: none !important; }

  :root {
    --nav-bg: rgba(255,255,255,0.92);
    --nav-border: rgba(0,103,79,0.07);
    --nav-blur: blur(20px) saturate(180%);
    --jade: #00A86B;
    --jade-light: rgba(0,168,107,0.1);
    --jade-ring: rgba(0,168,107,0.2);
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --text-faint: #cbd5e1;
    --surface: #f8fafc;
    --surface-hover: rgba(0,168,107,0.06);
    --surface-active: rgba(0,168,107,0.1);
    --dropdown-bg: #ffffff;
    --dropdown-border: rgba(0,0,0,0.06);
    --dropdown-shadow: 0 16px 48px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.05);
    --divider: rgba(0,0,0,0.05);
    --danger: #ef4444;
  }

  .dark {
    --nav-bg: rgba(13,20,35,0.92);
    --nav-border: rgba(0,168,107,0.1);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --text-faint: #475569;
    --surface: rgba(30,41,59,0.7);
    --surface-hover: rgba(0,168,107,0.1);
    --surface-active: rgba(0,168,107,0.15);
    --dropdown-bg: #1a2540;
    --dropdown-border: rgba(100,116,139,0.15);
    --dropdown-shadow: 0 16px 48px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.25);
    --divider: rgba(100,116,139,0.1);
  }

  /* ── Navbar shell ── */
  .nav {
    background: #ffffff;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-bottom: 1px solid rgba(226,232,240,0.9);
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px 0 calc(var(--sidebar-collapsed-width) + 20px);
    gap: 14px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 80;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    box-shadow: 0 1px 0 rgba(226,232,240,0.9), 0 8px 24px rgba(15,23,42,0.04);
  }

  body.sidebar-open .nav {
    padding-left: calc(var(--sidebar-expanded-width) + 20px);
  }

  /* ── Icon button base ── */
  .nav-btn {
    position: relative;
    width: 34px; height: 34px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-muted);
    transition: all 0.15s ease;
    background: transparent;
    border: none;
    cursor: pointer;
    flex-shrink: 0;
  }
  .nav-btn:hover { background: var(--surface-hover); color: var(--text-primary); }
  .nav-btn:active { transform: scale(0.95); }
  .nav-btn svg { width: 17px; height: 17px; stroke-width: 1.8; }

  /* ── Dropdown base ── */
  .nav-dropdown {
    position: absolute;
    top: calc(100% + 10px);
    background: var(--dropdown-bg);
    border: 1px solid var(--dropdown-border);
    border-radius: 14px;
    box-shadow: var(--dropdown-shadow);
    overflow: hidden;
    z-index: 50;
  }

  /* ── Store pill ── */
  /* FIX: satu deklarasi border — tidak ada duplikasi */
  .store-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border: 1px solid var(--nav-border);
    border-radius: 10px;
    background: #ffffff;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
    font-family: inherit;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
  }
  .store-pill:hover { background: #f8fafc; border-color: rgba(0,168,107,0.18); }
  .store-pill:active { transform: scale(0.98); }

  .store-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .store-dot.online { background: var(--jade); animation: pulse 2.5s ease infinite; }
  .store-dot.live { background: var(--jade); animation: pulse 2.5s ease infinite; }
  .store-dot.warning { background: #f59e0b; }
  .store-dot.busy { background: #f59e0b; }
  .store-dot.offline { background: #94a3b8; }

  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,168,107,0.4); }
    50% { box-shadow: 0 0 0 4px rgba(0,168,107,0); }
  }

  /* ── Store dropdown ── */
  .store-dropdown { left: 0; width: 280px; }

  .store-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    cursor: pointer;
    transition: background 0.12s ease;
    border: none;
    background: transparent;
    width: 100%;
    text-align: left;
  }
  .store-item:hover { background: var(--surface-hover); }
  .store-item.active { background: var(--surface-active); }

  .store-item-icon {
    width: 34px; height: 34px;
    border-radius: 9px;
    background: var(--surface);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 14px;
  }

  .store-status-badge {
    font-size: 9px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 99px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    flex-shrink: 0;
  }
  .store-status-badge.live    { background: rgba(0,168,107,0.12); color: #047857; }
  .store-status-badge.busy    { background: rgba(245,158,11,0.12); color: #92400e; }
  .store-status-badge.offline { background: rgba(148,163,184,0.15); color: #64748b; }
  .store-status-badge.online  { background: rgba(0,168,107,0.12); color: #047857; }

  .dark .store-status-badge.live    { background: rgba(0,168,107,0.18); color: #34d399; }
  .dark .store-status-badge.busy    { background: rgba(245,158,11,0.18); color: #fbbf24; }
  .dark .store-status-badge.offline { background: rgba(100,116,139,0.18); color: #94a3b8; }
  .dark .store-status-badge.online  { background: rgba(0,168,107,0.18); color: #34d399; }

  /* ── Search ── */
  .search-wrap { position: relative; flex: 1; width: 100%; max-width: 560px; min-width: 0; }

  .search-input {
    width: 100%;
    height: 36px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0 40px 0 36px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    font-family: inherit;
    transition: all 0.2s ease;
    outline: none;
  }
  .search-input:focus {
    background: #ffffff;
    border-color: var(--jade-ring);
    box-shadow: 0 0 0 3px rgba(0,168,107,0.1);
  }
  .search-input::placeholder { color: var(--text-faint); }

  .search-icon {
    position: absolute;
    left: 10px; top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: var(--text-muted);
    transition: color 0.15s;
  }

  /* FIX: selector class diperbaiki dari .search-hint-right → .search-right */
  .search-input:focus ~ .search-right .kbd { opacity: 0; }

  .search-right {
    position: absolute;
    right: 10px; top: 50%;
    transform: translateY(-50%);
    display: flex; align-items: center; gap: 4px;
  }

  /* Token chip */
  .cmd-token {
    display: inline-flex;
    align-items: center;
    padding: 2px 7px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .cmd-token.product  { background: rgba(0,168,107,0.12); color: #047857; }
  .cmd-token.location { background: rgba(59,130,246,0.1);  color: #1d4ed8; }
  .cmd-token.stock    { background: rgba(245,158,11,0.12); color: #92400e; }

  .dark .cmd-token.product  { background: rgba(0,168,107,0.18); color: #34d399; }
  .dark .cmd-token.location { background: rgba(59,130,246,0.18); color: #60a5fa; }
  .dark .cmd-token.stock    { background: rgba(245,158,11,0.18); color: #fbbf24; }

  /* Kbd hint */
  .kbd {
    display: inline-flex;
    align-items: center;
    padding: 1px 5px;
    border: 1px solid var(--divider);
    border-radius: 5px;
    background: var(--surface);
    font-size: 10px;
    font-family: 'SF Mono','Fira Code',monospace;
    font-weight: 600;
    color: var(--text-muted);
    line-height: 1.6;
    transition: opacity 0.15s;
  }

  /* Search dropdown */
  .search-dropdown { left: 0; right: 0; top: calc(100% + 8px); }

  .search-result-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    cursor: pointer;
    transition: background 0.1s;
    position: relative;
  }
  .search-result-item:hover { background: var(--surface-hover); }
  .search-result-item.kb-active { background: var(--surface-active); }
  .search-result-item.kb-active::before {
    content: '';
    position: absolute;
    left: 0; top: 15%; bottom: 15%;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: var(--jade);
  }

  .result-type-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px;
    font-weight: 700;
    flex-shrink: 0;
  }
  .result-type-icon.product  { background: rgba(0,168,107,0.1);  color: #047857; }
  .result-type-icon.location { background: rgba(59,130,246,0.1);  color: #1d4ed8; }
  .result-type-icon.stock    { background: rgba(245,158,11,0.1);  color: #92400e; }
  .dark .result-type-icon.product  { background: rgba(0,168,107,0.18); color: #34d399; }
  .dark .result-type-icon.location { background: rgba(59,130,246,0.18); color: #60a5fa; }
  .dark .result-type-icon.stock    { background: rgba(245,158,11,0.18); color: #fbbf24; }

  .badge-pill {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 99px;
    flex-shrink: 0;
  }
  .badge-pill.success { background: rgba(0,168,107,0.1);  color: #047857; }
  .badge-pill.warning { background: rgba(245,158,11,0.1);  color: #92400e; }
  .badge-pill.danger  { background: rgba(239,68,68,0.1);   color: #dc2626; }
  .badge-pill.neutral { background: var(--surface-hover);  color: var(--text-muted); }
  .dark .badge-pill.success { background: rgba(0,168,107,0.18); color: #34d399; }
  .dark .badge-pill.warning { background: rgba(245,158,11,0.18); color: #fbbf24; }
  .dark .badge-pill.danger  { background: rgba(239,68,68,0.18);  color: #f87171; }

  .section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-faint);
    padding: 10px 14px 5px;
    user-select: none;
  }

  /* Scrollbar */
  .scroll-thin::-webkit-scrollbar { width: 3px; }
  .scroll-thin::-webkit-scrollbar-track { background: transparent; }
  .scroll-thin::-webkit-scrollbar-thumb { background: var(--text-faint); border-radius: 10px; }

  /* ── Notification dot ── */
  .notif-dot {
    position: absolute;
    top: 5px; right: 5px;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--danger);
    border: 2px solid var(--nav-bg);
    animation: notifPulse 2.5s ease infinite;
  }
  @keyframes notifPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50%       { box-shadow: 0 0 0 4px rgba(239,68,68,0); }
  }

  /* ── Notif panel ── */
  .notif-dropdown { right: 0; width: 320px; }

  .notif-type-badge {
    font-size: 9px;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .notif-type-badge.stock  { background: rgba(245,158,11,0.12); color: #92400e; }
  .notif-type-badge.system { background: rgba(59,130,246,0.1);  color: #1d4ed8; }
  .notif-type-badge.report { background: rgba(0,168,107,0.1);   color: #047857; }
  .notif-type-badge.alert  { background: rgba(239,68,68,0.1);   color: #dc2626; }

  .dark .notif-type-badge.stock  { background: rgba(245,158,11,0.18); color: #fbbf24; }
  .dark .notif-type-badge.system { background: rgba(59,130,246,0.18); color: #60a5fa; }
  .dark .notif-type-badge.report { background: rgba(0,168,107,0.18);  color: #34d399; }
  .dark .notif-type-badge.alert  { background: rgba(239,68,68,0.18);  color: #f87171; }

  .notif-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 11px 14px;
    transition: background 0.12s;
    text-decoration: none;
    position: relative;
  }
  .notif-item:hover { background: var(--surface-hover); }
  .notif-item.unread { background: rgba(0,168,107,0.02); }
  .notif-unread-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--jade);
    flex-shrink: 0;
    margin-top: 5px;
  }

  /* ── Profile ── */
  .profile-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px 4px 4px;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.15s;
    border: none;
    background: transparent;
    font-family: inherit;
  }
  .profile-trigger:hover { background: #f8fafc; }

  .profile-dropdown { right: 0; width: 220px; }

  .profile-menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    font-size: 13px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.12s;
    cursor: pointer;
    border: none;
    background: transparent;
    width: 100%;
    text-align: left;
    font-family: inherit;
  }
  .profile-menu-item:hover { background: var(--surface-hover); color: var(--text-primary); }
  .profile-menu-item svg { width: 15px; height: 15px; flex-shrink: 0; color: var(--text-muted); }

  .profile-menu-item.danger       { color: #ef4444; }
  .profile-menu-item.danger:hover { background: rgba(239,68,68,0.06); color: #dc2626; }
  .profile-menu-item.danger svg   { color: #ef4444; }
  .dark .profile-menu-item.danger { color: #f87171; }

  /* ── Avatar ring ── */
  .avatar-img {
    border-radius: 50%;
    object-fit: cover;
    border: 1.5px solid var(--divider);
    transition: border-color 0.15s;
  }
  .profile-trigger:hover .avatar-img { border-color: var(--jade); }

  /* ── Divider ── */
  .nav-divider { width: 1px; height: 20px; background: var(--divider); flex-shrink: 0; }

  .nav-toggle {
    margin-right: 2px;
  }

  @media (max-width: 768px) {
    .nav {
      height: 60px;
      padding: 0 12px;
      gap: 8px;
    }

    body.sidebar-open .nav {
      padding-left: 12px;
    }

    .store-pill {
      max-width: 160px;
      padding: 6px 10px;
    }

    .store-pill > span:nth-child(2) {
      max-width: 84px !important;
    }

    .search-input {
      font-size: 12px;
    }

    .notif-dropdown,
    .profile-dropdown {
      width: min(320px, calc(100vw - 20px));
      right: 0;
    }
  }

  @media (max-width: 640px) {
    .nav {
      flex-wrap: nowrap;
    }

    .search-wrap {
      max-width: none;
    }

    .store-pill > span:nth-child(3) {
      display: none;
    }
  }
</style>

<!--
  FIX SUMMARY:
  1. Tambah class `header-shift` — navbar sekarang mengikuti lebar sidebar
  2. Store pill duplikat di sidebar dihapus — hanya navbar yang manage store switcher
  3. Selector CSS `.search-hint-right` → `.search-right` diperbaiki
  4. `border: none` duplikat di `.store-pill` dihapus
  5. `border-radius` + `overflow:hidden` di `.nav` dihapus — mencegah dropdown terpotong
  6. z-index navbar turun ke 20 — sidebar tetap tampil di atas saat overlay mobile
  7. `notifCount` dipindah ke Alpine data object — reaktif, tidak lagi hardcode di x-show
-->
<header
  class="nav header-shift"
  x-data="navApp()"
  x-init="init()"
  x-cloak>

  <!-- ── LEFT: Store Switcher ── -->
  <div class="flex items-center gap-2 flex-shrink-0">
    <button
      @click="$dispatch('toggle-sidebar'); window.dispatchEvent(new CustomEvent('toggle-sidebar'))"
      class="nav-btn nav-toggle"
      aria-label="Toggle sidebar">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h16M4 17h16"/>
      </svg>
    </button>

    <!-- Store Switcher — SATU-SATUNYA store switcher, sidebar tidak punya lagi -->
    <div class="relative" @click.outside="storeOpen=false">
      <button @click="storeOpen=!storeOpen"
              class="store-pill"
              :aria-expanded="storeOpen.toString()">
        <span class="store-dot" :class="activeStore.status || 'online'"></span>
        <span style="max-width:140px;overflow:hidden;text-overflow:ellipsis;" x-text="activeStore.name"></span>
        <span x-show="activeStore.city"
              style="font-size:11px;color:var(--text-muted);font-weight:500;"
              x-text="activeStore.city"></span>
        <svg style="width:12px;height:12px;color:var(--text-muted);transition:transform 0.2s;"
             :style="storeOpen ? 'transform:rotate(180deg)' : ''"
             fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      <!-- Store dropdown -->
      <div x-show="storeOpen"
           x-transition:enter="transition ease-out duration-150"
           x-transition:enter-start="opacity-0 scale-95 -translate-y-1"
           x-transition:enter-end="opacity-100 scale-100 translate-y-0"
           x-transition:leave="transition ease-in duration-100"
           x-transition:leave-end="opacity-0 scale-95 -translate-y-1"
           class="nav-dropdown store-dropdown">

        <div class="section-label">Pilih Cabang</div>

        <div class="scroll-thin" style="max-height:240px;overflow-y:auto;">
          <template x-for="store in stores" :key="store.id">
            <button @click="switchStore(store)"
                    class="store-item"
                    :class="store.id === activeStore.id ? 'active' : ''">
              <div class="store-item-icon" x-text="store.emoji || '🏪'"></div>
              <div style="flex:1;min-width:0;">
                <p style="font-size:13px;font-weight:600;color:var(--text-primary);margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                   x-text="store.name"></p>
                <p style="font-size:11px;color:var(--text-muted);margin:0;"
                   x-text="store.city || store.address || ''"></p>
              </div>
              <span class="store-status-badge"
                    :class="store.status || 'live'"
                    x-text="store.statusLabel || 'Live'"></span>
              <svg x-show="store.id === activeStore.id"
                   style="width:14px;height:14px;flex-shrink:0;color:var(--jade);"
                   fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            </button>
          </template>
        </div>

        <div style="border-top:1px solid var(--divider);padding:10px 14px;">
          <a href="#" style="font-size:12px;font-weight:600;color:var(--jade);text-decoration:none;">+ Tambah Cabang</a>
        </div>
      </div>
    </div>
  </div>

  <!-- ── CENTER: Search ── -->
  <div class="flex-1 flex justify-center px-2" style="min-width:0;">
    <div class="search-wrap" @click.outside="closeSearch()">
      <div style="position:relative;">

        <!-- Left icon -->
        <div class="search-icon">
          <svg style="width:15px;height:15px;"
               :style="searchFocused ? 'color:var(--jade)' : 'color:var(--text-muted)'"
               fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
        </div>

        <!-- Token chip (muncul saat pakai prefix P:/L:/S:) -->
        <div x-show="parsedCmd.prefix"
             style="position:absolute;left:32px;top:50%;transform:translateY(-50%);z-index:5;pointer-events:none;">
          <span class="cmd-token" :class="parsedCmd.type" x-ref="tokenEl" x-text="parsedCmd.label"></span>
        </div>

        <!-- Input -->
        <input id="nav-search"
               type="text"
               x-model="query"
               :placeholder="searchFocused ? '' : placeholderHints[hintIdx]"
               @focus="onFocus()"
               @blur="searchFocused=false"
               @input="onInput()"
               @keydown.escape="closeSearch()"
               @keydown.arrow-down.prevent="kbDown()"
               @keydown.arrow-up.prevent="kbUp()"
               @keydown.enter.prevent="onEnter()"
               @keydown.slash.prevent.window="focusSearch()"
               @keydown.meta.k.prevent.window="focusSearch()"
               @keydown.ctrl.k.prevent.window="focusSearch()"
               autocomplete="off"
               spellcheck="false"
               class="search-input"
               :style="parsedCmd.prefix && tokenW > 0 ? `padding-left: calc(2.25rem + ${tokenW}px + 6px)` : 'padding-left:2.25rem'"
               aria-label="Cari produk, lokasi, atau stok">

        <!-- Right: clear + kbd hint -->
        <div class="search-right">
          <button x-show="query.length > 0"
                  @click="clearSearch()"
                  class="nav-btn"
                  style="width:24px;height:24px;border-radius:6px;"
                  aria-label="Hapus">
            <svg style="width:12px;height:12px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <span x-show="query.length === 0 && !searchFocused" class="kbd">/</span>
          <span x-show="query.length === 0 && searchFocused" class="kbd" style="font-size:9px;">ESC</span>
        </div>
      </div>

      <!-- Search dropdown -->
      <div x-show="showDropdown"
           x-transition:enter="transition ease-out duration-150"
           x-transition:enter-start="opacity-0 scale-[0.98] -translate-y-1"
           x-transition:enter-end="opacity-100 scale-100 translate-y-0"
           x-transition:leave="transition ease-in duration-100"
           x-transition:leave-end="opacity-0 -translate-y-1"
           class="nav-dropdown search-dropdown">

        <!-- Idle: hints + recent -->
        <template x-if="!query && searchFocused">
          <div>
            <div class="section-label">Shortcut Pencarian</div>
            <div style="padding:4px 10px 8px;">
              <template x-for="h in cmdHints" :key="h.prefix">
                <button @click="query = h.prefix + ' '; $nextTick(() => document.getElementById('nav-search').focus())"
                        style="display:flex;align-items:center;gap:10px;width:100%;padding:8px 10px;border-radius:9px;border:none;background:transparent;cursor:pointer;transition:background 0.1s;"
                        onmouseover="this.style.background='var(--surface-hover)'"
                        onmouseout="this.style.background='transparent'">
                  <span class="cmd-token" :class="h.type" x-text="h.label"></span>
                  <span style="font-size:12px;flex:1;text-align:left;color:var(--text-muted);" x-text="h.desc"></span>
                  <span class="kbd" x-text="h.prefix"></span>
                </button>
              </template>
            </div>
            <template x-if="recent.length > 0">
              <div>
                <div class="section-label" style="border-top:1px solid var(--divider);padding-top:10px;margin-top:2px;">Terakhir Dicari</div>
                <div style="padding-bottom:6px;">
                  <template x-for="r in recent" :key="r">
                    <button @click="query=r;onInput()"
                            style="display:flex;align-items:center;gap:8px;width:100%;padding:8px 14px;border:none;background:transparent;cursor:pointer;transition:background 0.1s;font-family:inherit;"
                            onmouseover="this.style.background='var(--surface-hover)'"
                            onmouseout="this.style.background='transparent'">
                      <svg style="width:13px;height:13px;color:var(--text-faint);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      <span style="font-size:13px;color:var(--text-secondary);" x-text="r"></span>
                    </button>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </template>

        <!-- Loading -->
        <template x-if="loading && query">
          <div style="display:flex;align-items:center;gap:10px;padding:16px 14px;">
            <svg style="width:15px;height:15px;color:var(--jade);" class="animate-spin" fill="none" viewBox="0 0 24 24">
              <circle style="opacity:0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path style="opacity:0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <span style="font-size:13px;color:var(--text-muted);">Mencari...</span>
          </div>
        </template>

        <!-- Results -->
        <template x-if="!loading && results.length > 0 && query">
          <div>
            <div class="section-label" x-text="resultsLabel"></div>
            <div class="scroll-thin" style="max-height:260px;overflow-y:auto;padding-bottom:6px;">
              <template x-for="(item, idx) in results" :key="item.id">
                <button @click="selectResult(item)"
                        class="search-result-item"
                        :class="idx === kbIdx ? 'kb-active' : ''"
                        style="width:100%;border:none;font-family:inherit;background:transparent;">
                  <div class="result-type-icon" :class="item.type"
                       x-text="item.type === 'product' ? 'P' : item.type === 'location' ? 'L' : 'S'"></div>
                  <div style="flex:1;min-width:0;text-align:left;">
                    <p style="font-size:13px;font-weight:500;color:var(--text-primary);margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                       x-text="item.name"></p>
                    <p style="font-size:11px;color:var(--text-muted);margin:0;"
                       x-text="item.subtitle"></p>
                  </div>
                  <span x-show="item.badge"
                        class="badge-pill"
                        :class="item.badgeType || 'neutral'"
                        x-text="item.badge"></span>
                </button>
              </template>
            </div>
            <div style="border-top:1px solid var(--divider);padding:8px 14px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:11px;color:var(--text-muted);" x-text="results.length + ' hasil'"></span>
              <span style="font-size:11px;color:var(--text-muted);display:flex;gap:4px;align-items:center;">
                <span class="kbd">↵</span> lihat semua
              </span>
            </div>
          </div>
        </template>

        <!-- Empty -->
        <template x-if="!loading && results.length === 0 && query.length > 1">
          <div style="padding:32px 14px;text-align:center;">
            <svg style="width:28px;height:28px;color:var(--text-faint);margin:0 auto 10px;" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <p style="font-size:13px;font-weight:500;color:var(--text-secondary);margin:0 0 4px;">
              Tidak ada hasil untuk "<span style="color:var(--text-primary);" x-text="parsedCmd.term || query"></span>"
            </p>
            <p x-show="!parsedCmd.prefix" style="font-size:11px;color:var(--text-faint);margin:0;">
              Coba: <span class="kbd" style="font-size:9px;">P:</span>
              <span class="kbd" style="font-size:9px;">L:</span>
              <span class="kbd" style="font-size:9px;">S:</span>
            </p>
          </div>
        </template>
      </div>
    </div>
  </div>

  <!-- ── RIGHT: Notif + divider + Profile ── -->
  <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">

    <!-- Notifications -->
    <div style="position:relative;" @click.outside="notifOpen=false">
      <!-- FIX: x-show pakai notifCount dari Alpine data — reaktif, bukan hardcode Django -->
      <button @click="notifOpen=!notifOpen"
              class="nav-btn"
              :aria-expanded="notifOpen.toString()"
              aria-label="Notifikasi">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 00-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <span x-show="notifCount > 0" class="notif-dot"></span>
      </button>

      <div x-show="notifOpen"
           x-transition:enter="transition ease-out duration-150"
           x-transition:enter-start="opacity-0 scale-95 translate-y-1"
           x-transition:enter-end="opacity-100 scale-100 translate-y-0"
           x-transition:leave="transition ease-in duration-100"
           x-transition:leave-end="opacity-0 scale-95 translate-y-1"
           class="nav-dropdown notif-dropdown">

        <!-- Header with filter tabs -->
        <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px 0;border-bottom:1px solid var(--divider);">
          <span style="font-size:13px;font-weight:700;color:var(--text-primary);">Notifikasi</span>
          <div style="display:flex;gap:2px;">
            <template x-for="tab in notifTabs" :key="tab.key">
              <button @click="activeNotifTab = tab.key"
                      style="padding:6px 10px;border:none;background:transparent;font-size:11px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.15s;font-family:inherit;"
                      :style="activeNotifTab === tab.key ? 'color:var(--jade);border-bottom-color:var(--jade);' : 'color:var(--text-muted);'"
                      x-text="tab.label">
              </button>
            </template>
          </div>
        </div>

        <!-- Notif list -->
        <div class="scroll-thin" style="max-height:280px;overflow-y:auto;">
          <template x-for="notif in filteredNotifs" :key="notif.id">
            <a :href="notif.url || '#'"
               class="notif-item"
               :class="notif.read ? '' : 'unread'"
               style="color:inherit;">
              <div style="width:32px;height:32px;border-radius:9px;background:var(--surface);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg style="width:15px;height:15px;" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="notifIcon(notif.type)"/>
                </svg>
              </div>
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
                  <span class="notif-type-badge" :class="notif.type" x-text="notifTypeLabel(notif.type)"></span>
                  <span style="font-size:10px;color:var(--text-faint);" x-text="notif.time"></span>
                </div>
                <p style="font-size:12.5px;color:var(--text-primary);margin:0;line-height:1.4;" x-text="notif.message"></p>
              </div>
              <span x-show="!notif.read" class="notif-unread-dot"></span>
            </a>
          </template>

          <template x-if="filteredNotifs.length === 0">
            <div style="padding:32px 14px;text-align:center;">
              <svg style="width:26px;height:26px;color:var(--text-faint);margin:0 auto 8px;" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 00-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <p style="font-size:12px;color:var(--text-muted);margin:0;">Tidak ada notifikasi</p>
            </div>
          </template>
        </div>

        <div style="border-top:1px solid var(--divider);padding:10px 14px;">
          <a href="{% url 'notifications' %}" style="font-size:12px;font-weight:600;color:var(--jade);text-decoration:none;">Lihat semua →</a>
        </div>
      </div>
    </div>

    <div class="nav-divider"></div>

    <!-- Profile -->
    <div style="position:relative;" @click.outside="profileOpen=false">
      <button @click="profileOpen=!profileOpen"
              class="profile-trigger"
              :aria-expanded="profileOpen.toString()">
        <img class="avatar-img"
             style="width:28px;height:28px;"
             src="{{ user.profile.avatar.url|default:'/static/img/default-avatar.png' }}"
             alt="{{ user.get_full_name|default:user.username }}"
             loading="lazy"
             onerror="this.src='/static/img/default-avatar.png'">
        <div class="hidden md:block" style="text-align:left;line-height:1;">
          <p style="font-size:13px;font-weight:600;color:var(--text-primary);margin:0;white-space:nowrap;">{{ user.get_full_name|default:user.username }}</p>
          <p style="font-size:10px;color:var(--text-muted);margin:2px 0 0;white-space:nowrap;">{{ user.profile.role|default:"User" }}</p>
        </div>
        <svg class="hidden md:block"
             style="width:12px;height:12px;color:var(--text-faint);transition:transform 0.2s;"
             :style="profileOpen ? 'transform:rotate(180deg)' : ''"
             fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      <!-- Profile dropdown -->
      <div x-show="profileOpen"
           x-transition:enter="transition ease-out duration-150"
           x-transition:enter-start="opacity-0 scale-95 translate-y-1"
           x-transition:enter-end="opacity-100 scale-100 translate-y-0"
           x-transition:leave="transition ease-in duration-100"
           x-transition:leave-end="opacity-0"
           class="nav-dropdown profile-dropdown">

        <!-- Context header -->
        <div style="padding:12px 14px;border-bottom:1px solid var(--divider);background:var(--surface);">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
            <span class="store-dot" :class="activeStore.status || 'online'"></span>
            <span style="font-size:12px;font-weight:600;color:var(--text-primary);" x-text="activeStore.name"></span>
          </div>
          <p style="font-size:11px;color:var(--text-muted);margin:0;">{{ user.email }}</p>
        </div>

        <div style="padding:4px 0;">
          <a href="{% url 'profile' %}" class="profile-menu-item">
            <svg fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            Profil Saya
          </a>
          <a href="{% url 'settings' %}" class="profile-menu-item">
            <svg fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Pengaturan
          </a>
          <button @click="toggleTheme()" class="profile-menu-item" style="width:100%;">
            <svg x-show="theme==='light'" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
            <svg x-show="theme==='dark'" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" style="color:#fbbf24;">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>
            </svg>
            <span x-text="theme==='dark' ? 'Mode Terang' : 'Mode Gelap'"></span>
          </button>
        </div>

        <div style="border-top:1px solid var(--divider);padding:4px 0;">
          <a href="{% url 'logout' %}" class="profile-menu-item danger">
            <svg fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Keluar
          </a>
        </div>
      </div>
    </div>

  </div>
</header>

<script>
function navApp() {
  return {
    theme: localStorage.getItem('theme') || 'light',
    storeOpen:   false,
    notifOpen:   false,
    profileOpen: false,
    searchFocused: false,
    showDropdown:  false,
    query:   '',
    results: [],
    kbIdx:   -1,
    loading: false,
    tokenW:  0,
    recent: JSON.parse(localStorage.getItem('nav_recent') || '[]').slice(0, 5),

    /* Rotating placeholder */
    placeholderHints: [
      'Cari produk, lokasi, stok…',
      'Ketik P: untuk cari produk…',
      'Ketik L: untuk cari lokasi…',
      'Ketik S: untuk cek stok…',
    ],
    hintIdx: 0,
    _hintTimer: null,

    /* Store data — dari Django context */
    activeStore: {{ active_store|default:'{"id":1,"name":"Toko Utama","city":"Jakarta","status":"online","emoji":"🏪"}' }},
    stores: {{ stores_json|default:'[{"id":1,"name":"Toko Utama","city":"Jakarta","status":"live","statusLabel":"Live","emoji":"🏪"},{"id":2,"name":"Cabang Bandung","city":"Bandung","status":"busy","statusLabel":"Sibuk","emoji":"🏬"},{"id":3,"name":"Cabang Surabaya","city":"Surabaya","status":"offline","statusLabel":"Offline","emoji":"🏪"}]' }},

    /* Command hints */
    cmdHints: [
      { prefix: 'P:', type: 'product',  label: 'Produk',  desc: 'Cari nama produk atau SKU' },
      { prefix: 'L:', type: 'location', label: 'Lokasi',  desc: 'Filter cabang atau kota' },
      { prefix: 'S:', type: 'stock',    label: 'Stok',    desc: 'Lihat produk stok rendah' },
    ],

    /* Notification tabs */
    notifTabs: [
      { key: 'all',    label: 'Semua'   },
      { key: 'stock',  label: 'Stok'    },
      { key: 'alert',  label: 'Alert'   },
      { key: 'report', label: 'Laporan' },
    ],
    activeNotifTab: 'all',

    /* FIX: notifCount dipindah ke sini — x-show di template pakai `notifCount` bukan hardcode Django */
    notifCount: {{ notifications_count|default:0 }},

    /* Notifications — ganti dengan endpoint API di production */
    notifications: [
      { id:1, type:'stock',  message:'Kopi Mandheling stok di bawah batas minimum (12 Kg)', time:'5 mnt',  read:false, url:'/products/2/' },
      { id:2, type:'alert',  message:'Gayo Natural Process habis di Toko Utama',             time:'23 mnt', read:false, url:'/products/3/' },
      { id:3, type:'report', message:'Laporan penjualan harian sudah siap',                  time:'1 jam',  read:true,  url:'/reports/sales/' },
      { id:4, type:'system', message:'Sinkronisasi data selesai — semua cabang terhubung',   time:'2 jam',  read:true,  url:'#' },
      { id:5, type:'stock',  message:'Kopi Luwak Toraja mendekati batas kritis (5 Kg)',      time:'3 jam',  read:true,  url:'/products/5/' },
    ],

    get filteredNotifs() {
      if (this.activeNotifTab === 'all') return this.notifications;
      return this.notifications.filter(n => n.type === this.activeNotifTab);
    },

    notifTypeLabel(type) {
      return { stock:'Stok', system:'Sistem', report:'Laporan', alert:'Alert' }[type] || type;
    },

    notifIcon(type) {
      const icons = {
        stock:  'M20 7l-8-4-8 4m16 0v10l-8 4m0-14L4 17m8-10v14',
        alert:  'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
        report: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        system: 'M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18',
      };
      return icons[type] || icons.system;
    },

    /* ── Computed ── */
    get parsedCmd() {
      const q = this.query.trim();
      const map = {
        'P:': { type:'product',  label:'Produk',  url:'/api/search/products/' },
        'L:': { type:'location', label:'Lokasi',  url:'/api/search/locations/' },
        'S:': { type:'stock',    label:'Stok',    url:'/api/search/stock/' },
      };
      for (const [pfx, meta] of Object.entries(map)) {
        if (q.toUpperCase().startsWith(pfx)) return { prefix:true, ...meta, term:q.slice(2).trim() };
      }
      return { prefix:false, type:null, label:null, term:q, url:'/api/search/' };
    },

    get resultsLabel() {
      return { product:'Produk', location:'Lokasi', stock:'Stok Rendah' }[this.parsedCmd.type] || 'Hasil';
    },

    /* ── Init ── */
    init() {
      if (this.theme === 'dark') document.documentElement.classList.add('dark');

      /* Rotating placeholder */
      this._hintTimer = setInterval(() => {
        this.hintIdx = (this.hintIdx + 1) % this.placeholderHints.length;
      }, 3000);

      /* Update token chip width setiap kali parsedCmd berubah */
      this.$watch('parsedCmd', () => {
        this.$nextTick(() => {
          const el = this.$el.querySelector('.cmd-token');
          this.tokenW = el ? el.offsetWidth : 0;
        });
      });

      /* Sync activeStore jika sidebar dispatch event ganti store */
      window.addEventListener('store-changed', (e) => {
        if (e.detail?.store) this.activeStore = e.detail.store;
      });

      this.$nextTick(() => {
        const el = this.$el.querySelector('.cmd-token');
        this.tokenW = el ? el.offsetWidth : 0;
      });
    },

    /* ── Search ── */
    focusSearch() {
      const el = document.getElementById('nav-search');
      if (el) { el.focus(); el.select(); }
    },

    onFocus() {
      this.searchFocused = true;
      this.showDropdown  = true;
    },

    closeSearch() {
      this.searchFocused = false;
      this.showDropdown  = false;
      this.kbIdx = -1;
    },

    clearSearch() {
      this.query   = '';
      this.results = [];
      this.kbIdx   = -1;
      this.tokenW  = 0;
      this.$nextTick(() => document.getElementById('nav-search')?.focus());
    },

    _timer: null,
    onInput() {
      this.showDropdown = true;
      this.kbIdx = -1;
      clearTimeout(this._timer);
      const term = this.parsedCmd.term;
      if (!term) { this.results = []; this.loading = false; return; }
      this.loading = true;
      this._timer = setTimeout(() => this._search(), 250);
    },

    async _search() {
      const { term, type } = this.parsedCmd;
      if (!term) { this.loading = false; return; }
      await new Promise(r => setTimeout(r, 180));

      const products = [
        { id:1, name:'Kopi Gayo Arabica',   subtitle:'SKU: KGA-001 · Stok: 240 Kg', badge:'Tersedia', badgeType:'success', type:'product', url:'/products/1/' },
        { id:2, name:'Kopi Mandheling',      subtitle:'SKU: KMN-004 · Stok: 12 Kg',  badge:'Terbatas', badgeType:'warning', type:'product', url:'/products/2/' },
        { id:3, name:'Gayo Natural Process', subtitle:'SKU: GNP-007 · Stok: 0',      badge:'Habis',    badgeType:'danger',  type:'product', url:'/products/3/' },
        { id:4, name:'Kopi Toraja Kalosi',   subtitle:'SKU: KTR-002 · Stok: 88 Kg',  badge:'Tersedia', badgeType:'success', type:'product', url:'/products/4/' },
      ];
      const locations = [
        { id:10, name:'Jakarta Pusat', subtitle:'12 cabang aktif', badge:'12 Cabang', type:'location', url:'/locations/jkt/' },
        { id:11, name:'Bandung',       subtitle:'4 cabang aktif',  badge:'4 Cabang',  type:'location', url:'/locations/bdg/' },
      ];
      const stock = [
        { id:20, name:'Kopi Mandheling',      subtitle:'Stok: 12 Kg — di bawah threshold', badge:'< 20 Kg', badgeType:'warning', type:'stock', url:'/products/2/' },
        { id:21, name:'Gayo Natural Process', subtitle:'Stok: 0 — habis',                  badge:'Habis',   badgeType:'danger',  type:'stock', url:'/products/3/' },
      ];

      const pool = type === 'location' ? locations : type === 'stock' ? stock : products;
      this.results = pool.filter(p =>
        p.name.toLowerCase().includes(term.toLowerCase()) ||
        (p.subtitle || '').toLowerCase().includes(term.toLowerCase())
      );
      this.loading = false;
    },

    kbDown() { if (this.kbIdx < this.results.length - 1) this.kbIdx++; },
    kbUp()   { if (this.kbIdx > 0) this.kbIdx--; },

    onEnter() {
      if (this.kbIdx >= 0 && this.results[this.kbIdx]) {
        this.selectResult(this.results[this.kbIdx]);
      } else {
        this._saveRecent(this.query);
        window.location.href = `/search/?q=${encodeURIComponent(this.query)}`;
      }
    },

    selectResult(item) {
      this._saveRecent(this.query);
      this.closeSearch();
      if (item.url) window.location.href = item.url;
    },

    _saveRecent(q) {
      if (!q.trim()) return;
      const list = [q, ...this.recent.filter(r => r !== q)].slice(0, 5);
      this.recent = list;
      localStorage.setItem('nav_recent', JSON.stringify(list));
    },

    /* ── Store ── */
    switchStore(store) {
      this.activeStore = store;
      this.storeOpen   = false;
      /* Broadcast ke komponen lain (mis. sidebar jika perlu tahu store aktif) */
      window.dispatchEvent(new CustomEvent('store-changed', { detail: { store } }));
      fetch('/api/switch-store/', {
        method: 'POST',
        headers: { 'Content-Type':'application/json', 'X-CSRFToken':this._csrf() },
        body: JSON.stringify({ store_id: store.id }),
      }).then(r => r.ok && window.location.reload()).catch(console.error);
    },

    /* ── Theme ── */
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', this.theme);
      document.documentElement.classList.toggle('dark', this.theme === 'dark');
      this.profileOpen = false;
    },

    /* ── Util ── */
    _csrf() {
      return document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')?.[1] ?? '';
    },
  };
}
</script>

base.html
<!-- templates/base/base.html -->
{% load tailwind_tags %}
{% load static %}
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Dashboard{% endblock %}</title>

    {% tailwind_css %}

    {% block extra_head %}{% endblock %}
    {% block extra_css %}{% endblock %}

    <!-- Font Awesome -->
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw=="
          crossorigin="anonymous"
          referrerpolicy="no-referrer">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    {% block chart_scripts %}{% endblock %}

    <style>
        :root {
            --sidebar-collapsed-width: 72px;
            --sidebar-expanded-width: 260px;
            --navbar-height: 64px;
        }

        /* ── Skip link ── */
        .skip-link {
            position: absolute; left: -9999px; top: auto;
            width: 1px; height: 1px; overflow: hidden;
        }
        .skip-link:focus {
            position: static; left: auto; top: auto;
            width: auto; height: auto; overflow: visible;
            padding: 0.5rem; background: #fff; color: #111;
            border-radius: 0.375rem;
            box-shadow: 0 0 0 3px rgba(16,185,129,0.25);
        }

        /* ── Prevent scroll on mobile sidebar open ── */
        @media (max-width: 767px) {
            body.sidebar-open { overflow: hidden; }
        }

        /* ──────────────────────────────────────────────────────────────
         * ── Navbar header-shift ──
         *
         * Sidebar Emerald Odyssey:
         *   collapsed : w-[64px]   = 64px
         *   expanded  : w-[240px]  = 240px
         *
         * Navbar sticky menggunakan `header-shift` agar tidak tertimpa
         * sidebar di desktop. Nilai diupdate sesuai dimensi sidebar baru.
         *
         * Di mobile (< 768px) sidebar adalah overlay fixed — navbar
         * tidak perlu digeser sama sekali.
         * ────────────────────────────────────────────────────────────── */
        @media (min-width: 768px) {
            .header-shift { margin-left: 0; }
        }
        @media (max-width: 767px) {
            .header-shift { margin-left: 0; }
        }

        /*
         * ── Main content margin ──────────────────────────────────────
         * Sama dengan header-shift agar konten tidak tertimpa sidebar.
         * Seamless integration dengan navbar + sidebar.
         * ────────────────────────────────────────────────────────────── */
        @media (min-width: 768px) {
            .content-shift {
                margin-left  : var(--sidebar-collapsed-width);
                transition   : margin-left 0.3s ease;
            }
            body.sidebar-open .content-shift {
                margin-left  : var(--sidebar-expanded-width);
            }
        }
        @media (max-width: 767px) {
            .content-shift { margin-left: 0; }
        }

        .app-shell {
            position: relative;
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, rgba(0, 168, 107, 0.05), transparent 28%),
                radial-gradient(circle at top right, rgba(239, 191, 4, 0.04), transparent 24%),
                #f8fafc;
            overflow: hidden;
        }

        .app-main-shell {
            min-width: 0;
            min-height: 100vh;
            background: transparent;
            padding-top: var(--navbar-height);
        }

        main.content-surface {
            background: transparent;
            height: calc(100vh - var(--navbar-height));
        }

        /* ── Grid/table sections within content ── */
        .content-grid-section {
            background: rgba(255, 255, 255, 0.88);
            border: 0.5px solid rgba(0, 103, 79, 0.08);
            border-radius: 12px;
            transition: box-shadow 0.2s ease, background 0.2s ease;
        }

        .content-grid-section:hover {
            background: rgba(255, 255, 255, 0.92);
            box-shadow: 0 2px 8px rgba(0, 103, 79, 0.08);
        }

        /* ── Semantic bordered sections ── */
        .perf-strip {
            background: linear-gradient(135deg, #0f172a, #111827) !important;
            border-radius: 20px;
            color: #f8fafc;
        }

        .metric-strip {
            background: #ffffff !important;
            border-radius: 20px;
        }

        .quick-stats-bar {
            background: #ffffff !important;
            border-radius: 18px;
        }

        /* ── Chart container border ── */
        .chart-container {
            background: #ffffff;
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }

        /* ── Side container border ── */
        .side-container {
            background: #ffffff;
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }

        /* ── Screen-reader only ── */
        .sr-only {
            position: absolute; width: 1px; height: 1px;
            padding: 0; margin: -1px; overflow: hidden;
            clip: rect(0,0,0,0); white-space: nowrap; border: 0;
        }

        /*
         * ── Footer shift ────────────────────────────────────────────
         * Footer sticky bottom mengikuti lebar sidebar.
         * ────────────────────────────────────────────────────────────── */
        .fixed-footer { box-shadow: 0 -1px 0 rgba(0,0,0,0.04); }
        .footer-container { transition: margin-left .3s ease; }

        @media (min-width: 768px) {
            .fixed-footer .footer-container {
                margin-left: 64px;   /* Odyssey collapsed */
            }
            body.sidebar-open .fixed-footer .footer-container {
                margin-left: 240px;  /* Odyssey expanded */
            }
        }
        @media (max-width: 767px) {
            .fixed-footer .footer-container { margin-left: 0; }
        }

        /* ── Misc ── */
        .mini-tooltip { position: relative; z-index: 20; transition: opacity .15s ease; }
        .card-heading i { width: 1.25rem; display: inline-block; text-align: center; }

        html { scroll-behavior: smooth; }
        body {
            color: var(--slate-700);
            background: #f8fafc;
            font-family: var(--font);
            overflow: hidden;
        }

        @media (max-width: 767px) {
            :root {
                --navbar-height: 60px;
            }
        }

        .app-shell::before {
            content: '';
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.55), rgba(248,250,252,0)),
                linear-gradient(90deg, rgba(0,103,79,0.015), transparent 25%, transparent 75%, rgba(0,168,107,0.015));
            z-index: 0;
        }
        .content-surface {
            position: relative;
            z-index: 1;
        }
    </style>



<style>
/* ═══════════════════════════════════════════════════════════════════════
   LUMRA GLASS DESIGN TOKENS — Emerald Odyssey v3.0
   ═══════════════════════════════════════════════════════════════════════ */
:root {
  /* ═══════════════════════════════════════════════════════════════════
     EMERALD ODYSSEY PALETTE — v3.0 Enhanced
     ═══════════════════════════════════════════════════════════════════ */
  
  /* ── Core Color Palette ── */
  --em: #00674F;                       /* Primary Emerald — Deep & rich */
  --em-600: #00674F;                   /* Same as primary */
  --em-500: #008B63;                   /* Lighter emerald */
  --em-400: #00A874;                   /* Light emerald */
  
  --jade: #00A86B;                     /* Secondary Jade — Vibrant */
  --jade-600: #008B5C;                 /* Darker jade */
  --jade-500: #00A86B;                 /* Standard jade */
  --jade-400: #00C77D;                 /* Light jade */
  
  --gold: #EFBF04;                     /* Accent Gold — Warm */
  --gold-600: #D4A804;                 /* Dark gold */
  --gold-500: #EFBF04;                 /* Standard gold */
  
  --cream: #FDFBD4;                    /* Neutral Cream — Warm base */
  --navy: #000080;                     /* Contrast Navy — Deep */
  
  /* ── Extended Semantic Colors ── */
  /* Emerald Variants */
  --em-02: rgba(0, 103, 79, 0.02);     /* Subtle bg */
  --em-05: rgba(0, 103, 79, 0.05);     /* Soft hover */
  --em-08: rgba(0, 103, 79, 0.08);     /* Light bg */
  --em-12: rgba(0, 103, 79, 0.12);     /* Medium bg */
  --em-15: rgba(0, 103, 79, 0.15);     /* Darker bg */
  --em-20: rgba(0, 103, 79, 0.20);     /* Focus ring bg */
  --em-25: rgba(0, 103, 79, 0.25);     /* Border */
  --em-30: rgba(0, 103, 79, 0.30);     /* Strong border */
  
  /* Jade Variants */
  --jade-02: rgba(0, 168, 107, 0.02);  /* Subtle bg */
  --jade-05: rgba(0, 168, 107, 0.05);  /* Extra-soft hover */
  --jade-08: rgba(0, 168, 107, 0.08);  /* Light bg */
  --jade-12: rgba(0, 168, 107, 0.12);  /* Medium bg */
  --jade-15: rgba(0, 168, 107, 0.15);  /* Darker bg */
  --jade-20: rgba(0, 168, 107, 0.20);  /* Focus bg */
  --jade-25: rgba(0, 168, 107, 0.25);  /* Medium border */
  --jade-35: rgba(0, 168, 107, 0.35);  /* Logo shadow */
  --jade-50: rgba(0, 168, 107, 0.50);  /* Strong element */
  
  /* Gold Variants */
  --gold-02: rgba(239, 191, 4, 0.02);  /* Subtle */
  --gold-08: rgba(239, 191, 4, 0.08);  /* Light */
  --gold-12: rgba(239, 191, 4, 0.12);  /* Medium */
  --gold-15: rgba(239, 191, 4, 0.15);  /* Darker */
  
  /* Navy Variants */
  --navy-02: rgba(0, 0, 128, 0.02);    /* Subtle */
  --navy-05: rgba(0, 0, 128, 0.05);    /* Soft */
  --navy-08: rgba(0, 0, 128, 0.08);    /* Light */
  
  /* ── Semantic Slate Colors ── */
  --slate-50: #f8fafc;                 /* Lightest bg */
  --slate-100: #f1f5f9;                /* Light bg */
  --slate-200: #e2e8f0;                /* Border light */
  --slate-300: #cbd5e1;                /* Section labels */
  --slate-400: #94a3b8;                /* Sub-items text */
  --slate-600: #6b8a7a;                /* Nav items text */
  --slate-700: #475569;                /* Strong text */
  
  /* ── Glass Protocol ── */
  --glass-blur: blur(12px) saturate(180%);
  --glass-bg: rgba(255, 255, 255, 0.92);  /* 92% opaque white */
  --glass-border: 0.5px solid rgba(255, 255, 255, 0.12);
  --glass-border-em: 0.5px solid rgba(0, 103, 79, 0.1);  /* Emerald frosted */
  
  /* ── Shadow System ── */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1), 0 8px 24px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12), 0 16px 48px rgba(0, 0, 0, 0.08);
  --shadow-h: 0 4px 16px rgba(0, 103, 79, 0.16), 0 8px 24px rgba(0, 0, 0, 0.06);
  --shadow-glow: 0 0 8px rgba(0, 168, 107, 0.5);
  
  /* ── Border Radius ── */
  --r2: 2px;
  --r4: 4px;
  --r6: 6px;
  --r8: 8px;
  --r10: 10px;
  --r12: 12px;
  --r14: 14px;
  --r16: 16px;
  --rpill: 100px;
  
  /* ── Typography Scale ── */
  --font: 'Plus Jakarta Sans', -apple-system, sans-serif;
  --font-mono: 'Courier New', monospace;
  --font-size-xs: 10px;
  --font-size-sm: 12px;
  --font-size-base: 13px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 22px;
  
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  
  /* ── Spacing & Grid ── */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  
  /* ── Transitions ── */
  --transition-fast: 0.12s;
  --transition-base: 0.2s;
  --transition-slow: 0.3s;
  --transition-ease: cubic-bezier(0.4, 0, 0.2, 1);
}

.lumra-glass {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : var(--glass-border-em);
  border-radius          : var(--r14);
  box-shadow             : var(--shadow);
  transition             : box-shadow var(--transition-base) var(--transition-ease), 
                          transform var(--transition-base) var(--transition-ease);
  font-family            : var(--font);
}

.lumra-glass:hover { 
  box-shadow: var(--shadow-h);
  transform: translateY(-2px);
}

.lumra-kpi-glass {
  background: rgba(255, 255, 255, 0.88);
  border: 0.5px solid rgba(0, 103, 79, 0.08);
  border-top-color: rgba(255, 255, 255, 0.4);
  border-left-color: rgba(255, 255, 255, 0.3);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--r14);
  box-shadow: var(--shadow);
  transition: box-shadow var(--transition-base) var(--transition-ease), 
             transform var(--transition-base) var(--transition-ease),
             background var(--transition-base) var(--transition-ease);
  position: relative;
  overflow: hidden;
}

.lumra-kpi-glass:hover {
  box-shadow: var(--shadow-h);
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.92);
}

.bg-blob {
  position: fixed; border-radius: 50%; filter: blur(100px);
  opacity: 0.05; pointer-events: none; z-index: 0;
  animation: drift 18s ease-in-out infinite alternate;
}
.bg-blob-1 { width:480px; height:480px; background: var(--em); top:-120px; left:-160px; animation-delay:0s; }
.bg-blob-2 { width:320px; height:320px; background: var(--jade); bottom:-80px; right:-80px; animation-delay:-7s; }
.bg-blob-3 { width:220px; height:220px; background: var(--gold); top:40%; left:55%; animation-delay:-3.5s; opacity: 0.03; }

@keyframes drift {
  from { transform: translate(0,0) scale(1); }
  to   { transform: translate(20px,28px) scale(1.06); }
}
</style>


</head>

<body class="bg-gray-100 font-sans antialiased text-slate-700">

    <!-- Peringatan tanpa JavaScript -->
    <noscript>
        <div style="text-align:center;background:#f8d7da;color:#721c24;padding:15px;border-bottom:1px solid #f5c6cb;">
            <strong>Peringatan:</strong> Aplikasi ini memerlukan JavaScript.
        </div>
    </noscript>

    <!-- Skip link aksesibilitas -->
    <a href="#main-content" class="skip-link">Lompat ke konten</a>

    <!-- Live region untuk screen reader -->
    <div id="sr-announcer" class="sr-only" aria-live="polite" aria-atomic="true"></div>

    <div class="app-shell flex h-screen" id="app-root">

        {% include 'base/sidebar.html' %}

        <div class="app-main-shell flex-1 flex flex-col h-screen overflow-hidden content-shift">

            {% include 'base/navbar.html' %}

            <main id="main-content"
                  role="main"
                  tabindex="-1"
                  class="content-surface w-full flex-1 overflow-x-hidden overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 pb-20 md:pb-16">
                {% block content %}{% endblock %}
            </main>

        </div>

    </div>

    {% block dashboard_scripts %}{% endblock %}
    {% block scripts %}{% endblock %}

    <!-- Alpine.js — defer agar DOM sudah siap -->
    <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <!-- uncloak fallback in case Alpine fails to load; also reveal elements that
         rely on Alpine-init (e.g. .reveal) so page isn’t blank. -->
    <script>
    function showIfNoAlpine() {
        if (!window.Alpine) {
            document.querySelectorAll('[x-cloak]').forEach(el => el.removeAttribute('x-cloak'));
            document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        showIfNoAlpine();
        // always uncloak after 500ms in case Alpine initialization fails later
        setTimeout(showIfNoAlpine, 500);
    });
    window.addEventListener('error', e => {
        if (e.target && e.target.tagName === 'SCRIPT' &&
            e.target.src && e.target.src.includes('alpinejs')) {
            showIfNoAlpine();
        }
    }, true);
    </script>


    <script>
    (function () {
        var sr       = document.getElementById('sr-announcer');
        var removeTrap = null;

        function announce(msg) {
            if (sr) sr.textContent = msg;
        }

        /* Focus trap untuk aksesibilitas sidebar mobile */
        function enableFocusTrap(container) {
            var sel = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
            var focusable = container.querySelectorAll(sel);
            if (!focusable.length) return function () {};
            var first = focusable[0];
            var last  = focusable[focusable.length - 1];

            function handler(e) {
                if (e.key !== 'Tab') return;
                if (e.shiftKey) {
                    if (document.activeElement === first) { e.preventDefault(); last.focus(); }
                } else {
                    if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
                }
            }
            document.addEventListener('keydown', handler);
            return function () { document.removeEventListener('keydown', handler); };
        }

        /* Watch body.sidebar-open untuk kelola focus trap di mobile */
        var body    = document.body;
        var sidebar = document.getElementById('sidebar');

        var bodyObs = new MutationObserver(function () {
            var isOpen  = body.classList.contains('sidebar-open');
            var isMobile = window.innerWidth < 768;

            if (isOpen && isMobile && sidebar) {
                setTimeout(function () {
                    removeTrap = enableFocusTrap(sidebar);
                    announce('Sidebar terbuka');
                }, 150);
            } else {
                if (typeof removeTrap === 'function') { removeTrap(); removeTrap = null; }
                if (!isOpen) announce('Sidebar ditutup');
            }
        });
        bodyObs.observe(body, { attributes: true, attributeFilter: ['class'] });

        /* Hapus focus trap saat resize ke desktop */
        window.addEventListener('resize', function () {
            if (window.innerWidth >= 768 && typeof removeTrap === 'function') {
                removeTrap(); removeTrap = null;
            }
        });

    })();
    </script>

</body>
</html>
