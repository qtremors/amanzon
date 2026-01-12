import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils import timezone

logger = logging.getLogger(__name__)


class User(AbstractUser):
    """Extended User model with profile picture and OTP for password reset."""
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    verification_token_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Optimize profile picture on upload
        if self.profile_picture and hasattr(self.profile_picture, 'file'):
            from . import services
            try:
                self.profile_picture = services.optimize_image(self.profile_picture)
            except Exception as e:
                logger.warning(
                    f"Failed to optimize profile picture for user {self.username}: {e}"
                )
                # Keep original if optimization fails
        super().save(*args, **kwargs)


class Address(models.Model):
    """Saved shipping/billing address for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')  # Home, Work, etc.
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    # CR-3: Use getattr with fallback to prevent AttributeError if setting is missing
    country = models.CharField(max_length=100, default=getattr(settings, 'DEFAULT_COUNTRY', 'India'))
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.label} - {self.first_name} {self.last_name}, {self.city}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # If this is the first address, make it default
        elif not self.pk and not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)


class Category(models.Model):
    """Product category."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Product subcategory linked to a parent category."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'Subcategories'
        ordering = ['name']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Product(models.Model):
    """Product with category, pricing, and rating."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original price before discount")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0

    @property
    def discount_percent(self):
        if self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def save(self, *args, **kwargs):
        # Optimize product image on upload
        if self.image and hasattr(self.image, 'file'):
            from . import services
            try:
                self.image = services.optimize_image(self.image)
            except Exception as e:
                logger.warning(
                    f"Failed to optimize image for product {self.name}: {e}"
                )
                # Keep original if optimization fails
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Shopping cart for a user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Individual item in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    """Wishlist item for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.product.name}"


class Coupon(models.Model):
    """Discount coupon."""
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to


class CouponUsage(models.Model):
    """Track coupon usage per user to prevent reuse."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['coupon', 'user']

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"


class Order(models.Model):
    """Customer order."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Billing details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    is_paid = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    """Individual item in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Saved in case product is deleted
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Review(models.Model):
    """Product review by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class ContactMessage(models.Model):
    """Contact form submission."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"
