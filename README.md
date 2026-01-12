<p align="center">
  <img src="app/static/img/amanzon.png" alt="Amanzon Logo" width="120"/>
</p>

<h1 align="center"><a href="https://amanzon.onrender.com">Amanzon</a></h1>

<p align="center">
  A full-featured e-commerce platform built with Django 5 — featuring Razorpay payments, email verification, dark mode, and a clean minimalist design.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white" alt="Bootstrap">
  <img src="https://img.shields.io/badge/License-TSL-red" alt="License">
</p>

> [!NOTE]
> **Personal Project** 🎯 I built this to learn Django and explore e-commerce patterns. It's a passion project for skill development, not a production-ready solution. Feel free to explore, learn from it, or use it as a starting point for your own projects!

## Live Website 

**➡️ [https://amanzon.onrender.com](https://amanzon.onrender.com)**

> [!WARNING]
> **Live Demo Limitations**: The demo hosted on Render free tier may experience slow cold starts (~60s) and occasional timeouts. For the best experience, clone and run locally.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🛍️ **Shop** | Product catalog with categories, search, filtering & sorting |
| 🛒 **Cart & Wishlist** | Add products, manage quantities, save for later |
| 💳 **Payments** | Razorpay integration with demo mode for testing |
| 🎟️ **Coupons** | Discount codes with usage tracking |
| 📦 **Orders** | Order history, status tracking, cancellation with refunds |
| ⭐ **Reviews** | 1-5 star ratings with comments |
| 🔐 **Auth** | Email verification, OTP password reset, rate limiting |
| 📍 **Addresses** | Save multiple addresses, select at checkout |
| 🌙 **Dark Mode** | Manual toggle with localStorage persistence |

---

## 🚀 Quick Start

```bash
# Clone and navigate
git clone https://github.com/qtremors/amanzon.git
cd amanzon/app

# Install dependencies
uv sync

# Setup environment (if needed)
cp .env.example .env

# Initialize database
uv run python manage.py migrate

# (Optional) Seed sample products
uv run python manage.py seed_products

# Run the project
uv run python manage.py runserver
```

Visit **http://localhost:8000** 🎉

---

## 🎮 Demo

### Test Coupons
| Code | Discount | Min Order |
|------|----------|-----------|
| `WELCOME10` | 10% off | ₹500 |
| `SAVE20` | 20% off | ₹2,000 |

### Admin Panel
Create a superuser to access `/admin/`:
```bash
uv run python manage.py createsuperuser
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.2, Python 3.12 |
| **Frontend** | Bootstrap 5.3, Vanilla JS |
| **Database** | PostgreSQL (Supabase) |
| **Storage** | Supabase Storage |
| **Payments** | Razorpay API |
| **Deployment** | Render |

---

## 📁 Project Structure

```
amanzon/
├── app/                  # Django application root
│   ├── amanzon/          # Django settings & URLs
│   ├── store/            # Main app (models, views, services)
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── DEVELOPMENT.md        # Developer documentation
├── CHANGELOG.md          # Version history
├── LICENSE.md            # License terms
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
uv run python manage.py test store

# Run with verbosity
uv run python manage.py test store -v 2
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Architecture, setup, API reference |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [LICENSE.md](LICENSE.md) | License terms and attribution |
| [.env.example](app/.env.example) | Environment variable template |

---

## 📄 License

**Tremors Source License (TSL)** - Source-available license allowing viewing, forking, and derivative works with **mandatory attribution**. Commercial use requires written permission.

See [LICENSE.md](LICENSE.md) for full terms.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/qtremors">Tremors</a>
</p>
