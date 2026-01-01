from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Category, SubCategory, Product, Cart, CartItem,
    Wishlist, Coupon, CouponUsage, Order, OrderItem, Review, ContactMessage
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('profile_picture',)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'stock', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'subtotal', 'updated_at']
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'min_order_amount', 'is_active', 'valid_from', 'valid_to']
    list_filter = ['is_active']
    list_editable = ['is_active']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__username']
    readonly_fields = ['coupon', 'user', 'order', 'used_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['user__username', 'email', 'razorpay_order_id']
    inlines = [OrderItemInline]
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    list_editable = ['is_read']
