# Amanzon - Project Context for AI Agents

> **Purpose:** This file preserves project context so any AI agent can continue development if a session is interrupted.

---

## 📋 Project Overview

**Name:** Amanzon  
**Type:** Django E-commerce Application  
**Status:** Active development

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.x (Python 3.11+) |
| Frontend | HTML, CSS, Bootstrap 5, minimal JavaScript |
| Database | SQLite (dev) / MySQL (production) |
| Payments | Razorpay (test mode) |
| Email | Gmail SMTP |
| Package Manager | uv (not pip) |

---

## ✨ Features (Implemented)

### Authentication
- User registration with email verification
- Login/logout with rate limiting
- Password reset via email OTP
- User profile with picture upload
- Session security (fixation protection, HttpOnly cookies)

### Products
- Categories and subcategories
- Product listings with images
- Product detail pages
- Search, filters, sorting
- Pagination

### Shopping
- Add to cart with stock validation
- Update cart quantities
- Remove from cart
- Wishlist (add/remove)
- Coupon/discount codes

### Checkout & Orders
- Billing address form
- Razorpay payment integration
- Order creation on payment success
- Order history
- Order cancellation with stock restoration and refunds

### Reviews
- Star ratings (1-5)
- Text reviews
- Average rating calculation

---

##  Project Structure

```
amanzon/
├── app/
│   ├── manage.py
│   ├── pyproject.toml
│   ├── .env
│   │
│   ├── amanzon/              # Project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── store/                # Main app
│   │   ├── models.py
│   │   ├── views/            # Modular views
│   │   │   ├── auth.py       # Login, register, profile
│   │   │   ├── shop.py       # Products, categories
│   │   │   ├── cart.py       # Cart management
│   │   │   ├── orders.py     # Checkout, orders
│   │   │   └── main.py       # Contact, misc
│   │   ├── tests/            # Test package
│   │   │   ├── test_general.py
│   │   │   ├── test_verification.py
│   │   │   ├── test_orders.py
│   │   │   ├── test_security.py
│   │   │   └── test_session.py
│   │   ├── forms.py
│   │   ├── services.py       # Business logic
│   │   ├── middleware.py     # Rate limiting
│   │   └── urls.py
│   │
│   ├── templates/
│   └── static/
│
├── README.md
├── TASKS.md
├── CHANGELOG.md
└── AGENTS.md
```

---

## 🔄 Current Status

**Tests:** 57 passing  
**Last Update:** 2026-01-01

### Completed
- [x] Email verification
- [x] Order cancellation with refunds
- [x] Rate limiting on auth
- [x] Session security audit
- [x] View refactoring (modular views/)
- [x] Test consolidation (tests/ package)
- [x] Payment flow tests
- [x] Database indexes
- [x] Image optimization

### Remaining (Medium Priority)
- [ ] Search autocomplete
- [ ] PDF invoice generation
- [ ] Type hints

---

## 🔐 Environment Variables (.env)

```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## 🤖 For AI Agents

1. Read this file and TASKS.md for context
2. Use `uv run manage.py test store` to verify changes
3. Views are in `store/views/` package (not single file)
4. Tests are in `store/tests/` package
5. Use uv, not pip
6. All secrets in .env
