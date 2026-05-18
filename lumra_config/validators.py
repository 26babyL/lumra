"""
Validators for Accounting Precision (ISO 20022 Compliance)

Ensures all financial data maintains proper decimal precision as required
by Indonesian accounting standards and international compliance.

Configuration in settings.py:
    ACCOUNTING_PRECISION = {
        'MAX_DIGITS': 18,
        'DECIMAL_PLACES': 2,
        'ROUNDING_MODE': ROUND_HALF_UP,
    }

Usage in models:
    from lumra_config.validators import validate_decimal_precision
    
    class Invoice(models.Model):
        total = models.DecimalField(
            max_digits=18,
            decimal_places=2,
            validators=[validate_decimal_precision]
        )
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def validate_decimal_precision(value, max_digits=18, decimal_places=2):
    """
    Validate decimal field meets accounting precision requirements.
    
    ISO 20022 compliance validator for financial calculations.
    
    Args:
        value: Decimal value to validate
        max_digits: Maximum total digits (default 18)
        decimal_places: Maximum decimal places (default 2)
    
    Raises:
        ValidationError: If precision exceeds limits
    """
    try:
        # Convert to Decimal for precision handling
        if isinstance(value, str):
            d = Decimal(value)
        elif isinstance(value, (int, float)):
            d = Decimal(str(value))
        else:
            d = value
        
        # Check if value is None or 0
        if d is None or d == 0:
            return
        
        # Extract sign, digits, and exponent
        sign, digits, exponent = d.as_tuple()
        
        # Calculate actual precision
        num_integer_digits = len(digits) + exponent
        num_decimal_digits = -exponent if exponent < 0 else 0
        total_digits = len(digits)
        
        # Validate decimal places
        if num_decimal_digits > decimal_places:
            raise ValidationError(
                f'Maximum {decimal_places} decimal places allowed. '
                f'Got {num_decimal_digits} decimal places.'
            )
        
        # Validate total digits
        if total_digits > max_digits:
            raise ValidationError(
                f'Maximum {max_digits} total digits allowed. '
                f'Got {total_digits} digits.'
            )
    
    except (InvalidOperation, TypeError, ValueError) as e:
        raise ValidationError(f'Invalid decimal value: {str(e)}')


def round_accounting_value(value, decimal_places=2, rounding_mode=None):
    """
    Round a decimal value according to accounting standards.
    
    Uses ROUND_HALF_UP by default (banker's rounding).
    
    Args:
        value: Decimal value to round
        decimal_places: Decimal places to round to
        rounding_mode: Rounding mode (default ROUND_HALF_UP)
    
    Returns:
        Rounded Decimal value
    """
    if rounding_mode is None:
        rounding_mode = getattr(
            settings,
            'ACCOUNTING_PRECISION',
            {}
        ).get('ROUNDING_MODE', ROUND_HALF_UP)
    
    try:
        d = Decimal(str(value))
        quantize_exp = Decimal(10) ** -decimal_places
        return d.quantize(quantize_exp, rounding_mode=rounding_mode)
    except (InvalidOperation, TypeError) as e:
        logger.error(f"Error rounding accounting value: {e}")
        raise


def validate_positive_amount(value):
    """
    Validate that amount is positive.
    
    Usage:
        validators=[validate_positive_amount]
    """
    try:
        d = Decimal(str(value))
        if d <= 0:
            raise ValidationError('Amount must be greater than zero.')
    except (InvalidOperation, TypeError):
        raise ValidationError('Invalid amount.')


def validate_currency_amount(value):
    """
    Validate amount is suitable for currency (2 decimal places, positive).
    
    Usage:
        validators=[validate_currency_amount]
    """
    try:
        d = Decimal(str(value))
        
        # Must be positive
        if d < 0:
            raise ValidationError('Amount cannot be negative.')
        
        # Must have at most 2 decimal places
        sign, digits, exponent = d.as_tuple()
        if exponent < -2:
            raise ValidationError(
                'Currency amounts must have at most 2 decimal places.'
            )
    
    except (InvalidOperation, TypeError):
        raise ValidationError('Invalid currency amount.')


def validate_percentage(value):
    """
    Validate percentage value (0-100).
    
    Usage:
        validators=[validate_percentage]
    """
    try:
        d = Decimal(str(value))
        if d < 0 or d > 100:
            raise ValidationError('Percentage must be between 0 and 100.')
    except (InvalidOperation, TypeError):
        raise ValidationError('Invalid percentage.')


def validate_tax_rate(value):
    """
    Validate tax rate (typically 0-100%).
    
    Usage:
        validators=[validate_tax_rate]
    """
    try:
        d = Decimal(str(value))
        if d < 0 or d > 100:
            raise ValidationError('Tax rate must be between 0% and 100%.')
        
        # Check decimal places for tax rates (usually 4 places for precision)
        sign, digits, exponent = d.as_tuple()
        if exponent < -4:
            raise ValidationError(
                'Tax rates must have at most 4 decimal places.'
            )
    
    except (InvalidOperation, TypeError):
        raise ValidationError('Invalid tax rate.')


# ============ CALCULATION UTILITIES ============

def calculate_with_tax(amount, tax_rate):
    """
    Calculate amount with tax applied.
    
    Uses proper decimal arithmetic to avoid floating-point errors.
    
    Args:
        amount: Decimal amount
        tax_rate: Tax rate as decimal (e.g., Decimal('0.10') for 10%)
    
    Returns:
        Tuple: (amount_with_tax, tax_amount)
    """
    try:
        amount_d = Decimal(str(amount))
        rate_d = Decimal(str(tax_rate))
        
        # Validate inputs
        validate_decimal_precision(amount_d)
        validate_decimal_precision(rate_d)
        
        # Calculate tax
        tax_amount = amount_d * rate_d
        tax_amount = round_accounting_value(tax_amount)
        
        # Calculate total
        total = amount_d + tax_amount
        total = round_accounting_value(total)
        
        return total, tax_amount
    
    except Exception as e:
        logger.error(f"Error calculating with tax: {e}")
        raise


def calculate_discount_amount(amount, discount_percent):
    """
    Calculate discount amount from percentage.
    
    Args:
        amount: Original amount
        discount_percent: Discount percentage (e.g., 10 for 10%)
    
    Returns:
        Tuple: (discounted_amount, discount_amount)
    """
    try:
        amount_d = Decimal(str(amount))
        discount_pct = Decimal(str(discount_percent)) / 100
        
        discount_amount = amount_d * discount_pct
        discount_amount = round_accounting_value(discount_amount)
        
        discounted = amount_d - discount_amount
        discounted = round_accounting_value(discounted)
        
        return discounted, discount_amount
    
    except Exception as e:
        logger.error(f"Error calculating discount: {e}")
        raise


def calculate_margin(cost, selling_price):
    """
    Calculate profit margin.
    
    Args:
        cost: Cost amount
        selling_price: Selling price amount
    
    Returns:
        Margin percentage
    """
    try:
        cost_d = Decimal(str(cost))
        price_d = Decimal(str(selling_price))
        
        if cost_d == 0:
            return Decimal('0')
        
        profit = price_d - cost_d
        margin = (profit / price_d) * 100
        
        return round_accounting_value(margin, decimal_places=2)
    
    except (InvalidOperation, TypeError) as e:
        logger.error(f"Error calculating margin: {e}")
        return Decimal('0')


def format_currency(value, currency='IDR'):
    """
    Format decimal value as currency string.
    
    Args:
        value: Decimal value
        currency: Currency code (default 'IDR')
    
    Returns:
        Formatted string like 'IDR 1,234,567.89'
    """
    try:
        d = Decimal(str(value))
        formatted = '{:,.2f}'.format(d)
        return f'{currency} {formatted}'
    except Exception as e:
        logger.error(f"Error formatting currency: {e}")
        return f'{currency} 0.00'
