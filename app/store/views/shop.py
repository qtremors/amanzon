from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg

from ..models import Category, Product, Wishlist, Review
from ..forms import ReviewForm

def index(request):
    """Homepage with featured products."""
    categories = Category.objects.prefetch_related('subcategories').all()[:6]
    featured_products = Product.objects.filter(is_active=True).select_related('category')[:8]
    
    # Wishlist IDs for current user
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(request.user.wishlist.values_list('product_id', flat=True))
    
    return render(request, 'store/index.html', {
        'categories': categories,
        'featured_products': featured_products,
        'wishlist_ids': wishlist_ids,
    })


def shop(request, category_slug=None):
    """Shop page with filtering and pagination."""
    products = Product.objects.filter(is_active=True).select_related('category', 'subcategory').annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    )
    categories = Category.objects.prefetch_related('subcategories').all()
    
    # Filter by category
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    
    # Filter by subcategory
    subcategory_id = request.GET.get('subcategory')
    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)
    
    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Wishlist IDs for current user
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(request.user.wishlist.values_list('product_id', flat=True))
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'wishlist_ids': wishlist_ids,
        'query': query,
    })


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory').prefetch_related('reviews__user'),
        slug=slug, is_active=True
    )
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    })


@login_required
def wishlist(request):
    """Wishlist page."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items,
    })


@login_required
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        messages.info(request, f'Removed "{product.name}" from wishlist.')
    else:
        messages.success(request, f'Added "{product.name}" to wishlist.')
    
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'store:shop'))
    return redirect(next_url)


@login_required
@require_POST
def add_review(request, product_id):
    """Add a product review."""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('store:product_detail', slug=product.slug)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        Review.objects.create(
            user=request.user,
            product=product,
            rating=form.cleaned_data['rating'],
            comment=form.cleaned_data['comment'],
        )
        messages.success(request, 'Thank you for your review!')
    
    return redirect('store:product_detail', slug=product.slug)
