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

@login_required
def checkout(request):
    """Checkout page."""
    # Validate Razorpay credentials before proceeding
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, 'Payment system is not configured. Please contact support.')
        return redirect('store:cart')
    
    cart_obj = get_object_or_404(Cart, user=request.user)
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
    
    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        'amount': int(totals['total'] * 100),  # Amount in paise
        'currency': 'INR',
        'payment_capture': 1,
    })
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        # Form validation handled by JavaScript before Razorpay
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
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    })


@login_required
@require_POST
@transaction.atomic
def payment_callback(request):
    """Handle Razorpay payment callback with atomic transaction."""
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        # Verify payment signature first
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        
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
        
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('store:checkout')
    except Exception as e:
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
