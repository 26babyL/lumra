#!/usr/bin/env python3
"""
LUMRA ERP — Audit Fixer Script v1.0
====================================
Memperbaiki semua isu dari laporan audit UI/UX secara otomatis.

Penggunaan:
    python fix_audit.py /path/to/templates
    python fix_audit.py /path/to/templates --dry-run
    python fix_audit.py /path/to/templates --fix empty_button,xcloak
    python fix_audit.py /path/to/templates --no-backup

Jenis perbaikan:
    empty_button     — Tambah aria-label ke tombol kosong (227 isu)
    xcloak           — Tambah CSS [x-cloak]{display:none} jika perlu
    heading_skip     — Perbaiki lompatan heading (h1→h3)
    table_no_header  — Tambah <thead> ke tabel tanpa header
    input_no_label   — Tambah aria-label ke input tanpa label
    form_no_action   — Tambah action ke form tanpa action
    scroll_nesting   — Perbaiki scroll nesting
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

# ═══════════════════════════════════════════════════════════════════
# WARNA TERMINAL
# ═══════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════
# KONFIGURASI & PEMETAAN
# ═══════════════════════════════════════════════════════════════════

# Pemetaan keyword class → aria-label (URUTAN PENTING: spesifik dulu)
CLASS_LABEL_RULES = [
    # ── Spesifik LUMRA ──
    (r'drawer-btn-approve|modal-btn-approve', 'Setujui'),
    (r'drawer-btn-reject|modal-btn-reject', 'Tolak'),
    (r'drawer-btn-secondary', 'Batal'),
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

    # ── Aksi umum ──
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
    (r'refresh|reload|\brefresh\b', 'Muat ulang'),
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

# Fallback berdasarkan warna class
COLOR_LABEL_RULES = [
    (r'rose-\d|red-\d|text-rose|text-red|bg-rose|bg-red', 'Hapus'),
    (r'emerald-\d|green-\d|text-emerald|text-green|bg-emerald|bg-green', 'Setujui'),
    (r'blue-\d|indigo-\d|text-blue|text-indigo|bg-blue|bg-indigo', 'Lihat'),
    (r'amber-\d|yellow-\d|orange-\d|text-amber|text-yellow', 'Peringatan'),
    (r'purple-\d|text-purple|bg-purple', 'Detail'),
]

# Pemetaan kata (ID/attr) → bahasa Indonesia (untuk input label)
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
    'schedule': 'Jadwal', 'supplier': 'Supplier', 'price': 'Harga',
    'confirm': 'Konfirmasi', 'delete': 'Hapus', 'campaign': 'Kampanye',
    'bar': 'Batang', 'select': 'Pilih', 'input': 'Masukan',
}

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def find_close_tag(html, after_open_pos, tag_name):
    """
    Cari posisi tag penutup yang sesuai dengan tag pembuka.
    after_open_pos: posisi setelah '>' dari tag pembuka.
    Mengembalikan posisi awal '</tag>' atau -1 jika tidak ditemukan.
    """
    depth = 1
    pos = after_open_pos
    tag_lower = tag_name.lower()
    open_re = re.compile(rf'<{re.escape(tag_name)}\b[^>]*>', re.IGNORECASE)
    close_re = re.compile(rf'</{re.escape(tag_name)}\s*>', re.IGNORECASE)

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
    """Hapus semua tag HTML dari teks."""
    return re.sub(r'<[^>]+>', '', text)


def is_button_empty(inner_html):
    """
    Cek apakah tombol kosong (tidak punya teks visible).
    Abaikan ikon SVG/<i> dan tag Django {{ }} / {% %}.
    """
    # Hapus semua tag HTML
    text = strip_html_tags(inner_html)
    # Hapus output Django (mereka menyediakan konten dinamis)
    text_no_django = re.sub(r'\{%.*?%\}|\{\{.*?\}\}', '', text)
    return text_no_django.strip() == ''


def infer_svg_label(inner_html):
    """Coba infer label dari ikon SVG di dalam tombol."""
    # Cek SVG dengan class
    svg_class_match = re.search(
        r'<svg[^>]*class=["\']([^"\']*)["\']', inner_html, re.IGNORECASE
    )
    if svg_class_match:
        svg_class = svg_class_match.group(1)
        for pattern, label in CLASS_LABEL_RULES:
            if re.search(pattern, svg_class, re.IGNORECASE):
                return label

    # Cek <title> di dalam SVG
    title_match = re.search(r'<title>([^<]+)</title>', inner_html, re.IGNORECASE)
    if title_match:
        title_text = title_match.group(1).strip()
        if title_text:
            return title_text

    # Cek elemen <i> dengan class ikon
    i_matches = re.finditer(
        r'<i[^>]*class=["\']([^"\']*)["\']', inner_html, re.IGNORECASE
    )
    for im in i_matches:
        i_class = im.group(1)
        for pattern, label in CLASS_LABEL_RULES:
            if re.search(pattern, i_class, re.IGNORECASE):
                return label

    # Cek class path/circle/rect di dalam SVG (heroicons pattern)
    path_class_match = re.search(
        r'<(?:path|circle|rect|line|polyline|polygon)[^>]*class=["\']([^"\']*)["\']',
        inner_html, re.IGNORECASE
    )
    if path_class_match:
        path_class = path_class_match.group(1)
        for pattern, label in CLASS_LABEL_RULES:
            if re.search(pattern, path_class, re.IGNORECASE):
                return label

    return None


def infer_button_label(class_attr, inner_html='', type_attr=''):
    """
    Infer aria-label dari class, inner HTML (ikon), dan type tombol.
    """
    cls = class_attr or ''

    # 1. Cek class patterns (spesifik → umum)
    for pattern, label in CLASS_LABEL_RULES:
        if re.search(pattern, cls, re.IGNORECASE):
            return label

    # 2. Cek ikon di inner HTML
    svg_label = infer_svg_label(inner_html)
    if svg_label:
        return svg_label

    # 3. Fallback warna
    for pattern, label in COLOR_LABEL_RULES:
        if re.search(pattern, cls, re.IGNORECASE):
            return label

    # 4. Fallback type
    type_lower = (type_attr or '').lower().strip()
    if type_lower == 'submit':
        return 'Kirim'
    if type_lower == 'reset':
        return 'Reset'
    if type_lower == 'button':
        return 'Tombol'

    # 5. Default
    return 'Tombol'


def id_to_label(id_str):
    """Konversi ID/nama attr menjadi label yang bisa dibaca."""
    if not id_str:
        return None

    # Hilangkan prefix umum
    cleaned = re.sub(r'^(edit|add|new|create|update|delete|set|get|search|filter)_', '', id_str, flags=re.IGNORECASE)
    # Ganti _ dan - dengan spasi
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
    # Kapitalisasi huruf pertama
    if result:
        result = result[0].upper() + result[1:]
    return result


def infer_input_label(tag, attrs):
    """Infer aria-label untuk input/select/textarea."""
    # Coba id
    id_match = re.search(r'id\s*=\s*["\']([^"\']+)', attrs, re.IGNORECASE)
    if id_match:
        label = id_to_label(id_match.group(1))
        if label and len(label) > 1:
            return label

    # Coba name
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)', attrs, re.IGNORECASE)
    if name_match:
        label = id_to_label(name_match.group(1))
        if label and len(label) > 1:
            return label

    # Coba class
    class_match = re.search(r'class\s*=\s*["\']([^"\']+)', attrs, re.IGNORECASE)
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

    # Default berdasarkan tag
    if tag == 'select':
        return 'Pilih opsi'
    if tag == 'textarea':
        return 'Teks'

    return None


def escape_label(label):
    """Escape karakter khusus untuk atribut HTML."""
    return label.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


# ═══════════════════════════════════════════════════════════════════
# FIXER FUNCTIONS
# Setiap fungsi menerima (content, filename) → (new_content, fix_count)
# ═══════════════════════════════════════════════════════════════════

def fix_empty_buttons(content, filename=''):
    """Tambah aria-label ke tombol tanpa teks/aria-label."""
    count = 0
    button_open_re = re.compile(r'<button\b((?:\s[^>]*)?)\s*>', re.IGNORECASE)
    changes = []  # (pos_insert, text_to_insert)

    for m in button_open_re.finditer(content):
        attrs_str = m.group(1)

        # Skip jika sudah punya aria-label
        if re.search(r'aria-label\s*=', attrs_str, re.IGNORECASE):
            continue

        # Skip jika aria-hidden="true" (dekoratif)
        if re.search(r'aria-hidden\s*=\s*["\']true["\']', attrs_str, re.IGNORECASE):
            continue

        # Skip jika role="presentation" atau role="none"
        if re.search(r'role\s*=\s*["\'](?:presentation|none)["\']', attrs_str, re.IGNORECASE):
            continue

        # Cari tag penutup
        close_pos = find_close_tag(content, m.end(), 'button')
        if close_pos == -1:
            continue

        inner_html = content[m.end():close_pos]

        # Cek apakah tombol kosong
        if not is_button_empty(inner_html):
            continue

        # Ekstrak class dan type
        class_match = re.search(r'class\s*=\s*["\']([^"\']*)["\']', attrs_str, re.IGNORECASE)
        class_attr = class_match.group(1) if class_match else ''
        type_match = re.search(r'type\s*=\s*["\']?(\w+)', attrs_str, re.IGNORECASE)
        type_attr = type_match.group(1) if type_match else ''

        # Infer label
        label = infer_button_label(class_attr, inner_html, type_attr)
        escaped = escape_label(label)

        # Insert aria-label setelah "<button"
        insert_pos = m.start() + len('<button')
        changes.append((insert_pos, f' aria-label="{escaped}"'))
        count += 1

    # Terapkan perubahan (dari belakang agar posisi tidak bergeser)
    for pos, text in reversed(changes):
        content = content[:pos] + text + content[pos:]

    return content, count


def fix_xcloak(content, filename=''):
    """Pastikan CSS [x-cloak]{display:none} ada jika x-cloak dipakai."""
    if 'x-cloak' not in content:
        return content, 0

    # Cek apakah rule CSS sudah ada
    if re.search(r'\[x-cloak\]\s*\{[^}]*display\s*:\s*none', content, re.IGNORECASE):
        return content, 0

    css_rule = '[x-cloak]{display:none!important}'

    # 1. Coba masukkan ke dalam <style> yang sudah ada
    style_match = re.search(r'(<style[^>]*>)(.*?)(</style>)', content, re.IGNORECASE | re.DOTALL)
    if style_match:
        insert_pos = style_match.start(2)
        existing = style_match.group(2)
        # Tambahkan di awal style yang sudah ada
        content = content[:insert_pos] + css_rule + '\n' + content[insert_pos:]
        return content, 1

    # 2. Coba masukkan ke dalam <head>
    head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
    if head_match:
        insert_pos = head_match.end()
        content = content[:insert_pos] + f'\n<style>{css_rule}</style>' + content[insert_pos:]
        return content, 1

    # 3. Masukkan di awal file (untuk partial template)
    content = f'<style>{css_rule}</style>\n' + content
    return content, 1


def fix_heading_skip(content, filename=''):
    """Perbaiki heading yang melompat (h1 → h3 tanpa h2)."""
    count = 0
    heading_re = re.compile(r'<(h[1-6])\b([^>]*)>', re.IGNORECASE)

    headings = list(heading_re.finditer(content))
    if not headings:
        return content, 0

    changes = []  # (start, end, replacement)
    last_h1_end = -1

    for idx, m in enumerate(headings):
        tag = m.group(1).lower()

        if tag == 'h1':
            last_h1_end = m.end()
            continue

        if tag == 'h3' and last_h1_end >= 0:
            # Cek apakah ada h2 di antara h1 terakhir dan h3 ini
            has_h2 = False
            for prev in headings[:idx]:
                if prev.end() > last_h1_end and prev.start() < m.start():
                    if prev.group(1).lower() == 'h2':
                        has_h2 = True
                        break

            if not has_h2:
                # Ganti opening tag h3 → h2
                changes.append((m.start(1), m.end(1), 'h2'))

                # Ganti closing tag </h3> → </h2>
                close_pos = find_close_tag(content, m.end(), 'h3')
                if close_pos >= 0:
                    close_m = re.match(r'</h3\s*>', content[close_pos:], re.IGNORECASE)
                    if close_m:
                        changes.append((
                            close_pos,
                            close_pos + close_m.end(),
                            '</h2>'
                        ))

                count += 1
                last_h1_end = -1  # Reset agar h3 berikutnya tidak otomatis diubah

        elif tag == 'h2':
            last_h1_end = -1  # Sudah ada h2, reset

    # Terapkan perubahan
    for start, end, repl in reversed(changes):
        content = content[:start] + repl + content[end:]

    return content, count


def fix_table_no_header(content, filename=''):
    """Tambah <thead> ke tabel yang tidak punya header."""
    count = 0
    pos = 0

    while pos < len(content):
        # Cari <table
        table_start = content.lower().find('<table', pos)
        if table_start == -1:
            break

        # Cari akhir tag pembuka
        gt_pos = content.find('>', table_start)
        if gt_pos == -1:
            break

        # Cari </table> yang sesuai
        table_close = find_close_tag(content, gt_pos + 1, 'table')
        if table_close == -1:
            pos = gt_pos + 1
            continue

        table_inner = content[gt_pos + 1:table_close]

        # Skip jika sudah ada <thead>
        if re.search(r'<thead', table_inner, re.IGNORECASE):
            pos = table_close + 8  # len('</table>')
            continue

        # Cari <tbody> jika ada
        tbody_match = re.search(r'<tbody[^>]*>', table_inner, re.IGNORECASE)
        if tbody_match:
            search_area = table_inner[tbody_match.end():]
            offset = tbody_match.end()
            tbody_close_match = re.search(r'</tbody\s*>', table_inner, re.IGNORECASE)
        else:
            search_area = table_inner
            offset = 0

        # Cari baris pertama
        first_row_re = re.compile(r'(<tr[^>]*>)(.*?)(</tr>)', re.IGNORECASE | re.DOTALL)
        first_row_m = first_row_re.search(search_area)
        if not first_row_m:
            pos = table_close + 8
            continue

        first_row = first_row_m.group(0)
        first_row_body = first_row_m.group(2)

        # Cek apakah baris pertama punya <td>
        if not re.search(r'<td\b', first_row_body, re.IGNORECASE):
            pos = table_close + 8
            continue

        # Pastikan ada minimal 2 baris (header + data)
        all_rows = re.findall(r'<tr[^>]*>', search_area, re.IGNORECASE)
        if len(all_rows) < 2:
            pos = table_close + 8
            continue

        # Konversi <td> → <th> di baris pertama
        new_first_row = re.sub(r'<td\b', '<th', first_row, flags=re.IGNORECASE)
        new_first_row = re.sub(r'</td\s*>', '</th>', new_first_row, flags=re.IGNORECASE)

        # Bangun thead
        thead_block = f'<thead>{new_first_row}</thead>'

        # Hapus baris pertama dari posisi aslinya
        abs_row_start = gt_pos + 1 + offset + first_row_m.start()
        abs_row_end = gt_pos + 1 + offset + first_row_m.end()

        content = content[:abs_row_start] + thead_block + content[abs_row_end:]
        count += 1

        # Update posisi
        pos = abs_row_start + len(thead_block) + 8

    return content, count


def fix_input_no_label(content, filename=''):
    """Tambah aria-label ke input/select/textarea tanpa label/placeholder."""
    count = 0
    input_re = re.compile(
        r'<(input|select|textarea)\b((?:\s[^>]*)?)\s*/?\s*>',
        re.IGNORECASE
    )
    changes = []  # (insert_pos, text_to_insert)

    for m in input_re.finditer(content):
        tag = m.group(1).lower()
        attrs = m.group(2)

        # Skip type hidden/submit/reset/button/image
        if tag == 'input':
            type_match = re.search(
                r'type\s*=\s*["\']?(hidden|submit|reset|button|image)\b',
                attrs, re.IGNORECASE
            )
            if type_match:
                continue

        # Skip jika sudah punya aria-label
        if re.search(r'aria-label\s*=', attrs, re.IGNORECASE):
            continue

        # Skip jika sudah punya aria-labelledby
        if re.search(r'aria-labelledby\s*=', attrs, re.IGNORECASE):
            continue

        # Skip jika punya placeholder yang tidak kosong
        ph_match = re.search(r'placeholder\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if ph_match and ph_match.group(1).strip():
            continue

        # Skip jika punya title yang tidak kosong
        title_match = re.search(r'title\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if title_match and title_match.group(1).strip():
            continue

        # Infer label
        label = infer_input_label(tag, attrs)
        if not label:
            continue

        escaped = escape_label(label)
        # Insert setelah nama tag
        insert_pos = m.start(1) + len(tag)
        changes.append((insert_pos, f' aria-label="{escaped}"'))
        count += 1

    for pos, text in reversed(changes):
        content = content[:pos] + text + content[pos:]

    return content, count


def fix_form_no_action(content, filename=''):
    """Tambah action="#" ke form tanpa action/submit handler."""
    count = 0
    form_re = re.compile(r'<form\b((?:\s[^>]*)?)\s*>', re.IGNORECASE)
    changes = []

    for m in form_re.finditer(content):
        attrs = m.group(1)

        # Skip jika sudah punya action
        if re.search(r'action\s*=', attrs, re.IGNORECASE):
            continue

        # Skip jika punya Alpine submit handler
        if re.search(r'@submit|x-data.*?submit|\.submit\(', attrs, re.IGNORECASE):
            continue

        # Skip jika punya onsubmit
        if re.search(r'onsubmit\s*=', attrs, re.IGNORECASE):
            continue

        # Insert action="#" sebelum '>'
        insert_pos = m.end() - 1
        changes.append((insert_pos, insert_pos, ' action="#"'))
        count += 1

    for start, end, repl in reversed(changes):
        content = content[:start] + repl + content[end:]

    return content, count


def fix_scroll_nesting(content, filename=''):
    """Perbaiki scroll nesting (overflow di dalam overflow)."""
    count = 0
    div_re = re.compile(r'<div\b((?:\s[^>]*)?)\s*>', re.IGNORECASE)
    class_overflow_re = re.compile(r'overflow[-xyz]?-\w+', re.IGNORECASE)
    style_overflow_re = re.compile(r'overflow[-xyz]*\s*:\s*(auto|scroll|overlay)', re.IGNORECASE)

    divs = list(div_re.finditer(content))
    if len(divs) < 2:
        return content, 0

    changes = []  # (abs_start, abs_end, new_attrs)

    for i, outer_m in enumerate(divs):
        outer_attrs = outer_m.group(1)

        # Cek apakah outer punya overflow
        has_outer = bool(style_overflow_re.search(outer_attrs))
        if not has_outer:
            has_outer = bool(class_overflow_re.search(outer_attrs))
        if not has_outer:
            continue

        # Cari closing div
        outer_close = find_close_tag(content, outer_m.end(), 'div')
        if outer_close == -1:
            continue

        outer_inner = content[outer_m.end():outer_close]

        # Cari inner div dengan overflow
        for inner_m in div_re.finditer(outer_inner):
            inner_attrs = inner_m.group(1)

            has_inner = bool(style_overflow_re.search(inner_attrs))
            if not has_inner:
                has_inner = bool(class_overflow_re.search(inner_attrs))
            if not has_inner:
                continue

            # Hapus class overflow dari inner
            new_attrs = class_overflow_re.sub('', inner_attrs)
            # Juga hapus dari style attribute jika ada
            new_attrs = style_overflow_re.sub('', new_attrs)
            # Bersihkan double spaces dan trailing space
            new_attrs = re.sub(r' {2,}', ' ', new_attrs)
            new_attrs = re.sub(r'\s+$', '', new_attrs)
            # Bersihkan empty style=""
            new_attrs = re.sub(r'style\s*=\s*["\']\s*["\']\s*', '', new_attrs)
            new_attrs = re.sub(r' {2,}', ' ', new_attrs)
            new_attrs = re.sub(r'\s+$', '', new_attrs)

            if new_attrs.strip() != inner_attrs.strip():
                abs_start = outer_m.end() + inner_m.start(1)
                abs_end = outer_m.end() + inner_m.end(1)
                changes.append((abs_start, abs_end, new_attrs))
                count += 1

    for start, end, repl in reversed(changes):
        content = content[:start] + repl + content[end:]

    return content, count


# ═══════════════════════════════════════════════════════════════════
# FIXER REGISTRY
# ═══════════════════════════════════════════════════════════════════

FIXERS = {
    'empty_button': {
        'fn': fix_empty_buttons,
        'desc': 'Tambah aria-label ke tombol kosong',
        'icon': '🔘',
    },
    'xcloak': {
        'fn': fix_xcloak,
        'desc': 'Tambah CSS [x-cloak]{display:none}',
        'icon': '🫥',
    },
    'heading_skip': {
        'fn': fix_heading_skip,
        'desc': 'Perbaiki lompatan heading level',
        'icon': '📌',
    },
    'table_no_header': {
        'fn': fix_table_no_header,
        'desc': 'Tambah <thead> ke tabel tanpa header',
        'icon': '📋',
    },
    'input_no_label': {
        'fn': fix_input_no_label,
        'desc': 'Tambah aria-label ke input tanpa label',
        'icon': '📝',
    },
    'form_no_action': {
        'fn': fix_form_no_action,
        'desc': 'Tambah action ke form tanpa action',
        'icon': '📄',
    },
    'scroll_nesting': {
        'fn': fix_scroll_nesting,
        'desc': 'Perbaiki scroll nesting',
        'icon': '🔄',
    },
}


# ═══════════════════════════════════════════════════════════════════
# FILE PROCESSING
# ═══════════════════════════════════════════════════════════════════

def should_process_file(filepath):
    """Cek apakah file layak diproses."""
    name = filepath.name.lower()
    # Skip non-HTML
    if not (name.endswith('.html') or name.endswith('.htm')):
        return False
    # Skip vendor/third-party
    parts = filepath.parts
    skip_dirs = {'node_modules', 'vendor', 'third_party', '.git', '__pycache__',
                 'static', 'media', '.venv', 'venv', 'env'}
    for part in parts:
        if part.lower() in skip_dirs:
            return False
    return True


def process_file(filepath, dry_run=False, fix_types=None, no_backup=False):
    """
    Proses satu file HTML. Mengembalikan dict hasil per fixer.
    """
    results = {}
    original = filepath.read_text(encoding='utf-8', errors='replace')
    current = original

    for fix_key, fix_info in FIXERS.items():
        if fix_types and fix_key not in fix_types:
            continue

        new_content, count = fix_info['fn'](current, filepath.name)
        results[fix_key] = count
        if count > 0:
            current = new_content

    total_fixes = sum(results.values())

    # Tulis file jika ada perubahan
    if total_fixes > 0 and not dry_run:
        # Backup
        if not no_backup:
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
            if not backup_path.exists():
                shutil.copy2(filepath, backup_path)

        filepath.write_text(current, encoding='utf-8')

    return results


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='LUMRA ERP — Audit Fixer: Perbaiki isu UI/UX secara otomatis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\nContoh:
  python fix_audit.py ./templates                    # Fix semua isu
  python fix_audit.py ./templates --dry-run           # Preview tanpa menulis
  python fix_audit.py ./templates --fix empty_button  # Fix hanya empty button
  python fix_audit.py ./templates --fix empty_button,xcloak,heading_skip
  python fix_audit.py ./templates --no-backup         # Tanpa file backup
"""
    )

    parser.add_argument(
        'path',
        type=str,
        help='Path ke direktori template HTML'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Tampilkan perubahan tanpa menulis file'
    )
    parser.add_argument(
        '--fix',
        type=str,
        default=None,
        help='Pilih jenis fix (pisah koma). Kosongkan = semua. '
             'Opsi: ' + ', '.join(FIXERS.keys())
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Jangan buat file .bak'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Tampilkan detail per file'
    )

    args = parser.parse_args()

    # Parse fix types
    fix_types = None
    if args.fix:
        fix_types = [f.strip() for f in args.fix.split(',')]
        invalid = set(fix_types) - set(FIXERS.keys())
        if invalid:
            print(C(RED, f"✗ Fix type tidak valid: {', '.join(invalid)}"))
            print(C(DIM, f"  Opsi valid: {', '.join(FIXERS.keys())}"))
            sys.exit(1)

    # Validasi path
    root_path = Path(args.path)
    if not root_path.exists():
        print(C(RED, f"✗ Path tidak ditemukan: {root_path}"))
        sys.exit(1)
    if not root_path.is_dir():
        print(C(RED, f"✗ Bukan direktori: {root_path}"))
        sys.exit(1)

    # Kumpulkan file HTML
    html_files = sorted(
        f for f in root_path.rglob('*')
        if should_process_file(f)
    )

    if not html_files:
        print(C(YELLOW, "⚠ Tidak ada file HTML ditemukan di path tersebut."))
        sys.exit(0)

    # Header
    print()
    print(C(CYAN, "╔══════════════════════════════════════════════════════════╗"))
    print(C(CYAN, "║        LUMRA ERP — Audit Fixer Script v1.0             ║"))
    print(C(CYAN, "╚══════════════════════════════════════════════════════════╝"))
    print()
    print(f"  📂 Path       : {C(BOLD, str(root_path))}")
    print(f"  📄 File HTML  : {C(BOLD, str(len(html_files)))}")
    print(f"  🔧 Fix types  : {C(BOLD, ', '.join(fix_types) if fix_types else 'semua')}")
    print(f"  🧪 Mode       : {C(BOLD, 'DRY RUN (preview)' if args.dry_run else 'LIVE (menulis file)')}")
    if not args.dry_run and not args.no_backup:
        print(f"  💾 Backup     : {C(BOLD, 'Ya (.bak)')}")
    print()

    # Proses setiap file
    totals = {k: 0 for k in FIXERS.keys()}
    files_changed = 0
    file_details = []

    for filepath in html_files:
        results = process_file(
            filepath,
            dry_run=args.dry_run,
            fix_types=fix_types,
            no_backup=args.no_backup
        )

        file_total = sum(results.values())
        for k, v in results.items():
            totals[k] += v

        if file_total > 0:
            files_changed += 1
            detail_parts = []
            for k, v in results.items():
                if v > 0 and (fix_types is None or k in fix_types):
                    detail_parts.append(f"{FIXERS[k]['icon']}{v}")
            file_details.append((filepath, file_total, ' '.join(detail_parts)))

            if args.verbose:
                rel = filepath.relative_to(root_path) if filepath.is_relative_to(root_path) else filepath.name
                fixes_str = ' '.join(detail_parts)
                print(f"  {C(GREEN, '✓')} {C(DIM, rel)}")
                print(f"    {fixes_str}")

    # Summary
    print()
    print(C(CYAN, "─── Ringkasan Perbaikan ─────────────────────────────────"))
    print()

    active_fixers = fix_types or list(FIXERS.keys())
    grand_total = 0
    for k in active_fixers:
        v = totals[k]
        grand_total += v
        icon = FIXERS[k]['icon']
        desc = FIXERS[k]['desc']
        if v > 0:
            print(f"  {icon} {C(GREEN, f'{v:>4}')}  {desc}")
        else:
            print(f"  {icon} {C(DIM, f'{v:>4}')}  {desc}")

    print()
    print(f"  File berubah : {C(BOLD, str(files_changed))} / {len(html_files)}")
    print(f"  Total fix    : {C(BOLD, str(grand_total))}")

    if args.dry_run and grand_total > 0:
        print()
        print(C(YELLOW, "  ⚡ Mode DRY RUN — tidak ada file yang diubah."))
        print(C(YELLOW, "    Hapus --dry-run untuk menerapkan perbaikan."))

    if grand_total == 0:
        print()
        print(C(GREEN, "  ✅ Semua file sudah bersih! Tidak ada perbaikan diperlukan."))

    # Detail per file (jika tidak verbose tapi ada perubahan)
    if not args.verbose and file_details and grand_total > 0:
        print()
        print(C(CYAN, "─── File yang Berubah ─────────────────────────────────"))
        print()
        for filepath, total, fixes_str in file_details:
            rel = filepath.relative_to(root_path) if filepath.is_relative_to(root_path) else filepath.name
            print(f"  {C(GREEN, '✓')} {rel}  {C(DIM, f'({total} fix: {fixes_str})')}")

    print()
    if not args.dry_run and grand_total > 0 and not args.no_backup:
        print(C(DIM, "  💡 File backup (.bak) tersimpan. Hapus dengan:"))
        print(C(DIM, "     find . -name '*.bak' -delete"))

    print()


if __name__ == '__main__':
    main()