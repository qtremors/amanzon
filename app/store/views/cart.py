from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from ..models import Cart, CartItem, Product, Coupon, CouponUsage
from .. import services

@login_required
def cart(request):
    """Shopping cart page."""
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart_obj.items.select_related('product').all()
    
    # Get coupon from session
    coupon_code = request.session.get('coupon_code')
    coupon = None
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            # Check if user already used this coupon
            if CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                coupon = None
                request.session.pop('coupon_code', None)
                messages.warning(request, 'You have already used this coupon.')
            elif not coupon.is_valid():
                coupon = None
                request.session.pop('coupon_code', None)
        except Coupon.DoesNotExist:
            request.session.pop('coupon_code', None)
    
    # Use services layer for calculations
    totals = services.calculate_cart_totals(cart_obj, coupon)
    
    return render(request, 'store/cart.html', {
        'cart': cart_obj,
        'cart_items': cart_items,
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'coupon': coupon,
        'discount': totals['discount'],
        'total': totals['total'],
    })


@login_required
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check stock availability
    if product.stock <= 0:
        messages.error(request, f'Sorry, "{product.name}" is out of stock.')
        next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'store:shop'))
        return redirect(next_url)
    
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj, product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Check if adding more would exceed stock
        if cart_item.quantity >= product.stock:
            messages.warning(request, f'Only {product.stock} units of "{product.name}" available.')
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Added "{product.name}" to cart.')
    else:
        messages.success(request, f'Added "{product.name}" to cart.')
    
    # Redirect back to previous page or shop
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'store:shop'))
    return redirect(next_url)


@login_required
@require_POST
def update_cart(request, item_id):
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    action = request.POST.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('store:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed "{product_name}" from cart.')
    return redirect('store:cart')


@login_required
@require_POST
def apply_coupon(request):
    """Apply coupon code."""
    code = request.POST.get('coupon_code', '').strip()
    
    coupon, error = services.get_valid_coupon(code, request.user)
    
    if error:
        messages.error(request, error)
    else:
        request.session['coupon_code'] = code.upper()
        messages.success(request, f'Coupon "{coupon.code}" applied! {coupon.discount_percent}% off.')
    
    return redirect('store:cart')


@login_required
def remove_coupon(request):
    """Remove applied coupon code."""
    request.session.pop('coupon_code', None)
    messages.info(request, 'Coupon removed.')
    return redirect('store:cart')
