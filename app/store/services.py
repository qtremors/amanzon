"""
Amanzon Business Logic Services

Centralized business logic for cart calculations, shipping, order creation, etc.
"""

from __future__ import annotations
from decimal import Decimal
from io import BytesIO
from typing import TYPE_CHECKING, Any, Optional
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from PIL import Image

if TYPE_CHECKING:
    from .models import Cart, Coupon, Order, User

# ============================================================================
# CONSTANTS (configurable via settings)
# ============================================================================

FREE_SHIPPING_THRESHOLD = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 500)))
SHIPPING_COST = Decimal(str(getattr(settings, 'SHIPPING_COST', 50)))
OTP_EXPIRY_SECONDS = 600  # 10 minutes
MAX_IMAGE_SIZE = (800, 800)
IMAGE_QUALITY = 85


# ============================================================================
# IMAGE OPTIMIZATION
# ============================================================================

def optimize_image(
    image_field: Any,
    max_size: tuple[int, int] = MAX_IMAGE_SIZE,
    quality: int = IMAGE_QUALITY
) -> InMemoryUploadedFile:
    """
    Resize and compress an uploaded image.
    
    Args:
        image_field: Django ImageField or uploaded file
        max_size: Tuple (width, height) for max dimensions
        quality: JPEG quality (1-100)
    
    Returns:
        InMemoryUploadedFile with optimized image
    """
    img = Image.open(image_field)
    
    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if larger than max_size
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    
    # Create new file
    return InMemoryUploadedFile(
        file=buffer,
        field_name='image',
        name=image_field.name.rsplit('.', 1)[0] + '.jpg',
        content_type='image/jpeg',
        size=buffer.getbuffer().nbytes,
        charset=None
    )


# ============================================================================
# SHIPPING & CART CALCULATIONS
# ============================================================================

def calculate_shipping(subtotal: Decimal) -> Decimal:
    """
    Calculate shipping cost based on subtotal.
    Free shipping for orders >= FREE_SHIPPING_THRESHOLD.
    """
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0')
    return SHIPPING_COST


def calculate_discount(subtotal: Decimal, coupon: Optional[Coupon]) -> Decimal:
    """
    Calculate discount amount for a coupon.
    Returns 0 if coupon is invalid or doesn't meet minimum order.
    """
    if not coupon:
        return Decimal('0')
    
    if not coupon.is_valid():
        return Decimal('0')
    
    if subtotal < coupon.min_order_amount:
        return Decimal('0')
    
    return (subtotal * coupon.discount_percent) / 100


def calculate_cart_totals(cart: Cart, coupon: Optional[Coupon] = None) -> dict[str, Decimal]:
    """
    Calculate all cart totals including subtotal, shipping, discount, and total.
    
    Returns dict with:
        - subtotal: Sum of all item prices
        - shipping: Shipping cost (0 if free shipping applies)
        - discount: Discount amount (0 if no valid coupon)
        - total: Final total (subtotal + shipping - discount)
    """
    subtotal = cart.subtotal
    shipping = calculate_shipping(subtotal)
    discount = calculate_discount(subtotal, coupon)
    total = subtotal + shipping - discount
    
    return {
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'total': total,
    }


# ============================================================================
# ORDER SERVICES
# ============================================================================

@transaction.atomic
def create_order_from_cart(user, cart, billing_data, razorpay_order_id, razorpay_payment_id, coupon=None):
    """
    Create an order from a cart after successful payment.
    
    This function:
    1. Creates the Order with billing details
    2. Creates OrderItems for each cart item
    3. Decrements product stock
    4. Records coupon usage if applicable
    5. Clears the cart
    
    Returns the created Order instance.
    """
    from .models import Order, OrderItem, CouponUsage
    
    totals = calculate_cart_totals(cart, coupon)
    
    # Create the order
    order = Order.objects.create(
        user=user,
        first_name=billing_data.get('first_name', ''),
        last_name=billing_data.get('last_name', ''),
        email=billing_data.get('email', ''),
        phone=billing_data.get('phone', ''),
        address_line1=billing_data.get('address_line1', ''),
        address_line2=billing_data.get('address_line2', ''),
        city=billing_data.get('city', ''),
        state=billing_data.get('state', ''),
        country=billing_data.get('country', 'India'),
        zip_code=billing_data.get('zip_code', ''),
        subtotal=totals['subtotal'],
        shipping_cost=totals['shipping'],
        discount=totals['discount'],
        total=totals['total'],
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        is_paid=True,
        status='confirmed',
    )
    
    # Create order items and decrement stock
    for item in cart.items.select_related('product').all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )
        
        # Decrement stock
        item.product.stock -= item.quantity
        item.product.save(update_fields=['stock'])
    
    # Record coupon usage if applicable
    if coupon:
        CouponUsage.objects.create(coupon=coupon, user=user, order=order)
    
    # Clear cart
    cart.items.all().delete()
    
    return order


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer.
    Returns True if successful, False otherwise.
    """
    try:
        send_mail(
            subject=f'Order Confirmation - #{order.id}',
            message=f'''Hi {order.first_name},

Thank you for your order!

Order ID: #{order.id}
Total: ₹{order.total}
Status: {order.get_status_display()}

We'll notify you when your order ships.

Best regards,
Amanzon Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


@transaction.atomic
def cancel_order(order):
    """
    Cancel an order, restore stock, and process refund if paid.
    
    Returns (success, message) tuple.
    """
    if order.status not in ['pending', 'confirmed']:
        return False, 'Order cannot be cancelled in its current state.'
    
    # Process Refund FIRST if paid (before restoring stock)
    if order.is_paid and order.razorpay_payment_id:
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            refund_amount = int(order.total * 100)
            client.payment.refund(order.razorpay_payment_id, {'amount': refund_amount})
        except Exception as e:
            # Refund failed - do not cancel order
            return False, f'Refund failed: {str(e)}. Order not cancelled.'
    
    # Refund succeeded (or order was unpaid) - now restore stock
    for item in order.items.select_related('product').all():
        if item.product:  # Product may have been deleted
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
    
    order.status = 'cancelled'
    order.save()
    
    return True, 'Order cancelled successfully.'


# ============================================================================
# COUPON SERVICES
# ============================================================================

def get_valid_coupon(code, user=None):
    """
    Get a valid coupon by code.
    
    Returns (coupon, error_message) tuple.
    If valid, error_message is None.
    If invalid, coupon is None.
    """
    from .models import Coupon, CouponUsage
    
    if not code:
        return None, 'Please enter a coupon code.'
    
    try:
        coupon = Coupon.objects.get(code__iexact=code.strip())
    except Coupon.DoesNotExist:
        return None, 'Invalid coupon code.'
    
    if not coupon.is_valid():
        return None, 'This coupon has expired.'
    
    # Check if user has already used this coupon
    if user and CouponUsage.objects.filter(coupon=coupon, user=user).exists():
        return None, 'You have already used this coupon.'
    
    return coupon, None


# ============================================================================
# STOCK VALIDATION
# ============================================================================

def validate_cart_stock(cart):
    """
    Validate that all items in cart are still in stock.
    
    Returns list of items with insufficient stock.
    Each item is a dict with 'product', 'requested', 'available'.
    """
    issues = []
    
    for item in cart.items.select_related('product').all():
        if item.quantity > item.product.stock:
            issues.append({
                'product': item.product,
                'requested': item.quantity,
                'available': item.product.stock,
            })
    
    return issues
