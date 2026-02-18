# Amanzon - Tasks

> **Project:** Amanzon  
> **Version:** 1.3.1  
> **Last Updated:** 2026-02-18  
> **Review:** Deep Codebase Analysis (Round 2)

---

## ✅ Completed (v1.3.1)

### Documentation
- [x] Update documentation from templates
- [x] Create comprehensive DEVELOPMENT.md
- [x] Create custom LICENSE.md

---

## 🔴 Critical Priority (Security & Bugs)

### Security Issues
- [ ] **SEC-01:** `cancel_order` in `services.py` doesn't use `F()` expressions for stock restoration - potential race condition when restoring stock (line 284-285)
- [ ] **SEC-02:** Demo mode in payment callback has weak validation - only checks prefix `pay_demo_` (orders.py line 163)
- [ ] **SEC-03:** OTP stored in plain text in database (`User.otp` field) - should be hashed
- [ ] **SEC-04:** Razorpay key ID exposed in client-side JavaScript (`checkout.html` line 251: `"key": "{{ razorpay_key }}"`) - while the public key is designed for client-side use, the template variable name `razorpay_key` is ambiguous and should be explicitly named `razorpay_key_id` to prevent accidental secret-key exposure during future changes
- [ ] **SEC-05:** No IDOR protection on `order_detail` view - user can view any order by ID without ownership check (orders.py `order_detail` fetches by `order.id` and `user` but should verify; `cancel_order` view does check)
- [ ] **SEC-06:** No IDOR protection on `edit_address` / `delete_address` / `set_default_address` - any authenticated user could manipulate another user's address if they guess the ID (auth.py)
- [ ] **SEC-07:** `add_to_cart` uses GET method for state-changing operation (creates CartItem) - vulnerable to CSRF via image tags / links
- [ ] **SEC-08:** `checkout.html` renders `{{ csrf_token }}` (line 269) inside JavaScript string - if CSRF token contains special characters it could break JS or be XSS vector; should use `{% csrf_token %}` in a hidden form field pattern
- [ ] **SEC-09:** Review comment rendered with `{{ review.comment }}` (product_detail.html line 157) - Django auto-escapes but the template has no explicit `escape` filter and reviews accept arbitrary text; should add `|escape` or `|striptags` for defense-in-depth

### Bugs
- [ ] **BUG-01:** `remove_from_cart` (cart.py line 112) uses GET method - should use POST for state-changing operation
- [ ] **BUG-02:** `remove_coupon` (cart.py line 139) uses GET method - should use POST for state-changing operation
- [ ] **BUG-03:** `toggle_wishlist` (shop.py line 149) uses GET method - should use POST for state-changing operation
- [ ] **BUG-04:** Related products query in `product_detail` (shop.py line 122-124) doesn't annotate ratings - causes N+1 for `avg_rating` in `_product_card.html`
- [ ] **BUG-05:** `wishlist_ids` not passed to related products in `product_detail.html` (line 180) - wishlist icons won't work correctly
- [ ] **BUG-06:** `orders.html` line 69 renders product image without null check: `{% if item.product %}{{ item.product.image.url }}{% endif %}` - will crash if `item.product.image` is null (unlike other templates that check for image existence)
- [ ] **BUG-07:** `cart.html` line 166-172 has a `{% with remaining=500|add:"-1" %}` block that computes `remaining` but never uses it - the `remaining` variable is dead code within the `{% with %}` block
- [ ] **BUG-08:** Hardcoded `₹500` free shipping threshold in `cart.html` (line 169) and `index.html` (line 88) instead of using the `FREE_SHIPPING_THRESHOLD` setting - will become stale if setting changes
- [ ] **BUG-09:** `currency` template filter in `store_tags.py` references `settings.CURRENCY_SYMBOL` which is never defined in `settings.py` - will use fallback `₹` but the setting should either be defined or the reference removed
- [ ] **BUG-10:** `currency` filter is defined but never `{% load store_tags %}` in templates - all templates hardcode `₹{{ price }}` instead of using `{{ price|currency }}`; the filter is effectively unused
- [ ] **BUG-11:** Dark mode FOUC (Flash of Unstyled Content) - theme is applied via JS after DOM load (`base.html` line 202-230) but the `<html>` element starts without `data-theme`, causing a visible flash when dark mode is active

---

## 🟠 High Priority (Functional Issues)

### Code Quality
- [ ] **CQ-01:** Mixed quote styles throughout codebase (single vs double quotes) - need standardization
- [ ] **CQ-02:** `services.py` imports `razorpay` at module level - will fail if not installed but not using payments
- [ ] **CQ-03:** Missing type hints on most functions in `views/` modules
- [ ] **CQ-04:** `AddressForm` is a `forms.Form` instead of `ModelForm` - duplicates field definitions from model
- [ ] **CQ-05:** Form Bootstrap classes repeated in every form - need a mixin or widget override
- [ ] **CQ-06:** `checkout.html` has `<style>` block inside `{% block extra_js %}` (line 168-195) - CSS should be in `{% block extra_css %}` or in `style.css`
- [ ] **CQ-07:** `views/__init__.py` is empty - should re-export views or contain a module docstring explaining the package structure

### Logical Issues
- [ ] **LI-01:** `Coupon.is_valid()` doesn't check if it's already been used by anyone - only `get_valid_coupon` does per-user check
- [ ] **LI-02:** No validation that `original_price >= price` in `Product` model - could have negative discount
- [ ] **LI-03:** Phone validation only in `CheckoutForm.clean_phone()` - not in `AddressForm`
- [ ] **LI-04:** `ProfileForm` doesn't validate email uniqueness on update (could create duplicates)
- [ ] **LI-05:** No maximum quantity limit on `add_to_cart` - user can add unlimited quantity beyond stock level (stock is only checked at checkout, not on cart add)
- [ ] **LI-06:** Review form on `product_detail.html` doesn't check if user already reviewed - allows duplicate reviews from same user for same product
- [ ] **LI-07:** Deleting the default address doesn't promote another address to default - user can end up with addresses but no default
- [ ] **LI-08:** `payment_callback` in `orders.py` reads `billing_country` from POST data but falls back to `settings.DEFAULT_COUNTRY` - the checkout form has a `country` field but it's never disabled or hidden, creating potential mismatch
- [ ] **LI-09:** `password_reset` flow stores OTP in `User.otp` and `User.otp_created_at` fields but doesn't clear them after successful password change - stale OTP data remains in DB

### Half-Implemented Features
- [ ] **HI-01:** Contact form saves to DB but no admin notification/email is sent
- [ ] **HI-02:** `ContactMessage.is_read` field exists but no UI to mark as read outside admin
- [ ] **HI-03:** SubCategory filtering UI exists but subcategory filter in shop is by ID only, not URL-friendly
- [ ] **HI-04:** Newsletter "Stay Updated" section in footer has no email signup form
- [ ] **HI-05:** Social media links in footer all point to `#` (non-functional)
- [ ] **HI-06:** Footer "Shop" section links (New Arrivals, Best Sellers, Accessories) all point to the same `{% url 'store:shop' %}` - no actual filtering applied

---

## 🟡 Medium Priority (Improvements)

### Architecture
- [ ] **AR-01:** Views have some business logic that should be in services layer (e.g., coupon validation in `cart.py` lines 20-32)
- [ ] **AR-02:** No separate serializers/DTOs - views directly use model instances and dictionaries
- [ ] **AR-03:** `SupabaseStorage` handles all storage - no abstraction for swapping storage backends
- [ ] **AR-04:** Rate limiting config hardcoded in middleware - should be in settings
- [ ] **AR-05:** Cart calculations duplicated between views and services layer
- [ ] **AR-06:** `checkout.html` contains ~170 lines of JavaScript inline - should be extracted to a separate `checkout.js` static file

### Code Organization
- [ ] **CO-01:** All models in single `models.py` (317 lines) - consider splitting by domain
- [ ] **CO-02:** All services in single `services.py` (347 lines) - consider splitting by domain
- [ ] **CO-03:** Template tags file is minimal (42 lines) - underutilized for DRY templates
- [ ] **CO-04:** No custom managers on models - queries scattered in views
- [ ] **CO-05:** `seed_products.py` has product data embedded in source code (95 lines of dict literals) - should be moved to a JSON/YAML fixture file

### Database
- [ ] **DB-01:** No database index on `Coupon.code` despite frequent lookups by code
- [ ] **DB-02:** No index on `Order.razorpay_order_id` despite uniqueness check in payment callback
- [ ] **DB-03:** `CouponUsage` unique constraint could be violated if same request processed twice (race)
- [ ] **DB-04:** `Review` allows any user to review any product (no purchase verification)
- [ ] **DB-05:** `Wishlist` model has no unique constraint on `(user, product)` pair - could create duplicate wishlist entries under race conditions

### Performance
- [ ] **PF-01:** `cart.subtotal` and `cart.total_items` properties iterate all items - could use aggregation
- [ ] **PF-02:** `Product.average_rating` property does DB query each time - should use annotation in views
- [ ] **PF-03:** `context_processors.py` runs queries on every request even for anonymous static pages
- [ ] **PF-04:** `seed_products.py` downloads images synchronously - could be parallelized
- [ ] **PF-05:** `product_detail.html` line 137 uses `product.reviews.all` without `select_related('user')` - causes N+1 query for each review's username
- [ ] **PF-06:** `product_detail.html` line 46 calls `product.reviews.count` separately from `product.average_rating` - two DB queries that could be one annotation

---

## 🟢 Low Priority (Polish & Nice-to-Have)

### UI/UX Issues
- [ ] **UX-01:** No loading indicators on form submissions (except checkout)
- [ ] **UX-02:** Cart quantity update requires form submit - could use AJAX for better UX
- [ ] **UX-03:** No confirmation modal for order cancellation (only `onsubmit="return confirm()"`)
- [ ] **UX-04:** Search form in navbar doesn't preserve current search term
- [ ] **UX-05:** No pagination on reviews in `product_detail.html`
- [ ] **UX-06:** Empty cart page could show recently viewed/recommended products
- [ ] **UX-07:** No breadcrumbs on cart, wishlist, or profile pages
- [ ] **UX-08:** Wishlist page uses a different card layout than shop page (`product-card card` vs `product-card h-100 card-hover`) - inconsistent design
- [ ] **UX-09:** No visual indicator of stock level on product detail page (only "In Stock" / "Out of Stock" - no "Only 2 left!" warnings)

### Accessibility
- [ ] **A11Y-01:** Rating radio buttons in `product_detail.html` have poor labels (just number + star)
- [ ] **A11Y-02:** Some form fields missing explicit `<label>` elements with `for` attribute
- [ ] **A11Y-03:** Cart quantity input is `readonly` - should be disabled or editable
- [ ] **A11Y-04:** No skip navigation link for keyboard users
- [ ] **A11Y-05:** Color contrast issues in dark mode for some text-secondary elements
- [ ] **A11Y-06:** `base.html` navbar toggler button has no accessible label text (line 32) - `aria-label` is missing
- [ ] **A11Y-07:** Social media links in footer use `title` for "(Coming Soon)" state but screen readers may not convey this

### Responsive Design
- [ ] **RD-01:** Filter sidebar in `shop.html` not collapsible on mobile - takes full width
- [ ] **RD-02:** Product action buttons on mobile require hover (not touch-friendly)
- [ ] **RD-03:** Order table in `cart.html` could overflow on small screens

### CSS Issues
- [ ] **CSS-01:** Dark mode overrides all `.alert` backgrounds to `#1e293b` (`style.css` line 546-549) - breaks Bootstrap success/warning/danger alert color semantics
- [ ] **CSS-02:** `.footer-link:hover` changes `display` from `block` to `inline-block` (line 289-293) - causes layout shift on hover
- [ ] **CSS-03:** `.tracking-wide` utility class is used in templates but never defined in `style.css` - relies on it being a no-op (no visible letter-spacing effect)
- [ ] **CSS-04:** `.theme-toggle:hover` uses hardcoded light-mode colors (`#f1f5f9`, `#0f172a`) that don't adapt to the current theme - dark mode override exists but creates specificity issues
- [ ] **CSS-05:** Dark mode variables redefine `--white: #111827` which is semantically confusing - variable name implies white but value is dark

### Naming & Typos
- [ ] **NM-01:** Inconsistent naming: `toggle_wishlist` vs `add_to_cart` (toggle vs add)
- [ ] **NM-02:** Parameter `item_id` in cart views but `product_id` in shop views - inconsistent
- [ ] **NM-03:** Comment `# H2:` `# C4:` prefixes are cryptic - should be descriptive
- [ ] **NM-04:** `category_slug` parameter but `product_id` (not `product_slug`) - inconsistent
- [ ] **NM-05:** `index.html` says "New Collection 2026" (line 14) - year is hardcoded instead of dynamic

### Dead/Unused Code
- [ ] **DC-01:** `OrderError` exception defined but never raised
- [ ] **DC-02:** `CouponError` exception defined but never raised  
- [ ] **DC-03:** `StorageError` exception defined but never raised
- [ ] **DC-04:** `alt_default` template filter defined but not used in any template
- [ ] **DC-05:** `CURRENCY_SYMBOL` setting referenced in `store_tags.py` but never defined in settings
- [ ] **DC-06:** `SimpleUploadedFile` import in `test_orders.py` is used but creates empty image files (`content=b''`) - these aren't valid images
- [ ] **DC-07:** `import os` in `seed_products.py` (line 5) is unused - never referenced in the file

---

## 📋 Documentation Issues

### Missing Documentation
- [ ] **DOC-01:** No API error response documentation
- [ ] **DOC-02:** No documentation for custom exceptions in `exceptions.py`
- [ ] **DOC-03:** Template tags `store_tags.py` not documented in DEVELOPMENT.md (actually they ARE documented at line 484-489, but `currency` filter description doesn't mention the undefined `CURRENCY_SYMBOL` fallback behavior)
- [ ] **DOC-04:** No inline comments explaining complex checkout JavaScript
- [ ] **DOC-05:** Service functions missing parameter/return type documentation
- [ ] **DOC-06:** `CSRF_TRUSTED_ORIGINS` env var is in `.env.example` but not documented in DEVELOPMENT.md's Environment Variables section
- [ ] **DOC-07:** `create_superuser` management command is not documented with `--help` usage - only described briefly in DEVELOPMENT.md
- [ ] **DOC-08:** `migrate_media` management command has no documentation about what it expects (file structure, Supabase bucket config)

### Outdated / Incorrect Documentation
- [ ] **DOC-09:** DEVELOPMENT.md says `settings.py` is "259 lines" (line 93) - should be verified and kept up-to-date or removed
- [ ] **DOC-10:** DEVELOPMENT.md says `style.css` is "598 lines" (line 142) - same issue with hardcoded line count
- [ ] **DOC-11:** DEVELOPMENT.md says "57+ tests" (line 124, 196) - actual test count should be verified
- [ ] **DOC-12:** CHANGELOG lists "12 database models" in v1.0.0 but later says model count is 14
- [ ] **DOC-13:** README project structure shows `media/` but it's in `app/media/`
- [ ] **DOC-14:** DEVELOPMENT.md Relationships Diagram (line 279) shows `SubCategory ── 1:N ──── Product` but `Product.subcategory` is nullable/optional FK - diagram implies it's required
- [ ] **DOC-15:** DEVELOPMENT.md says `store_tags.py` `currency` filter outputs `₹1,234.56` (line 488) but the actual implementation uses `intcomma` which outputs `₹1,234` for integer values - no `.56` decimal formatting

### Code Comments
- [ ] **CC-01:** Inconsistent comment prefixes (CR-1, SEC-02, H2, C4, etc.) - no legend explaining what they mean
- [ ] **CC-02:** Some TODOs or improvement suggestions would be helpful in complex areas
- [ ] **CC-03:** `CR-2` and `CR-7` comments appear in templates referencing past bug fixes but the referenced issue tracker (CR-#) is not documented anywhere

---

## 🧪 Test Coverage Gaps

### Missing Tests
- [ ] **TC-01:** No tests for `SupabaseStorage` class
- [ ] **TC-02:** No tests for `optimize_image` service function
- [ ] **TC-03:** No tests for address management views (add, edit, delete, set_default)
- [ ] **TC-04:** No tests for wishlist toggle functionality
- [ ] **TC-05:** No tests for template tags (`currency`, `alt_default`)
- [ ] **TC-06:** No tests for `seed_products` management command
- [ ] **TC-07:** No tests for context processor with anonymous user
- [ ] **TC-08:** No integration tests for full purchase flow with coupon
- [ ] **TC-09:** No tests for profile update (`profile` view in auth.py)
- [ ] **TC-10:** No tests for password reset OTP flow end-to-end
- [ ] **TC-11:** No tests for order cancellation authorization (verifying user can't cancel another user's order)
- [ ] **TC-12:** No tests for demo payment mode end-to-end flow
- [ ] **TC-13:** No tests for `create_superuser` or `migrate_media` management commands

### Test Quality
- [ ] **TQ-01:** Tests don't verify email content, only that `send_mail` was called
- [ ] **TQ-02:** No tests for edge cases (negative prices, zero stock, etc.)
- [ ] **TQ-03:** No tests for concurrent stock updates (race condition scenarios)
- [ ] **TQ-04:** `test_orders.py` creates `SimpleUploadedFile` with empty content (`b''`) - not a valid image file, could mask bugs in image handling
- [ ] **TQ-05:** No test isolation for rate limiting - some tests call `cache.clear()` in setUp but this is fragile and could cause flaky tests if tests run in different order

---

## 💡 Future Enhancements

### Feature Ideas
- [ ] Product search autocomplete
- [ ] Order status email notifications
- [ ] Product variants (size, color)
- [ ] Inventory low stock alerts
- [ ] Admin dashboard with analytics
- [ ] Product comparison feature
- [ ] Customer support chat integration
- [ ] Multi-currency support
- [ ] Wishlist sharing
- [ ] Guest checkout option

### Technical Improvements
- [ ] Redis for rate limiting (production)
- [ ] Celery for async email sending
- [ ] API endpoints for mobile app
- [ ] GraphQL API alternative
- [ ] CDN for static/media files
- [ ] Database query optimization with django-debug-toolbar

---

## 🏗️ Architecture Notes

### Strengths
- Service layer properly separates business logic from views
- Atomic transactions used for critical operations (order creation)
- F() expressions for stock updates prevent race conditions
- Custom exceptions provide clear error hierarchy
- Good test coverage for core flows (57+ tests)
- Lazy Supabase client initialization improves startup time
- Clean dark mode implementation with CSS custom properties
- Good use of Django template tags and template inheritance

### Areas for Improvement
- Views still contain some business logic (coupon validation, stock checks)
- Consider splitting large files (models.py, services.py) by domain
- Form classes duplicate model field definitions
- Template logic could be simplified with more template tags/filters
- IDOR vulnerabilities in several views need ownership checks
- Hardcoded values in templates should reference settings
- Inline JS in checkout template should be extracted

---

## 📊 Summary Statistics

| Category | Critical | High | Medium | Low |
|----------|:--------:|:----:|:------:|:---:|
| Security | 9 | - | - | - |
| Bugs | 11 | - | - | - |
| Code Quality | - | 7 | - | - |
| Logical Issues | - | 9 | - | - |
| Half-Implemented | - | 6 | - | - |
| Architecture | - | - | 6 | - |
| Code Organization | - | - | 5 | - |
| Database | - | - | 5 | - |
| Performance | - | - | 6 | - |
| UI/UX | - | - | - | 9 |
| Accessibility | - | - | - | 7 |
| Responsive | - | - | - | 3 |
| CSS Issues | - | - | - | 5 |
| Naming/Typos | - | - | - | 5 |
| Dead Code | - | - | - | 7 |
| Documentation | - | - | - | 18 |
| Test Gaps | - | - | - | 18 |

**Total Issues Found: 130**
- 🔴 Critical: 20
- 🟠 High: 22  
- 🟡 Medium: 22
- 🟢 Low: 72

---

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
