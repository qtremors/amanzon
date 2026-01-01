"""Context processor for cart and wishlist counts."""

def cart_wishlist_count(request):
    """Add cart and wishlist counts to all templates."""
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        # Get cart count
        if hasattr(request.user, 'cart'):
            cart_count = request.user.cart.total_items
        
        # Get wishlist count
        wishlist_count = request.user.wishlist.count()
    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
