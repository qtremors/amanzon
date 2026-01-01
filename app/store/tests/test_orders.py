
import decimal
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from ..models import User, Product, Category, Order, OrderItem, Cart

class OrderCancellationTest(TestCase):
    """Tests for order cancellation logic."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='desc',
            price=decimal.Decimal('100.00'),
            original_price=decimal.Decimal('100.00'),
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            stock=10
        )
        self.client.login(username='testuser', password='password')

    def test_cancel_unpaid_order_restores_stock(self):
        """Test cancelling an unpaid order restores stock."""
        # Create order
        order = Order.objects.create(
            user=self.user,
            total=decimal.Decimal('100.00'),
            subtotal=decimal.Decimal('100.00'),
            status='pending',
            is_paid=False
        )
        OrderItem.objects.create(order=order, product=self.product, price=self.product.price, quantity=2)
        
        # Deduct stock initially (simulating purchase)
        self.product.stock -= 2
        self.product.save()
        
        # Cancel order
        response = self.client.get(reverse('store:cancel_order', args=[order.id]), follow=True)
        
        self.assertContains(response, 'Order cancelled successfully')
        
        # Check stock restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        
        # Check status
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

    @patch('store.services.razorpay.Client')
    def test_cancel_paid_order_refunds(self, mock_client_cls):
        """Test cancelling a paid order initiates refund."""
        # Create paid order
        order = Order.objects.create(
            user=self.user,
            total=decimal.Decimal('100.00'),
            subtotal=decimal.Decimal('100.00'),
            status='confirmed',
            is_paid=True,
            razorpay_payment_id='pay_123'
        )
        OrderItem.objects.create(order=order, product=self.product, price=self.product.price, quantity=1)
        
        # Deduct stock
        self.product.stock -= 1
        self.product.save()
        
        # Mock Razorpay
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        # Cancel order
        response = self.client.get(reverse('store:cancel_order', args=[order.id]), follow=True)
        
        self.assertContains(response, 'Order cancelled successfully')
        
        # Verify refund called
        mock_client.payment.refund.assert_called_once_with('pay_123', {'amount': 10000}) # 100 * 100
        
        # Check stock restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_cannot_cancel_shipped_order(self):
        """Test cannot cancel shipped order."""
        order = Order.objects.create(
            user=self.user,
            total=decimal.Decimal('100.00'),
            subtotal=decimal.Decimal('100.00'),
            status='shipped',
            is_paid=True
        )
        
        response = self.client.get(reverse('store:cancel_order', args=[order.id]), follow=True)
        
        self.assertContains(response, 'This order cannot be cancelled')
        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')


class CheckoutFlowTest(TestCase):
    """Tests for checkout and payment flow."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user(username='checkoutuser', email='checkout@test.com', password='password')
        self.category = Category.objects.create(name='Checkout Cat', slug='checkout-cat')
        self.product = Product.objects.create(
            category=self.category,
            name='Checkout Product',
            slug='checkout-product',
            description='desc',
            price=decimal.Decimal('50.00'),
            original_price=decimal.Decimal('50.00'),
            image=SimpleUploadedFile(name='test.jpg', content=b'', content_type='image/jpeg'),
            stock=10
        )

    def test_checkout_requires_login(self):
        """Test checkout redirects anonymous users to login."""
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_checkout_requires_cart_items(self):
        """Test checkout redirects if cart is empty."""
        self.client.login(username='checkoutuser', password='password')
        # Create empty cart
        Cart.objects.create(user=self.user)
        response = self.client.get(reverse('store:checkout'), follow=True)
        self.assertContains(response, 'Your cart is empty')

    @patch('store.views.orders.razorpay.Client')
    def test_checkout_page_loads_with_items(self, mock_client_cls):
        """Test checkout page loads when cart has items."""
        self.client.login(username='checkoutuser', password='password')
        
        # Create cart with item
        cart = Cart.objects.create(user=self.user)
        from ..models import CartItem
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        # Mock Razorpay order creation
        mock_client = MagicMock()
        mock_client.order.create.return_value = {'id': 'order_test123', 'amount': 5000}
        mock_client_cls.return_value = mock_client
        
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Checkout')

    @patch('store.views.orders.razorpay.Client')
    @patch('store.services.send_order_confirmation_email')
    def test_payment_callback_creates_order(self, mock_email, mock_client_cls):
        """Test successful payment callback creates order."""
        self.client.login(username='checkoutuser', password='password')
        
        # Create cart with item
        cart = Cart.objects.create(user=self.user)
        from ..models import CartItem
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        # Mock Razorpay
        mock_client = MagicMock()
        mock_client.utility.verify_payment_signature.return_value = True
        mock_client_cls.return_value = mock_client
        
        # Submit payment callback
        response = self.client.post(reverse('store:payment_callback'), {
            'razorpay_payment_id': 'pay_test123',
            'razorpay_order_id': 'order_test123',
            'razorpay_signature': 'sig_test123',
            'billing_first_name': 'Test',
            'billing_last_name': 'User',
            'billing_email': 'test@test.com',
            'billing_phone': '1234567890',
            'billing_address_line1': '123 Test St',
            'billing_city': 'Mumbai',
            'billing_state': 'MH',
            'billing_zip_code': '400001',
        }, follow=True)
        
        # Check order created
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.is_paid, True)
        self.assertEqual(order.status, 'confirmed')
        
        # Check stock deducted
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        
        # Check email sent
        mock_email.assert_called_once()
