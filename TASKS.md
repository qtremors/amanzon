# Amanzon - Tasks

> **Version:** 1.2.5 | **Last Updated:** 2026-01-11

## ✅ Completed

### Critical (C1-C5)
- Version mismatch fixed in pyproject.toml
- Open redirect protection in cart/shop views
- Race condition fix with F() expression in stock deduction
- Stock re-validation in order creation
- OTP brute force protection (5 attempts max)

### High Priority (H1-H7)
- StockError exception now used in services.py
- Cart get_or_create in checkout
- Email failure handling in registration
- Pagination filter preservation + template syntax fix
- Product image made optional
- Redis cache note added
- DEFAULT_COUNTRY configuration added

### Medium Priority
- Footer copyright duplication removed
- SupabaseStorage.size() implemented
- Contact form honeypot added
- 404/500 custom templates created
- AddressInline added to UserAdmin

---

## 📋 Remaining (Lower Priority)

### Future Enhancements
- **M3:** Change cart/wishlist to POST (requires template refactoring)
- **M4:** Base form mixin for Bootstrap classes
- **M5:** Review edit/delete functionality
- **M9:** Use currency filter consistently
- **L11:** AJAX shop filtering

### Code Quality
- Quote standardization, type hints, test coverage gaps
- View logging, documentation updates

---

## 🏗️ Architecture Notes
- Service layer handles business logic well
- Views properly organized by module
- Tests well-structured with good mocking

