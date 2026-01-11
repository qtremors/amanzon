<p align="center">
  <img src="app/static/img/amanzon.png" alt="Amanzon Logo" width="120"/>
</p>

<h1 align="center"><a href="https://amanzon.onrender.com">Amanzon</a></h1>

<p align="center">
  A modern, minimalist e-commerce platform built with Django 5
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white" alt="Bootstrap">
</p>

> [!WARNING]
> **Live Demo Limitations**: The demo hosted on Render free tier may experience slow cold starts (~60s) and occasional timeouts due to memory constraints, it's better if you clone the repo and run it locally.

---

## Features

### 🛍️ Shopping Experience
- Product catalog with categories, subcategories, search & filtering
- Shopping cart with quantity management
- Wishlist functionality
- Product reviews and ratings (1-5 stars)

### 💳 Payments & Orders
- Razorpay payment integration (with demo mode for testing)
- Coupon/discount code system with usage tracking
- Order history and status tracking
- Order cancellation with automatic stock restoration

### 🔐 Authentication & Security
- Email verification for new accounts (24-hour token expiry)
- OTP-based password reset via email
- Profile management with avatar upload
- **Saved addresses** with checkout integration
- Rate limiting on authentication endpoints
- CSRF protection, secure cookies, HTTPS enforcement

### 🛠️ Technical Highlights
- Service layer architecture for business logic
- Custom storage backend for Supabase
- Image optimization on upload (auto-resize, compression)
- Database indexes on frequently queried fields
- Comprehensive test suite (57+ tests)

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 5.2, Python 3.12 |
| **Frontend** | Bootstrap 5, Vanilla JS |
| **Database** | Supabase PostgreSQL |
| **Storage** | Supabase Storage |
| **Payments** | Razorpay API |

---

## Project Structure

```
amanzon/
├── app/
│   ├── amanzon/          # Django project settings
│   ├── store/            # Main application
│   │   ├── models.py     # 12 database models
│   │   ├── views/        # View modules
│   │   ├── services.py   # Business logic layer
│   │   └── storage.py    # Supabase storage backend
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── CHANGELOG.md
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Local Development

```bash
# Clone the repository
git clone https://github.com/qtremors/amanzon.git
cd amanzon/app

# Install dependencies
uv sync

# Copy environment file and configure
cp .env.example .env

# Run migrations
uv run python manage.py migrate

# Create admin user
uv run python manage.py createsuperuser

# Seed sample products (optional)
uv run python manage.py seed_products

# Start development server
uv run python manage.py runserver
```

Visit `http://localhost:8000` to view the app.

### Running Tests

```bash
uv run python manage.py test store
```

---

## License

MIT License

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/qtremors">qtremors</a>
</p>
