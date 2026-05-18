from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name='rupiah')
# TODO[C3-LONG]: 'rupiah' = 31 baris (max 30). Pecah: rupiah_validate(), rupiah_query(), rupiah_render()
# TODO[C3-LONG]: 'rupiah' terlalu panjang (31 baris). Pecah: rupiah_validate(), rupiah_build_context(), rupiah_render()
def rupiah(value, symbol=True):
    """Format number to Indonesian Rupiah style.
    Examples:
        1000000 -> Rp 1.000.000
        1234.5 -> Rp 1.234,50
    If symbol=False returns only the number string.
    """
    if value is None:
        return '-'
    try:
        d = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    # Separate integer and fractional parts
    sign = '-' if d < 0 else ''
    d = abs(d)
    int_part = int(d)
    frac = (d - int_part).quantize(Decimal('0.01'))
    frac_part = int((frac * 100) % 100)

    int_str = f"{int_part:,}".replace(',', '.')
    if frac_part:
        frac_str = f",{frac_part:02d}"
    else:
        frac_str = ''

    out = f"{sign}{int_str}{frac_str}"
    if symbol:
        return f"Rp {out}"
    return out
