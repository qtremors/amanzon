# Amanzon - Task List

> **Last Updated:** 2026-01-01
> **Status:** All High Priority Complete ✅

---

## ✅ Completed

- [x] **Email Verification** - Users receive verification email before activation
- [x] **Order Cancellation & Refunds** - Stock restoration and Razorpay refund initiation
- [x] **Rate Limiting** - Applied to Login/Register endpoints (5 req/min)
- [x] **Session Security** - Verified session fixation protection and HttpOnly cookies
- [x] **View Refactoring** - Split into `views/auth.py`, `shop.py`, `cart.py`, `orders.py`, `main.py`
- [x] **Test Consolidation** - All tests in `store/tests/` package (57 tests passing)
- [x] **Payment Flow Tests** - Checkout and payment callback tests with mocked Razorpay
- [x] **Database Indexes** - Added to `Product.is_active`, `Product.price`, `Order.status`, `Order.created_at`
- [x] **Image Optimization** - Auto-resize/compress on upload for User profiles and Product images

---

## 🟡 Medium Priority

### UI/UX
- [ ] Search autocomplete
- [ ] Loading states during checkout
- [ ] Product gallery (multiple images)

### Features
- [ ] Order tracking integration
- [ ] PDF invoice generation
- [ ] Wishlist to cart button

### Code Quality
- [ ] Type hints for complex functions
- [ ] Replace prints with logging

---

## 🟢 Low Priority

- [ ] Breadcrumb navigation
- [ ] Social login (Google/GitHub)
- [ ] Newsletter subscription
- [ ] Soft delete for orders/products
