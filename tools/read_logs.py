#!/usr/bin/env python
# =============================================================
# tools/read_logs.py
# 
# CLI tool untuk baca dan filter log Lumra dengan mudah.
# Jalankan: python tools/read_logs.py
# =============================================================

import os
import re
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'

LOGS = {
    '1': ('error.log',       '🔴 Error Log      — semua ERROR & CRITICAL'),
    '2': ('debug.log',       '🔵 Debug Log       — semua aktivitas (dev)'),
    '3': ('security.log',    '🟡 Security Log    — auth & permission events'),
    '4': ('performance.log', '🟠 Performance Log — slow queries & requests'),
}

LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def read_log(filename, tail=50, level=None, search=None):
    filepath = LOGS_DIR / filename
    if not filepath.exists():
        print(f"  ⚠️  File tidak ditemukan: {filepath}")
        return

    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    # Filter by level
    if level:
        lines = [l for l in lines if f' {level.upper()} ' in l]

    # Filter by keyword
    if search:
        lines = [l for l in lines if search.lower() in l.lower()]

    # Ambil N baris terakhir
    lines = lines[-tail:]

    if not lines:
        print("  ℹ️  Tidak ada log yang cocok dengan filter.")
        return

    print(f"\n{'='*70}")
    for line in lines:
        line = line.rstrip()
        # Warnai berdasarkan level
        if 'CRITICAL' in line:
            print(f"\033[35m{line}\033[0m")   # Magenta
        elif 'ERROR' in line:
            print(f"\033[31m{line}\033[0m")   # Merah
        elif 'WARNING' in line:
            print(f"\033[33m{line}\033[0m")   # Kuning
        elif 'INFO' in line:
            print(f"\033[32m{line}\033[0m")   # Hijau
        else:
            print(line)
    print(f"{'='*70}")
    print(f"  → Menampilkan {len(lines)} baris terakhir dari {filename}")


def show_summary():
    """Ringkasan ukuran dan jumlah error tiap log file."""
    print(f"\n📊 LUMRA LOG SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    for key, (filename, label) in LOGS.items():
        filepath = LOGS_DIR / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            with open(filepath, encoding='utf-8') as f:
                lines = f.readlines()
            errors   = sum(1 for l in lines if ' ERROR    ' in l)
            critical = sum(1 for l in lines if ' CRITICAL ' in l)
            warnings = sum(1 for l in lines if ' WARNING  ' in l)
            print(f"  {label}")
            print(f"    📁 {size_kb:.1f} KB | "
                  f"🔴 {errors} errors | "
                  f"🟣 {critical} critical | "
                  f"🟡 {warnings} warnings")
        else:
            print(f"  {label}")
            print(f"    📁 Belum ada log")
    print(f"{'='*60}")


def main():
    print("\n🚀 LUMRA LOG READER")
    print("=" * 40)

    show_summary()

    print("\nPilih log yang ingin dibaca:")
    for key, (_, label) in LOGS.items():
        print(f"  [{key}] {label}")
    print("  [s] Summary saja")
    print("  [q] Keluar")

    choice = input("\nPilihan: ").strip().lower()

    if choice == 'q':
        return
    if choice == 's':
        return

    if choice not in LOGS:
        print("Pilihan tidak valid.")
        return

    filename, label = LOGS[choice]

    # Filter opsional
    tail_input = input("Tampilkan berapa baris terakhir? [default: 50]: ").strip()
    tail = int(tail_input) if tail_input.isdigit() else 50

    level_input = input(f"Filter level? ({'/'.join(LEVELS)}) [kosongkan=semua]: ").strip().upper()
    level = level_input if level_input in LEVELS else None

    search_input = input("Cari keyword? [kosongkan=semua]: ").strip()
    search = search_input if search_input else None

    read_log(filename, tail=tail, level=level, search=search)


if __name__ == "__main__":
    main()