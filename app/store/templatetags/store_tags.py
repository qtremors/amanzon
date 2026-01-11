"""
Custom template tags and filters for Amanzon.
"""

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def currency(value, symbol=None):
    """
    Format a number as currency with configurable symbol.
    
    Usage:
        {{ price|currency }}          -> ₹1,234.56
        {{ price|currency:"$" }}      -> $1,234.56
    """
    if value is None:
        return ""
    
    symbol = symbol or getattr(settings, 'CURRENCY_SYMBOL', '₹')
    
    try:
        # Format with thousand separators
        formatted = f"{float(value):,.2f}"
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def alt_default(value, default="Product image"):
    """
    Provide default alt text if value is empty.
    
    Usage:
        {{ product.name|alt_default:"Default description" }}
    """
    return value if value else default
