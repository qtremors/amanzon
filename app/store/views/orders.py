import logging
import uuid

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages

from ..models import Cart, Coupon, CouponUsage, Order
from ..forms import CheckoutForm
from .. import services

logger = logging.getLogger(__name__)

@login_required
def checkout(request):
    """Checkout page with saved address support."""
    from ..models import Address
    
    # Check if Razorpay keys are configured
    razorpay_configured = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
    
    # H2: Use get_or_create instead of get_object_or_404 to handle users without cart
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart_obj.items.select_related('product').all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:shop')
    
    # Validate stock before checkout
    stock_issues = services.validate_cart_stock(cart_obj)
    if stock_issues:
        for issue in stock_issues:
            messages.error(
                request, 
                f'"{issue["product"].name}" only has {issue["available"]} left in stock.'
            )
        return redirect('store:cart')
    
    # Get coupon if applicable
    coupon = None
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            if not coupon.is_valid() or CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                coupon = None
                request.session.pop('coupon_code', None)
        except Coupon.DoesNotExist:
            request.session.pop('coupon_code', None)
    
    # Calculate totals using services layer
    totals = services.calculate_cart_totals(cart_obj, coupon)
    
    # Create Razorpay order (or dummy order in demo mode)
    if razorpay_configured:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(totals['total'] * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': 1,
        })
    else:
        # Demo mode: Create a dummy order object
        razorpay_order = {
            'id': f'order_demo_{uuid.uuid4().hex[:8]}',
            'amount': int(totals['total'] * 100),
            'currency': 'INR',
        }

    # Get saved addresses for the user
    saved_addresses = request.user.addresses.all()
    default_address = saved_addresses.filter(is_default=True).first()
    
    # Handle address selection from query param
    selected_address_id = request.GET.get('address')
    if selected_address_id:
        try:
            selected_address = saved_addresses.get(id=selected_address_id)
        except Address.DoesNotExist:
            selected_address = default_address
    else:
        selected_address = default_address
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        # Form validation handled by JavaScript before Razorpay
    else:
        # Prefill form with selected address or user info
        if selected_address:
            form = CheckoutForm(initial={
                'email': request.user.email,
                'first_name': selected_address.first_name,
                'last_name': selected_address.last_name,
                'phone': selected_address.phone,
                'address_line1': selected_address.address_line1,
                'address_line2': selected_address.address_line2,
                'city': selected_address.city,
                'state': selected_address.state,
                'country': selected_address.country,
                'zip_code': selected_address.zip_code,
            })
        else:
            form = CheckoutForm(initial={
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            })
    
    return render(request, 'store/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'discount': totals['discount'],
        'total': totals['total'],
        'razorpay_order': razorpay_order,
        'saved_addresses': saved_addresses,
        'selected_address': selected_address,
        'razorpay_key': settings.RAZORPAY_KEY_ID or 'demo_key',
        'demo_mode': not razorpay_configured,
    })


@login_required
@require_POST
@transaction.atomic
def payment_callback(request):
    """Handle Razorpay payment callback with atomic transaction."""
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    
    # SEC-03: Idempotency check - prevent duplicate order creation
    if Order.objects.filter(razorpay_order_id=razorpay_order_id).exists():
        existing_order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        messages.info(request, 'Order already processed.')
        return redirect('store:order_detail', order_id=existing_order.id)
    
    # Check if we are in demo mode
    razorpay_configured = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
    
    if razorpay_configured:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            # Verify payment signature first
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            logger.warning(f'Payment signature verification failed for order {razorpay_order_id}')
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('store:checkout')
    else:
        # Demo mode: Skip verification
        if not razorpay_payment_id.startswith('pay_demo_'):
             # Basic check to ensure it looks like a demo payment
             logger.warning(f'Invalid demo payment ID: {razorpay_payment_id}')
        
    try:
        
        # Get billing data from POST (sent from checkout JS)
        billing_data = {
            'first_name': request.POST.get('billing_first_name', ''),
            'last_name': request.POST.get('billing_last_name', ''),
            'email': request.POST.get('billing_email', ''),
            'phone': request.POST.get('billing_phone', ''),
            'address_line1': request.POST.get('billing_address_line1', ''),
            'address_line2': request.POST.get('billing_address_line2', ''),
            'city': request.POST.get('billing_city', ''),
            'state': request.POST.get('billing_state', ''),
            'country': request.POST.get('billing_country', 'India'),
            'zip_code': request.POST.get('billing_zip_code', ''),
        }
        
        cart_obj = Cart.objects.get(user=request.user)
        
        # Get coupon if applicable
        coupon = None
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
                if not coupon.is_valid():
                    coupon = None
            except Coupon.DoesNotExist:
                coupon = None
        
        # Create order using services layer (handles stock deduction, coupon tracking)
        order = services.create_order_from_cart(
            user=request.user,
            cart=cart_obj,
            billing_data=billing_data,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            coupon=coupon,
        )
        
        # Clear session data
        request.session.pop('coupon_code', None)
        
        # Send order confirmation email
        services.send_order_confirmation_email(order)
        
        messages.success(request, 'Order placed successfully!')
        return redirect('store:order_detail', order_id=order.id)
        
    except Exception as e:
        logger.exception(f'Error processing payment callback: {e}')
        messages.error(request, 'An error occurred while processing your order. Please contact support.')
        return redirect('store:checkout')


@login_required
def orders(request):
    """Order history page."""
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    return render(request, 'store/orders.html', {
        'orders': user_orders,
    })


@login_required
def order_detail(request, order_id):
    """Order detail page."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id, user=request.user
    )
    
    return render(request, 'store/order_detail.html', {
        'order': order,
    })


@login_required
@require_POST
def cancel_order(request, order_id):
    """Cancel an order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'confirmed']:
        try:
            success, message = services.cancel_order(order)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception:
            messages.error(request, 'An error occurred while processing the refund/cancellation.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('store:orders')
