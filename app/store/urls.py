from django.urls import path
from django.contrib.auth import views as auth_views
from .views import auth, shop, cart, orders, main

app_name = 'store'

urlpatterns = [
    # Home & Shop
    path('', shop.index, name='index'),
    path('shop/', shop.shop, name='shop'),
    path('shop/<slug:category_slug>/', shop.shop, name='shop_category'),
    path('product/<slug:slug>/', shop.product_detail, name='product_detail'),
    path('product/<int:product_id>/wishlist/', shop.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', shop.wishlist, name='wishlist'),
    path('product/<int:product_id>/review/', shop.add_review, name='add_review'),
    
    # Cart
    path('cart/', cart.cart, name='cart'),
    path('cart/add/<int:product_id>/', cart.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', cart.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', cart.remove_from_cart, name='remove_from_cart'),
    path('cart/apply-coupon/', cart.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', cart.remove_coupon, name='remove_coupon'),
    
    # Checkout & Orders
    path('checkout/', orders.checkout, name='checkout'),
    path('payment-callback/', orders.payment_callback, name='payment_callback'),
    path('orders/', orders.orders, name='orders'),
    path('orders/<int:order_id>/', orders.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', orders.cancel_order, name='cancel_order'),
    
    # Contact
    path('contact/', main.contact, name='contact'),
    
    # Authentication
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register, name='register'),
    path('register/verification-sent/', auth.verification_sent, name='verification_sent'),
    path('verify-email/<str:token>/', auth.verify_email, name='verify_email'),
    path('profile/', auth.profile, name='profile'),
    
    # Password Reset
    path('password-reset/', auth.password_reset, name='password_reset'),
    path('password-reset/confirm/', auth.password_reset_confirm, name='password_reset_confirm'),
]
