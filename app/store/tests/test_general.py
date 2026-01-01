"""
Amanzon Test Suite

Tests for models, views, and forms.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import (
    User, Category, SubCategory, Product, Cart, CartItem,
    Wishlist, Coupon, Order, OrderItem, Review, ContactMessage
)
from ..forms import RegisterForm, LoginForm, ContactForm, CheckoutForm


# =============================================================================
# MODEL TESTS
# =============================================================================

class UserModelTest(TestCase):
    """Tests for the User model."""
    
    def test_create_user(self):
        """Test user creation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(username='testuser', password='test')
        self.assertEqual(str(user), 'testuser')


class CategoryModelTest(TestCase):
    """Tests for Category and SubCategory models."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')
    
    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.category), 'Electronics')
    
    def test_subcategory_str(self):
        """Test subcategory string representation."""
        subcategory = SubCategory.objects.create(
            category=self.category,
            name='Phones',
            slug='phones'
        )
        self.assertEqual(str(subcategory), 'Electronics > Phones')


class ProductModelTest(TestCase):
    """Tests for the Product model."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='A test product',
            price=Decimal('99.99'),
            original_price=Decimal('149.99'),
            stock=10
        )
    
    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_discount_percent(self):
        """Test discount percentage calculation."""
        # (149.99 - 99.99) / 149.99 * 100 = 33.33%
        self.assertEqual(self.product.discount_percent, 33)
    
    def test_no_discount(self):
        """Test product with no discount."""
        product = Product.objects.create(
            category=self.category,
            name='Full Price',
            slug='full-price',
            description='No discount',
            price=Decimal('100.00'),
            original_price=Decimal('100.00'),
            stock=5
        )
        self.assertEqual(product.discount_percent, 0)
    
    def test_average_rating_no_reviews(self):
        """Test average rating with no reviews."""
        self.assertEqual(self.product.average_rating, 0)


class CartModelTest(TestCase):
    """Tests for Cart and CartItem models."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='cartuser', password='test')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Cart Product',
            slug='cart-product',
            description='Test',
            price=Decimal('50.00'),
            original_price=Decimal('50.00'),
            stock=10
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_str(self):
        """Test cart string representation."""
        self.assertEqual(str(self.cart), 'Cart for cartuser')
    
    def test_empty_cart(self):
        """Test empty cart totals."""
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.subtotal, 0)
    
    def test_cart_with_items(self):
        """Test cart with items."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(self.cart.subtotal, Decimal('100.00'))


class CouponModelTest(TestCase):
    """Tests for the Coupon model."""
    
    def test_valid_coupon(self):
        """Test valid coupon."""
        coupon = Coupon.objects.create(
            code='TEST10',
            discount_percent=Decimal('10.00'),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertTrue(coupon.is_valid())
    
    def test_expired_coupon(self):
        """Test expired coupon."""
        coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_percent=Decimal('10.00'),
            valid_from=timezone.now() - timezone.timedelta(days=10),
            valid_to=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertFalse(coupon.is_valid())
    
    def test_inactive_coupon(self):
        """Test inactive coupon."""
        coupon = Coupon.objects.create(
            code='INACTIVE',
            discount_percent=Decimal('10.00'),
            is_active=False,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertFalse(coupon.is_valid())


# =============================================================================
# VIEW TESTS
# =============================================================================

class HomeViewTest(TestCase):
    """Tests for home page views."""
    
    def setUp(self):
        self.client = Client()
    
    def test_index_page(self):
        """Test homepage loads successfully."""
        response = self.client.get(reverse('store:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/index.html')


class ShopViewTest(TestCase):
    """Tests for shop views."""
    
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Shop Product',
            slug='shop-product',
            description='Test product',
            price=Decimal('25.00'),
            original_price=Decimal('30.00'),
            stock=5
        )
    
    def test_shop_page(self):
        """Test shop page loads."""
        response = self.client.get(reverse('store:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shop Product')
    
    def test_shop_category_filter(self):
        """Test shop category filter."""
        Category.objects.create(name='Test Category Filter', slug='test-filter')
        response = self.client.get(reverse('store:shop_category', args=['test-filter']))
        self.assertEqual(response.status_code, 200)
    
    def test_product_detail(self):
        """Test product detail page."""
        response = self.client.get(reverse('store:product_detail', args=['shop-product']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shop Product')


class AuthViewTest(TestCase):
    """Tests for authentication views."""
    
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='testpass123'
        )
    
    def test_login_page(self):
        """Test login page loads."""
        response = self.client.get(reverse('store:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """Test register page loads."""
        response = self.client.get(reverse('store:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(reverse('store:login'), {
            'email': 'auth@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success


class CartViewTest(TestCase):
    """Tests for cart views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cartuser', password='test123')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Cart Test',
            slug='cart-test',
            description='Test',
            price=Decimal('100.00'),
            original_price=Decimal('100.00'),
            stock=10
        )
    
    def test_cart_requires_login(self):
        """Test cart page requires authentication."""
        response = self.client.get(reverse('store:cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_cart_page_authenticated(self):
        """Test cart page for logged in user."""
        self.client.login(username='cartuser', password='test123')
        response = self.client.get(reverse('store:cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_cart(self):
        """Test adding product to cart."""
        self.client.login(username='cartuser', password='test123')
        response = self.client.get(reverse('store:add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after add
        
        # Check cart has item
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_items, 1)


class ContactViewTest(TestCase):
    """Tests for contact view."""
    
    def setUp(self):
        self.client = Client()
    
    def test_contact_page(self):
        """Test contact page loads."""
        response = self.client.get(reverse('store:contact'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_form_submit(self):
        """Test contact form submission."""
        response = self.client.post(reverse('store:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(ContactMessage.objects.count(), 1)


# =============================================================================
# FORM TESTS  
# =============================================================================

class RegisterFormTest(TestCase):
    """Tests for registration form."""
    
    def test_valid_form(self):
        """Test valid registration form."""
        form = RegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!'
        })
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test password mismatch validation."""
        form = RegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Pass123!',
            'confirm_password': 'Different123!'
        })
        self.assertFalse(form.is_valid())
    
    def test_duplicate_email(self):
        """Test duplicate email validation."""
        User.objects.create_user(username='existing', email='exists@example.com', password='test')
        form = RegisterForm(data={
            'username': 'newuser',
            'email': 'exists@example.com',
            'password': 'Pass123!',
            'confirm_password': 'Pass123!'
        })
        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):
    """Tests for login form."""
    
    def test_valid_form(self):
        """Test valid login form."""
        form = LoginForm(data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertTrue(form.is_valid())


class ContactFormTest(TestCase):
    """Tests for contact form."""
    
    def test_valid_form(self):
        """Test valid contact form."""
        form = ContactForm(data={
            'name': 'Test',
            'email': 'test@example.com',
            'subject': 'Subject',
            'message': 'Message content'
        })
        self.assertTrue(form.is_valid())
    
    def test_missing_fields(self):
        """Test form with missing required fields."""
        form = ContactForm(data={
            'name': 'Test'
        })
        self.assertFalse(form.is_valid())


# =============================================================================
# SERVICES TESTS
# =============================================================================

class ServicesTest(TestCase):
    """Tests for the services layer."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='serviceuser', password='test123')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Service Test',
            slug='service-test',
            description='Test product',
            price=Decimal('100.00'),
            original_price=Decimal('100.00'),
            stock=10
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
    
    def test_calculate_shipping_free(self):
        """Test free shipping over threshold."""
        from ..services import calculate_shipping
        self.assertEqual(calculate_shipping(Decimal('500')), Decimal('0'))
        self.assertEqual(calculate_shipping(Decimal('1000')), Decimal('0'))
    
    def test_calculate_shipping_paid(self):
        """Test paid shipping under threshold."""
        from ..services import calculate_shipping
        self.assertEqual(calculate_shipping(Decimal('499')), Decimal('50'))
        self.assertEqual(calculate_shipping(Decimal('0')), Decimal('50'))
    
    def test_calculate_cart_totals(self):
        """Test cart total calculations."""
        from ..services import calculate_cart_totals
        totals = calculate_cart_totals(self.cart)
        self.assertEqual(totals['subtotal'], Decimal('200.00'))
        self.assertEqual(totals['shipping'], Decimal('50'))  # Under 500
        self.assertEqual(totals['discount'], Decimal('0'))
        self.assertEqual(totals['total'], Decimal('250.00'))
    
    def test_calculate_cart_totals_with_coupon(self):
        """Test cart totals with valid coupon."""
        from ..services import calculate_cart_totals
        coupon = Coupon.objects.create(
            code='TEST20',
            discount_percent=Decimal('20.00'),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1)
        )
        totals = calculate_cart_totals(self.cart, coupon)
        self.assertEqual(totals['discount'], Decimal('40.00'))  # 20% of 200
        self.assertEqual(totals['total'], Decimal('210.00'))  # 200 + 50 - 40


class CouponUsageTest(TestCase):
    """Tests for coupon usage tracking."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='couponuser', password='test123')
        self.coupon = Coupon.objects.create(
            code='ONEUSE10',
            discount_percent=Decimal('10.00'),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1)
        )
    
    def test_get_valid_coupon(self):
        """Test getting a valid coupon."""
        from ..services import get_valid_coupon
        coupon, error = get_valid_coupon('ONEUSE10', self.user)
        self.assertIsNotNone(coupon)
        self.assertIsNone(error)
    
    def test_get_valid_coupon_already_used(self):
        """Test coupon rejection when already used."""
        from ..services import get_valid_coupon
        from ..models import CouponUsage
        
        # Mark coupon as used
        CouponUsage.objects.create(coupon=self.coupon, user=self.user)
        
        coupon, error = get_valid_coupon('ONEUSE10', self.user)
        self.assertIsNone(coupon)
        self.assertEqual(error, 'You have already used this coupon.')
    
    def test_get_invalid_coupon(self):
        """Test invalid coupon code."""
        from ..services import get_valid_coupon
        coupon, error = get_valid_coupon('NOTEXIST', self.user)
        self.assertIsNone(coupon)
        self.assertEqual(error, 'Invalid coupon code.')


class StockValidationTest(TestCase):
    """Tests for stock validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='stockuser', password='test123')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Low Stock',
            slug='low-stock',
            description='Test',
            price=Decimal('50.00'),
            original_price=Decimal('50.00'),
            stock=2
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_valid_stock(self):
        """Test cart with sufficient stock."""
        from ..services import validate_cart_stock
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        issues = validate_cart_stock(self.cart)
        self.assertEqual(len(issues), 0)
    
    def test_insufficient_stock(self):
        """Test cart with insufficient stock."""
        from ..services import validate_cart_stock
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=5)
        issues = validate_cart_stock(self.cart)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['requested'], 5)
        self.assertEqual(issues[0]['available'], 2)


class CheckoutFormPhoneTest(TestCase):
    """Tests for phone validation in CheckoutForm."""
    
    def test_valid_phone(self):
        """Test valid phone numbers."""
        form = CheckoutForm(data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '9876543210',
            'address_line1': '123 Street',
            'city': 'City',
            'state': 'State',
            'country': 'India',
            'zip_code': '123456'
        })
        self.assertTrue(form.is_valid())
    
    def test_valid_phone_with_format(self):
        """Test phone with formatting."""
        form = CheckoutForm(data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+91-98765-43210',
            'address_line1': '123 Street',
            'city': 'City',
            'state': 'State',
            'country': 'India',
            'zip_code': '123456'
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_phone_too_short(self):
        """Test phone with too few digits."""
        form = CheckoutForm(data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '12345',
            'address_line1': '123 Street',
            'city': 'City',
            'state': 'State',
            'country': 'India',
            'zip_code': '123456'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
