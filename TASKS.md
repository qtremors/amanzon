# Amanzon - Tasks

> **Version:** 1.3.0 | **Last Updated:** 2026-01-11

---

## ✅ Completed (v1.3.0)

### Documentation Overhaul
- [x] Rewrote README.md with surface-level content, features table, quick start
- [x] Created DEVELOPMENT.md with comprehensive developer docs (567 lines)
- [x] Created LICENSE.md with simple custom license (Tremors Source License)
- [x] Added personal project note to README
- [x] Fixed model count (13 → 14) across documentation
- [x] Added LICENSE.md to project structure in all docs

## 🐰 CodeRabbit PR Review (v1.2.5)

### Bug Fixes
- [ ] **CR-1:** `AddressInline.readonly_fields = ['label']` prevents admins from editing the label
  - Remove `'label'` from `readonly_fields` in `app/store/admin.py` (line 13)
  
- [ ] **CR-2:** Templates access `item.product.image.url` directly without null check
  - Update `cart.html`, `checkout.html`, `wishlist.html`, `order_detail.html` with `{% if item.product.image %}` conditional
  - Use same fallback as `product_detail.html` (placeholder image)

- [ ] **CR-3:** `Address.country` uses `settings.DEFAULT_COUNTRY` directly (fails if missing)
  - Change to `default=getattr(settings, 'DEFAULT_COUNTRY', 'US')` in `app/store/models.py` (line 49)

- [ ] **CR-4:** `avg_rating` annotation not rounded (inconsistent with `Product.average_rating`)
  - Update `app/store/views/shop.py` to use `Round(Avg('reviews__rating'), 1)`

- [ ] **CR-5:** `exists()` and `size()` in `SupabaseStorage` fail silently for >100 items in folder
  - Use `search` parameter: `list(folder, {"search": filename})` in `app/store/storage.py`

### UX Improvements
- [ ] **CR-6:** `address_form.html` doesn't show validation errors
  - Add `form.non_field_errors` block and per-field `.errors` display

- [ ] **CR-7:** Primary product image uses `loading="lazy"` (hurts LCP)
  - Remove `loading="lazy"` from main image in `product_detail.html` (line 24)

### Dead Code
- [ ] **CR-8:** `currency` and `alt_default` filters in `store_tags.py` are unused
  - Either use them in templates or delete them

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

