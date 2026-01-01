"""Context processor for cart and wishlist counts."""

from django.db.models import Sum


def cart_wishlist_count(request):
    """Add cart and wishlist counts to all templates."""
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        # CQ-01: Use aggregation to avoid N+1 query
        if hasattr(request.user, 'cart'):
            result = request.user.cart.items.aggregate(total=Sum('quantity'))
            cart_count = result['total'] or 0
        
        # Get wishlist count
        wishlist_count = request.user.wishlist.count()
    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }

