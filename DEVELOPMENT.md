# Amanzon - Developer Documentation

> Comprehensive documentation for developers working on the Amanzon e-commerce platform.

**Version:** 1.3.0 | **Last Updated:** 2026-01-11

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Routes](#api-routes)
- [Environment Variables](#environment-variables)
- [Configuration](#configuration)
- [Services Layer](#services-layer)
- [Custom Components](#custom-components)
- [Testing](#testing)
- [Deployment](#deployment)
- [Management Commands](#management-commands)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Architecture Overview

Amanzon follows a **service-layer architecture** that separates business logic from views:

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                              │
│              Bootstrap 5 + Vanilla JS + Templates             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                          VIEWS                                │
│        shop.py │ cart.py │ orders.py │ auth.py │ main.py     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      SERVICES LAYER                           │
│    services.py - Business logic, calculations, validation     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                         MODELS                                │
│           14 Django models with PostgreSQL backend            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                          │
│         Supabase (DB + Storage) │ Razorpay │ Gmail SMTP       │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Service Layer | Keeps views thin, centralizes business logic for testing |
| Custom Storage Backend | Enables Supabase Storage integration with Django's file handling |
| Lazy Supabase Client | Faster app startup by deferring client initialization |
| F() Expressions for Stock | Prevents race conditions in concurrent stock updates |
| Custom Exceptions | Clear error handling with specific exception types |

---

## Project Structure

```
amanzon/
├── README.md                 # User-facing documentation
├── DEVELOPMENT.md            # This file
├── CHANGELOG.md              # Version history
├── LICENSE.md                # License terms
├── TASKS.md                  # Task tracking
├── .gitignore
│
└── app/                      # Django application root
    ├── manage.py             # Django CLI
    ├── pyproject.toml        # Dependencies (uv)
    ├── requirements.txt      # Dependencies (pip fallback)
    ├── .env.example          # Environment template
    │
    ├── amanzon/              # Django project settings
    │   ├── settings.py       # Configuration (259 lines)
    │   ├── urls.py           # Root URL routing
    │   ├── wsgi.py           # WSGI application
    │   └── asgi.py           # ASGI application
    │
    ├── store/                # Main Django app
    │   ├── models.py         # 14 database models
    │   ├── services.py       # Business logic layer
    │   ├── forms.py          # 8 form classes
    │   ├── admin.py          # Django admin config
    │   ├── urls.py           # App URL routing
    │   ├── middleware.py     # Rate limiting
    │   ├── storage.py        # Supabase storage backend
    │   ├── exceptions.py     # Custom exceptions
    │   ├── context_processors.py  # Cart/wishlist counts
    │   │
    │   ├── views/            # View modules
    │   │   ├── shop.py       # Homepage, shop, products, wishlist
    │   │   ├── cart.py       # Cart operations
    │   │   ├── orders.py     # Checkout, payments, order history
    │   │   ├── auth.py       # Login, register, profile, addresses
    │   │   └── main.py       # Contact page
    │   │
    │   ├── templatetags/
    │   │   └── store_tags.py # Custom filters (currency, alt_default)
    │   │
    │   ├── management/commands/
    │   │   ├── seed_products.py    # Seed sample data
    │   │   ├── create_superuser.py # Create admin from env
    │   │   └── migrate_media.py    # Migrate to Supabase Storage
    │   │
    │   ├── tests/            # Test suite (57+ tests)
    │   │   ├── test_general.py      # Models, views, forms
    │   │   ├── test_orders.py       # Order flow
    │   │   ├── test_security.py     # Rate limiting
    │   │   ├── test_verification.py # Email verification
    │   │   ├── test_session.py      # Session security
    │   │   └── test_email_settings.py
    │   │
    │   └── migrations/       # Database migrations
    │
    ├── templates/            # HTML templates
    │   ├── base.html         # Base template with navbar/footer
    │   ├── 404.html          # Custom error page
    │   ├── 500.html          # Custom error page
    │   ├── auth/             # Authentication templates (5)
    │   └── store/            # Store templates (12)
    │
    ├── static/
    │   ├── css/style.css     # Custom styles (598 lines)
    │   ├── img/              # Images
    │   └── robots.txt        # SEO
    │
    └── media/                # User uploads (local dev only)
```

---

## Database Schema

### Models Overview (14 total)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **User** | Extended AbstractUser | `profile_picture`, `otp`, `verification_token` |
| **Address** | Saved shipping addresses | `label`, `is_default`, address fields |
| **Category** | Product categories | `name`, `slug` |
| **SubCategory** | Nested categories | `category` FK, `name`, `slug` |
| **Product** | Products | `price`, `original_price`, `stock`, `image` |
| **Cart** | User's shopping cart | OneToOne with User |
| **CartItem** | Cart line items | `cart` FK, `product` FK, `quantity` |
| **Wishlist** | Wishlist items | `user` FK, `product` FK |
| **Coupon** | Discount coupons | `code`, `discount_percent`, `valid_from/to` |
| **CouponUsage** | Tracks coupon usage | Prevents reuse per user |
| **Order** | Customer orders | Billing details, Razorpay IDs, `status` |
| **OrderItem** | Order line items | `product_name` (preserved if deleted) |
| **Review** | Product reviews | `rating` (1-5), `comment` |
| **ContactMessage** | Contact submissions | `name`, `email`, `subject`, `message` |

### Relationships Diagram

```
User ─────┬──── 1:1 ──── Cart ──────── 1:N ──── CartItem ──── N:1 ──── Product
          │                                                              │
          ├──── 1:N ──── Address                                         │
          │                                                              │
          ├──── 1:N ──── Wishlist ──────────────────── N:1 ──────────────┤
          │                                                              │
          ├──── 1:N ──── Order ─────── 1:N ──── OrderItem ─── N:1 ───────┤
          │                                                              │
          ├──── 1:N ──── Review ────────────────────── N:1 ──────────────┤
          │                                                              │
          └──── 1:N ──── CouponUsage ─── N:1 ──── Coupon                 │
                                                                         │
Category ──── 1:N ──── SubCategory ──── 1:N ─────────────────────────────┘
```

### Model Properties

**Product:**
- `average_rating` - Computed from reviews (rounded to 1 decimal)
- `discount_percent` - Calculated from `original_price` and `price`

**Cart:**
- `total_items` - Sum of all item quantities
- `subtotal` - Sum of all item totals

---

## API Routes

### Shop & Products

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `/` | `shop.index` | Homepage with featured products |
| GET | `/shop/` | `shop.shop` | Shop page with filtering |
| GET | `/shop/<category_slug>/` | `shop.shop` | Filter by category |
| GET | `/product/<slug>/` | `shop.product_detail` | Product detail page |
| GET | `/wishlist/` | `shop.wishlist` | User's wishlist |
| GET | `/product/<id>/wishlist/` | `shop.toggle_wishlist` | Add/remove from wishlist |
| POST | `/product/<id>/review/` | `shop.add_review` | Submit product review |

### Cart

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | `/cart/` | `cart.cart` | Shopping cart page |
| GET | `/cart/add/<id>/` | `cart.add_to_cart` | Add product to cart |
| POST | `/cart/update/<id>/` | `cart.update_cart` | Update quantity |
| GET | `/cart/remove/<id>/` | `cart.remove_from_cart` | Remove from cart |
| POST | `/cart/apply-coupon/` | `cart.apply_coupon` | Apply coupon code |
| GET | `/cart/remove-coupon/` | `cart.remove_coupon` | Remove coupon |

### Orders & Checkout

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET/POST | `/checkout/` | `orders.checkout` | Checkout page |
| POST | `/payment-callback/` | `orders.payment_callback` | Razorpay callback |
| GET | `/orders/` | `orders.orders` | Order history |
| GET | `/orders/<id>/` | `orders.order_detail` | Order details |
| POST | `/orders/<id>/cancel/` | `orders.cancel_order` | Cancel order |

### Authentication

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET/POST | `/login/` | `auth.login_view` | Login page |
| GET | `/logout/` | `auth.logout_view` | Logout |
| GET/POST | `/register/` | `auth.register` | Registration |
| GET | `/register/verification-sent/` | `auth.verification_sent` | Verification pending |
| GET | `/verify-email/<token>/` | `auth.verify_email` | Verify email |
| GET/POST | `/profile/` | `auth.profile` | Profile settings |
| GET/POST | `/password-reset/` | `auth.password_reset` | Request OTP |
| GET/POST | `/password-reset/confirm/` | `auth.password_reset_confirm` | Reset password |

### Address Management

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET/POST | `/address/add/` | `auth.add_address` | Add address |
| GET/POST | `/address/<id>/edit/` | `auth.edit_address` | Edit address |
| POST | `/address/<id>/delete/` | `auth.delete_address` | Delete address |
| POST | `/address/<id>/set-default/` | `auth.set_default_address` | Set as default |

### Other

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET/POST | `/contact/` | `main.contact` | Contact page |
| GET | `/admin/` | Django Admin | Admin panel |

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |

### Supabase Storage

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key | `eyJhbGci...` |
| `SUPABASE_BUCKET` | Storage bucket name | `media` |

### Email (Gmail SMTP)

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_HOST_USER` | Gmail address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | App password | `xxxx-xxxx-xxxx-xxxx` |
| `DEFAULT_FROM_EMAIL` | From address | `Amanzon <support@amanzon.com>` |

### Razorpay (Optional)

| Variable | Description | Example |
|----------|-------------|---------|
| `RAZORPAY_KEY_ID` | Razorpay key ID | `rzp_test_xxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | `xxx` |

> **Note:** If Razorpay keys are not set, the app runs in **demo mode** - payments are simulated.

### Admin (for Render deployment)

| Variable | Description |
|----------|-------------|
| `DJANGO_SUPERUSER_USERNAME` | Admin username |
| `DJANGO_SUPERUSER_EMAIL` | Admin email |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password |

---

## Configuration

### Settings (`amanzon/settings.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `FREE_SHIPPING_THRESHOLD` | 500 | Minimum order for free shipping |
| `SHIPPING_COST` | 50 | Default shipping cost |
| `DEFAULT_COUNTRY` | "India" | Default country for addresses |
| `VERIFICATION_TOKEN_EXPIRY_HOURS` | 24 | Email verification token expiry |
| `OTP_EXPIRY_SECONDS` | 600 | Password reset OTP expiry (10 min) |
| `SESSION_COOKIE_AGE` | 1209600 | Session lifetime (2 weeks) |

### Rate Limiting (`middleware.py`)

| Path | Limit | Window |
|------|-------|--------|
| `/login/` | 5 requests | 60 seconds |
| `/register/` | 5 requests | 60 seconds |
| `/password-reset/` | 3 requests | 600 seconds (10 min) |

### Image Optimization (`services.py`)

| Setting | Value |
|---------|-------|
| `MAX_IMAGE_SIZE` | 800x800 pixels |
| `IMAGE_QUALITY` | 85% JPEG |

---

## Services Layer

### `services.py` Functions

| Function | Purpose |
|----------|---------|
| `optimize_image()` | Resize and compress uploaded images |
| `calculate_shipping()` | Determine shipping cost based on subtotal |
| `calculate_discount()` | Calculate coupon discount amount |
| `calculate_cart_totals()` | Get all cart totals (subtotal, shipping, discount, total) |
| `create_order_from_cart()` | Create order, deduct stock, record coupon usage |
| `send_order_confirmation_email()` | Send order confirmation |
| `cancel_order()` | Cancel order, restore stock, process refund |
| `get_valid_coupon()` | Validate coupon code |
| `validate_cart_stock()` | Check stock availability for all cart items |

### Atomic Transactions

`create_order_from_cart()` uses `@transaction.atomic` to ensure:
1. Order creation
2. OrderItem creation
3. Stock decrement (using `F()` expressions)
4. Coupon usage recording
5. Cart clearing

All succeed or all fail.

---

## Custom Components

### Storage Backend (`storage.py`)

`SupabaseStorage` class implements Django's `Storage` interface:

| Method | Description |
|--------|-------------|
| `_save()` | Upload file to Supabase |
| `_open()` | Download file from Supabase |
| `delete()` | Remove file from Supabase |
| `exists()` | Check if file exists |
| `url()` | Get public URL |
| `size()` | Get file size from metadata |

### Middleware (`middleware.py`)

`RateLimitMiddleware` provides IP-based rate limiting using Django's cache framework.

### Template Tags (`store_tags.py`)

| Filter | Usage | Output |
|--------|-------|--------|
| `currency` | `{{ price\|currency }}` | `₹1,234.56` |
| `alt_default` | `{{ name\|alt_default:"Default" }}` | Value or default |

### Custom Exceptions (`exceptions.py`)

| Exception | When Raised |
|-----------|-------------|
| `PaymentError` | Payment processing fails |
| `StockError` | Insufficient stock |
| `CouponError` | Invalid/expired coupon |
| `OrderError` | Order processing fails |
| `StorageError` | File storage operation fails |

---

## Testing

### Running Tests

```bash
# All tests
uv run python manage.py test store

# Specific test file
uv run python manage.py test store.tests.test_orders

# With verbosity
uv run python manage.py test store -v 2
```

### Test Coverage

| Test File | Coverage |
|-----------|----------|
| `test_general.py` | Models, views, forms, services |
| `test_orders.py` | Order creation, cancellation, checkout flow |
| `test_security.py` | Rate limiting middleware |
| `test_verification.py` | Email verification flow |
| `test_session.py` | Session fixation, HttpOnly cookies |
| `test_email_settings.py` | Email sender configuration |

### Mocking External Services

Tests mock external services:
- `razorpay.Client` - Payment gateway
- `django.core.mail.send_mail` - Email sending

---

## Deployment

### Render Deployment

1. **Create Web Service** on Render
2. **Set Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py create_superuser && python manage.py collectstatic --noinput
   ```
3. **Set Start Command:**
   ```bash
   gunicorn amanzon.wsgi:application
   ```
4. **Configure Environment Variables** (see above)

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Configure `CSRF_TRUSTED_ORIGINS` with your domain
- [ ] Set up Supabase (PostgreSQL + Storage)
- [ ] Set up Razorpay (or leave empty for demo mode)
- [ ] Configure email (Gmail SMTP)
- [ ] Consider Redis for rate limiting (LocMemCache doesn't sync across workers)

### Static Files

Static files are served by WhiteNoise in production. Run:
```bash
python manage.py collectstatic
```

---

## Management Commands

### `seed_products`

Seeds the database with sample data:
- 5 categories (Electronics, Fashion, Shoes, Accessories, Home & Living)
- Subcategories per category
- 25 products with images from Unsplash
- 2 coupons (WELCOME10, SAVE20)

```bash
uv run python manage.py seed_products
```

### `create_superuser`

Creates a superuser from environment variables (for Render without shell access):

```bash
uv run python manage.py create_superuser
```

Requires: `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`

### `migrate_media`

Migrates local media files to Supabase Storage:

```bash
uv run python manage.py migrate_media
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Slow cold starts on Render** | Free tier limitation, upgrade or run locally |
| **Email not sending** | Check Gmail app password, enable "Less secure apps" |
| **Supabase connection error** | Verify `DATABASE_URL` format and credentials |
| **Images not uploading** | Check `SUPABASE_SERVICE_ROLE_KEY` permissions |
| **Rate limited during testing** | Clear cache: `from django.core.cache import cache; cache.clear()` |
| **Static files not loading** | Run `collectstatic`, check WhiteNoise config |

### Debug Mode

For debugging, set in `.env`:
```
DEBUG=True
```

Check logs in console for detailed error messages.

---

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep views thin, put logic in services

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run python manage.py test store`)
5. Commit with clear messages
6. Push and create a Pull Request

### Project Standards

- Services layer for business logic
- Form validation in form classes
- Rate limiting for sensitive endpoints
- Atomic transactions for data integrity
- Custom exceptions for clear error handling

---

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
