"""
Custom exceptions for Amanzon e-commerce platform.

Provides specific exception types for better error handling and debugging.
"""


class AmanzonException(Exception):
    """Base exception for all Amanzon-related errors."""
    pass


class PaymentError(AmanzonException):
    """Raised when payment processing fails."""
    pass


class StockError(AmanzonException):
    """Raised when there are stock-related issues."""
    pass


class CouponError(AmanzonException):
    """Raised when coupon validation fails."""
    pass


class OrderError(AmanzonException):
    """Raised when order processing fails."""
    pass


class StorageError(AmanzonException):
    """Raised when file storage operations fail."""
    pass
