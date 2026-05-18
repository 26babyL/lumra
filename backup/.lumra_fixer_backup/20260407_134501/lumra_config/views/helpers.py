# lumra_config/views/helpers.py
# Helper functions yang digunakan di berbagai view module

from django.utils import timezone
from datetime import datetime, timedelta


# ════════════════════════════════════════════════════
# DATE HELPERS
# ════════════════════════════════════════════════════

def parse_date_aware(date_str, time_type='start'):
    """
    Parse a date string (YYYY-MM-DD format) as a timezone-aware datetime.
    time_type: 'start' for beginning of day (00:00:00), 'end' for end of day (23:59:59)
    """
    try:
        naive_dt = datetime.strptime(date_str, '%Y-%m-%d')
        if time_type == 'end':
            naive_dt = naive_dt.replace(hour=23, minute=59, second=59)
        return timezone.make_aware(naive_dt, timezone.get_current_timezone())
    except (ValueError, TypeError):
        now = timezone.now()
        return now if time_type == 'start' else now.replace(hour=23, minute=59, second=59)


# ════════════════════════════════════════════════════
# DEFENSIVE FIELD ACCESS
# ════════════════════════════════════════════════════

def safe_get(obj, *attrs, default='—'):
    """
    Safely traverse chained attributes — tidak crash meski field belum ada
    di model, relasi None, atau atribut tidak terdefinisi.

    Contoh:
        safe_get(item.order, 'location', 'name')     → '—' kalau location None
        safe_get(item.order, 'payment_method')        → '—' kalau field belum ada
        safe_get(item, 'variant', 'product', 'name') → nama produk kalau ada
        safe_get(None, 'anything')                    → '—'
    """
    if obj is None:
        return default
    for attr in attrs:
        try:
            model_instance = getattr(obj, attr)
            if obj is None:
                return default
        except AttributeError:
            return default
    return obj if obj is not None else default


def safe_related(obj, *attrs, default=None):
    """
    Seperti safe_get tapi default-nya None — berguna untuk kondisi
    boolean di view (bukan display string).

        if safe_related(item.order, 'location'):
            ...
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    """
    if obj is None:
        return default
    for attr in attrs:
        try:
            obj = getattr(obj, attr)
            if obj is None:
                return default
        except AttributeError:
            return default
    return obj


def model_has_field(model_class, field_name):
    """
    Cek apakah sebuah model punya field tertentu — berguna sebelum
    melakukan select_related atau filter agar tidak crash.

        if model_has_field(Order, 'location'):
            qs = qs.select_related('order__location')
    """
    try:
        model_class._meta.get_field(field_name)
        return True
    except Exception:
        return False


def safe_select_related(qs, *fields):
    """
    Hanya tambahkan field ke select_related kalau field-nya benar-benar
    ada di model — tidak crash meski field belum ditambahkan ke model.

        qs = safe_select_related(qs, 'order__location', 'order__cashier')
    """
    from django.db.models.query import QuerySet
    if not isinstance(qs, QuerySet):
        return qs

    model = qs.model
    valid = []
    for field_path in fields:
        parts  = field_path.split('__')
        cur    = model
        ok     = True
        for part in parts:
            try:
                field = cur._meta.get_field(part)
                # Kalau ada related model, lanjut traverse
                cur = getattr(field, 'related_model', None) or cur
            except Exception:
                ok = False
                break
        if ok:
            valid.append(field_path)

    return qs.select_related(*valid) if valid else qs


# ════════════════════════════════════════════════════
# CURRENCY FORMATTING
# ════════════════════════════════════════════════════

def smart_currency_format(value):
    """
    Smart currency formatting yang auto-select unit (T/Md/Jt/Rb).
    Contoh: Rp 4.7Md (milyar) bukan 4.700Jt
    """
    try:
        val = float(value) if value else 0
        if val == 0:
            return "Rp 0"
        abs_val = abs(val)
        if abs_val >= 1_000_000_000_000:
            return f"Rp {val/1_000_000_000_000:.1f}T"
        elif abs_val >= 1_000_000_000:
            return f"Rp {val/1_000_000_000:.1f}Md"
        elif abs_val >= 1_000_000:
            fv = val / 1_000_000
            if abs_val >= 100_000_000:
                return f"Rp {fv:,.0f}Jt"
            return f"Rp {fv:.1f}Jt"
        elif abs_val >= 1_000:
            return f"Rp {val/1_000:,.0f}Rb"
        else:
            return f"Rp {val:,.0f}"
    except Exception:
        return "Rp 0"


def safe_percent_format(value, decimal_places=1):
    """Safely format percentage values."""
    try:
        val = float(value) if value else 0
        return f"{val:.{decimal_places}f}%" if val > 0 else "0%"
    except Exception:
        return "0%"


# ════════════════════════════════════════════════════
# EMPTY / ERROR CONTEXT
# ════════════════════════════════════════════════════

def get_empty_message():
    return "Data tidak ditemukan"


def check_queryset_empty(queryset):
    """Returns (is_empty, message)."""
    try:
        if not queryset.exists():
            return True, get_empty_message()
        return False, None
    except Exception:
        return True, get_empty_message()


def create_empty_context(title, message=None):
    return {
        "report_title" : title,
        "message"      : message or get_empty_message(),
        "is_empty"     : True,
        "data"         : [],
        "object_list"  : [],
    }


def create_error_context(title, error_message):
    return {
        "report_title" : title,
        "error"        : error_message,
        "is_error"     : True,
        "data"         : [],
    }