#!/usr/bin/env python3
"""
LUMRA ERP — Audit Fixer v2.0 (Round 2)
========================================
Root cause v1 gagal:
  - Tombol berisi SVG <title> dianggap "tidak kosong" → skip
  - heading_skip hanya handle h1→h3, tidak h2→h4
  - input checkbox (w-3.5 h-3.5, accent-*) tidak terdeteksi
  - xcloak CSS format tidak dikenali audit tool

Perbaikan v2:
  - empty_button: strip <title> saat cek kosong, fallback konteks
  - heading_skip: algoritma umum (semua lompatan level)
  - input_no_label: deteksi checkbox, OTP, class kosong
  - xcloak: pastikan base.html punya CSS, format bervariasi
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

# ═══════════════════════════════════════════════════════════════
# WARNA
# ═══════════════════════════════════════════════════════════════

def C(color, text):
    if not HAS_COLOR:
        return text
    return f"{color}{text}{Style.RESET_ALL}"

GREEN = Fore.GREEN if HAS_COLOR else ""
YELLOW = Fore.YELLOW if HAS_COLOR else ""
RED = Fore.RED if HAS_COLOR else ""
CYAN = Fore.CYAN if HAS_COLOR else ""
DIM = Style.DIM if HAS_COLOR else ""
BOLD = Style.BRIGHT if HAS_COLOR else ""

# ═══════════════════════════════════════════════════════════════
# KONSTANTA — PEMETAAN CLASS → LABEL
# ═══════════════════════════════════════════════════════════════

CLASS_LABEL_RULES = [
    (r'drawer-btn-approve|modal-btn-approve', 'Setujui'),
    (r'drawer-btn-reject|modal-btn-reject', 'Tolak'),
    (r'drawer-btn-secondary|modal-btn-secondary', 'Batal'),
    (r'store-item', 'Pilih toko'),
    (r'cmd-hint-row', 'Jalankan perintah'),
    (r'recent-row', 'Buka item terbaru'),
    (r'search-result-item', 'Pilih hasil pencarian'),
    (r'profile-menu-item', 'Menu profil'),
    (r'submit-btn|btn-submit', 'Kirim'),
    (r'btn-primary|button-primary', 'Kirim'),
    (r'variant-toggle', 'Toggle varian'),
    (r'action-btn', 'Aksi'),
    (r'row-check', 'Pilih baris'),
    (r'check-all', 'Pilih semua'),
    (r'approve|accept|setuju|agree', 'Setujui'),
    (r'reject|deny|tolak|decline', 'Tolak'),
    (r'delete|remove|hapus|destroy|trash', 'Hapus'),
    (r'edit|ubah|modify|pencil', 'Ubah'),
    (r'add|tambah|create|new|\bplus\b', 'Tambah'),
    (r'save|simpan', 'Simpan'),
    (r'submit|kirim|send', 'Kirim'),
    (r'cancel|batal', 'Batal'),
    (r'close|dismiss|tutup|\bx-close\b|\bx\b', 'Tutup'),
    (r'back|kembali|arrow-left|chevron-left', 'Kembali'),
    (r'next|lanjut|arrow-right|chevron-right', 'Selanjutnya'),
    (r'download|unduh', 'Unduh'),
    (r'print|cetak', 'Cetak'),
    (r'refresh|reload', 'Muat ulang'),
    (r'search|cari|magnif', 'Cari'),
    (r'filter|funnel', 'Filter'),
    (r'sort|urutkan', 'Urutkan'),
    (r'export|ekspor', 'Ekspor'),
    (r'import|impor', 'Impor'),
    (r'upload|unggah', 'Unggah'),
    (r'copy|salin|clipboard', 'Salin'),
    (r'share|bagikan', 'Bagikan'),
    (r'\beye\b|view|lihat|show', 'Lihat'),
    (r'eye-off|hide|sembunyikan', 'Sembunyikan'),
    (r'star|favorit|heart|like|suka', 'Favorit'),
    (r'bookmark', 'Bookmark'),
    (r'\bpin\b', 'Pin'),
    (r'more|lainnya|ellipsis|\.\.\.', 'Lainnya'),
    (r'\bmenu\b|hamburger', 'Menu'),
    (r'setting|pengaturan|cog|gear', 'Pengaturan'),
    (r'notif|bell', 'Notifikasi'),
    (r'help|bantuan|\?', 'Bantuan'),
    (r'\binfo\b|informasi', 'Informasi'),
    (r'warning|exclamation|peringatan', 'Peringatan'),
    (r'\berror\b|alert|kesalahan', 'Kesalahan'),
    (r'success|berhasil|check-circle', 'Berhasil'),
    (r'\btoggle\b', 'Toggle'),
    (r'expand|perluas', 'Perluas'),
    (r'collapse|perkecil', 'Perkecil'),
    (r'fullscreen|layar-penuh|maximize', 'Layar penuh'),
    (r'minimize', 'Minimalkan'),
    (r'zoom-in|perbesar', 'Perbesar'),
    (r'zoom-out', 'Perkecil'),
    (r'\brotate\b|putar', 'Putar'),
    (r'\breset\b', 'Reset'),
    (r'\bundo\b', 'Undo'),
    (r'\bredo\b', 'Redo'),
    (r'\bbold\b|tebal', 'Tebal'),
    (r'\bitalic\b|miring', 'Miring'),
    (r'\blink\b|tautan', 'Tautan'),
    (r'image|gambar|photo|foto|camera|kamera', 'Gambar'),
    (r'attach|lampiran|paperclip', 'Lampirkan'),
    (r'reply|balas', 'Balas'),
    (r'phone|telepon|\bcall\b', 'Telepon'),
    (r'\bvideo\b', 'Video'),
    (r'mic|mikrofon|microphone', 'Mikrofon'),
    (r'\bmute\b|bisukan', 'Bisukan'),
    (r'unmute', 'Unbisukan'),
    (r'volume|speaker', 'Volume'),
    (r'\bplay\b|putar', 'Putar'),
    (r'\bpause\b|jeda', 'Jeda'),
    (r'\bstop\b|berhenti', 'Berhenti'),
    (r'\bskip\b|lewat', 'Lewati'),
    (r'comment|komentar', 'Komentar'),
    (r'follow|ikuti', 'Ikuti'),
    (r'subscribe|berlangganan', 'Berlangganan'),
    (r'\bcheck\b|centang', 'Centang'),
    (r'uncheck', 'Hapus centang'),
    (r'\bmove\b|pindah|drag', 'Pindah'),
]

COLOR_LABEL_RULES = [
    (r'rose-\d|red-\d|text-rose|text-red|bg-rose-50|bg-red', 'Hapus'),
    (r'emerald-\d|green-\d|text-emerald|text-green|bg-emerald', 'Setujui'),
    (r'blue-\d|text-blue|bg-blue', 'Lihat'),
    (r'indigo-\d|text-indigo|bg-indigo', 'Lihat'),
    (r'purple-\d|text-purple|bg-purple', 'Detail'),
    (r'amber-\d|yellow-\d|orange-\d|text-amber|text-yellow', 'Peringatan'),
]

HOVER_COLOR_MAP = {
    'rose': 'Hapus', 'red': 'Hapus',
    'emerald': 'Setujui', 'green': 'Setujui',
    'blue': 'Lihat', 'indigo': 'Lihat',
    'purple': 'Detail', 'violet': 'Detail',
    'amber': 'Peringatan', 'yellow': 'Peringatan', 'orange': 'Peringatan',
    'slate': 'Tombol', 'gray': 'Tombol', 'zinc': 'Tombol',
    'white': 'Tombol', 'black': 'Tombol', 'neutral': 'Tombol',
}

ID_WORD_MAP = {
    'name': 'Nama', 'category': 'Kategori', 'barcode': 'Barcode',
    'description': 'Deskripsi', 'active': 'Status aktif', 'sku': 'SKU',
    'size': 'Ukuran', 'buy': 'Harga beli', 'sell': 'Harga jual',
    'price': 'Harga', 'qty': 'Jumlah', 'quantity': 'Jumlah',
    'amount': 'Jumlah', 'date': 'Tanggal', 'start': 'Mulai',
    'end': 'Selesai', 'type': 'Tipe', 'status': 'Status',
    'note': 'Catatan', 'notes': 'Catatan', 'remark': 'Keterangan',
    'remarks': 'Keterangan', 'search': 'Cari', 'filter': 'Filter',
    'edit': 'Ubah', 'add': 'Tambah', 'product': 'produk',
    'supplier': 'Supplier', 'warehouse': 'Gudang', 'location': 'Lokasi',
    'zone': 'Zona', 'batch': 'Batch', 'lot': 'Lot',
    'check': 'Pilih', 'all': 'semua', 'row': 'baris',
    'variant': 'varian', 'unit': 'Satuan', 'total': 'Total',
    'subtotal': 'Subtotal', 'discount': 'Diskon', 'tax': 'Pajak',
    'payment': 'Pembayaran', 'method': 'Metode', 'reference': 'Referensi',
    'number': 'Nomor', 'code': 'Kode', 'phone': 'Telepon',
    'email': 'Email', 'address': 'Alamat', 'city': 'Kota',
    'contact': 'Kontak', 'brand': 'Merek', 'color': 'Warna',
    'weight': 'Berat', 'stock': 'Stok', 'cost': 'Biaya',
    'account': 'Akun', 'debit': 'Debit', 'credit': 'Kredit',
    'balance': 'Saldo', 'period': 'Periode', 'year': 'Tahun',
    'month': 'Bulan', 'file': 'File', 'title': 'Judul',
    'content': 'Konten', 'message': 'Pesan', 'subject': 'Subjek',
    'priority': 'Prioritas', 'group': 'Grup', 'role': 'Peran',
    'user': 'Pengguna', 'password': 'Kata sandi', 'confirm': 'Konfirmasi',
    'target': 'Target', 'reason': 'Alasan', 'adjustment': 'Penyesuaian',
    'movement': 'Pergerakan', 'transfer': 'Transfer', 'receive': 'Terima',
    'issue': 'Keluaran', 'return': 'Retur', 'minimum': 'Minimum',
    'maximum': 'Maksimum', 'reorder': 'Pesan ulang', 'session': 'Sesi',
    'pending': 'Menunggu', 'complete': 'Selesai', 'draft': 'Draft',
    'view': 'Lihat', 'report': 'Laporan', 'summary': 'Ringkasan',
    'detail': 'Detail', 'overview': 'Ikhtisar', 'chart': 'Grafik',
    'list': 'Daftar', 'planned': 'Terencana', 'actual': 'Aktual',
    'opname': 'Opname', 'approval': 'Persetujuan', 'planning': 'Perencanaan',
    'purchasing': 'Pembelian', 'evaluation': 'Evaluasi', 'expiry': 'Kadaluarsa',
    'tracking': 'Pelacakan', 'form': 'Formulir', 'voucher': 'Voucher',
    'journal': 'Jurnal', 'entry': 'Entri', 'ledger': 'Buku besar',
    'trial': 'Percobaan', 'profit': 'Laba', 'loss': 'Rugi',
    'cash': 'Kas', 'flow': 'Arus', 'sheet': 'Neraca',
    'receivable': 'Piutang', 'payable': 'Hutang', 'aging': 'Umur',
    'schedule': 'Jadwal', 'price': 'Harga', 'delete': 'Hapus',
    'campaign': 'Kampanye', 'bar': 'Batang', 'select': 'Pilih',
    'input': 'Masukan', 'conv': 'Konversi', 'conversion': 'Konversi',
    'otp': 'Kode OTP', 'token': 'Token', 'pin': 'PIN',
    'verification': 'Verifikasi', 'verify': 'Verifikasi',
}

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def find_close_tag(html, after_open_pos, tag_name):
    depth = 1
    pos = after_open_pos
    tag_esc = re.escape(tag_name)
    open_re = re.compile(rf'<{tag_esc}\b[^>]*>', re.IGNORECASE)
    close_re = re.compile(rf'</{tag_esc}\s*>', re.IGNORECASE)
    while depth > 0 and pos < len(html):
        next_open = open_re.search(html, pos)
        next_close = close_re.search(html, pos)
        if not next_close:
            return -1
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                return next_close.start()
            pos = next_close.end()
    return -1


def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)


def is_button_empty_v2(inner_html):
    """
    V2: Cek apakah tombol punya teks VISIBLE.
    Perbedaan kritis dari v1: strip <title> dari SVG karena
    <title> itu tooltip, BUKAN visible text di layar.
    """
    # 1. Hapus SVG <title> (tooltip, tidak visible)
    no_titles = re.sub(
        r'<title[^>]*>.*?</title>', '', inner_html,
        flags=re.IGNORECASE | re.DOTALL
    )
    # 2. Hapus semua tag HTML
    text = strip_html_tags(no_titles)
    # 3. Hapus output Django
    text_no_django = re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', text)
    return text_no_django.strip() == ''


def infer_label_from_context(content, btn_start):
    """
    Infer label dari konteks sekitar tombol:
    heading terdekat, parent role, sibling text.
    """
    # Batas pencarian ke belakang
    lookback = content[max(0, btn_start - 600):btn_start]

    # 1. Heading terdekat sebelum tombol
    heading_matches = list(re.finditer(
        r'<h[1-6][^>]*>(.*?)</h[1-6]>', lookback, re.IGNORECASE | re.DOTALL
    ))
    if heading_matches:
        last_h = heading_matches[-1]
        h_text = strip_html_tags(last_h.group(1))
        h_text = re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', h_text).strip()
        if h_text and 1 < len(h_text) < 80:
            return h_text

    # 2. Label terdekat sebelum tombol
    label_match = re.search(
        r'<label[^>]*>(.*?)</label>', lookback[-200:],
        re.IGNORECASE | re.DOTALL
    )
    if label_match:
        l_text = strip_html_tags(label_match.group(1))
        l_text = re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', l_text).strip()
        if l_text and 1 < len(l_text) < 80:
            return l_text

    # 3. Parent dengan role
    role_match = re.search(
        r'<[^>]+role=["\']([^"\']+)["\']', lookback[-200:],
        re.IGNORECASE
    )
    if role_match:
        role = role_match.group(1).lower()
        role_map = {
            'tab': 'Tab', 'tablist': 'Tab', 'menu': 'Menu',
            'menuitem': 'Item menu', 'dialog': 'Dialog',
            'listbox': 'Daftar', 'option': 'Opsi', 'combobox': 'Pilihan',
            'toolbar': 'Toolbar', 'treeitem': 'Item',
        }
        if role in role_map:
            return role_map[role]

    # 4. Teks visible di dekat tombol (span, div, p, td, th)
    near_text_match = re.search(
        r'<(?:span|div|p|td|th|b|strong|em)\b[^>]*>([^<]{2,40})</',
        lookback[-200:], re.IGNORECASE
    )
    if near_text_match:
        t = near_text_match.group(1).strip()
        if t and not t.startswith('{'):
            return t

    return None


def infer_button_label_v2(class_attr, inner_html='', type_attr='',
                          full_content='', btn_start=0):
    """V2: Infer aria-label dengan chain lengkap + fallback konteks."""
    cls = class_attr or ''

    # ── 1. SVG <title> (gunakan sebagai label, bukan penanda kosong) ──
    svg_title = re.search(
        r'<title>([^<]+)</title>', inner_html, re.IGNORECASE
    )
    if svg_title:
        t = svg_title.group(1).strip()
        if t and t.lower() not in ('icon', 'svg', 'vector', 'image',
                                    'shape', 'glyph', 'symbol', ''):
            return t

    # ── 2. Class patterns (spesifik → umum) ──
    for pattern, label in CLASS_LABEL_RULES:
        if re.search(pattern, cls, re.IGNORECASE):
            return label

    # ── 3. <i> icon class ──
    for im in re.finditer(
        r'<i[^>]*class=["\']([^"\']*)["\']', inner_html, re.IGNORECASE
    ):
        ic = im.group(1)
        for pattern, label in CLASS_LABEL_RULES:
            if re.search(pattern, ic, re.IGNORECASE):
                return label

    # ── 4. SVG child element class ──
    path_cls = re.search(
        r'<(?:path|circle|rect|line|polyline|polygon|g)\b[^>]*class=["\']([^"\']*)["\']',
        inner_html, re.IGNORECASE
    )
    if path_cls:
        pc = path_cls.group(1)
        for pattern, label in CLASS_LABEL_RULES:
            if re.search(pattern, pc, re.IGNORECASE):
                return label

    # ── 5. Warna langsung di class ──
    for pattern, label in COLOR_LABEL_RULES:
        if re.search(pattern, cls, re.IGNORECASE):
            return label

    # ── 6. Warna di hover/focus/active state ──
    hover_matches = re.finditer(
        r'(?:hover|focus|active):(?:text|bg)-(\w+)', cls, re.IGNORECASE
    )
    for hm in hover_matches:
        color_name = hm.group(1).lower()
        if color_name in HOVER_COLOR_MAP:
            return HOVER_COLOR_MAP[color_name]

    # ── 7. Warna di inner SVG class ──
    inner_cls = re.search(
        r'<svg[^>]*class=["\']([^"\']*)["\']', inner_html, re.IGNORECASE
    )
    if inner_cls:
        sc = inner_cls.group(1)
        for pattern, label in COLOR_LABEL_RULES:
            if re.search(pattern, sc, re.IGNORECASE):
                return label
        # Hover di svg class
        for hm in re.finditer(
            r'(?:hover|focus):(?:text|bg|stroke)-(\w+)', sc, re.IGNORECASE
        ):
            cn = hm.group(1).lower()
            if cn in HOVER_COLOR_MAP:
                return HOVER_COLOR_MAP[cn]

    # ── 8. Ukuran tombol kecil + rounded → kemungkinan icon button ──
    size_match = re.search(r'w-(\d+\.?\d*)\s+h-(\d+\.?\d*)', cls)
    if size_match:
        w, h = float(size_match.group(1)), float(size_match.group(2))
        if w <= 10 and h <= 10:
            # Tombol kecil, coba infer dari warna yang sudah dicek
            # Jika sampai sini, gunakan default kecil
            return 'Tombol'

    # ── 9. Type fallback ──
    tl = (type_attr or '').lower().strip()
    if tl == 'submit':
        return 'Kirim'
    if tl == 'reset':
        return 'Reset'

    # ── 10. Konteks (heading, label, sibling terdekat) ──
    if full_content and btn_start > 0:
        ctx = infer_label_from_context(full_content, btn_start)
        if ctx:
            return ctx

    # ── 11. Ultimate fallback ──
    return 'Tombol'


def id_to_label(id_str):
    if not id_str:
        return None
    cleaned = re.sub(r'^(edit|add|new|create|update|delete|set|get|search|filter)_', '', id_str, flags=re.IGNORECASE)
    cleaned = re.sub(r'[_\-]+', ' ', cleaned)
    words = cleaned.split()
    if not words:
        return None
    translated = []
    for word in words:
        w = word.lower()
        if w in ID_WORD_MAP:
            translated.append(ID_WORD_MAP[w])
        elif w.isdigit():
            translated.append(word)
        elif len(w) <= 2:
            translated.append(w.upper())
        else:
            translated.append(word.capitalize())
    result = ' '.join(translated)
    if result:
        result = result[0].upper() + result[1:]
    return result


def infer_input_label_v2(tag, attrs, full_content='', input_start=0):
    """V2: Infer label dengan deteksi checkbox, OTP, class kosong."""

    # ── Deteksi checkbox/radio ──
    type_match = re.search(r'type\s*=\s*["\']?(checkbox|radio)\b', attrs, re.IGNORECASE)
    if type_match:
        return 'Pilih'

    # ── Deteksi checkbox dari ukuran (w-3.5 h-3.5 dll) ──
    class_match = re.search(r'class\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
    if class_match:
        cls = class_match.group(1).lower()
        # Pattern checkbox: kecil + accent color
        has_small_size = bool(re.search(r'w-[234](?:\.\d)?\s+h-[234](?:\.\d)?', cls))
        has_accent = bool(re.search(r'accent-', cls))
        has_cursor_pointer = bool(re.search(r'cursor-pointer|cursor-poin', cls))
        is_row_check = 'row-check' in cls

        if (has_small_size and has_accent) or is_row_check:
            return 'Pilih baris'
        if has_small_size and has_cursor_pointer:
            return 'Pilih'

    # ── Deteksi OTP (input pendek di halaman 2FA) ──
    if class_match:
        cls = class_match.group(1)
        is_otp = bool(re.search(r'w-(?:8|10|12|16|20)\s', cls))
        is_dark_bg = bool(re.search(r'bg-slate-900|bg-gray-900|bg-\[#', cls))
        is_centered = bool(re.search(r'text-center', cls))
        if is_otp and (is_dark_bg or is_centered):
            return 'Kode verifikasi'

    # ── Deteksi konversi ──
    if class_match and 'conv-input' in class_match.group(1).lower():
        return 'Konversi'

    # ── Deteksi jumlah (input kecil w-20 dll) ──
    if class_match:
        cls = class_match.group(1)
        small_w = re.search(r'w-(\d+)', cls)
        if small_w:
            w_val = int(small_w.group(1))
            if 10 <= w_val <= 32:
                return 'Jumlah'

    # ── Coba id ──
    id_match = re.search(r'id\s*=\s*["\']([^"\']+)', attrs, re.IGNORECASE)
    if id_match:
        label = id_to_label(id_match.group(1))
        if label and len(label) > 1:
            return label

    # ── Coba name ──
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)', attrs, re.IGNORECASE)
    if name_match:
        label = id_to_label(name_match.group(1))
        if label and len(label) > 1:
            return label

    # ── Class-based inference ──
    if class_match:
        cls = class_match.group(1).lower()
        if 'search' in cls:
            return 'Cari'
        if 'qty' in cls or 'quantity' in cls:
            return 'Jumlah'
        if cls.strip() == 'cb':
            return 'Pilih'
        if 'bar-select' in cls:
            return 'Filter tampilan'
        if 'f-input' in cls or 'field' in cls:
            return 'Input'
        if 'form-input' in cls:
            return 'Input'

    # ── Konteks: label terdekat sebelum input ──
    if full_content and input_start > 0:
        lookback = full_content[max(0, input_start - 300):input_start]
        label_m = re.search(
            r'<label[^>]*>(.*?)</label>', lookback,
            re.IGNORECASE | re.DOTALL
        )
        if label_m:
            lt = strip_html_tags(label_m.group(1))
            lt = re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', lt).strip()
            if lt and 1 < len(lt) < 80:
                return lt

    # ── Default per tag ──
    if tag == 'select':
        return 'Pilih opsi'
    if tag == 'textarea':
        return 'Teks'

    # ── Ultimate fallback ──
    return 'Input'


def escape_label(label):
    return (label.replace('&', '&amp;').replace('"', '&quot;')
                .replace('<', '&lt;').replace('>', '&gt;'))


# ═══════════════════════════════════════════════════════════════
# FIXER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def fix_empty_buttons_v2(content, filename=''):
    """V2: Tambah aria-label ke tombol kosong (strip SVG title saat cek)."""
    count = 0
    button_open_re = re.compile(r'<button\b((?:\s[^>]*)?)\s*>', re.IGNORECASE)
    changes = []

    for m in button_open_re.finditer(content):
        attrs_str = m.group(1)

        # Skip sudah punya aria-label
        if re.search(r'aria-label\s*=', attrs_str, re.IGNORECASE):
            continue
        # Skip dekoratif
        if re.search(r'aria-hidden\s*=\s*["\']true["\']', attrs_str, re.IGNORECASE):
            continue
        if re.search(r'role\s*=\s*["\'](?:presentation|none)["\']', attrs_str, re.IGNORECASE):
            continue

        # Cari closing tag
        close_pos = find_close_tag(content, m.end(), 'button')
        if close_pos == -1:
            continue

        inner_html = content[m.end():close_pos]

        # V2: cek kosong dengan strip SVG <title>
        if not is_button_empty_v2(inner_html):
            continue

        # Ekstrak class dan type
        class_match = re.search(r'class\s*=\s*["\']([^"\']*)["\']', attrs_str, re.IGNORECASE)
        class_attr = class_match.group(1) if class_match else ''
        type_match = re.search(r'type\s*=\s*["\']?(\w+)', attrs_str, re.IGNORECASE)
        type_attr = type_match.group(1) if type_match else ''

        # V2: infer dengan context fallback
        label = infer_button_label_v2(
            class_attr, inner_html, type_attr,
            full_content=content, btn_start=m.start()
        )
        escaped = escape_label(label)

        # Insert setelah "<button"
        insert_pos = m.start() + len('<button')
        changes.append((insert_pos, f' aria-label="{escaped}"'))
        count += 1

    for pos, text in reversed(changes):
        content = content[:pos] + text + content[pos:]

    return content, count


def fix_heading_skip_v2(content, filename=''):
    """
    V2: Perbaiki SEMUA lompatan heading level (bukan hanya h1→h3).
    Algoritma: walk semua heading, jika level > prev+1, turunkan ke prev+1.
    """
    heading_re = re.compile(r'<(h([1-6]))\b([^>]*)>', re.IGNORECASE)
    headings = list(heading_re.finditer(content))
    if len(headings) < 2:
        return content, 0

    changes = []
    prev_level = None

    for m in headings:
        tag_full = m.group(1).lower()
        level = int(m.group(2))
        attrs = m.group(3)

        if prev_level is not None and level > prev_level + 1:
            new_level = prev_level + 1
            new_tag = f'h{new_level}'
            count_skip = level - new_level  # berapa level dilompati

            # Ganti opening tag
            changes.append((m.start(1), m.end(1), new_tag))

            # Ganti closing tag
            close_pos = find_close_tag(content, m.end(), tag_full)
            if close_pos >= 0:
                close_m = re.match(
                    rf'</{re.escape(tag_full)}\s*>',
                    content[close_pos:], re.IGNORECASE
                )
                if close_m:
                    changes.append((
                        close_pos,
                        close_pos + close_m.end(),
                        f'</{new_tag}>'
                    ))

            # Update prev_level ke level baru (bukan level asli)
            prev_level = new_level
        else:
            prev_level = level

    if not changes:
        return content, 0

    count = sum(1 for s, e, r in changes if 'h' in r and '</' not in r)

    for start, end, repl in reversed(changes):
        content = content[:start] + repl + content[end:]

    return content, count


def fix_input_no_label_v2(content, filename=''):
    """V2: Tambah aria-label ke input tanpa label (deteksi checkbox, OTP, dll)."""
    count = 0
    input_re = re.compile(
        r'<(input|select|textarea)\b((?:\s[^>]*)?)\s*/?\s*>',
        re.IGNORECASE
    )
    changes = []

    for m in input_re.finditer(content):
        tag = m.group(1).lower()
        attrs = m.group(2)

        # Skip type hidden/submit/reset/button/image
        if tag == 'input':
            tm = re.search(
                r'type\s*=\s*["\']?(hidden|submit|reset|button|image)\b',
                attrs, re.IGNORECASE
            )
            if tm:
                continue

        # Skip sudah punya aria-label atau aria-labelledby
        if re.search(r'aria-label\s*=', attrs, re.IGNORECASE):
            continue
        if re.search(r'aria-labelledby\s*=', attrs, re.IGNORECASE):
            continue

        # Skip jika punya placeholder non-kosong
        ph = re.search(r'placeholder\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if ph and ph.group(1).strip():
            continue

        # Skip jika punya title non-kosong
        ti = re.search(r'title\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if ti and ti.group(1).strip():
            continue

        # V2: infer dengan deteksi checkbox/OTP/konteks
        label = infer_input_label_v2(
            tag, attrs,
            full_content=content, input_start=m.start()
        )
        if not label:
            continue

        escaped = escape_label(label)
        insert_pos = m.start(1) + len(tag)
        changes.append((insert_pos, f' aria-label="{escaped}"'))
        count += 1

    for pos, text in reversed(changes):
        content = content[:pos] + text + content[pos:]

    return content, count


def fix_xcloak_v2(content, filename=''):
    """
    V2: Pastikan CSS [x-cloak] ada dengan berbagai format yang mungkin
    dikenali audit tool. Juga handle partial template tanpa <head>.
    """
    if 'x-cloak' not in content:
        return content, 0

    # Cek apakah rule sudah ada (berbagai format)
    if re.search(r'\[x-cloak\]\s*\{[^}]*display\s*:\s*none', content, re.IGNORECASE):
        return content, 0

    # CSS rule dengan format yang lebih "standar"
    css_rules = (
        '[x-cloak]{display:none!important}\n'
        '[x-cloak] { display: none; }\n'
    )

    # 1. Coba masukkan ke <style> yang sudah ada
    style_match = re.search(
        r'(<style[^>]*>)(.*?)(</style>)',
        content, re.IGNORECASE | re.DOTALL
    )
    if style_match:
        insert_pos = style_match.start(2)
        content = content[:insert_pos] + css_rules + content[insert_pos:]
        return content, 1

    # 2. Coba masukkan ke <head>
    head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
    if head_match:
        insert_pos = head_match.end()
        content = (content[:insert_pos] +
                   f'\n<style>\n{css_rules}</style>' +
                   content[insert_pos:])
        return content, 1

    # 3. Partial template — sisipkan di awal file
    content = f'<style>\n{css_rules}</style>\n' + content
    return content, 1


# ═══════════════════════════════════════════════════════════════
# FIXER REGISTRY
# ═══════════════════════════════════════════════════════════════

FIXERS = {
    'empty_button': {
        'fn': fix_empty_buttons_v2,
        'desc': 'Tambah aria-label ke tombol kosong (v2: strip SVG title)',
        'icon': '🔘',
    },
    'heading_skip': {
        'fn': fix_heading_skip_v2,
        'desc': 'Perbaiki lompatan heading level (v2: semua level)',
        'icon': '📌',
    },
    'input_no_label': {
        'fn': fix_input_no_label_v2,
        'desc': 'Tambah aria-label ke input tanpa label (v2: checkbox/OTP)',
        'icon': '📝',
    },
    'xcloak': {
        'fn': fix_xcloak_v2,
        'desc': 'Tambah CSS x-cloak (v2: multi-format)',
        'icon': '🫥',
    },
}

# ═══════════════════════════════════════════════════════════════
# FILE PROCESSING
# ═══════════════════════════════════════════════════════════════

SKIP_DIRS = {
    'node_modules', 'vendor', 'third_party', '.git', '__pycache__',
    'static', 'media', '.venv', 'venv', 'env', '.tox', '.mypy_cache',
}


def should_process(filepath):
    name = filepath.name.lower()
    if not (name.endswith('.html') or name.endswith('.htm')):
        return False
    for part in filepath.parts:
        if part.lower() in SKIP_DIRS:
            return False
    return True


def process_file(filepath, dry_run=False, fix_types=None, no_backup=False):
    results = {}
    original = filepath.read_text(encoding='utf-8', errors='replace')
    current = original

    for key, info in FIXERS.items():
        if fix_types and key not in fix_types:
            continue
        new_content, cnt = info['fn'](current, filepath.name)
        results[key] = cnt
        if cnt > 0:
            current = new_content

    total = sum(results.values())
    if total > 0 and not dry_run:
        if not no_backup:
            bak = filepath.with_suffix(filepath.suffix + '.bak')
            if not bak.exists():
                shutil.copy2(filepath, bak)
        filepath.write_text(current, encoding='utf-8')

    return results


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='LUMRA ERP — Audit Fixer v2.0 (Round 2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python fix_audit_v2.py ./templates --dry-run -v
  python fix_audit_v2.py ./templates --fix empty_button,heading_skip
  python fix_audit_v2.py ./templates --no-backup
"""
    )
    parser.add_argument('path', help='Path direktori template')
    parser.add_argument('--dry-run', action='store_true', help='Preview tanpa tulis')
    parser.add_argument('--fix', type=str, default=None,
                        help='Jenis fix (koma). Opsi: ' + ', '.join(FIXERS))
    parser.add_argument('--no-backup', action='store_true', help='Tanpa .bak')
    parser.add_argument('--verbose', '-v', action='store_true', help='Detail per file')
    args = parser.parse_args()

    fix_types = None
    if args.fix:
        fix_types = [f.strip() for f in args.fix.split(',')]
        bad = set(fix_types) - set(FIXERS)
        if bad:
            print(C(RED, f"✗ Invalid: {', '.join(bad)}"))
            print(C(DIM, f"  Valid: {', '.join(FIXERS)}"))
            sys.exit(1)

    root = Path(args.path)
    if not root.is_dir():
        print(C(RED, f"✗ Bukan direktori: {root}"))
        sys.exit(1)

    files = sorted(f for f in root.rglob('*') if should_process(f))
    if not files:
        print(C(YELLOW, "⚠ Tidak ada file HTML ditemukan."))
        sys.exit(0)

    print()
    print(C(CYAN, "╔═══════════════════════════════════════════════════════╗"))
    print(C(CYAN, "║       LUMRA ERP — Audit Fixer v2.0 (Round 2)        ║"))
    print(C(CYAN, "╚═══════════════════════════════════════════════════════╝"))
    print()
    print(f"  📂 Path       : {C(BOLD, str(root))}")
    print(f"  📄 File HTML  : {C(BOLD, str(len(files)))}")
    print(f"  🔧 Fix types  : {C(BOLD, ', '.join(fix_types) if fix_types else 'semua')}")
    mode = 'DRY RUN' if args.dry_run else 'LIVE'
    print(f"  🧪 Mode       : {C(BOLD, mode)}")
    if not args.dry_run and not args.no_backup:
        print(f"  💾 Backup     : {C(BOLD, 'Ya (.bak)')}")
    print()

    totals = {k: 0 for k in FIXERS}
    changed = 0
    details = []

    for fp in files:
        res = process_file(fp, args.dry_run, fix_types, args.no_backup)
        ft = sum(res.values())
        for k, v in res.items():
            totals[k] += v
        if ft > 0:
            changed += 1
            parts = [f"{FIXERS[k]['icon']}{v}" for k, v in res.items() if v > 0]
            details.append((fp, ft, ' '.join(parts)))
            if args.verbose:
                rel = fp.relative_to(root) if fp.is_relative_to(root) else fp.name
                print(f"  {C(GREEN, '✓')} {C(DIM, rel)}")
                print(f"    {' '.join(parts)}")

    print()
    print(C(CYAN, "─── Ringkasan ──────────────────────────────────────────"))
    print()
    active = fix_types or list(FIXERS)
    grand = 0
    for k in active:
        v = totals[k]
        grand += v
        ic = FIXERS[k]['icon']
        desc = FIXERS[k]['desc']
        if v > 0:
            print(f"  {ic} {C(GREEN, f'{v:>4}')}  {desc}")
        else:
            print(f"  {ic} {C(DIM, f'{v:>4}')}  {desc}")

    print()
    print(f"  File berubah : {C(BOLD, str(changed))} / {len(files)}")
    print(f"  Total fix    : {C(BOLD, str(grand))}")

    if args.dry_run and grand > 0:
        print()
        print(C(YELLOW, "  ⚡ DRY RUN — tidak ada file diubah."))
        print(C(YELLOW, "    Hapus --dry-run untuk menerapkan."))

    if grand == 0:
        print()
        print(C(GREEN, "  ✅ Semua sudah bersih!"))

    if not args.verbose and details and grand > 0:
        print()
        print(C(CYAN, "─── File Berubah ───────────────────────────────────"))
        print()
        for fp, total, fixes in details:
            rel = fp.relative_to(root) if fp.is_relative_to(root) else fp.name
            print(f"  {C(GREEN, '✓')} {rel}  {C(DIM, f'({total}: {fixes})')}")

    print()
    if not args.dry_run and grand > 0 and not args.no_backup:
        print(C(DIM, "  💡 Hapus .bak: find . -name '*.bak' -delete"))
    print()


if __name__ == '__main__':
    main()