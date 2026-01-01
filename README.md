<p align="center">
  <img src="app/static/img/amanzon.png" alt="Amanzon Logo" width="100"/>
</p>

# Amanzon

A minimalist e-commerce application built with Django 5. Features a clean shopping experience with essential functionality and performance.

## Features

### Shopping
- Product catalog with categories, search, and filtering
- Shopping cart and wishlist
- Product reviews and ratings

### Checkout
- Razorpay payment integration
- Coupon/discount codes
- Order history and tracking

### Authentication
- Email verification on registration
- OTP-based password reset
- User profiles

## Tech Stack

- **Backend**: Django 5.2, Python 3.12
- **Frontend**: Bootstrap 5, Vanilla JS
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Payment**: Razorpay API
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## Local Development

### Prerequisites
- Python 3.10+
- `uv` package manager

### Setup

```bash
# Clone and navigate
git clone https://github.com/qtremors/amanzon.git
cd amanzon/app

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Run server
uv run python manage.py runserver
```

Visit `http://127.0.0.1:8000`

## Deployment (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
   - `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`
   - `ALLOWED_HOSTS` (your Render domain)
4. Build command: `cd app && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start command: `cd app && gunicorn amanzon.wsgi:application`

## Testing

```bash
uv run python manage.py test store
```

## Project Structure

```
app/
├── amanzon/           # Project configuration
├── store/             # Core application
│   ├── models.py      # Database models
│   ├── services.py    # Business logic
│   ├── views/         # View controllers
│   └── tests/         # Test suite
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploads
```

## License

MIT License
