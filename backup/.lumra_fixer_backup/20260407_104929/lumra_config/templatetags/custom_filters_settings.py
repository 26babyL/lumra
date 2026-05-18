# templatetags/custom_filters_settings.py
"""
Lumra ERP — Unified Template Filter Library
============================================
Menggabungkan currency_filters.py + custom_filters.py menjadi satu file
yang lebih robust, presisi, dan siap production.

Cara registrasi di template:
    {% load custom_filters_settings %}

Author  : Lumra ERP Team
Version : 2.0.0
"""

from django import template
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math

register = template.Library()


# ─────────────────────────────────────────────
# 💰 CURRENCY FILTERS
# ─────────────────────────────────────────────

@register.filter(name='rupiah')
def rupiah(value, show_symbol=True):
    """
    Format angka ke format Rupiah Indonesia (presisi Decimal).

    Menggunakan Decimal untuk menghindari floating-point error
    pada nilai besar (misal: transaksi 118.000 SKU).

    Contoh:
        {{ 1000000 | rupiah }}          → Rp 1.000.000
        {{ 1234.5  | rupiah }}          → Rp 1.234,50
        {{ 1234.5  | rupiah:False }}    → 1.234,50
        {{ None    | rupiah }}          → -
        {{ "abc"   | rupiah }}          → Rp 0
    """
    if value is None or value == '':
        return '-'

    try:
        d = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return f"Rp 0" if show_symbol else "0"

    sign       = '-' if d < 0 else ''
    d_abs      = abs(d)
    int_part   = int(d_abs)
    frac_val   = int(round((d_abs - int_part) * 100))

    # Format ribuan dengan titik (standar ID)
    int_str    = f"{int_part:,}".replace(',', '.')
    frac_str   = f",{frac_val:02d}" if frac_val else ''

    formatted  = f"{sign}{int_str}{frac_str}"
    return f"Rp {formatted}" if show_symbol else formatted


@register.filter(name='rupiah_short')
def rupiah_short(value):
    """
    Format Rupiah singkat untuk tampilan KPI card / dashboard.

    Contoh:
        {{ 1500000    | rupiah_short }}  → Rp 1,5 Jt
        {{ 2000000000 | rupiah_short }}  → Rp 2 M
        {{ 750000     | rupiah_short }}  → Rp 750 Rb
        {{ 500        | rupiah_short }}  → Rp 500
    """
    if value is None or value == '':
        return '-'
    try:
        n = float(value)
    except (ValueError, TypeError):
        return 'Rp 0'

    abs_n = abs(n)
    sign  = '-' if n < 0 else ''

    if abs_n >= 1_000_000_000:
        result = f"{abs_n / 1_000_000_000:.1f}".rstrip('0').rstrip('.') + ' M'
    elif abs_n >= 1_000_000:
        result = f"{abs_n / 1_000_000:.1f}".rstrip('0').rstrip('.') + ' Jt'
    elif abs_n >= 1_000:
        result = f"{abs_n / 1_000:.1f}".rstrip('0').rstrip('.') + ' Rb'
    else:
        result = f"{abs_n:.0f}"

    return f"Rp {sign}{result}"


@register.filter(name='rupiah_input')
def rupiah_input(value):
    """
    Format untuk nilai input field (tanpa simbol, tanpa desimal jika bulat).
    Berguna untuk pre-fill form input harga.

    Contoh:
        {{ 1000000 | rupiah_input }}  → 1.000.000
    """
    return rupiah(value, show_symbol=False)


# ─────────────────────────────────────────────
# ➕ MATH FILTERS
# ─────────────────────────────────────────────

@register.filter(name='add_val')
def add_val(value, arg):
    """
    Penjumlahan aman (value + arg).
    Gunakan ini karena filter bawaan Django 'add' kadang concat string.

    Contoh:
        {{ 100 | add_val:50 }}   → 150
        {{ 100 | add_val:"50" }} → 150
    """
    try:
        return _to_decimal(value) + _to_decimal(arg)
    except Exception:
        return 0


@register.filter(name='sub')
def sub(value, arg):
    """
    Pengurangan aman (value - arg).

    Contoh:
        {{ 200 | sub:50 }}  → 150
    """
    try:
        return _to_decimal(value) - _to_decimal(arg)
    except Exception:
        return 0


@register.filter(name='mul')
def mul(value, arg):
    """
    Perkalian aman (value × arg).
    Berguna untuk: harga × qty, margin × 100, dsb.

    Contoh:
        {{ 5000 | mul:12 }}     → 60000
        {{ 0.15 | mul:100 }}    → 15.0
    """
    try:
        return _to_decimal(value) * _to_decimal(arg)
    except Exception:
        return 0


@register.filter(name='div')
def div(value, arg):
    """
    Pembagian aman (value ÷ arg). Menghindari ZeroDivisionError.

    Contoh:
        {{ 100 | div:4 }}   → 25.0
        {{ 100 | div:0 }}   → 0  (safe)
    """
    try:
        divisor = _to_decimal(arg)
        if divisor == 0:
            return 0
        return _to_decimal(value) / divisor
    except Exception:
        return 0


@register.filter(name='mod')
def mod(value, arg):
    """
    Modulo aman (value % arg).
    Berguna untuk logika paginasi atau pengelompokan baris tabel.

    Contoh:
        {{ 10 | mod:3 }}  → 1
    """
    try:
        divisor = _to_decimal(arg)
        if divisor == 0:
            return 0
        return _to_decimal(value) % divisor
    except Exception:
        return 0


@register.filter(name='percent')
def percent(value, total):
    """
    Hitung persentase (value / total × 100), dibulatkan 1 desimal.
    Berguna untuk progress bar, chart share, margin %.

    Contoh:
        {{ 30 | percent:120 }}  → 25.0
        {{ 0  | percent:0 }}    → 0
    """
    try:
        t = _to_decimal(total)
        if t == 0:
            return Decimal('0')
        result = (_to_decimal(value) / t * 100).quantize(
            Decimal('0.1'), rounding=ROUND_HALF_UP
        )
        return result
    except Exception:
        return 0


@register.filter(name='abs_val')
def abs_val(value):
    """
    Nilai absolut. Berguna untuk menampilkan selisih stok tanpa tanda minus.

    Contoh:
        {{ -500 | abs_val }}  → 500
    """
    try:
        return abs(_to_decimal(value))
    except Exception:
        return 0


# ─────────────────────────────────────────────
# 🔢 NUMBER FORMAT FILTERS
# ─────────────────────────────────────────────

@register.filter(name='number_id')
def number_id(value, decimal_places=0):
    """
    Format angka dengan separator Indonesia (titik=ribuan, koma=desimal).
    Tanpa simbol mata uang — cocok untuk qty, berat, volume.

    Contoh:
        {{ 1234567   | number_id }}    → 1.234.567
        {{ 1234.567  | number_id:2 }}  → 1.234,57
    """
    if value is None or value == '':
        return '-'
    try:
        places = int(decimal_places)
        d      = Decimal(str(value)).quantize(
            Decimal(10) ** -places, rounding=ROUND_HALF_UP
        )
        int_part = int(abs(d))
        frac_val = int(round(abs(abs(d) - int_part) * (10 ** places)))
        sign     = '-' if d < 0 else ''
        int_str  = f"{int_part:,}".replace(',', '.')
        frac_str = f",{frac_val:0{places}d}" if places > 0 else ''
        return f"{sign}{int_str}{frac_str}"
    except Exception:
        return value


@register.filter(name='intcomma_id')
def intcomma_id(value):
    """
    Alias ringkas untuk number_id tanpa desimal.
    Cocok untuk menampilkan stok, jumlah unit, qty.

    Contoh:
        {{ 5000 | intcomma_id }}  → 5.000
    """
    return number_id(value, decimal_places=0)


# ─────────────────────────────────────────────
# 🏷️ DISPLAY / LABEL FILTERS
# ─────────────────────────────────────────────

@register.filter(name='stock_status')
def stock_status(value, threshold=10):
    """
    Kembalikan label status stok berdasarkan nilai dan threshold.
    Berguna untuk badge warna di inventory list.

    Contoh:
        {{ 0  | stock_status }}     → 'empty'
        {{ 5  | stock_status:10 }}  → 'low'
        {{ 50 | stock_status:10 }}  → 'ok'
    """
    try:
        qty   = float(value)
        limit = float(threshold)
    except (ValueError, TypeError):
        return 'unknown'

    if qty <= 0:
        return 'empty'
    elif qty <= limit:
        return 'low'
    else:
        return 'ok'


@register.filter(name='pluralize_id')
def pluralize_id(value, singular_plural):
    """
    Pluralisasi sederhana untuk Bahasa Indonesia.
    Format arg: "singular,plural"

    Contoh:
        {{ 1 | pluralize_id:"item,item" }}    → item
        {{ 3 | pluralize_id:"produk,produk" }} → produk
        {{ 2 | pluralize_id:"kotak,kotak" }}   → kotak
    """
    try:
        count = int(value)
        parts = singular_plural.split(',')
        if len(parts) != 2:
            return singular_plural
        return parts[0] if count == 1 else parts[1]
    except Exception:
        return singular_plural


# ─────────────────────────────────────────────
# 🔧 INTERNAL HELPERS (tidak diekspos ke template)
# ─────────────────────────────────────────────

def _to_decimal(value):
    """Konversi value ke Decimal dengan aman."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))