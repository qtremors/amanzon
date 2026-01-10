# Changelog

All notable changes to Amanzon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-10

### Added
- Supabase PostgreSQL integration for persistent database storage
- Supabase Storage backend for media files (profile pictures, product images)
- Custom Django storage backend (`store/storage.py`) for Supabase
- Demo mode for Razorpay (works without real API keys)

### Changed
- Migrated from SQLite to PostgreSQL via `dj-database-url`
- Media files now stored in Supabase Storage instead of local filesystem
- Updated `.env.example` with Supabase configuration variables
- Updated tech stack documentation

### Dependencies
- Added `dj-database-url>=3.1.0`
- Added `psycopg2-binary>=2.9.11`
- Added `supabase>=2.27.1`

## [1.0.0] - 2026-01-01

### Added
- Django 5.x project with `uv` package manager
- Custom User model with profile picture, OTP, and email verification
- 12 database models: User, Category, SubCategory, Product, Cart, CartItem, Wishlist, Coupon, CouponUsage, Order, OrderItem, Review, ContactMessage
- Product catalog with categories, subcategories, search, filtering, and sorting
- Shopping cart with quantity management
- Wishlist functionality
- Razorpay payment integration with signature verification
- Order management with cancellation and stock restoration
- Product reviews and ratings (1-5 stars)
- Coupon/discount code system with usage tracking
- Contact form
- User authentication (login, register, logout)
- Email verification for new accounts
- OTP-based password reset via email
- User profile management
- Rate limiting middleware for auth endpoints
- Django admin with custom admin classes
- Context processor for cart/wishlist counts
- Responsive Bootstrap 5 frontend
- Image optimization on upload (auto-resize, compression)
- Database indexes on frequently queried fields
- Comprehensive test suite (57 tests)
- Service layer architecture for business logic

### Security
- Django password hashing
- CSRF protection on all forms
- Razorpay signature verification
- OTP expiry (10 minutes) with cryptographic generation
- Rate limiting on login/register
- Session fixation protection
- HttpOnly session cookies
- HTTPS enforcement when DEBUG=False
