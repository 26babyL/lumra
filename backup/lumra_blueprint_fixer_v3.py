#!/usr/bin/env python3
"""
lumra_blueprint_fixer_v3.py
============================
Lumra ERP — Blueprint Auto-Fixer v3.0
Lanjutan dari fixer v2 — selaras penuh dengan Emerald Odyssey Blueprint v3.

Perubahan dari v2:
  ─ INPUT  : audit_after.html (sama seperti v2)
  ─ OUTPUT : report HTML lengkap dari fixer sendiri (baru)

  FIXES YANG DIPERKUAT:
  D1 : rgba emerald/jade alpha variant sesuai token --color-*-a08/a10/a12/a15
  D2 : glass protocol LENGKAP — shadow 4 lapis + frosted border + blur + tint
  D3 : snap spacing scan SELURUH file (bukan hanya dari violations)
  D4 : + inject tabular-nums pada KPI value elements (D10 digabung)
  D5 : inject shimmer class template yang benar (bukan hanya comment)
  D6 : + fix table header bg + zebra pattern CSS
  D7 : inline style — perluas ke transition, border-radius, font
  C3 : scan SELURUH file untuk function > 30 baris (bukan hanya dari violations)
  C4 : scan SELURUH file untuk nama terlarang (bukan hanya per violation)

  KATEGORI BARU:
  C1 : Anti-God Class — file .py > 300 baris → inject TODO per class
  C6 : N+1 deep scan — detect .all() / .filter() dalam for-loop tanpa prefetch
  D8 : Transition token — replace '150ms ease', '200ms ease' dll → var(--transition-*)
  D9 : Border-radius token — snap 7px→8px, non-token value → var(--radius-*)

  REPORT:
  + HTML report lengkap setelah fix (bukan hanya terminal summary)
  + Severity: CRITICAL / HIGH / MEDIUM per kategori
  + Per-file diff summary

Cara pakai:
  python lumra_blueprint_fixer_v3.py                          # fix semua
  python lumra_blueprint_fixer_v3.py --audit audit_after.html
  python lumra_blueprint_fixer_v3.py --only D1,D2,D9,C1
  python lumra_blueprint_fixer_v3.py --dry-run
  python lumra_blueprint_fixer_v3.py --no-backup
  python lumra_blueprint_fixer_v3.py --report-out report_v3.html
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from html import escape as he


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_AUDIT_HTML  = Path("audit_after.html")
DEFAULT_HTML_ROOT   = Path("lumra_config/templates")
DEFAULT_PY_ROOT     = Path("lumra_config")
DEFAULT_REPORT_OUT  = Path("fixer_report_v3.html")
BACKUP_DIR          = Path(".lumra_fixer_backup")

ALL_CATEGORIES = {
    "D1","D2","D3","D4","D5","D6","D7","D8","D9",
    "C1","C2","C3","C4","C5","C6",
}

SEVERITY = {
    "D1": "HIGH",     "D2": "CRITICAL", "D3": "HIGH",
    "D4": "MEDIUM",   "D5": "HIGH",     "D6": "HIGH",
    "D7": "MEDIUM",   "D8": "MEDIUM",   "D9": "MEDIUM",
    "C1": "HIGH",     "C2": "HIGH",     "C3": "MEDIUM",
    "C4": "MEDIUM",   "C5": "HIGH",     "C6": "CRITICAL",
}

CATEGORY_DESC = {
    "D1": "Palette — rgba/hex hardcode → CSS token",
    "D2": "Glass Protocol — shadow, frosted border, blur, tint",
    "D3": "Grid 8px — spacing snap ke kelipatan 4/8px",
    "D4": "Typography — font-size, font-weight, tabular-nums",
    "D5": "Shimmer — loading state template injection",
    "D6": "Tabel Odyssey — class, header, zebra pattern",
    "D7": "CSS Token — inline style hex/rgba → token",
    "D8": "Transition Token — ms/ease hardcode → var(--transition-*)",
    "D9": "Border-radius Token — px value → var(--radius-*)",
    "C1": "Anti-God Class — file > 300 baris TODO injection",
    "C2": "Anti-Duplicate — DRY TODO injection",
    "C3": "Anti-Long Method — function > 30 baris TODO injection",
    "C4": "Naming — variabel/fungsi terlarang rename",
    "C5": "Architecture — N+1 & fat view TODO injection",
    "C6": "N+1 Deep Scan — .all()/.filter() dalam loop",
}


# ══════════════════════════════════════════════════════════════════
# D1 + D7: EXTENDED HEX & RGBA TOKEN MAP
# ══════════════════════════════════════════════════════════════════

HEX_TOKEN_MAP = {
    # ── Emerald Odyssey Primary ───────────────────────────────────
    "#00674f": "var(--color-primary)",
    "#00a86b": "var(--color-secondary)",
    "#efbf04": "var(--color-accent)",
    "#fdfbd4": "var(--color-neutral)",
    "#000080": "var(--color-contrast)",
    # ── Emerald variants ─────────────────────────────────────────
    "#047857": "var(--color-primary-dark)",
    "#059669": "var(--color-success)",
    "#34d399": "var(--color-success-light)",
    "#00c97e": "var(--color-secondary)",
    # ── Dark emerald (about/landing pages) ───────────────────────
    "#0a1a14": "var(--color-surface-dark)",
    "#080f0b": "var(--color-surface-dark)",
    "#060e09": "var(--color-surface-dark)",
    "#0a0f0a": "var(--color-surface-dark)",
    "#0f1a0f": "var(--color-surface-dark)",
    "#08120d": "var(--color-surface-dark)",
    "#060814": "var(--color-bg-deep)",
    "#0a1409": "var(--color-surface-dark)",
    "#1a2e24": "var(--color-primary-dark)",
    "#4a5a50": "var(--color-text-muted)",
    "#607060": "var(--color-text-muted)",
    "#7a8a7a": "var(--color-text-muted)",
    # ── Light surfaces ────────────────────────────────────────────
    "#f0faf5": "var(--color-surface-emerald)",
    "#f8faf8": "var(--color-surface-light)",
    "#f0f4ff": "var(--color-surface-blue)",
    "#f1f5f9": "var(--color-surface-faint)",
    "#f5f5f0": "var(--color-surface-faint)",
    "#f7f7f4": "var(--color-surface-faint)",
    "#e8ede6": "var(--color-border-light)",
    "#f0f0ec": "var(--color-surface-faint)",
    "#eff6ff": "var(--color-bg-info)",
    "#bfdbfe": "var(--color-info-light)",
    "#c9e8f0": "var(--color-info-faint)",
    # ── Blues ─────────────────────────────────────────────────────
    "#0284c7": "var(--color-info)",
    "#0ea5e9": "var(--color-info)",
    "#3b82f6": "var(--color-info)",
    "#1877f2": "var(--color-info)",
    "#4f46e5": "var(--color-indigo)",
    "#6366f1": "var(--color-indigo)",
    "#a5b4fc": "var(--color-indigo-light)",
    "#4f3cc9": "var(--color-indigo)",
    "#003087": "var(--color-navy)",
    "#0f172a": "var(--color-bg-deep)",
    "#1e293b": "var(--color-text-primary)",
    # ── Purples / Teals ──────────────────────────────────────────
    "#7c3aed": "var(--color-purple)",
    "#8b5cf6": "var(--color-purple)",
    "#00aed6": "var(--color-teal)",
    "#14b8a6": "var(--color-teal)",
    # ── Reds / Danger ─────────────────────────────────────────────
    "#a32d2d": "var(--color-danger)",
    "#dc2626": "var(--color-danger)",
    "#ef4444": "var(--color-danger)",
    "#e11d48": "var(--color-danger)",
    "#f43f5e": "var(--color-danger)",
    "#be185d": "var(--color-pink)",
    "#ec4899": "var(--color-pink)",
    "#e1306c": "var(--color-pink)",
    # ── Oranges / Warnings ───────────────────────────────────────
    "#f59e0b": "var(--color-warning)",
    "#d97706": "var(--color-warning)",
    "#f97316": "var(--color-orange)",
    "#92400e": "var(--color-warning-dark)",
    "#7a6000": "var(--color-warning-dark)",
    "#8b6800": "var(--color-warning-dark)",
    "#3a2e00": "var(--color-warning-dark)",
    "#635200": "var(--color-warning-dark)",
    # ── Greens / Others ──────────────────────────────────────────
    "#84cc16": "var(--color-lime)",
    "#25d366": "var(--color-whatsapp)",
    "#475569": "var(--color-text-secondary)",
    "#64748b": "var(--color-text-secondary)",
    "#94a3b8": "var(--color-text-muted)",
    "#8aab97": "var(--color-text-muted)",
    # ── Short hex ────────────────────────────────────────────────
    "#111":    "var(--color-text-primary)",
    "#218":    "var(--color-navy)",
    "#221":    "var(--color-text-primary)",
    "#109":    "var(--color-primary)",
    "#666":    "var(--color-text-secondary)",
    "#aaa":    "var(--color-text-muted)",
    "#bbb":    "var(--color-text-muted)",
    "#ccc":    "var(--color-border)",
    "#ddd":    "var(--color-border)",
    "#eee":    "var(--color-border-light)",
    "#fff":    "var(--color-white)",
    "#000":    "var(--color-text-primary)",
}

# Emerald/jade alpha — sesuai blueprint token --color-primary-a08 dst
RGBA_EMERALD_MAP = [
    # Primary alpha (0,103,79)
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.0[1-7]\s*\)",  "var(--color-primary-a08)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.08\s*\)",       "var(--color-primary-a08)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.09\s*\)",       "var(--color-primary-a10)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.1[0-1]\s*\)",   "var(--color-primary-a10)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.1[2-3]\s*\)",   "var(--color-primary-a12)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0?\.1[4-6]\s*\)",   "var(--color-primary-a15)"),
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*([\d.]+)\s*\)",    "var(--color-primary-alpha)"),
    # Secondary alpha (0,168,107)
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*0?\.1[0-1]\s*\)",  "var(--color-secondary-a12)"),
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*0?\.1[2-4]\s*\)",  "var(--color-secondary-a12)"),
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*0?\.1[5-9]\s*\)",  "var(--color-secondary-a15)"),
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*([\d.]+)\s*\)",   "var(--color-secondary-alpha)"),
    # Accent alpha (239,191,4)
    (r"rgba\(\s*239\s*,\s*191\s*,\s*4\s*,\s*0?\.1[0-9]\s*\)",  "var(--color-accent-a15)"),
    (r"rgba\(\s*239\s*,\s*191\s*,\s*4\s*,\s*([\d.]+)\s*\)",   "var(--color-accent-alpha)"),
    # Contrast alpha (0,0,128)
    (r"rgba\(\s*0\s*,\s*0\s*,\s*128\s*,\s*0?\.0[6-9]\s*\)",    "var(--color-contrast-a08)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*128\s*,\s*0?\.0[1-5]\s*\)",    "var(--color-contrast-a08)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*128\s*,\s*0?\.1[0-9]\s*\)",    "var(--color-contrast-a10)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*128\s*,\s*([\d.]+)\s*\)",     "var(--color-contrast-alpha)"),
]

RGBA_GENERIC_MAP = [
    # White overlays
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.9[5-9]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.8[0-9]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[6-7][0-9]?\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[4-5][0-9]?\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[2-3][0-9]?\s*\)", "var(--color-surface-glass)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[1][0-9]?\s*\)",   "var(--color-surface-glass)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[5-9]\s*\)",      "var(--color-surface-faint)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[1-4]\s*\)",      "var(--color-surface-faint)"),
    # Black overlays
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[5-9][0-9]?\s*\)",      "var(--color-overlay-heavy)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[3-4][0-9]?\s*\)",      "var(--color-overlay-heavy)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[1-2][0-9]?\s*\)",      "var(--color-overlay-md)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[7-9]\s*\)",           "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[4-6]\s*\)",           "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[1-3]\s*\)",           "var(--color-overlay-xs)"),
    # Slate overlays
    (r"rgba\(\s*15\s*,\s*23\s*,\s*42\s*,\s*0\.[5-9][0-9]?\s*\)",   "var(--color-overlay-heavy)"),
    (r"rgba\(\s*15\s*,\s*23\s*,\s*42\s*,\s*0\.[1-4][0-9]?\s*\)",   "var(--color-overlay-md)"),
    (r"rgba\(\s*30\s*,\s*41\s*,\s*59\s*,\s*([\d.]+)\s*\)",          "var(--color-overlay-md)"),
]

RGBA_TOKEN_MAP = RGBA_EMERALD_MAP + RGBA_GENERIC_MAP


# ══════════════════════════════════════════════════════════════════
# D8: TRANSITION TOKEN MAP
# Sesuai blueprint: --transition-fast:150ms, --transition-base:200ms,
#                   --transition-slow:300ms, --transition-modal:250ms
#                   --transition-drawer:300ms cubic-bezier
# ══════════════════════════════════════════════════════════════════

TRANSITION_TOKEN_MAP = [
    # cubic-bezier drawer/modal — harus sebelum ease generic
    (r"300ms\s+cubic-bezier\([\d.,\s]+\)",  "var(--transition-drawer)"),
    (r"250ms\s+cubic-bezier\([\d.,\s]+\)",  "var(--transition-modal)"),
    # Simple ease transitions
    (r"150ms\s+ease(?:-in|-out|-in-out)?",  "var(--transition-fast)"),
    (r"200ms\s+ease(?:-in|-out|-in-out)?",  "var(--transition-base)"),
    (r"300ms\s+ease(?:-in|-out|-in-out)?",  "var(--transition-slow)"),
    (r"250ms\s+ease(?:-in|-out|-in-out)?",  "var(--transition-modal)"),
    # Bare ms values in transition property context
    (r"(transition\s*:\s*[^;]*?)150ms\b",   r"\g<1>var(--transition-fast)"),
    (r"(transition\s*:\s*[^;]*?)200ms\b",   r"\g<1>var(--transition-base)"),
    (r"(transition\s*:\s*[^;]*?)300ms\b",   r"\g<1>var(--transition-slow)"),
]


# ══════════════════════════════════════════════════════════════════
# D9: BORDER-RADIUS TOKEN MAP
# Blueprint: --radius-xs:4px --radius-sm:6px --radius-md:8px
#            --radius-lg:10px --radius-xl:14px --radius-2xl:20px
#            --radius-pill:100px
# ══════════════════════════════════════════════════════════════════

RADIUS_TOKEN_MAP = {
    "4":   "var(--radius-xs)",
    "6":   "var(--radius-sm)",
    "8":   "var(--radius-md)",
    "10":  "var(--radius-lg)",
    "14":  "var(--radius-xl)",
    "20":  "var(--radius-2xl)",
    "100": "var(--radius-pill)",
    # snap non-standard → nearest
    "3":   "var(--radius-xs)",
    "5":   "var(--radius-sm)",
    "7":   "var(--radius-md)",     # 7→8
    "9":   "var(--radius-lg)",     # 9→10
    "12":  "var(--radius-xl)",     # 12→14
    "16":  "var(--radius-2xl)",    # 16→20
    "24":  "var(--radius-2xl)",
    "50":  "var(--radius-pill)",
    "9999":"var(--radius-pill)",
}


# ══════════════════════════════════════════════════════════════════
# D3: SPACING SNAP
# ══════════════════════════════════════════════════════════════════

def snap_to_grid(val: float) -> int:
    iv = int(round(val))
    r  = iv % 4
    return iv if r == 0 else (iv + (4 - r) if r >= 2 else iv - r)

VALID_FONT_SIZES   = {10, 11, 13, 14, 16, 18, 20, 22, 24, 28, 32, 36}
VALID_FONT_WEIGHTS = {400, 500, 600, 700}

def snap_font_size(v: float)   -> int: return min(VALID_FONT_SIZES,   key=lambda s: abs(s - v))
def snap_font_weight(v: int)   -> int: return min(VALID_FONT_WEIGHTS,  key=lambda w: abs(w - v))


# ══════════════════════════════════════════════════════════════════
# C4: NAMING MAP (extended)
# ══════════════════════════════════════════════════════════════════

RENAME_VAR_MAP = {
    "data":   "records",       "obj":    "model_instance",
    "val":    "field_value",   "item":   "record_item",
    "res":    "response_data", "result": "query_result",
    "tmp":    "temp_value",    "temp":   "temp_value",
    "flag":   "is_valid",      "check":  "is_checked",
    "info":   "detail_info",   "stuff":  "payload",
    "value":  "field_value",   "x":      "x_coord",
    "y":      "y_coord",       "q":      "queryset",
    "qs":     "queryset",      "pk":     "primary_key",
    "id":     "record_id",     "n":      "count",
    "l":      "items_list",    "d":      "data_dict",
    "s":      "text_value",    "f":      "file_obj",
    "p":      "page_obj",      "k":      "key_name",
    "v":      "value_item",    "e":      "error",
    "ex":     "exception",     "err":    "error",
    "msg":    "message",       "ctx":    "context",
    "rsp":    "response",      "req":    "request",
    "usr":    "user",          "usr_id": "user_id",
}

BAD_FUNC_NAMES = {
    "process", "handle", "do_stuff", "manage", "perform",
    "execute", "run_it", "go", "do_action", "handle_request",
}


# ══════════════════════════════════════════════════════════════════
# D2: GLASS PROTOCOL — full shadow spec
# ══════════════════════════════════════════════════════════════════

GLASS_SHADOW_NATURAL = (
    "0 1px 3px rgba(0,0,0,.08), "
    "0 4px 12px rgba(0,0,0,.06), "
    "0 8px 24px rgba(0,0,0,.04), "
    "0 16px 48px rgba(0,0,0,.03)"
)

GLASS_SHADOW_HOVER = (
    "0 4px 16px rgba(0,103,79,.16), "
    "0 8px 24px rgba(0,0,0,.06), "
    "0 16px 40px rgba(0,0,0,.04)"
)

# Frosted border spec
GLASS_BORDER_TOP  = "0.5px solid rgba(255,255,255,0.25)"
GLASS_BORDER_LEFT = "0.5px solid rgba(255,255,255,0.20)"
GLASS_BORDER_BASE = "0.5px solid rgba(255,255,255,0.10)"


# ══════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════════

USE_COLOR = True

def _c(code, text): return f"\033[{code}m{text}\033[0m" if USE_COLOR else text
def green(t):   return _c("92", t)
def yellow(t):  return _c("93", t)
def red(t):     return _c("91", t)
def cyan(t):    return _c("96", t)
def dim(t):     return _c("2",  t)
def bold(t):    return _c("1",  t)
def white(t):   return _c("97", t)
def magenta(t): return _c("95", t)
def hr(ch="─", n=70): return cyan(ch * n)


# ══════════════════════════════════════════════════════════════════
# PARSE AUDIT HTML (sama seperti v2)
# ══════════════════════════════════════════════════════════════════

def parse_audit_html(html_path: Path) -> dict[str, list[dict]]:
    content = html_path.read_text(encoding="utf-8")
    rows = re.findall(
        r'<tr>\s*<td><span class="badge"[^>]*>(\w+)</span></td>'
        r'\s*<td><span class="cat-badge">(\w+)</span></td>'
        r'\s*<td class="file-path">([^<]+)</td>'
        r'\s*<td class="line-num">L(\d+)</td>'
        r'\s*<td>([^<]*)</td>'
        r'\s*<td class="fix-hint">([^<]*)</td>',
        content,
    )
    by_file: dict[str, list] = defaultdict(list)
    for sev, cat, fpath, line, msg, hint in rows:
        by_file[fpath.strip()].append({
            "severity": sev.strip(), "category": cat.strip(),
            "file":     fpath.strip(), "line":   int(line),
            "message":  msg.strip(),   "fix_hint": hint.strip(),
        })
    return dict(by_file)


# ══════════════════════════════════════════════════════════════════
# FILE FIXER HELPER
# ══════════════════════════════════════════════════════════════════

class FileFixer:
    def __init__(self, path: Path, dry_run: bool, verbose: bool, backup_root):
        self.path        = path
        self.dry_run     = dry_run
        self.verbose     = verbose
        self.backup_root = backup_root
        self.original    = None
        self.content     = None
        self.changes: list[tuple[str,int,str]] = []  # (label, count, category)

    def load(self) -> bool:
        if not self.path.exists():
            return False
        try:
            self.original = self.path.read_text(encoding="utf-8")
            self.content  = self.original
            return True
        except Exception as e:
            print(f"  {red('✖')} Gagal baca {self.path}: {e}")
            return False

    def save(self) -> int:
        if self.content == self.original:
            return 0
        if not self.dry_run:
            if self.backup_root:
                dest = self.backup_root / self.path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(self.path, dest)
            self.path.write_text(self.content, encoding="utf-8")
        return len(self.changes)

    def replace(self, pattern: str, replacement: str,
                flags=re.IGNORECASE, label="", category="") -> int:
        try:
            found = re.findall(pattern, self.content, flags=flags)
            count = len(found)
            new   = re.sub(pattern, replacement, self.content, flags=flags)
        except re.error:
            return 0
        if new != self.content and count > 0:
            self.content = new
            self.changes.append((label or pattern[:50], count, category))
            if self.verbose:
                print(f"      {dim('→')} {dim((label or pattern)[:70])} ({count}×)")
        return count

    def get_lines(self)              -> list[str]: return self.content.splitlines(keepends=True)
    def set_lines(self, lines)                    : self.content = "".join(lines)
    def get_line(self, lineno: int)  -> str:
        lines = self.get_lines()
        return lines[lineno - 1] if 0 < lineno <= len(lines) else ""

    def replace_line(self, lineno: int, new_line: str) -> bool:
        lines = self.get_lines()
        if 0 < lineno <= len(lines):
            if lines[lineno - 1].rstrip("\n") != new_line.rstrip("\n"):
                lines[lineno - 1] = new_line
                self.set_lines(lines)
                self.changes.append((f"line {lineno}", 1, ""))
                return True
        return False

    def insert_before_line(self, lineno: int, text: str, category="") -> bool:
        lines = self.get_lines()
        if 0 < lineno <= len(lines) + 1:
            lines.insert(lineno - 1, text if text.endswith("\n") else text + "\n")
            self.set_lines(lines)
            self.changes.append((f"insert L{lineno}", 1, category))
            return True
        return False

    def total_fixes(self) -> int:
        return sum(c for _, c, _ in self.changes)


# ══════════════════════════════════════════════════════════════════
# [D1] Palette — rgba/hex → token (DIPERKUAT dari v2)
# ══════════════════════════════════════════════════════════════════

def fix_d1(fixer: FileFixer, violations: list) -> int:
    total = 0
    # 1. Emerald-specific rgba (paling presisi, duluan)
    for pattern, token in RGBA_EMERALD_MAP:
        total += fixer.replace(pattern, token, label=f"D1 emerald rgba→{token}", category="D1")
    # 2. Generic rgba
    for pattern, token in RGBA_GENERIC_MAP:
        total += fixer.replace(pattern, token, label=f"D1 rgba→{token}", category="D1")
    # 3. Hex — dari violations + full map
    for hex_val, token in HEX_TOKEN_MAP.items():
        pattern = rf"(?<!var\()(?<!url\(){re.escape(hex_val)}(?![0-9a-fA-F])"
        total += fixer.replace(pattern, token, flags=re.IGNORECASE,
                               label=f"D1 {hex_val}→{token}", category="D1")
    return total


# ══════════════════════════════════════════════════════════════════
# [D2] Glass Protocol LENGKAP (DIPERKUAT dari v2)
# ══════════════════════════════════════════════════════════════════

def fix_d2(fixer: FileFixer, violations: list) -> int:
    total = 0

    # 1. Tambah .kpi-glass ke card yang belum punya
    for v in violations:
        if "tidak menggunakan class .kpi-glass" in v.get("message", ""):
            line = fixer.get_line(v["line"])
            if "kpi-glass" not in line:
                new = re.sub(
                    r'class="([^"]*(?:kpi|stat-card|card)[^"]*)"',
                    lambda m: f'class="{m.group(1)} kpi-glass"',
                    line, flags=re.IGNORECASE,
                )
                if fixer.replace_line(v["line"], new):
                    total += 1

    # 2. Backdrop blur — snap ke minimum 12px
    total += fixer.replace(
        r"backdrop-filter\s*:\s*blur\(([1-9]|1[01])px\)",
        "backdrop-filter: blur(12px)",
        label="D2 blur snap→12px", category="D2",
    )

    # Shadow upgrade hanya dalam context glass card
    # Cari blok CSS yang mengandung kpi-glass atau card-glass
    def do_shadow_upgrade(block_match):
        block = block_match.group(0)
        upgraded = re.sub(
            r"box-shadow\s*:\s*(?!var\()(?!none)([^;{}\n]+)",
            lambda m: f"box-shadow: {GLASS_SHADOW_NATURAL}"
                      if m.group(0).count(",") <= 1 and "rgba(0,0,0" in m.group(0) and "var(" not in m.group(0)
                      else m.group(0),
            block, flags=re.IGNORECASE,
        )
        return upgraded

    new = re.sub(
        r"\.(?:kpi|card|stat|panel)-glass[^{]*\{[^}]+\}",
        do_shadow_upgrade,
        fixer.content, flags=re.IGNORECASE | re.DOTALL,
    )
    if new != fixer.content:
        fixer.content = new
        fixer.changes.append(("D2 glass shadow→4-layer natural", 1, "D2"))
        total += 1

    # 4. Fix border yang sudah solid tapi belum frosted spec
    total += fixer.replace(
        r"border\s*:\s*1px\s+solid\s+rgba\(255\s*,\s*255\s*,\s*255\s*,\s*0\.[0-9]+\)",
        f"border: {GLASS_BORDER_BASE}",
        label="D2 border→glass spec", category="D2",
    )

    # 5. Inject --glass-bg-emerald tint jika background putih polos pada .kpi-glass
    total += fixer.replace(
        r"(\.kpi-glass\s*\{[^}]*?)background\s*:\s*#(?:fff|ffffff|FFFFFF)\s*;",
        r"\1background: var(--glass-bg-emerald);",
        label="D2 bg solid white→glass tint", category="D2",
    )

    return total


# ══════════════════════════════════════════════════════════════════
# [D3] Grid 8px — scan SELURUH file (DIPERKUAT dari v2)
# ══════════════════════════════════════════════════════════════════

SPACING_PROPS = r"(?:padding|margin|gap|top|left|right|bottom|width|height)"

def fix_d3(fixer: FileFixer, violations: list) -> int:
    total = 0

    # Kumpulkan bad values dari violations (prioritas)
    bad_from_violations: set[float] = set()
    for v in violations:
        m = re.search(r"([\d.]+)px", v.get("message", ""))
        if m:
            bad_from_violations.add(float(m.group(1)))

    # Scan SELURUH file untuk spacing yang bukan kelipatan 4px
    # Skip: nilai dalam calc(), nilai 0, nilai > 200 (kemungkinan width/height)
    all_bad: set[float] = set(bad_from_violations)
    for m in re.finditer(
        rf"(?:{SPACING_PROPS})\s*:\s*(?:[^;]*?\s)?([\d.]+)px",
        fixer.content, re.IGNORECASE
    ):
        # Skip jika dalam calc()
        start = max(0, m.start() - 10)
        ctx = fixer.content[start:m.start()]
        if "calc(" in ctx:
            continue
        try:
            val = float(m.group(1))
            # Skip 0px, skip nilai > 200 (width/height besar), skip kelipatan 4 yang sudah benar
            if val <= 0 or val > 200 or int(val) % 4 == 0:
                continue
            all_bad.add(val)
        except ValueError:
            pass

    # Apply snap
    for val in sorted(all_bad, reverse=True):
        snapped = snap_to_grid(val)
        if snapped == int(val):
            continue
        val_s = str(int(val)) if val == int(val) else str(val)
        pattern = rf"({SPACING_PROPS}\s*:\s*(?:[^;]*?\s)?){re.escape(val_s)}px"
        n = fixer.replace(pattern, rf"\g<1>{snapped}px",
                          label=f"D3 {val_s}px→{snapped}px", category="D3")
        total += n

    return total


# ══════════════════════════════════════════════════════════════════
# [D4] Typography + tabular-nums (DIPERKUAT dari v2 + D10 digabung)
# ══════════════════════════════════════════════════════════════════

def fix_d4(fixer: FileFixer, violations: list) -> int:
    total = 0

    for v in violations:
        msg = v.get("message", "")
        if "font-size" in msg:
            m = re.search(r"font-size:\s*([\d.]+)px", msg)
            if m:
                val = float(m.group(1))
                snapped = snap_font_size(val)
                if snapped != int(val):
                    val_s = str(int(val)) if val == int(val) else str(val)
                    total += fixer.replace(
                        rf"(font-size\s*:\s*){re.escape(val_s)}px",
                        rf"\g<1>{snapped}px",
                        label=f"D4 fs {val_s}→{snapped}px", category="D4",
                    )
        elif "font-weight" in msg:
            m = re.search(r"font-weight:\s*(\d+)", msg)
            if m:
                val = int(m.group(1))
                snapped = snap_font_weight(val)
                if snapped != val:
                    total += fixer.replace(
                        rf"(font-weight\s*:\s*){val}\b",
                        rf"\g<1>{snapped}",
                        label=f"D4 fw {val}→{snapped}", category="D4",
                    )

    # D10 (digabung): Inject tabular-nums pada KPI value elements
    # Detect .kpi-value / .kpi-number yang belum punya tabular-nums
    if "kpi-value" in fixer.content or "kpi-number" in fixer.content:
        if "tabular-nums" not in fixer.content:
            total += fixer.replace(
                r"(\.kpi-(?:value|number)\s*\{)([^}]*?)(})",
                r"\1\2  font-variant-numeric: tabular-nums;\n\3",
                label="D4 inject tabular-nums kpi", category="D4",
            )

    return total


# ══════════════════════════════════════════════════════════════════
# [D5] Shimmer — inject template yang lebih lengkap (DIPERKUAT)
# ══════════════════════════════════════════════════════════════════

D5_SHIMMER_COMMENT = """\
{# ── BLUEPRINT D5: Shimmer / Loading States ──────────────────────────── #}
{# Tambahkan class is-loading ke element saat data belum tersedia.         #}
{# Contoh KPI card:                                                        #}
{#   <div class="kpi-glass {% if not kpi_value %}is-loading{% endif %}"    #}
{#        data-kpi="{{ kpi_id }}">                                          #}
{#   </div>                                                                #}
{# CSS shimmer ada di lumra_design_system.css (.shimmer, .is-loading)      #}
{# ─────────────────────────────────────────────────────────────────────── #}
"""

D5_SHIMMER_JS = """\
{# BLUEPRINT D5 JS — fetch dan remove is-loading setelah data tersedia     #}
{# <script>                                                                 #}
{# document.querySelectorAll('[data-kpi]').forEach(async card => {         #}
{#   const data = await fetch(`/api/kpi/${card.dataset.kpi}/`).then(r=>r.json()); #}
{#   card.querySelector('.kpi-value').textContent = data.value;            #}
{#   card.classList.remove('is-loading');                                   #}
{#   card.classList.add('is-loaded');                                       #}
{# });                                                                      #}
{# </script>                                                                #}
"""

def fix_d5(fixer: FileFixer, violations: list) -> int:
    if not violations:
        return 0
    if "BLUEPRINT D5" in fixer.content:
        return 0
    inject = D5_SHIMMER_COMMENT
    # Tambah JS snippet jika ada kpi-glass atau data-kpi
    if "kpi-glass" in fixer.content or "data-kpi" in fixer.content:
        inject += D5_SHIMMER_JS
    # Inject sebelum {% block content %}, atau {% block %}
    target = re.search(r"(\{%\s*block\s+(?:content|main|body)\s*%\})", fixer.content)
    if target:
        pos = target.start()
        fixer.content = fixer.content[:pos] + inject + fixer.content[pos:]
        fixer.changes.append(("D5 shimmer template inject", 1, "D5"))
        return 1
    # Fallback: inject setelah {% extends %}
    target2 = re.search(r"(\{%\s*extends\s+[^%]+%\})", fixer.content)
    if target2:
        pos = target2.end()
        fixer.content = fixer.content[:pos] + "\n" + inject + fixer.content[pos:]
        fixer.changes.append(("D5 shimmer inject after extends", 1, "D5"))
        return 1
    return 0


# ══════════════════════════════════════════════════════════════════
# [D6] Tabel Odyssey — class + header + zebra CSS (DIPERKUAT)
# ══════════════════════════════════════════════════════════════════

ZEBRA_CSS_BLOCK = """\
/* Blueprint D6: Tabel Odyssey — otomatis diinjeksi */
.tbl-odyssey thead th {
  background: var(--color-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 10px 12px;
}
.tbl-odyssey tbody tr:nth-child(odd) td  { background: rgba(0,103,79,.035); }
.tbl-odyssey tbody tr:nth-child(even) td { background: #fff; }
.tbl-odyssey tbody tr:hover td           { background: rgba(0,103,79,.055); transition: 150ms; }
"""

def fix_d6(fixer: FileFixer, violations: list) -> int:
    total = 0

    # 1. Tambah class tbl-odyssey ke <table> yang belum punya
    total += fixer.replace(
        r"<table(?!\s[^>]*class=)([^>]*)>",
        r'<table class="tbl-odyssey"\1>',
        label="D6 <table>→tbl-odyssey", category="D6",
    )
    def append_class(m):
        existing = m.group(2)
        if "tbl-odyssey" not in existing:
            return f'<table{m.group(1)}class="{existing} tbl-odyssey"{m.group(3)}>'
        return m.group(0)
    new = re.sub(r'<table(\s[^>]*)class="([^"]*)"([^>]*)>', append_class, fixer.content, flags=re.IGNORECASE)
    if new != fixer.content:
        fixer.content = new
        fixer.changes.append(("D6 append tbl-odyssey class", 1, "D6"))
        total += 1

    # 2. Inject zebra CSS jika belum ada tbl-odyssey CSS di file ini
    if "tbl-odyssey" in fixer.content and ".tbl-odyssey tbody" not in fixer.content:
        target = re.search(r"<style[^>]*>", fixer.content)
        if target:
            pos = target.end()
            fixer.content = fixer.content[:pos] + "\n" + ZEBRA_CSS_BLOCK + fixer.content[pos:]
            fixer.changes.append(("D6 inject zebra CSS", 1, "D6"))
            total += 1

    return total


# ══════════════════════════════════════════════════════════════════
# [D7] CSS Token — inline style (sama seperti v2, diperluas)
# ══════════════════════════════════════════════════════════════════

def fix_d7(fixer: FileFixer, violations: list) -> int:
    total = 0
    for hex_val, token in HEX_TOKEN_MAP.items():
        pattern = rf'(style="[^"]*){re.escape(hex_val)}([^"]*")'
        total  += fixer.replace(pattern, rf'\g<1>{token}\2',
                                flags=re.IGNORECASE, label=f"D7 {hex_val}→{token}", category="D7")
    for pattern, token in RGBA_TOKEN_MAP:
        p = rf'(style="[^"]*){pattern}([^"]*")'
        total += fixer.replace(p, rf'\g<1>{token}\2', label=f"D7 rgba→{token}", category="D7")
    return total


# ══════════════════════════════════════════════════════════════════
# [D8] Transition Token — BARU di v3
# ══════════════════════════════════════════════════════════════════

def fix_d8(fixer: FileFixer, violations: list) -> int:
    """Replace hardcoded transition ms/ease values with CSS token variables.
    Line-by-line approach: skip lines that already contain var(--transition-*)
    to prevent double substitution.
    """
    total = 0
    lines = fixer.get_lines()
    changed = False
    for idx, line in enumerate(lines):
        # Skip lines already using transition tokens
        if "var(--transition" in line:
            continue
        new_line = line
        for pattern, token in TRANSITION_TOKEN_MAP:
            try:
                replaced = re.sub(pattern, token, new_line)
                if replaced != new_line:
                    new_line = replaced
            except re.error:
                pass
        if new_line != line:
            lines[idx] = new_line
            changed = True
            total += 1
            fixer.changes.append((f"D8 transition token L{idx+1}", 1, "D8"))
    if changed:
        fixer.set_lines(lines)
    return total


def fix_d9(fixer: FileFixer, violations: list) -> int:
    total = 0
    # Scan seluruh file untuk border-radius: Npx yang bukan dari var()
    for px_val, token in sorted(RADIUS_TOKEN_MAP.items(), key=lambda x: -len(x[0])):
        # Hanya ganti yang bukan sudah pakai var()
        pattern = rf"(border-radius\s*:\s*)(?!var\(){re.escape(px_val)}px\b"
        total  += fixer.replace(pattern, rf"\g<1>{token}",
                               label=f"D9 radius {px_val}px→{token}", category="D9")
    return total


# ══════════════════════════════════════════════════════════════════
# [C1] Anti-God Class — BARU di v3
# File Python > 300 baris → cari class definitions, inject TODO
# ══════════════════════════════════════════════════════════════════

C1_TODO = (
    "# TODO[C1-GOD-CLASS]: Class ini melebihi 300 baris.\n"
    "# Pisahkan tanggung jawab:\n"
    "#   views.py    → hanya orchestrate (< 20 baris per method)\n"
    "#   services.py → bisnis logic\n"
    "#   selectors.py → read-only queries\n"
    "#   forms.py    → validasi input\n"
    "# Lihat BAB 14 — Code Quality Constitution untuk panduan.\n"
)

def fix_c1(fixer: FileFixer, violations: list) -> int:
    """Detect and flag God Classes — classes with too many lines.
    File-level guard removed: we check per-class length instead.
    A class > 100 real lines is a candidate for splitting.
    """
    lines = fixer.get_lines()
    # Skip very small files (< 30 lines) — nothing to split
    if len(lines) < 30:
        return 0

    # Cari class definitions
    injected = 0
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\s*)class\s+(\w+)', line)
        if m and "TODO[C1-GOD-CLASS]" not in (lines[i-1] if i > 0 else ""):
            indent = m.group(1)
            # Hitung panjang class ini
            class_start = i
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() == "":
                    j += 1
                    continue
                # Baris non-blank dengan indent sama atau kurang = class baru atau end
                stripped = next_line.lstrip()
                curr_indent = len(next_line) - len(stripped)
                if curr_indent <= len(indent) and stripped and not stripped.startswith("#"):
                    if re.match(r'class\s+\w+', stripped) or curr_indent == 0:
                        break
                j += 1
            class_len = j - class_start
            if class_len > 100:  # class > ~100 baris dianggap too long
                for todo_line in (indent + l + "\n" for l in C1_TODO.strip().split("\n")):
                    new_lines.append(todo_line)
                fixer.changes.append((f"C1 TODO class L{i+1}", 1, "C1"))
                injected += 1
        new_lines.append(line)
        i += 1

    if injected:
        fixer.set_lines(new_lines)
    return injected


# ══════════════════════════════════════════════════════════════════
# [C2] Anti-Duplicate — inject TODO (sama seperti v2)
# ══════════════════════════════════════════════════════════════════

def fix_c2(fixer: FileFixer, violations: list) -> int:
    injected = 0
    lines  = fixer.get_lines()
    offset = 0
    for v in sorted(violations, key=lambda x: x["line"]):
        lineno = v["line"] + offset
        if 0 < lineno <= len(lines) and "TODO[C2]" not in lines[lineno - 1]:
            indent = " " * (len(lines[lineno - 1]) - len(lines[lineno - 1].lstrip()))
            lines.insert(lineno - 1, indent + "# TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial\n")
            offset += 1
            injected += 1
    fixer.set_lines(lines)
    if injected:
        fixer.changes.append(("C2 TODO DRY comments", injected, "C2"))
    return injected


# ══════════════════════════════════════════════════════════════════
# [C3] Anti-Long Method — scan SELURUH file (DIPERKUAT dari v2)
# ══════════════════════════════════════════════════════════════════

C3_MAX_LINES = 30

def fix_c3(fixer: FileFixer, violations: list) -> int:
    injected  = 0
    lines     = fixer.get_lines()
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Deteksi def function
        m = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
        if m:
            indent_len = len(m.group(1))
            fname      = m.group(2)
            # Hitung panjang function
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                stripped  = next_line.lstrip()
                if stripped == "" or stripped.startswith("#"):
                    j += 1
                    continue
                curr_indent = len(next_line) - len(stripped)
                if curr_indent <= indent_len and stripped:
                    break
                j += 1
            func_len = j - i
            already_tagged = (i > 0 and "TODO[C3]" in lines[i - 1])
            if func_len > C3_MAX_LINES and not already_tagged:
                indent = " " * indent_len
                new_lines.append(
                    f"{indent}# TODO[C3-LONG]: '{fname}' = {func_len} baris "
                    f"(maks {C3_MAX_LINES}). "
                    f"Pecah: {fname}_validate(), {fname}_process(), {fname}_respond()\n"
                )
                fixer.changes.append((f"C3 TODO '{fname}' L{i+1}", 1, "C3"))
                injected += 1
        new_lines.append(line)
        i += 1

    if injected:
        fixer.set_lines(new_lines)
    return injected


# ══════════════════════════════════════════════════════════════════
# [C4] Naming — scan SELURUH file (DIPERKUAT dari v2)
# ══════════════════════════════════════════════════════════════════

def fix_c4(fixer: FileFixer, violations: list) -> int:
    total = 0
    lines = fixer.get_lines()

    # A. Per-violation fix (dari audit HTML)
    for v in violations:
        m = re.search(r"terlarang:\s*'(\w+)'", v.get("message", ""))
        if not m:
            continue
        bad  = m.group(1)
        good = RENAME_VAR_MAP.get(bad, f"{bad}_value")
        is_func = "function" in v.get("message", "").lower()
        lineno  = v["line"] - 1
        if 0 <= lineno < len(lines):
            line = lines[lineno]
            if is_func:
                new = re.sub(rf"\bdef\s+{re.escape(bad)}\b", f"def {good}", line)
            else:
                new = re.sub(
                    rf"(?<!['\"\w]){re.escape(bad)}\b(?=\s*(?:=(?!=)|\s+in\s))",
                    good, line,
                )
            if new != line:
                lines[lineno] = new
                fixer.changes.append((f"C4 {bad}→{good} L{v['line']}", 1, "C4"))
                total += 1

    fixer.set_lines(lines)

    # B. Global scan: variabel nama 1-2 huruf dalam assignment dan loop
    single_char_pattern = re.compile(
        r"(?<!['\"\w\.])([a-z])\s*(?:=(?!=)|\s+in\s)"
    )
    lines = fixer.get_lines()
    for idx, line in enumerate(lines):
        # Skip comments, strings, imports
        stripped = line.lstrip()
        if stripped.startswith(("#", "import", "from", '"', "'")):
            continue
        for m in single_char_pattern.finditer(line):
            bad = m.group(1)
            if bad in RENAME_VAR_MAP and bad not in ("i", "j", "k", "e"):
                good = RENAME_VAR_MAP[bad]
                lines[idx] = lines[idx].replace(
                    m.group(0), m.group(0).replace(bad, good), 1
                )
                fixer.changes.append((f"C4 scan '{bad}'→'{good}' L{idx+1}", 1, "C4"))
                total += 1
                break  # max 1 per baris untuk keamanan

    fixer.set_lines(lines)
    return total


# ══════════════════════════════════════════════════════════════════
# [C5] Architecture — N+1 & fat view (sama seperti v2)
# ══════════════════════════════════════════════════════════════════

def fix_c5(fixer: FileFixer, violations: list) -> int:
    injected = 0
    lines    = fixer.get_lines()
    offset   = 0
    seen     = set()

    for v in sorted(violations, key=lambda x: x["line"]):
        lineno = v["line"] + offset
        key    = (v["file"], v["line"])
        if key in seen or lineno <= 0 or lineno > len(lines):
            continue
        line    = lines[lineno - 1]
        is_n1   = "N+1" in v.get("message", "")
        tag     = "TODO[C5-N1]" if is_n1 else "TODO[C5-FAT]"
        if tag in line:
            continue
        indent  = " " * (len(line) - len(line.lstrip()))
        if is_n1:
            comment = (
                indent + "# TODO[C5-N1]: Pindahkan query ini ke atas loop.\n" +
                indent + "# Gunakan Model.objects.select_related('...').prefetch_related('...')\n"
            )
        else:
            ind_m    = re.search(r"'(\w+)'", v.get("message", ""))
            ind_name = ind_m.group(1) if ind_m else "fungsi_ini"
            comment  = indent + f"# TODO[C5-FAT]: '{ind_name}' → pindahkan ke services/{{module}}_service.py\n"
        lines.insert(lineno - 1, comment)
        offset   += comment.count("\n")
        injected += 1
        seen.add(key)

    fixer.set_lines(lines)
    if injected:
        fixer.changes.append(("C5 TODO comments", injected, "C5"))
    return injected


# ══════════════════════════════════════════════════════════════════
# [C6] N+1 Deep Scan — BARU di v3
# Deteksi .all() atau .filter() di dalam for loop tanpa select_related
# ══════════════════════════════════════════════════════════════════

C6_TODO_N1 = (
    "    # TODO[C6-N1]: Query dalam loop — potensi N+1 problem!\n"
    "    # PERBAIKI: Pindahkan ke atas loop dengan select_related / prefetch_related.\n"
    "    # Contoh: Model.objects.select_related('fk').prefetch_related('m2m')\n"
)

def fix_c6(fixer: FileFixer, violations: list) -> int:
    injected  = 0
    lines     = fixer.get_lines()
    new_lines = []
    in_for    = False
    for_indent = 0
    i = 0

    while i < len(lines):
        line    = lines[i]
        stripped = line.lstrip()
        curr_indent = len(line) - len(stripped)

        # Deteksi for loop
        if re.match(r'for\s+\w+', stripped):
            in_for      = True
            for_indent  = curr_indent

        # Keluar dari for loop
        if in_for and curr_indent <= for_indent and not stripped.startswith("for") and stripped:
            if not stripped.startswith(("#", "else", "elif", "except", "finally")):
                in_for = False

        # Deteksi .objects.all() / .objects.filter() dalam loop
        if in_for and curr_indent > for_indent:
            is_query = re.search(r'\.objects\.(?:all|filter|get|exclude)\s*\(', line)
            if is_query and "TODO[C6" not in line and "TODO[C6" not in (lines[i-1] if i > 0 else ""):
                # Check apakah sudah ada select_related/prefetch_related di atas loop
                context = "".join(lines[max(0, i-10):i])
                if "select_related" not in context and "prefetch_related" not in context:
                    new_lines.append(C6_TODO_N1)
                    fixer.changes.append((f"C6 N+1 query L{i+1}", 1, "C6"))
                    injected += 1

        new_lines.append(line)
        i += 1

    if injected:
        fixer.set_lines(new_lines)
    return injected


# ══════════════════════════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════════════════════════

HTML_FIXERS = {
    "D1": fix_d1, "D2": fix_d2, "D3": fix_d3, "D4": fix_d4,
    "D5": fix_d5, "D6": fix_d6, "D7": fix_d7, "D8": fix_d8, "D9": fix_d9,
}
PY_FIXERS = {
    "C1": fix_c1, "C2": fix_c2, "C3": fix_c3, "C4": fix_c4,
    "C5": fix_c5, "C6": fix_c6,
}

def is_python(p: str) -> bool: return p.endswith(".py")
def is_html(p: str)   -> bool: return not is_python(p)


# ══════════════════════════════════════════════════════════════════
# HTML REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════

def build_html_report(
    run_meta: dict,
    stats: dict,
    file_results: list[dict],
    output_path: Path,
):
    sev_color = {"CRITICAL": "#A32D2D", "HIGH": "#8B6800", "MEDIUM": "#00674F"}
    sev_bg    = {"CRITICAL": "#FDF0F0", "HIGH":  "#FFFBEA",  "MEDIUM": "#EAF4EF"}

    # Per-category rows
    cat_rows = ""
    for cat in sorted(stats.keys()):
        s   = stats[cat]
        sev = SEVERITY.get(cat, "MEDIUM")
        cat_rows += f"""
        <tr>
          <td><span class="cat-badge" style="background:{sev_bg[sev]};color:{sev_color[sev]}">{he(cat)}</span></td>
          <td>{he(CATEGORY_DESC.get(cat,''))}</td>
          <td style="text-align:center"><span class="sev-badge" style="background:{sev_bg[sev]};color:{sev_color[sev]}">{he(sev)}</span></td>
          <td style="text-align:center;font-weight:600;color:#00674F">{s['files']}</td>
          <td style="text-align:center;font-weight:700;color:#00A86B">{s['fixes']}</td>
        </tr>"""

    # Per-file rows
    file_rows = ""
    for fr in file_results:
        if not fr["changes"]:
            continue
        changes_html = "".join(
            f'<li><code>{he(label)}</code> × {count}</li>'
            for label, count, _ in fr["changes"]
        )
        status_col = "#00A86B" if not fr["dry_run"] else "#8B6800"
        status_txt = "FIXED" if not fr["dry_run"] else "DRY-RUN"
        file_rows += f"""
        <tr>
          <td class="file-path">{he(fr['path'])}</td>
          <td style="text-align:center">
            <span class="sev-badge" style="background:{'#EAF4EF' if not fr['dry_run'] else '#FFFBEA'};color:{status_col}">{status_txt}</span>
          </td>
          <td style="text-align:center;font-weight:700;color:#00674F">{fr['total_fixes']}</td>
          <td><ul style="margin:0;padding-left:16px;font-size:11px">{changes_html}</ul></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Lumra Fixer Report v3 — {he(run_meta['timestamp'])}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #EEF3F0; color: #0D2018; font-size: 13px; }}
  .page {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px; }}

  /* Header */
  .header {{ background: #00674F; border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; color: #fff; }}
  .header-top {{ display: flex; align-items: center; gap: 16px; margin-bottom: 8px; }}
  .logo {{ width: 40px; height: 40px; background: rgba(255,255,255,.15); border-radius: 10px;
            display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; }}
  .header h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -.3px; }}
  .header-sub {{ font-size: 12px; color: rgba(255,255,255,.6); margin-top: 2px; }}
  .header-meta {{ display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap; }}
  .meta-item {{ background: rgba(255,255,255,.1); border-radius: 8px; padding: 8px 14px; }}
  .meta-label {{ font-size: 10px; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .06em; }}
  .meta-value {{ font-size: 18px; font-weight: 700; margin-top: 2px; }}
  .meta-value.green {{ color: #00C97E; }}
  .meta-value.gold  {{ color: #EFBF04; }}
  .meta-value.red   {{ color: #FF8080; }}

  /* Cards */
  .card {{ background: rgba(255,255,255,.88); border: 0.5px solid rgba(255,255,255,.25);
           backdrop-filter: blur(12px);
           box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06);
           border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; }}
  .card h2 {{ font-size: 14px; font-weight: 600; color: #0D2018; margin-bottom: 14px;
              padding-bottom: 10px; border-bottom: 0.5px solid rgba(0,103,79,.12); }}

  /* Tables */
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ background: #00674F; color: #fff; font-size: 10px; font-weight: 600;
              letter-spacing: .08em; text-transform: uppercase; padding: 10px 12px; text-align: left; }}
  tbody tr:nth-child(odd)  td {{ background: rgba(0,103,79,.035); }}
  tbody tr:nth-child(even) td {{ background: #fff; }}
  tbody tr:hover td {{ background: rgba(0,103,79,.06); }}
  td {{ padding: 9px 12px; font-size: 12px; border-bottom: 0.5px solid rgba(0,103,79,.07); vertical-align: top; }}
  .file-path {{ font-family: monospace; font-size: 11px; color: #00674F; }}

  /* Badges */
  .cat-badge, .sev-badge {{ font-size: 10px; font-weight: 700; padding: 3px 8px;
                             border-radius: 100px; display: inline-block; }}

  /* Dry run warning */
  .dry-run-banner {{ background: #FFFBEA; border: 1px solid #EFBF04; border-radius: 10px;
                     padding: 12px 16px; margin-bottom: 20px; color: #3A2000; font-size: 13px; }}

  /* Footer */
  .footer {{ text-align: center; font-size: 11px; color: #8AAB97; margin-top: 32px; padding: 16px; }}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-top">
      <div class="logo">L</div>
      <div>
        <h1>Lumra Blueprint Auto-Fixer v3.0</h1>
        <div class="header-sub">Emerald Odyssey — Fix Report · {he(run_meta['timestamp'])}</div>
      </div>
    </div>
    <div class="header-meta">
      <div class="meta-item">
        <div class="meta-label">Total Fixes</div>
        <div class="meta-value green">{run_meta['total_fixes']}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Files Diproses</div>
        <div class="meta-value">{run_meta['total_files']}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Files Dilewati</div>
        <div class="meta-value gold">{run_meta['skipped']}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Kategori Aktif</div>
        <div class="meta-value">{run_meta['categories']}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Mode</div>
        <div class="meta-value {'gold' if run_meta['dry_run'] else 'green'}">{'DRY-RUN' if run_meta['dry_run'] else 'APPLIED'}</div>
      </div>
    </div>
  </div>

  {'<div class="dry-run-banner">⚠ DRY-RUN MODE — Tidak ada file yang diubah. Hilangkan --dry-run untuk apply perubahan.</div>' if run_meta['dry_run'] else ''}

  <div class="card">
    <h2>Ringkasan per Kategori</h2>
    <table>
      <thead><tr><th>Kode</th><th>Deskripsi</th><th style="text-align:center">Severity</th><th style="text-align:center">Files</th><th style="text-align:center">Fixes</th></tr></thead>
      <tbody>{cat_rows}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>Detail per File ({len(file_results)} files diproses)</h2>
    <table>
      <thead><tr><th>File</th><th style="text-align:center">Status</th><th style="text-align:center">Fixes</th><th>Perubahan</th></tr></thead>
      <tbody>{file_rows}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>Langkah Selanjutnya</h2>
    <ul style="padding-left:20px;line-height:2">
      <li>Search <code>TODO[C2]</code> — blok duplikat yang perlu di-extract ke template partial</li>
      <li>Search <code>TODO[C3]</code> — function panjang yang perlu dipecah</li>
      <li>Search <code>TODO[C1]</code> — God Class yang perlu di-split ke services.py</li>
      <li>Search <code>TODO[C5]</code> — fat view yang perlu dipindah ke services</li>
      <li>Search <code>TODO[C6]</code> — N+1 query yang perlu dioptimasi dengan select_related</li>
      <li>Jalankan auditor ulang: <code>python lumra_blueprint_auditor.py --html audit_v4.html</code></li>
      <li>Verifikasi visual di browser bahwa glass protocol, warna, dan spacing sudah benar</li>
    </ul>
  </div>

  <div class="footer">
    Lumra ERP · Emerald Odyssey Blueprint v3 · Auto-Fixer Report · {he(run_meta['timestamp'])}
  </div>
</div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Blueprint Auto-Fixer v3.0 — selaras Emerald Odyssey Blueprint v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--audit",      type=Path, default=DEFAULT_AUDIT_HTML)
    p.add_argument("--html-root",  type=Path, default=DEFAULT_HTML_ROOT)
    p.add_argument("--py-root",    type=Path, default=DEFAULT_PY_ROOT)
    p.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT,
                   help=f"Path output HTML report (default: {DEFAULT_REPORT_OUT})")
    p.add_argument("--only",       type=str,  default=None,
                   help="Kategori spesifik, misal: D1,D2,C1,C6")
    p.add_argument("--scan-all",   action="store_true",
                   help="Jalankan D3/D8/D9/C3/C6 scan seluruh file tanpa perlu audit HTML")
    p.add_argument("--dry-run",    action="store_true",
                   help="Preview perubahan tanpa menulis file")
    p.add_argument("--no-backup",  action="store_true")
    p.add_argument("--verbose",    action="store_true")
    p.add_argument("--no-color",   action="store_true")
    return p.parse_args()


def main():
    global USE_COLOR
    args       = parse_args()
    if args.no_color:
        USE_COLOR = False

    categories = (
        {c.strip().upper() for c in args.only.split(",")}
        if args.only else ALL_CATEGORIES
    )

    # ── Header ──────────────────────────────────────────────────
    print(f"\n{hr('═')}")
    print(f"  {bold('Lumra Blueprint Auto-Fixer')}  {cyan('v3.0')}  {dim('— Emerald Odyssey Blueprint v3')}")
    if args.dry_run:
        print(f"  {yellow('⚠  DRY-RUN — tidak ada file yang diubah')}")
    print(hr('═'))

    # ── Load audit ──────────────────────────────────────────────
    # ── --scan-all mode: scan tanpa audit HTML ──────────────────
    if getattr(args, 'scan_all', False):
        print(f"\n  {cyan('⚡ SCAN-ALL MODE')} — scan seluruh file tanpa audit HTML")
        print(f"  {dim('  Kategori aktif: D3, D8, D9, C3, C6')}\n")
        categories = categories & {"D3", "D8", "D9", "C3", "C6"}
        by_file = {}  # kosong — fixer akan scan sendiri
    elif not args.audit.exists():
        print(f"\n  {red('✖')} File audit tidak ditemukan: {args.audit}")
        print(f"  {dim('  Jalankan auditor dulu, atau gunakan --scan-all untuk scan langsung')}")
        sys.exit(1)
    else:
        print(f"\n  {dim('Membaca')} {bold(str(args.audit))}...", end="", flush=True)
        by_file  = parse_audit_html(args.audit)
        total_v  = sum(len(vs) for vs in by_file.values())
        print(f" {green('✓')}  {white(str(total_v))} violations di {white(str(len(by_file)))} files\n")

    # ── Backup ──────────────────────────────────────────────────
    backup_root = None
    if not args.no_backup and not args.dry_run:
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = BACKUP_DIR / ts
        backup_root.mkdir(parents=True, exist_ok=True)
        print(f"  {dim('Backup → ' + str(backup_root))}\n")

    print(f"  Kategori aktif : {cyan(', '.join(sorted(categories)))}\n")

    # ── Group violations ─────────────────────────────────────────
    html_files: dict[str, dict] = {}
    py_files:   dict[str, dict] = {}

    for fpath, violations in sorted(by_file.items()):
        filtered = [v for v in violations if v["category"] in categories]
        if not filtered:
            continue
        bucket = py_files if is_python(fpath) else html_files
        bucket[fpath] = defaultdict(list)
        for v in filtered:
            bucket[fpath][v["category"]].append(v)

    # ── Run fixers ───────────────────────────────────────────────
    stats:        dict[str, dict] = defaultdict(lambda: {"files": 0, "fixes": 0})
    file_results: list[dict]      = []
    total_files = total_fixes = skipped = 0

    def process_group(file_map: dict, fixer_map: dict, root: Path, label: str):
        nonlocal total_files, total_fixes, skipped
        if not file_map:
            return
        print(f"  {bold(label)}  ({len(file_map)} files)")
        print(f"  {dim('─' * 65)}")

        for rel_path, cat_violations in file_map.items():
            full_path = root / rel_path
            fixer     = FileFixer(full_path, args.dry_run, args.verbose, backup_root)

            if not fixer.load():
                print(f"  {yellow('⚠')} Skip: {dim(rel_path)}")
                skipped += 1
                continue

            file_fixes = 0
            for cat, violations in sorted(cat_violations.items()):
                fn = fixer_map.get(cat)
                if fn:
                    n = fn(fixer, violations)
                    file_fixes += n
                    stats[cat]["fixes"] += n

            saved = fixer.save()
            file_results.append({
                "path":        rel_path,
                "dry_run":     args.dry_run,
                "total_fixes": fixer.total_fixes(),
                "changes":     fixer.changes,
            })

            if saved > 0 or (args.dry_run and file_fixes > 0):
                status   = yellow("[DRY]") if args.dry_run else green("✔")
                cats_str = dim(", ".join(sorted(cat_violations.keys())))
                print(f"  {status} {rel_path:<58} {dim(str(file_fixes)+'fx')} [{cats_str}]")
                total_files += 1
                total_fixes += file_fixes
                for cat in cat_violations:
                    stats[cat]["files"] += 1
            elif args.verbose:
                print(f"  {dim('–')} {dim(rel_path)}  (no change)")

        print()

    process_group(html_files, HTML_FIXERS, args.html_root, "HTML Templates")
    process_group(py_files,   PY_FIXERS,   args.py_root,   "Python Sources")

    # ── Terminal Summary ─────────────────────────────────────────
    print(hr('═'))
    print(f"  {bold('Ringkasan Fix')}")
    print(f"  {dim('─' * 55)}")
    if stats:
        print(f"  {'Cat':<8} {'Sev':<10} {'Files':>6} {'Fixes':>7}")
        print(f"  {dim('─' * 35)}")
        for cat in sorted(stats):
            sev = SEVERITY.get(cat, "MEDIUM")
            sev_col = red if sev == "CRITICAL" else (yellow if sev == "HIGH" else green)
            bar = "▪" * min(stats[cat]["fixes"] // 3 + 1, 22)
            print(
                f"  {cyan(cat):<8} {sev_col(sev):<10} "
                f"{str(stats[cat]['files']):>6} {green(str(stats[cat]['fixes'])):>7}  {dim(bar)}"
            )
    print()
    print(f"  Files diproses : {bold(str(total_files))}")
    print(f"  Files dilewati : {yellow(str(skipped))}")
    print(f"  Total fixes    : {green(bold(str(total_fixes)))}")
    print()

    # TODO reminder
    manual_cats = categories & {"C1","C2","C3","C5","C6"}
    if manual_cats:
        print(f"  {yellow('⚠  Perlu review manual:')} {', '.join(sorted(manual_cats))}")
        for cat in sorted(manual_cats):
            tag = f"TODO[{cat}"
            print(f"  {dim('   grep -rn \"' + tag + '\" --include=\"*.py\"')}")
        print()

    # ── HTML Report ──────────────────────────────────────────────
    run_meta = {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_fixes": total_fixes,
        "total_files": total_files,
        "skipped":     skipped,
        "categories":  len(categories),
        "dry_run":     args.dry_run,
    }
    report_path = build_html_report(run_meta, stats, file_results, args.report_out)
    print(f"  {green('✔')} Report HTML → {bold(str(report_path))}")

    if args.dry_run:
        print(f"\n  {yellow('── DRY-RUN: hilangkan --dry-run untuk apply ──')}")
        if total_fixes > 0:
            sys.exit(2)  # Exit code 2: dry-run ada changes yang belum diapply
    elif total_fixes > 0:
        print(f"\n  {green('✔ Selesai!')} Langkah berikutnya:")
        print(f"  {dim('  1. Buka ' + str(report_path) + ' untuk detail lengkap')}")
        print(f"  {dim('  2. Search TODO[C*] dan selesaikan manual refactor')}")
        print(f"  {dim('  3. python lumra_blueprint_auditor.py --html audit_v4.html')}")

    print(hr('═'))
    print()
    sys.exit(0)  # Exit code 0: sukses


if __name__ == "__main__":
    main()