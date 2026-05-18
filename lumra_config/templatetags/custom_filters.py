# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0
@register.filter
def rupiah(value):
    """Format number as Indonesian Rupiah currency (Rp format)"""
    try:
        field_value = float(value)
        # Format with thousand separator using locale or manual formatting
        return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"


@register.filter
def sub(value, arg):
    """Subtract arg from value (value - arg)."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0