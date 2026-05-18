#!/usr/bin/env python3
"""
lumra_full_migrator.py
======================
Script migrasi lengkap — lanjutan dari lumra_token_migrator.py.

Menangani dua kategori yang sebelumnya di luar scope:
  [A] Inline style=""  — ganti nilai hardcode dengan var(--token)
  [B] Tailwind classes — konsolidasi gray/zinc ke slate, emerald lama ke baru

Cara pakai:
  python lumra_full_migrator.py --dry-run             # preview semua perubahan
  python lumra_full_migrator.py --apply               # apply semua (A + B)
  python lumra_full_migrator.py --apply --only inline # hanya inline style
  python lumra_full_migrator.py --apply --only tw     # hanya tailwind classes
  python lumra_full_migrator.py --report out.json     # simpan laporan JSON

Opsi:
  --root     PATH   Template root (default: lumra_config/templates)
  --backup   PATH   Direktori backup (default: ./_full_migrator_backup)
  --only     MODE   "inline" | "tw" | "all" (default: all)
  --dry-run         Preview saja, tidak ubah file
  --apply           Apply perubahan
  --report   PATH   Simpan JSON report
  --verbose         Tampilkan setiap penggantian
"""

import re
import json
import shutil
import argparse
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_ROOT   = Path(r"lumra_config/templates")
DEFAULT_BACKUP = Path(r"_full_migrator_backup")

SKIP_DIRS = {
    ".lumra_dup_backup", ".lumra_fix_all_backup", ".lumra_master_backup",
    ".lumra_recolor_backup", ".lumra_rename_backup", ".lumra_reorg_backup",
    ".lumra_sync_backup", ".lumra_theme_backup", "_archive",
    "_emerald_upgrade_backup", "_theme_backup", "_theme_migrate_backup",
    "_token_migration_backup", "_full_migrator_backup",
}

# ══════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════════

C   = "\033[96m"
W   = "\033[97m"
G   = "\033[92m"
Y   = "\033[93m"
R   = "\033[91m"
DIM = "\033[2m"
B   = "\033[1m"
RST = "\033[0m"

def hr(char="─", n=68): return C + char * n + RST


# ══════════════════════════════════════════════════════════════════
# [A] INLINE STYLE MIGRATOR
# ══════════════════════════════════════════════════════════════════
#
# Strategi:
#   - Scan atribut style="..." di semua HTML
#   - Untuk setiap property: value, cek apakah value bisa diganti var(--token)
#   - Ganti value dengan var(--token), biarkan property-nya
#   - Khusus inline style yang hanya berisi satu property sederhana
#     dan sudah ada class padanannya → hapus style, tambah class
#
# ──────────────────────────────────────────────────────────────────

# Peta: hex/rgba hardcode → token dari design system v2
# Urutan: spesifik dulu (rgba panjang), baru hex pendek
INLINE_VALUE_MAP: list[tuple[str, str]] = [

    # ── Emerald lama (pre-v2) → token baru ──────────────────────
    ("#10b981",             "var(--color-emerald-500)"),
    ("#059669",             "var(--color-emerald-600)"),
    ("#047857",             "var(--color-primary)"),
    ("#065f46",             "var(--color-emerald-800)"),
    ("#064e3b",             "var(--color-emerald-900)"),
    ("#022c22",             "var(--color-emerald-950)"),
    ("#6ee7b7",             "var(--color-emerald-300)"),
    ("#a7f3d0",             "var(--color-emerald-200)"),
    ("#d1fae5",             "var(--color-emerald-100)"),
    ("#ecfdf5",             "var(--color-emerald-50)"),

    # ── Emerald baru (v2) → token ────────────────────────────────
    ("#00674F",             "var(--color-primary)"),
    ("#00674f",             "var(--color-primary)"),
    ("#2E8C69",             "var(--color-primary-light)"),
    ("#2e8c69",             "var(--color-primary-light)"),
    ("#E6F2EE",             "var(--color-primary-subtle)"),
    ("#e6f2ee",             "var(--color-primary-subtle)"),
    ("#003D2C",             "var(--color-primary-dark)"),
    ("#003d2c",             "var(--color-primary-dark)"),
    ("#5DA88A",             "var(--color-primary-glow)"),
    ("#5da88a",             "var(--color-primary-glow)"),

    # ── Slate / neutral ──────────────────────────────────────────
    ("#0f172a",             "var(--color-text)"),
    ("#0F172A",             "var(--color-text)"),
    ("#1e293b",             "var(--color-slate-800)"),
    ("#1E293B",             "var(--color-slate-800)"),
    ("#334155",             "var(--color-slate-700)"),
    ("#475569",             "var(--color-text-muted)"),
    ("#64748b",             "var(--color-slate-500)"),
    ("#64748B",             "var(--color-slate-500)"),
    ("#94a3b8",             "var(--color-text-subtle)"),
    ("#94A3B8",             "var(--color-text-subtle)"),
    ("#cbd5e1",             "var(--color-slate-300)"),
    ("#e2e8f0",             "var(--color-slate-200)"),
    ("#f1f5f9",             "var(--color-slate-100)"),
    ("#f8fafc",             "var(--color-slate-50)"),

    # ── Semantic ─────────────────────────────────────────────────
    ("#e11d48",             "var(--color-danger)"),
    ("#E11D48",             "var(--color-danger)"),
    ("#f43f5e",             "var(--color-danger)"),
    ("#F43F5E",             "var(--color-danger)"),
    ("#ef4444",             "var(--color-danger)"),
    ("#d97706",             "var(--color-warning)"),
    ("#D97706",             "var(--color-warning)"),
    ("#f59e0b",             "var(--color-warning)"),
    ("#F59E0B",             "var(--color-warning)"),
    ("#0284c7",             "var(--color-info)"),
    ("#0ea5e9",             "var(--color-info)"),
    ("#0EA5E9",             "var(--color-info)"),
    ("#4f46e5",             "var(--color-accent)"),
    ("#4F46E5",             "var(--color-accent)"),
    ("#6366f1",             "var(--color-accent)"),
    ("#6366F1",             "var(--color-accent)"),

    # ── White / Black ─────────────────────────────────────────────
    ("#ffffff",             "var(--color-fff)"),
    ("#FFFFFF",             "var(--color-fff)"),
    ("#fff",                "var(--color-fff)"),
    ("#FFF",                "var(--color-fff)"),

    # ── Indigo / Violet / Blue / Pink / Green ─────────────────────
    ("#C7D2FE",             "var(--color-indigo-200)"),
    ("#c7d2fe",             "var(--color-indigo-200)"),
    ("#A5B4FC",             "var(--color-indigo-300)"),
    ("#a5b4fc",             "var(--color-indigo-300)"),
    ("#6366F1",             "var(--color-indigo-500)"),
    ("#6366f1",             "var(--color-indigo-500)"),
    ("#4F46E5",             "var(--color-accent)"),
    ("#A78BFA",             "var(--color-violet-400)"),
    ("#a78bfa",             "var(--color-violet-400)"),
    ("#8B5CF6",             "var(--color-violet-500)"),
    ("#8b5cf6",             "var(--color-violet-500)"),
    ("#BFDBFE",             "var(--color-blue-200)"),
    ("#bfdbfe",             "var(--color-blue-200)"),
    ("#3B82F6",             "var(--color-blue-500)"),
    ("#3b82f6",             "var(--color-blue-500)"),
    ("#BE185D",             "var(--color-pink-700)"),
    ("#be185d",             "var(--color-pink-700)"),
    ("#BBF7D0",             "var(--color-green-200)"),
    ("#bbf7d0",             "var(--color-green-200)"),

    # ── Extended — misc colors found in audit ─────────────────────
    ("#CBD5E1",             "var(--color-slate-300)"),
    ("#E2E8F0",             "var(--color-slate-200)"),
    ("#F1F5F9",             "var(--color-slate-100)"),
    ("#ECFDF5",             "var(--color-emerald-50)"),
    ("#ecfdf5",             "var(--color-emerald-50)"),
    ("#D1FAE5",             "var(--color-emerald-100-alt)"),
    ("#d1fae5",             "var(--color-emerald-100-alt)"),
    ("#A7F3D0",             "var(--color-emerald-200-alt)"),
    ("#a7f3d0",             "var(--color-emerald-200-alt)"),
    ("#34D399",             "var(--color-emerald-400-alt)"),
    ("#34d399",             "var(--color-emerald-400-alt)"),
    ("#10B981",             "var(--color-emerald-500)"),
    ("#10b981",             "var(--color-emerald-500)"),
    ("#EF4444",             "var(--color-red-500)"),
    ("#ef4444",             "var(--color-red-500)"),
    ("#92400E",             "var(--color-amber-800)"),
    ("#92400e",             "var(--color-amber-800)"),
    ("#FBBF24",             "var(--color-warning)"),
    ("#fbbf24",             "var(--color-warning)"),
    ("#7C3AED",             "var(--color-violet-600)"),
    ("#7c3aed",             "var(--color-violet-600)"),
    ("#EC4899",             "var(--color-pink-400)"),
    ("#ec4899",             "var(--color-pink-400)"),
    ("#38BDF8",             "var(--color-sky-400)"),
    ("#38bdf8",             "var(--color-sky-400)"),
    ("#EFF6FF",             "var(--color-indigo-50)"),
    ("#eff6ff",             "var(--color-indigo-50)"),
    ("#DBEAFE",             "var(--color-blue-100)"),
    ("#dbeafe",             "var(--color-blue-100)"),
    ("#BBF7D0",             "var(--color-green-200)"),
    ("#F0FDF4",             "var(--color-green-100)"),
    ("#f0fdf4",             "var(--color-green-100)"),
    ("#86EFAC",             "var(--color-green-300)"),
    ("#86efac",             "var(--color-green-300)"),
    ("#16A34A",             "var(--color-green-500)"),
    ("#16a34a",             "var(--color-green-500)"),
    ("#0284C7",             "var(--color-info)"),
    ("#2563EB",             "var(--color-blue-500)"),
    ("#2563eb",             "var(--color-blue-500)"),
    ("#334155",             "var(--color-slate-700)"),
    # 3-char hex edge cases
    ("#111",                "var(--color-text)"),

    # ── rgba — indigo / violet / sky / rose / amber ───────────────
    ("rgba(99,102,241,0.10)",  "var(--color-indigo-a10)"),
    ("rgba(99,102,241,.10)",   "var(--color-indigo-a10)"),
    ("rgba(99,102,241,.1)",    "var(--color-indigo-a10)"),
    ("rgba(99,102,241,0.12)",  "var(--color-indigo-a12)"),
    ("rgba(99,102,241,.12)",   "var(--color-indigo-a12)"),
    ("rgba(139,92,246,0.10)",  "var(--color-violet-a10)"),
    ("rgba(139,92,246,.10)",   "var(--color-violet-a10)"),
    ("rgba(139,92,246,.1)",    "var(--color-violet-a10)"),
    ("rgba(14,165,233,0.10)",  "var(--color-sky-a10)"),
    ("rgba(14,165,233,.10)",   "var(--color-sky-a10)"),
    ("rgba(14,165,233,.1)",    "var(--color-sky-a10)"),
    ("rgba(244,63,94,0.08)",   "var(--color-rose-a08)"),
    ("rgba(244,63,94,.08)",    "var(--color-rose-a08)"),
    ("rgba(245,158,11,0.10)",  "var(--color-amber-a10)"),
    ("rgba(245,158,11,.10)",   "var(--color-amber-a10)"),
    ("rgba(245,158,11,.1)",    "var(--color-amber-a10)"),

    # ── rgba — white missing values ───────────────────────────────
    ("rgba(255,255,255,0.50)",  "var(--color-white-a050)"),
    ("rgba(255,255,255,.50)",   "var(--color-white-a050)"),
    ("rgba(255,255,255,0.5)",   "var(--color-white-a050)"),
    ("rgba(255,255,255,.5)",    "var(--color-white-a050)"),
    ("rgba(255,255,255,0.40)",  "var(--color-white-a040)"),
    ("rgba(255,255,255,.40)",   "var(--color-white-a040)"),
    ("rgba(255,255,255,0.4)",   "var(--color-white-a040)"),
    ("rgba(255,255,255,.4)",    "var(--color-white-a040)"),
    ("rgba(255,255,255,0.30)",  "var(--color-white-a030)"),
    ("rgba(255,255,255,.30)",   "var(--color-white-a030)"),
    ("rgba(255,255,255,0.3)",   "var(--color-white-a030)"),
    ("rgba(255,255,255,.3)",    "var(--color-white-a030)"),
    ("rgba(255,255,255,0.70)",  "var(--glass-bg)"),
    ("rgba(255,255,255,.70)",   "var(--glass-bg)"),
    ("rgba(255,255,255,0.7)",   "var(--glass-bg)"),
    ("rgba(255,255,255,.7)",    "var(--glass-bg)"),

    # ── rgba — slate utilities ─────────────────────────────────────
    ("rgba(248,250,252,0.90)",  "var(--color-surface-strong)"),
    ("rgba(248,250,252,.90)",   "var(--color-surface-strong)"),
    ("rgba(248,250,252,.9)",    "var(--color-surface-strong)"),
    ("rgba(226,232,240,0.90)",  "var(--color-border)"),
    ("rgba(226,232,240,.90)",   "var(--color-border)"),
    ("rgba(226,232,240,.9)",    "var(--color-border)"),
    ("rgba(241,245,249,1)",     "var(--color-slate-100)"),
    ("rgba(241,245,249,1.0)",   "var(--color-slate-100)"),

    # ── rgba — dark overlay missing values ────────────────────────
    ("rgba(15,23,42,0.92)",    "var(--glass-bg-strong)"),
    ("rgba(15,23,42,.92)",     "var(--glass-bg-strong)"),
    ("rgba(15,23,42,0.35)",    "var(--glass-dark-bg)"),
    ("rgba(15,23,42,.35)",     "var(--glass-dark-bg)"),
    ("rgba(4,120,87,0.20)",    "var(--color-primary-a25)"),
    ("rgba(4,120,87,.20)",     "var(--color-primary-a25)"),
    ("rgba(4,120,87,.2)",      "var(--color-primary-a25)"),
    ("rgba(4,120,87,0.12)",    "var(--color-primary-a12)"),
    ("rgba(4,120,87,.12)",     "var(--color-primary-a12)"),
    ("rgba(4,120,87,0.10)",    "var(--color-primary-a10)"),
    ("rgba(4,120,87,.10)",     "var(--color-primary-a10)"),
    ("rgba(4,120,87,.1)",      "var(--color-primary-a10)"),

    # ── rgba — emerald lama (5,150,105) — EXHAUSTIVE ─────────────
    # Semua format: 0.XX, .XX, dengan spasi setelah koma
    ("rgba(5,150,105, 0.08)", "var(--color-primary-a08)"),
    ("rgba(5,150,105, 0.1)",  "var(--color-primary-a10)"),
    ("rgba(5,150,105, 0.10)", "var(--color-primary-a10)"),
    ("rgba(5,150,105,0.00)",  "var(--color-primary-a03)"),
    ("rgba(5,150,105,0.0)",   "var(--color-primary-a03)"),
    ("rgba(5,150,105,0.03)",  "var(--color-primary-a03)"),
    ("rgba(5,150,105,0.05)",  "var(--color-primary-a05)"),
    ("rgba(5,150,105,.05)",   "var(--color-primary-a05)"),
    ("rgba(5,150,105,0.06)",  "var(--color-primary-a06)"),
    ("rgba(5,150,105,.06)",   "var(--color-primary-a06)"),
    ("rgba(5,150,105,0.08)",  "var(--color-primary-a08)"),
    ("rgba(5,150,105,.08)",   "var(--color-primary-a08)"),
    ("rgba(5,150,105,0.10)",  "var(--color-primary-a10)"),
    ("rgba(5,150,105,.10)",   "var(--color-primary-a10)"),
    ("rgba(5,150,105,0.1)",   "var(--color-primary-a10)"),
    ("rgba(5,150,105,.1)",    "var(--color-primary-a10)"),
    ("rgba(5,150,105,0.12)",  "var(--color-primary-a12)"),
    ("rgba(5,150,105,.12)",   "var(--color-primary-a12)"),
    ("rgba(5,150,105,0.15)",  "var(--color-primary-a15)"),
    ("rgba(5,150,105,.15)",   "var(--color-primary-a15)"),
    ("rgba(5,150,105,0.2)",   "var(--color-primary-a20)"),
    ("rgba(5,150,105,.2)",    "var(--color-primary-a20)"),
    ("rgba(5,150,105,0.20)",  "var(--color-primary-a20)"),
    ("rgba(5,150,105,.20)",   "var(--color-primary-a20)"),
    ("rgba(5,150,105,0.25)",  "var(--color-primary-a25)"),
    ("rgba(5,150,105,.25)",   "var(--color-primary-a25)"),
    ("rgba(5,150,105,0.28)",  "var(--color-primary-a28)"),
    ("rgba(5,150,105,.28)",   "var(--color-primary-a28)"),
    ("rgba(5,150,105,0.3)",   "var(--color-primary-a30)"),
    ("rgba(5,150,105,.3)",    "var(--color-primary-a30)"),
    ("rgba(5,150,105,0.30)",  "var(--color-primary-a30)"),
    ("rgba(5,150,105,.30)",   "var(--color-primary-a30)"),
    ("rgba(5,150,105,0.35)",  "var(--color-primary-a35)"),
    ("rgba(5,150,105,.35)",   "var(--color-primary-a35)"),
    ("rgba(5,150,105,0.4)",   "var(--color-primary-a40)"),
    ("rgba(5,150,105,.4)",    "var(--color-primary-a40)"),
    ("rgba(5,150,105,0.40)",  "var(--color-primary-a40)"),
    ("rgba(5,150,105,.40)",   "var(--color-primary-a40)"),
    ("rgba(5,150,105,0.50)",  "var(--color-primary-a50)"),
    ("rgba(5,150,105,.50)",   "var(--color-primary-a50)"),
    ("rgba(5,150,105,0.5)",   "var(--color-primary-a50)"),
    ("rgba(5,150,105,.5)",    "var(--color-primary-a50)"),
    ("rgba(5,150,105,0.55)",  "var(--color-primary-a55)"),
    ("rgba(5,150,105,.55)",   "var(--color-primary-a55)"),
    ("rgba(5,150,105,0.6)",   "var(--color-primary-a60)"),
    ("rgba(5,150,105,.6)",    "var(--color-primary-a60)"),
    ("rgba(5,150,105,0.60)",  "var(--color-primary-a60)"),
    ("rgba(5,150,105,.60)",   "var(--color-primary-a60)"),
    ("rgba(5,150,105,0.65)",  "var(--color-primary-a65)"),
    ("rgba(5,150,105,.65)",   "var(--color-primary-a65)"),
    ("rgba(5,150,105,0.7)",   "var(--color-primary-a70)"),
    ("rgba(5,150,105,.7)",    "var(--color-primary-a70)"),
    ("rgba(5,150,105,0.70)",  "var(--color-primary-a70)"),
    ("rgba(5,150,105,.70)",   "var(--color-primary-a70)"),
    ("rgba(5,150,105,0.8)",   "var(--color-primary-a80)"),
    ("rgba(5,150,105,.8)",    "var(--color-primary-a80)"),
    ("rgba(5,150,105,0.80)",  "var(--color-primary-a80)"),
    ("rgba(5,150,105,.80)",   "var(--color-primary-a80)"),
    ("rgba(5,150,105,0.9)",   "var(--color-primary-a90)"),
    ("rgba(5,150,105,.9)",    "var(--color-primary-a90)"),
    ("rgba(5,150,105,0.90)",  "var(--color-primary-a90)"),
    ("rgba(5,150,105,.90)",   "var(--color-primary-a90)"),

    # ── rgba — emerald semi-lama (4,120,87) — EXHAUSTIVE ─────────
    ("rgba(4,120,87,.06)",   "var(--color-primary-a06)"),
    ("rgba(4,120,87,0.06)",  "var(--color-primary-a06)"),
    ("rgba(4,120,87,.08)",   "var(--color-primary-a08)"),
    ("rgba(4,120,87,0.08)",  "var(--color-primary-a08)"),
    ("rgba(4,120,87,.1)",    "var(--color-primary-a10)"),
    ("rgba(4,120,87,0.1)",   "var(--color-primary-a10)"),
    ("rgba(4,120,87,.10)",   "var(--color-primary-a10)"),
    ("rgba(4,120,87,0.10)",  "var(--color-primary-a10)"),
    ("rgba(4,120,87,.12)",   "var(--color-primary-a12)"),
    ("rgba(4,120,87,0.12)",  "var(--color-primary-a12)"),
    ("rgba(4,120,87,.15)",   "var(--color-primary-a15)"),
    ("rgba(4,120,87,0.15)",  "var(--color-primary-a15)"),
    ("rgba(4,120,87,.2)",    "var(--color-primary-a20)"),
    ("rgba(4,120,87,0.2)",   "var(--color-primary-a20)"),
    ("rgba(4,120,87,.20)",   "var(--color-primary-a20)"),
    ("rgba(4,120,87,0.20)",  "var(--color-primary-a20)"),
    ("rgba(4,120,87,.25)",   "var(--color-primary-a25)"),
    ("rgba(4,120,87,0.25)",  "var(--color-primary-a25)"),
    ("rgba(4,120,87,.28)",   "var(--color-primary-a28)"),
    ("rgba(4,120,87,0.28)",  "var(--color-primary-a28)"),
    ("rgba(4,120,87,.3)",    "var(--color-primary-a30)"),
    ("rgba(4,120,87,0.3)",   "var(--color-primary-a30)"),
    ("rgba(4,120,87,.35)",   "var(--color-primary-a35)"),
    ("rgba(4,120,87,0.35)",  "var(--color-primary-a35)"),
    ("rgba(4,120,87,.4)",    "var(--color-primary-a40)"),
    ("rgba(4,120,87,0.4)",   "var(--color-primary-a40)"),
    ("rgba(4,120,87,.5)",    "var(--color-primary-a50)"),
    ("rgba(4,120,87,0.5)",   "var(--color-primary-a50)"),
    ("rgba(4,120,87,.6)",    "var(--color-primary-a60)"),
    ("rgba(4,120,87,0.6)",   "var(--color-primary-a60)"),
    ("rgba(4,120,87,.8)",    "var(--color-primary-a80)"),
    ("rgba(4,120,87,0.8)",   "var(--color-primary-a80)"),
    ("rgba(4,120,87,.9)",    "var(--color-primary-a90)"),
    ("rgba(4,120,87,0.9)",   "var(--color-primary-a90)"),

    # ── rgba — emerald baru (0,103,79) — EXHAUSTIVE ───────────────
    ("rgba(0,103,79,0.03)",  "var(--color-primary-a03)"),
    ("rgba(0,103,79,0.05)",  "var(--color-primary-a05)"),
    ("rgba(0,103,79,.05)",   "var(--color-primary-a05)"),
    ("rgba(0,103,79,0.06)",  "var(--color-primary-a06)"),
    ("rgba(0,103,79,.06)",   "var(--color-primary-a06)"),
    ("rgba(0,103,79,0.08)",  "var(--color-primary-a08)"),
    ("rgba(0,103,79,.08)",   "var(--color-primary-a08)"),
    ("rgba(0,103,79,0.10)",  "var(--color-primary-a10)"),
    ("rgba(0,103,79,0.1)",   "var(--color-primary-a10)"),
    ("rgba(0,103,79,.1)",    "var(--color-primary-a10)"),
    ("rgba(0,103,79,0.12)",  "var(--color-primary-a12)"),
    ("rgba(0,103,79,.12)",   "var(--color-primary-a12)"),
    ("rgba(0,103,79,0.15)",  "var(--color-primary-a15)"),
    ("rgba(0,103,79,.15)",   "var(--color-primary-a15)"),
    ("rgba(0,103,79,0.20)",  "var(--color-primary-a20)"),
    ("rgba(0,103,79,0.2)",   "var(--color-primary-a20)"),
    ("rgba(0,103,79,.2)",    "var(--color-primary-a20)"),
    ("rgba(0,103,79,0.25)",  "var(--color-primary-a25)"),
    ("rgba(0,103,79,.25)",   "var(--color-primary-a25)"),
    ("rgba(0,103,79,0.30)",  "var(--color-primary-a30)"),
    ("rgba(0,103,79,0.3)",   "var(--color-primary-a30)"),
    ("rgba(0,103,79,.3)",    "var(--color-primary-a30)"),
    ("rgba(0,103,79,0.40)",  "var(--color-primary-a40)"),
    ("rgba(0,103,79,0.4)",   "var(--color-primary-a40)"),
    ("rgba(0,103,79,.4)",    "var(--color-primary-a40)"),
    ("rgba(0,103,79,0.50)",  "var(--color-primary-a50)"),
    ("rgba(0,103,79,0.5)",   "var(--color-primary-a50)"),
    ("rgba(0,103,79,.5)",    "var(--color-primary-a50)"),
    ("rgba(0,103,79,0.60)",  "var(--color-primary-a60)"),
    ("rgba(0,103,79,0.6)",   "var(--color-primary-a60)"),
    ("rgba(0,103,79,.6)",    "var(--color-primary-a60)"),
    ("rgba(0,103,79,0.70)",  "var(--color-primary-a70)"),
    ("rgba(0,103,79,0.7)",   "var(--color-primary-a70)"),
    ("rgba(0,103,79,.7)",    "var(--color-primary-a70)"),
    ("rgba(0,103,79,0.80)",  "var(--color-primary-a80)"),
    ("rgba(0,103,79,0.8)",   "var(--color-primary-a80)"),
    ("rgba(0,103,79,.8)",    "var(--color-primary-a80)"),
    ("rgba(0,103,79,0.90)",  "var(--color-primary-a90)"),
    ("rgba(0,103,79,0.9)",   "var(--color-primary-a90)"),
    ("rgba(0,103,79,.9)",    "var(--color-primary-a90)"),

    # ── rgba — glass ──────────────────────────────────────────────
    ("rgba(255,255,255,0.72)", "var(--glass-bg)"),
    ("rgba(255,255,255,.72)",  "var(--glass-bg)"),
    ("rgba(255,255,255,0.94)", "var(--glass-bg-strong)"),
    ("rgba(255,255,255,.94)",  "var(--glass-bg-strong)"),
    ("rgba(255,255,255,0.92)", "var(--glass-bg-strong)"),
    ("rgba(255,255,255,.92)",  "var(--glass-bg-strong)"),
    ("rgba(255,255,255,0.48)", "var(--glass-bg-subtle)"),
    ("rgba(255,255,255,.48)",  "var(--glass-bg-subtle)"),
    ("rgba(255,255,255,0.82)", "var(--glass-border)"),
    ("rgba(255,255,255,.82)",  "var(--glass-border)"),
    ("rgba(255,255,255,0.80)", "var(--glass-border)"),
    ("rgba(255,255,255,.80)",  "var(--glass-border)"),
    ("rgba(15,23,42,0.42)",    "var(--glass-dark-bg)"),
    ("rgba(15,23,42,.42)",     "var(--glass-dark-bg)"),
    ("rgba(15,23,42,0.40)",    "var(--glass-dark-bg)"),
    ("rgba(255,255,255,0.08)", "var(--glass-dark-border)"),
    ("rgba(255,255,255,.08)",  "var(--glass-dark-border)"),

    # ── rgba — black utilities ─────────────────────────────────────
    ("rgba(0,0,0,0.02)",  "var(--color-black-a002)"),
    ("rgba(0,0,0,.02)",   "var(--color-black-a002)"),
    ("rgba(0,0,0,0.04)",  "var(--color-black-a004)"),
    ("rgba(0,0,0,.04)",   "var(--color-black-a004)"),
    ("rgba(0,0,0,0.06)",  "var(--color-black-a006)"),
    ("rgba(0,0,0,.06)",   "var(--color-black-a006)"),
    ("rgba(0,0,0,0.10)",  "var(--color-black-a010)"),
    ("rgba(0,0,0,0.1)",   "var(--color-black-a010)"),
    ("rgba(0,0,0,.10)",   "var(--color-black-a010)"),
    ("rgba(0,0,0,.1)",    "var(--color-black-a010)"),
    ("rgba(0,0,0,0.20)",  "var(--color-black-a020)"),
    ("rgba(0,0,0,0.2)",   "var(--color-black-a020)"),
    ("rgba(0,0,0,.20)",   "var(--color-black-a020)"),
    ("rgba(0,0,0,.2)",    "var(--color-black-a020)"),
]

# Regex untuk menangkap atribut style="..."
RE_INLINE_STYLE = re.compile(
    r'(style\s*=\s*["\'])([^"\']*?)(["\'])',
    re.IGNORECASE
)

def _build_inline_replace_patterns() -> list[tuple[re.Pattern, str, str]]:
    """
    Compile semua pola untuk inline style replacement.
    Urutan: rgba panjang dulu, baru hex pendek.
    Toleran terhadap spasi di dalam rgba().
    Hex pakai word boundary agar tidak partial match.
    """
    patterns = []
    for raw_val, token in INLINE_VALUE_MAP:
        if raw_val.startswith("rgba") or raw_val.startswith("rgb"):
            nums = re.findall(r'[\d.]+', raw_val)
            func = r'rgba' if raw_val.lower().startswith("rgba") else r'rgb'
            inner = r'\s*,\s*'.join(re.escape(n) for n in nums)
            pat = re.compile(
                func + r'\s*\(\s*' + inner + r'\s*\)',
                re.IGNORECASE
            )
        else:
            # Word boundary: tidak match jika dikelilingi karakter hex lain
            pat = re.compile(
                r'(?<![a-fA-F0-9])' + re.escape(raw_val) + r'(?![a-fA-F0-9])',
                re.IGNORECASE
            )
        patterns.append((pat, token, raw_val))

    def sort_key(entry):
        val = entry[2]
        if val.startswith("rgba") or val.startswith("rgb"):
            return (0, -len(val))
        return (1, -len(val))

    patterns.sort(key=sort_key)
    return patterns


def migrate_inline_style(
    attr_value: str,
    patterns: list,
) -> tuple[str, int]:
    """
    Proses isi satu atribut style="...".
    Return: (new_value, count_replaced)
    """
    result = attr_value
    count  = 0
    for pat, token, _ in patterns:
        new, n = pat.subn(token, result)
        count += n
        result = new
    return result, count


def process_inline_styles(
    content: str,
    patterns: list,
) -> tuple[str, int]:
    """
    Proses semua style="" di seluruh file HTML.
    Hanya sentuh nilai di dalam atribut, bukan <style> block.
    """
    total = 0

    def replacer(m):
        nonlocal total
        quote_open  = m.group(1)
        style_value = m.group(2)
        quote_close = m.group(3)

        new_value, n = migrate_inline_style(style_value, patterns)
        total += n
        return f"{quote_open}{new_value}{quote_close}"

    new_content = RE_INLINE_STYLE.sub(replacer, content)
    return new_content, total


# ══════════════════════════════════════════════════════════════════
# [B] TAILWIND CLASS CONSOLIDATOR
# ══════════════════════════════════════════════════════════════════
#
# Dua masalah utama:
#   1. gray + zinc overlap dengan slate → standarisasi ke slate
#   2. Tailwind emerald (tw values) → kita biarkan karena
#      Tailwind emerald sekarang dikontrol via CSS var di design system
#      Yang perlu diganti hanya kelas yang "salah family"
#
# Pendekatan: regex pada atribut class="..."
# Hanya ganti class name, TIDAK hapus class
# ──────────────────────────────────────────────────────────────────

# Pasangan: (tw_class_lama, tw_class_baru)
# Gray → Slate (mapping visual terdekat)
TW_CLASS_MAP: list[tuple[str, str]] = [

    # ── text-gray → text-slate ───────────────────────────────────
    ("text-gray-50",   "text-slate-50"),
    ("text-gray-100",  "text-slate-100"),
    ("text-gray-200",  "text-slate-200"),
    ("text-gray-300",  "text-slate-300"),
    ("text-gray-400",  "text-slate-400"),
    ("text-gray-500",  "text-slate-500"),
    ("text-gray-600",  "text-slate-600"),
    ("text-gray-700",  "text-slate-700"),
    ("text-gray-800",  "text-slate-800"),
    ("text-gray-900",  "text-slate-900"),

    # ── bg-gray → bg-slate ───────────────────────────────────────
    ("bg-gray-50",     "bg-slate-50"),
    ("bg-gray-100",    "bg-slate-100"),
    ("bg-gray-200",    "bg-slate-200"),
    ("bg-gray-300",    "bg-slate-300"),
    ("bg-gray-400",    "bg-slate-400"),
    ("bg-gray-500",    "bg-slate-500"),
    ("bg-gray-600",    "bg-slate-600"),
    ("bg-gray-700",    "bg-slate-700"),
    ("bg-gray-800",    "bg-slate-800"),
    ("bg-gray-900",    "bg-slate-900"),

    # ── border-gray → border-slate ───────────────────────────────
    ("border-gray-50",   "border-slate-50"),
    ("border-gray-100",  "border-slate-100"),
    ("border-gray-200",  "border-slate-200"),
    ("border-gray-300",  "border-slate-300"),
    ("border-gray-400",  "border-slate-400"),
    ("border-gray-500",  "border-slate-500"),
    ("border-gray-600",  "border-slate-600"),
    ("border-gray-700",  "border-slate-700"),
    ("border-gray-800",  "border-slate-800"),
    ("border-gray-900",  "border-slate-900"),

    # ── divide-gray → divide-slate ───────────────────────────────
    ("divide-gray-50",   "divide-slate-50"),
    ("divide-gray-100",  "divide-slate-100"),
    ("divide-gray-200",  "divide-slate-200"),
    ("divide-gray-300",  "divide-slate-300"),

    # ── ring-gray → ring-slate ───────────────────────────────────
    ("ring-gray-200",    "ring-slate-200"),
    ("ring-gray-300",    "ring-slate-300"),

    # ── placeholder-gray → placeholder-slate ─────────────────────
    ("placeholder-gray-300",  "placeholder-slate-300"),
    ("placeholder-gray-400",  "placeholder-slate-400"),
    ("placeholder-gray-500",  "placeholder-slate-500"),

    # ── text-zinc → text-slate ───────────────────────────────────
    ("text-zinc-400",  "text-slate-400"),
    ("text-zinc-500",  "text-slate-500"),
    ("text-zinc-600",  "text-slate-600"),
    ("text-zinc-700",  "text-slate-700"),
    ("text-zinc-800",  "text-slate-800"),
    ("text-zinc-900",  "text-slate-900"),

    # ── bg-zinc → bg-slate ───────────────────────────────────────
    ("bg-zinc-50",     "bg-slate-50"),
    ("bg-zinc-100",    "bg-slate-100"),
    ("bg-zinc-200",    "bg-slate-200"),
    ("bg-zinc-800",    "bg-slate-800"),
    ("bg-zinc-900",    "bg-slate-900"),

    # ── border-zinc → border-slate ───────────────────────────────
    ("border-zinc-200", "border-slate-200"),
    ("border-zinc-300", "border-slate-300"),

    # ── Tailwind emerald lama → biarkan untuk yang sudah ada di slate
    # Tapi ganti hover variant yang tidak konsisten
    ("hover:text-emerald-600",  "hover:text-emerald-400"),
    ("hover:bg-emerald-600",    "hover:bg-emerald-400"),

    # ── focus ring lama ───────────────────────────────────────────
    ("focus:ring-emerald-500",  "focus:ring-emerald-400"),
    ("focus:border-emerald-500","focus:border-emerald-400"),
]

# Bangun regex per class — harus match whole word (bukan substring)
# Tailwind class bisa diikuti: spasi, quote, > , newline
_TW_WORD_BOUNDARY = r'(?=[\s"\'>/\n\r]|$)'

def _build_tw_patterns() -> list[tuple[re.Pattern, str, str]]:
    patterns = []
    for old_cls, new_cls in TW_CLASS_MAP:
        pat = re.compile(
            r'(?<![a-zA-Z0-9_-])' + re.escape(old_cls) + _TW_WORD_BOUNDARY
        )
        patterns.append((pat, new_cls, old_cls))
    return patterns


def process_tailwind_classes(
    content: str,
    patterns: list,
) -> tuple[str, int]:
    """
    Ganti Tailwind class di seluruh file.
    Berlaku di: class="...", :class="...", x-bind:class="..."
    """
    total  = 0
    result = content
    for pat, new_cls, _ in patterns:
        new_result, n = pat.subn(new_cls, result)
        total  += n
        result  = new_result
    return result, total


# ══════════════════════════════════════════════════════════════════
# [C] BACKDROP FILTER MIGRATOR
# ══════════════════════════════════════════════════════════════════
#
# Dua kasus:
#   C1. var(--backdrop-blur-20px-saturate-160) → var(--glass-blur)
#       Artefak dari token migrator v1 yang bikin nama panjang.
#   C2. blur(12px) raw → var(--glass-blur-sm)
#       Backdrop filter yang belum ditokenisasi sama sekali.
#
# Hanya touch backdrop-filter property, tidak yang lain.
# ──────────────────────────────────────────────────────────────────

# C1: var(--backdrop-*) artefak → var(--glass-*)
BACKDROP_VAR_MAP: list[tuple[str, str]] = [
    # sm — ≤ 16px atau tanpa saturate tinggi
    ("var(--backdrop-blur-8px)",                            "var(--glass-dark-blur)"),
    ("var(--backdrop-blur-10px)",                           "var(--glass-blur-sm)"),
    ("var(--backdrop-blur-12px)",                           "var(--glass-blur-sm)"),
    ("var(--backdrop-blur-14px)",                           "var(--glass-blur-sm)"),
    ("var(--backdrop-blur-16px)",                           "var(--glass-blur-sm)"),
    ("var(--backdrop-blur-18px-saturate-150)",              "var(--glass-blur-sm)"),
    ("var(--backdrop-blur-18px-saturate-155)",              "var(--glass-blur-sm)"),
    ("var(--backdrop-var-blur)",                            "var(--glass-blur-sm)"),
    ("var(--backdrop-var-glass-blur-blur-14px-saturate-1)", "var(--glass-blur-sm)"),
    ("var(--backdrop-var-glass-dark-blur-blur-6px)",        "var(--glass-dark-blur)"),
    ("var(--backdrop-blur-4px)",                            "blur(4px)"),
    ("var(--backdrop-blur-3px)",                            "blur(3px)"),
    # base — ~20px
    ("var(--backdrop-blur-20px-saturate-160)",              "var(--glass-blur)"),
    ("var(--backdrop-blur-20px-saturate-150)",              "var(--glass-blur)"),
    ("var(--backdrop-blur-20px-saturate-180)",              "var(--glass-blur)"),
    ("var(--backdrop-blur-20px)",                           "var(--glass-blur)"),
    ("var(--backdrop-var-glass-blur)",                      "var(--glass-blur)"),
    # lg — ≥ 22px
    ("var(--backdrop-blur-22px-saturate-170)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-22px-saturate-165)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-22px-saturate-160)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-24px-saturate-180)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-24px-saturate-160)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-24px)",                           "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-28px-saturate-180)",              "var(--glass-blur-lg)"),
    ("var(--backdrop-blur-30px-saturate-200)",              "var(--glass-blur-lg)"),
]

# C2: raw blur() → var(--glass-*)
BACKDROP_RAW_MAP: list[tuple[str, str]] = [
    ("blur(3px)",                  "var(--glass-dark-blur)"),
    ("blur(4px)",                  "var(--glass-dark-blur)"),
    ("blur(6px)",                  "var(--glass-dark-blur)"),
    ("blur(8px)",                  "var(--glass-dark-blur)"),
    ("blur(10px)",                 "var(--glass-blur-sm)"),
    ("blur(12px)",                 "var(--glass-blur-sm)"),
    ("blur(14px)",                 "var(--glass-blur-sm)"),
    ("blur(16px)",                 "var(--glass-blur-sm)"),
    ("blur(20px) saturate(160%)",  "var(--glass-blur)"),
    ("blur(20px) saturate(180%)",  "var(--glass-blur)"),
    ("blur(20px)",                 "var(--glass-blur)"),
]

# Regex: hanya match di dalam backdrop-filter property
# backdrop-filter: <value>;
# -webkit-backdrop-filter: <value>;
RE_BACKDROP_PROP = re.compile(
    r'(-webkit-)?backdrop-filter\s*:\s*([^;}"\']+)',
    re.IGNORECASE
)

def _build_backdrop_patterns():
    """Compile pola untuk C1 (var) dan C2 (raw), urutan panjang dulu."""
    all_pairs = BACKDROP_VAR_MAP + BACKDROP_RAW_MAP
    all_pairs.sort(key=lambda x: -len(x[0]))
    patterns = []
    for old_val, new_val in all_pairs:
        pat = re.compile(re.escape(old_val), re.IGNORECASE)
        patterns.append((pat, new_val, old_val))
    return patterns


def process_backdrop_filters(content: str, patterns: list) -> tuple[str, int]:
    """
    Ganti backdrop-filter value di seluruh file.
    Berlaku di <style> block DAN inline style.
    """
    total = 0

    def replacer(m):
        nonlocal total
        prefix = m.group(1) or ""
        value  = m.group(2)
        new_val = value
        for pat, replacement, _ in patterns:
            new_str, n = pat.subn(replacement, new_val)
            total += n
            new_val = new_str
        return f"{prefix}backdrop-filter: {new_val}"

    new_content = RE_BACKDROP_PROP.sub(replacer, content)
    return new_content, total


# ══════════════════════════════════════════════════════════════════
# FILE UTILITIES
# ══════════════════════════════════════════════════════════════════

def is_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def find_templates(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.html")
        if not is_skip(p)
    )


def backup_file(path: Path, backup_root: Path) -> Path:
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel      = path.relative_to(path.anchor) if path.is_absolute() else path
    dest_dir = backup_root / stamp
    dest     = dest_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


# ══════════════════════════════════════════════════════════════════
# REPORTER
# ══════════════════════════════════════════════════════════════════

def build_report(results: list[dict]) -> dict:
    total_inline_files   = sum(1 for r in results if r["inline_count"] > 0)
    total_inline_n       = sum(r["inline_count"] for r in results)
    total_tw_files       = sum(1 for r in results if r["tw_count"] > 0)
    total_tw_n           = sum(r["tw_count"] for r in results)
    total_backdrop_files = sum(1 for r in results if r["backdrop_count"] > 0)
    total_backdrop_n     = sum(r["backdrop_count"] for r in results)

    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_files_scanned"        : len(results),
            "inline_style_files"         : total_inline_files,
            "inline_style_replacements"  : total_inline_n,
            "tailwind_class_files"       : total_tw_files,
            "tailwind_class_replacements": total_tw_n,
            "backdrop_files"             : total_backdrop_files,
            "backdrop_replacements"      : total_backdrop_n,
        },
        "files": results,
    }


def print_summary(report: dict, dry_run: bool) -> None:
    s    = report["summary"]
    mode = f"{Y}DRY-RUN{RST}" if dry_run else f"{G}APPLIED{RST}"
    print(f"\n{hr('═')}")
    print(f"  {B}Lumra Full Migrator{RST}  —  {mode}")
    print(hr('═'))
    print(f"  File di-scan                   : {W}{s['total_files_scanned']}{RST}")
    print()
    print(f"  {B}[A] Inline style=\"\"{RST}")
    print(f"  File terpengaruh               : {W}{s['inline_style_files']}{RST}")
    print(f"  Total penggantian              : {G}{s['inline_style_replacements']}{RST}")
    print()
    print(f"  {B}[B] Tailwind class consolidation{RST}")
    print(f"  File terpengaruh               : {W}{s['tailwind_class_files']}{RST}")
    print(f"  Total penggantian              : {G}{s['tailwind_class_replacements']}{RST}")
    print()
    print(f"  {B}[C] Backdrop filter normalisasi{RST}")
    print(f"  File terpengaruh               : {W}{s['backdrop_files']}{RST}")
    print(f"  Total penggantian              : {G}{s['backdrop_replacements']}{RST}")
    print(hr())


def print_detail(results: list[dict], verbose: bool) -> None:
    changed = [r for r in results if r["inline_count"] > 0 or r["tw_count"] > 0 or r["backdrop_count"] > 0]
    if not changed:
        print(f"  {Y}Tidak ada perubahan terdeteksi.{RST}")
        return

    print(f"\n  {'File':<52} {'Inline':>7} {'TW':>6} {'BDrop':>6}")
    print(f"  {DIM}{'─'*52} {'───────':>7} {'──────':>6} {'──────':>6}{RST}")

    for r in sorted(changed, key=lambda x: -(x["inline_count"] + x["tw_count"] + x["backdrop_count"])):
        il = f"{G}{r['inline_count']:>7}{RST}"    if r["inline_count"]   else f"{DIM}{'—':>7}{RST}"
        tw = f"{G}{r['tw_count']:>6}{RST}"        if r["tw_count"]       else f"{DIM}{'—':>6}{RST}"
        bd = f"{G}{r['backdrop_count']:>6}{RST}"  if r["backdrop_count"] else f"{DIM}{'—':>6}{RST}"
        print(f"  {DIM}{r['path']:<52}{RST} {il} {tw} {bd}")

        if verbose and r.get("inline_samples"):
            for s in r["inline_samples"][:3]:
                print(f"    {DIM}  ↳ {s['from'][:38]} → {s['to'][:38]}{RST}")


# ══════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ══════════════════════════════════════════════════════════════════

def run(
    root      : Path,
    backup_dir: Path,
    mode      : str,
    dry_run   : bool,
    verbose   : bool,
) -> list[dict]:
    templates         = find_templates(root)
    inline_patterns   = _build_inline_replace_patterns()
    tw_patterns       = _build_tw_patterns()
    backdrop_patterns = _build_backdrop_patterns()
    results           = []

    do_inline   = mode in ("all", "inline")
    do_tw       = mode in ("all", "tw")
    do_backdrop = mode in ("all", "backdrop")

    for path in templates:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {Y}⚠  Gagal baca {path.name}: {e}{RST}")
            continue

        rel          = str(path.relative_to(root)).replace("\\", "/")
        orig_content = content
        inline_count   = 0
        tw_count       = 0
        backdrop_count = 0
        inline_samples = []

        if do_inline:
            if verbose:
                RE_STYLE_ATTR = re.compile(r'style\s*=\s*["\']([^"\']*?)["\']', re.IGNORECASE)
                for m in RE_STYLE_ATTR.finditer(content):
                    old_v = m.group(1)
                    new_v, n = migrate_inline_style(old_v, inline_patterns)
                    if n > 0:
                        inline_samples.append({"from": old_v[:60], "to": new_v[:60]})
            content, inline_count = process_inline_styles(content, inline_patterns)

        if do_tw:
            content, tw_count = process_tailwind_classes(content, tw_patterns)

        if do_backdrop:
            content, backdrop_count = process_backdrop_filters(content, backdrop_patterns)

        results.append({
            "path"           : rel,
            "inline_count"   : inline_count,
            "tw_count"       : tw_count,
            "backdrop_count" : backdrop_count,
            "inline_samples" : inline_samples,
            "changed"        : content != orig_content,
        })

        if content != orig_content and not dry_run:
            backup_file(path, backup_dir)
            path.write_text(content, encoding="utf-8")

    return results


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Full Migrator — inline style + Tailwind consolidation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--root",    type=Path, default=DEFAULT_ROOT,
                   help=f"Template root (default: {DEFAULT_ROOT})")
    p.add_argument("--backup",  type=Path, default=DEFAULT_BACKUP,
                   help=f"Backup dir (default: {DEFAULT_BACKUP})")
    p.add_argument("--only",    choices=["inline", "tw", "backdrop", "all"], default="all",
                   help="Jalankan hanya satu mode (default: all)")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Preview saja, tidak ubah file")
    p.add_argument("--apply",   action="store_true", default=False,
                   help="Apply perubahan ke file")
    p.add_argument("--report",  type=Path, default=None,
                   help="Simpan JSON report")
    p.add_argument("--verbose", action="store_true", default=False,
                   help="Tampilkan detail setiap penggantian")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.apply:
        args.dry_run = True

    if not args.root.exists():
        print(f"{R}[ERROR] Root tidak ditemukan: {args.root}{RST}")
        sys.exit(1)

    print(f"\n{hr('═')}")
    print(f"  {B}Lumra Full Migrator  v1.0{RST}")
    print(hr('═'))
    print(f"  Root    : {DIM}{args.root}{RST}")
    print(f"  Mode    : {W}{args.only.upper()}{RST}")
    print(f"  Action  : {Y if args.dry_run else G}{'DRY-RUN' if args.dry_run else 'APPLY'}{RST}\n")

    results = run(
        root       = args.root,
        backup_dir = args.backup,
        mode       = args.only,
        dry_run    = args.dry_run,
        verbose    = args.verbose,
    )

    report = build_report(results)
    print_summary(report, dry_run=args.dry_run)
    print_detail(results, verbose=args.verbose)

    if args.report:
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\n  {G}📄 JSON report: {args.report}{RST}")

    if args.dry_run:
        print(f"\n  {Y}DRY-RUN — tidak ada file yang diubah.{RST}")
        print(f"  Jalankan dengan {W}--apply{RST} untuk apply.\n")
    else:
        s = report["summary"]
        total = (s["inline_style_replacements"]
                 + s["tailwind_class_replacements"]
                 + s["backdrop_replacements"])
        changed_files = max(
            s["inline_style_files"],
            s["tailwind_class_files"],
            s["backdrop_files"],
        )
        print(f"\n  {G}✅ Selesai — {total} penggantian di {changed_files} file.{RST}")
        print(f"  {DIM}Backup: {args.backup}{RST}\n")

    print(hr('═') + "\n")


if __name__ == "__main__":
    main()