# Amanzon 🛒

A modern Django e-commerce application with clean design and essential features.

## Features

- 🔐 User authentication (register, login, password reset with OTP)
- ✉️ Email verification for new accounts
- 🛍️ Product catalog with categories, search, and filters
- 🛒 Shopping cart with quantity management
- ❤️ Wishlist functionality
- 💳 Razorpay payment integration
- 📦 Order management with cancellation & refunds
- ⭐ Product reviews and ratings
- 🎟️ Coupon/discount codes
- 🔒 Rate limiting on auth endpoints
- 📧 Contact form

## Tech Stack

- **Backend:** Django 5.x
- **Frontend:** Bootstrap 5, HTML, CSS
- **Database:** SQLite (dev) / MySQL (production)
- **Payments:** Razorpay
- **Package Manager:** uv

## Quick Start

### 1. Clone and navigate
```bash
git clone https://github.com/yourusername/amanzon.git
cd amanzon/app
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Run migrations
```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

### 5. Start server
```bash
uv run python manage.py runserver
```

Visit http://localhost:8000

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `RAZORPAY_KEY_ID` | Razorpay API key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret |
| `EMAIL_HOST_USER` | Gmail address for SMTP |
| `EMAIL_HOST_PASSWORD` | Gmail app password |

## Project Structure

```
app/
├── amanzon/           # Django project settings
├── store/             # Main application
│   ├── models.py      # Database models
│   ├── views/         # Modular view package
│   │   ├── auth.py    # Authentication views
│   │   ├── shop.py    # Shop & product views
│   │   ├── cart.py    # Cart management
│   │   ├── orders.py  # Checkout & orders
│   │   └── main.py    # Contact, misc
│   ├── tests/         # Test package (53 tests)
│   ├── forms.py       # Form definitions
│   ├── services.py    # Business logic
│   ├── middleware.py  # Rate limiting
│   └── urls.py        # URL routing
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploads
```

## Running Tests

```bash
uv run python manage.py test store
```

## Deployment (PythonAnywhere)

1. Upload code to PythonAnywhere
2. Create virtualenv with Python 3.11
3. Install dependencies: `pip install -r requirements.txt`
4. Configure WSGI to point to `amanzon.wsgi`
5. Set environment variables in .env
6. Run `python manage.py collectstatic`
7. Configure MySQL database
