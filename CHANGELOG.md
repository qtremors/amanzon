# Changelog

All notable changes to Amanzon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.5] - 2026-01-11

### Added
- Custom 404 and 500 error pages with branded design
- AddressInline in Django admin for user management
- Honeypot field in contact form for spam protection
- `loading="lazy"` on all product images for faster page loads
- Redis cache configuration note for production rate limiting
- `DEFAULT_COUNTRY` setting for configurable country default

### Changed
- Supabase client now uses lazy initialization (faster startup)
- `SupabaseStorage.size()` now returns actual file size from metadata
- Product image field made optional (`blank=True, null=True`)

### Fixed
- Open redirect vulnerabilities in cart and wishlist views
- Race condition in stock deduction using F() expressions
- OTP brute force vulnerability (5 attempts max)
- Cart handling in checkout using `get_or_create()`
- Email sending failures now handled gracefully
- Pagination now preserves all filter parameters
- Template syntax errors in shop.html
- Footer copyright duplication removed

### Security
- URL validation for all redirect URLs
- Contact form spam protection with honeypot
- Stock re-validation inside atomic transaction

## [1.2.0] - 2026-01-11

### Added
- **Saved Addresses Feature** - Users can save, edit, delete addresses in profile and select at checkout
- **Dark Mode Toggle** - Manual theme toggle (sun/moon icon) with localStorage persistence
- **Verification Token Expiry** - 24-hour expiry for email verification tokens
- **Custom Exception Classes** - `PaymentError`, `StockError`, `CouponError`, `OrderError`, `StorageError`
- **Template Tags** - `currency` filter and `alt_default` filter in `store_tags.py`
- Favicon redirect to prevent 404 errors
- ARIA labels on product card action buttons

### Changed
- Order cancellation now uses POST instead of GET (RESTful)
- Address auto-saved on first checkout for new users
- Checkout prefills from saved/default address
- Homepage featured products query optimized (no N+1 for ratings)
- Supabase Storage now used for both local and production environments
- Settings centralized `VERIFICATION_TOKEN_EXPIRY_HOURS` and `OTP_EXPIRY_SECONDS`

### Fixed
- Silent failures in image optimization now logged
- Silent deletion errors in Supabase Storage now logged
- Dead code and duplicate imports removed
- Duplicate comments in checkout template removed
- Form labels properly associated with inputs (accessibility)
- Missing Razorpay config in `.env.example`
- Template tag rendering issue in product cards

### Security
- Email verification tokens now expire after 24 hours

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
