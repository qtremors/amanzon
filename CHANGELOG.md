# Changelog

All notable changes to Amanzon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial Django 5.x project setup with `uv` package manager
- Custom User model extending AbstractUser with profile picture, OTP, and email verification
- 12 database models: User, Category, SubCategory, Product, Cart, CartItem, Wishlist, Coupon, Order, OrderItem, Review, ContactMessage
- Full e-commerce feature set:
  - User authentication (login, register, password reset via email OTP)
  - Email verification for new accounts
  - Product catalog with categories, subcategories, search, and filters
  - Shopping cart with quantity management
  - Wishlist functionality (add/remove)
  - Razorpay payment integration
  - Order management with cancellation and refunds
  - Product reviews and ratings (1-5 stars)
  - Coupon/discount codes
  - Contact form
- Django admin configuration with custom admin classes
- Context processor for cart and wishlist counts in navbar
- Responsive Bootstrap 5 frontend with custom CSS
- 14 HTML templates with proper inheritance structure
- Environment variable support via python-dotenv
- Comprehensive test suite (57 tests across 5 test modules)
- Modular view architecture (`views/auth.py`, `shop.py`, `cart.py`, `orders.py`, `main.py`)
- Consolidated test package (`tests/test_general.py`, `test_verification.py`, `test_orders.py`, `test_security.py`, `test_session.py`)
- Rate limiting middleware for auth endpoints (5 req/min)
- Order cancellation with stock restoration and Razorpay refund initiation
- Payment flow tests with mocked Razorpay
- Database indexes on frequently queried fields (`Product.is_active`, `Product.price`, `Order.status`, `Order.created_at`)
- Image optimization on upload (auto-resize to 800x800, JPEG compression)

### Security
- Django's built-in password hashing
- CSRF protection on all forms
- Razorpay signature verification for payments
- OTP-based password reset with 10-minute expiry
- OTP generation uses `secrets` module for cryptographic security
- Rate limiting on login/register endpoints
- Session fixation protection
- HttpOnly session cookies

### Fixed
- Checkout flow bug - form no longer submits before Razorpay modal opens
- Login authentication - properly looks up user by email before authenticate
- OTP expiry calculation - uses `total_seconds()` instead of `seconds`
- Stock validation - prevents adding out-of-stock items to cart
- Homepage wishlist - featured products show correct wishlist status
- Currency format - standardized to ₹ symbol throughout
- Free shipping - conditional (free over ₹500, otherwise ₹50)
- Coupon lookup - case-insensitive
- Session cleanup - uses safe `pop()` method
- Shop template syntax - fixed split Django tags

### Technical
- HTTPS enforcement settings (auto-enabled when DEBUG=False)
- Order confirmation email on successful payment
- Remove coupon button in cart
- Modular view architecture for maintainability
- Service layer for business logic (`services.py`)

---

## [0.0.0] - 2024-XX-XX

### Removed (from old EShopper codebase)
- Plaintext password storage
- Hardcoded API keys
- Empty SECRET_KEY
- Duplicate template code
- Debug print statements
- N+1 query issues
