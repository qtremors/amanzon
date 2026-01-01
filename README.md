<p align="center">
  <img src="app/static/img/amanzon.png" alt="Amanzon Logo" width="100"/>
</p>

# Amanzon

A minimalist e-commerce application built with Django 5.

## Features

- Product catalog with categories, search, and filtering
- Shopping cart and wishlist
- Razorpay payment integration
- Coupon/discount codes
- Order history
- Email verification and OTP password reset
- Product reviews and ratings

## Tech Stack

- Django 5.2, Python 3.12
- Bootstrap 5, Vanilla JS
- SQLite
- Razorpay API

## Local Development

```bash
cd amanzon/app
uv sync
cp .env.example .env  # Edit with your credentials
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Deployment (Render)

1. Create Web Service, connect GitHub repo
2. Root Directory: `app`
3. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_superuser`
4. Start Command: `gunicorn amanzon.wsgi:application`
5. Set environment variables (see `.env.example`)

## Testing

```bash
uv run python manage.py test store
```

## License

MIT License
