"""
Management command to seed the database with sample products.
Uses Unsplash for product images.
"""
import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from store.models import Category, SubCategory, Product, Coupon
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    """Create sample products for testing and development."""
    
    help = 'Seed the database with sample categories and products for testing'

    # Unsplash image URLs for different categories
    IMAGES = {
        'electronics': [
            'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',  # Headphones
            'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',  # Watch
            'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400',  # Smart watch
            'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400',  # Headphones 2
            'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=400',  # Camera
        ],
        'fashion': [
            'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',  # Jeans
            'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400',  # T-shirt
            'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400',  # Jacket
            'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400',  # Clothes
            'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400',  # Shirt
        ],
        'shoes': [
            'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',  # Red Nike
            'https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=400',  # White sneaker
            'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400',  # Colorful Nike
            'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400',  # Running shoe
            'https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=400',  # Boots
        ],
        'accessories': [
            'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',  # Backpack
            'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400',  # Watch
            'https://images.unsplash.com/photo-1509941943102-10c232fc06e0?w=400',  # Wallet
            'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400',  # Sunglasses
            'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400',  # Bag
        ],
        'home': [
            'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400',  # Lamp
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400',  # Kitchen
            'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=400',  # Living room
            'https://images.unsplash.com/photo-1484101403633-571c270c58a5?w=400',  # Desk
            'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400',  # Sofa
        ],
    }

    PRODUCTS = [
        # Electronics
        {'name': 'Wireless Bluetooth Headphones', 'cat': 'electronics', 'sub': 'audio', 'price': 2499, 'orig': 3999, 'desc': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear sound quality. Perfect for music lovers and professionals.'},
        {'name': 'Smart Fitness Watch Pro', 'cat': 'electronics', 'sub': 'wearables', 'price': 4999, 'orig': 6999, 'desc': 'Advanced fitness tracker with heart rate monitoring, GPS, sleep tracking, and 7-day battery life. Water-resistant up to 50m.'},
        {'name': 'Premium Smart Watch', 'cat': 'electronics', 'sub': 'wearables', 'price': 8999, 'orig': 12999, 'desc': 'Elegant smartwatch with AMOLED display, health monitoring, cellular connectivity, and premium stainless steel finish.'},
        {'name': 'Studio Monitor Headphones', 'cat': 'electronics', 'sub': 'audio', 'price': 5999, 'orig': 7999, 'desc': 'Professional-grade studio headphones with exceptional clarity and flat frequency response. Ideal for audio production.'},
        {'name': 'Compact Digital Camera', 'cat': 'electronics', 'sub': 'cameras', 'price': 34999, 'orig': 44999, 'desc': 'High-resolution compact camera with 4K video, 20x optical zoom, and advanced autofocus system.'},
        
        # Fashion
        {'name': 'Classic Slim Fit Jeans', 'cat': 'fashion', 'sub': 'bottoms', 'price': 1299, 'orig': 1999, 'desc': 'Comfortable slim-fit jeans made from premium stretch denim. Available in multiple washes.'},
        {'name': 'Organic Cotton T-Shirt', 'cat': 'fashion', 'sub': 'tops', 'price': 599, 'orig': 899, 'desc': '100% organic cotton t-shirt with a relaxed fit. Soft, breathable, and eco-friendly.'},
        {'name': 'Winter Puffer Jacket', 'cat': 'fashion', 'sub': 'outerwear', 'price': 3499, 'orig': 4999, 'desc': 'Warm and lightweight puffer jacket with water-resistant coating. Perfect for cold weather.'},
        {'name': 'Casual Linen Shirt', 'cat': 'fashion', 'sub': 'tops', 'price': 1199, 'orig': 1599, 'desc': 'Breathable linen shirt perfect for summer. Relaxed fit with button-down collar.'},
        {'name': 'Designer Printed Dress', 'cat': 'fashion', 'sub': 'dresses', 'price': 2499, 'orig': 3499, 'desc': 'Elegant printed dress with flattering silhouette. Perfect for any occasion.'},
        
        # Shoes
        {'name': 'Sport Running Shoes', 'cat': 'shoes', 'sub': 'athletic', 'price': 3999, 'orig': 5999, 'desc': 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Designed for maximum performance.'},
        {'name': 'White Leather Sneakers', 'cat': 'shoes', 'sub': 'casual', 'price': 2499, 'orig': 3499, 'desc': 'Classic white leather sneakers with minimalist design. Versatile and timeless.'},
        {'name': 'Colorful Athletic Trainers', 'cat': 'shoes', 'sub': 'athletic', 'price': 4499, 'orig': 5999, 'desc': 'Bold and vibrant trainers with air cushion technology. Stand out from the crowd.'},
        {'name': 'Performance Running Shoe', 'cat': 'shoes', 'sub': 'athletic', 'price': 5999, 'orig': 7999, 'desc': 'Elite performance running shoes with carbon fiber plate. Built for speed.'},
        {'name': 'Classic Leather Boots', 'cat': 'shoes', 'sub': 'boots', 'price': 4999, 'orig': 6499, 'desc': 'Handcrafted leather boots with durable construction. Timeless style meets modern comfort.'},
        
        # Accessories
        {'name': 'Urban Travel Backpack', 'cat': 'accessories', 'sub': 'bags', 'price': 1999, 'orig': 2999, 'desc': 'Spacious backpack with laptop compartment, multiple pockets, and water-resistant fabric.'},
        {'name': 'Luxury Analog Watch', 'cat': 'accessories', 'sub': 'watches', 'price': 7999, 'orig': 9999, 'desc': 'Elegant analog watch with Swiss movement, sapphire crystal, and genuine leather strap.'},
        {'name': 'Leather Bifold Wallet', 'cat': 'accessories', 'sub': 'wallets', 'price': 999, 'orig': 1499, 'desc': 'Premium leather wallet with RFID protection, multiple card slots, and bill compartments.'},
        {'name': 'Designer Sunglasses', 'cat': 'accessories', 'sub': 'eyewear', 'price': 2499, 'orig': 3999, 'desc': 'Stylish sunglasses with UV400 protection and polarized lenses. Includes case.'},
        {'name': 'Canvas Messenger Bag', 'cat': 'accessories', 'sub': 'bags', 'price': 1499, 'orig': 2199, 'desc': 'Vintage-style canvas messenger bag with leather accents. Perfect for everyday use.'},
        
        # Home
        {'name': 'Modern Desk Lamp', 'cat': 'home', 'sub': 'lighting', 'price': 1299, 'orig': 1799, 'desc': 'Sleek LED desk lamp with adjustable brightness, color temperature, and USB charging port.'},
        {'name': 'Premium Kitchen Set', 'cat': 'home', 'sub': 'kitchen', 'price': 3999, 'orig': 5499, 'desc': 'Complete kitchen essentials set with cookware, utensils, and storage containers.'},
        {'name': 'Cozy Throw Blanket', 'cat': 'home', 'sub': 'decor', 'price': 999, 'orig': 1499, 'desc': 'Ultra-soft throw blanket made from premium microfiber. Machine washable.'},
        {'name': 'Ergonomic Desk Organizer', 'cat': 'home', 'sub': 'office', 'price': 799, 'orig': 1199, 'desc': 'Multi-compartment desk organizer to keep your workspace tidy and efficient.'},
        {'name': 'Velvet Cushion Set', 'cat': 'home', 'sub': 'decor', 'price': 1499, 'orig': 1999, 'desc': 'Set of 4 luxury velvet cushions with removable covers. Elevate your living space.'},
    ]

    def download_image(self, url, product_name):
        """Download image from URL and return as ContentFile."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filename = f"{slugify(product_name)}.jpg"
                return ContentFile(response.content, name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to download image: {e}'))
        return None

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...\n')

        # Create categories
        categories = {
            'electronics': Category.objects.get_or_create(name='Electronics', slug='electronics')[0],
            'fashion': Category.objects.get_or_create(name='Fashion', slug='fashion')[0],
            'shoes': Category.objects.get_or_create(name='Shoes', slug='shoes')[0],
            'accessories': Category.objects.get_or_create(name='Accessories', slug='accessories')[0],
            'home': Category.objects.get_or_create(name='Home & Living', slug='home-living')[0],
        }
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # Create subcategories
        subcategories = {}
        sub_data = {
            'electronics': ['audio', 'wearables', 'cameras'],
            'fashion': ['tops', 'bottoms', 'outerwear', 'dresses'],
            'shoes': ['athletic', 'casual', 'boots'],
            'accessories': ['bags', 'watches', 'wallets', 'eyewear'],
            'home': ['lighting', 'kitchen', 'decor', 'office'],
        }
        for cat_key, subs in sub_data.items():
            for sub in subs:
                key = f"{cat_key}_{sub}"
                subcategories[sub] = SubCategory.objects.get_or_create(
                    category=categories[cat_key],
                    name=sub.capitalize(),
                    slug=sub
                )[0]
        self.stdout.write(self.style.SUCCESS(f'Created subcategories'))

        # Create products
        image_idx = {k: 0 for k in self.IMAGES.keys()}
        for i, p in enumerate(self.PRODUCTS):
            slug = slugify(p['name'])
            if Product.objects.filter(slug=slug).exists():
                self.stdout.write(f"  Skipping {p['name']} (already exists)")
                continue

            cat = categories[p['cat']]
            sub = subcategories.get(p['sub'])
            
            # Get image URL
            cat_images = self.IMAGES[p['cat']]
            img_url = cat_images[image_idx[p['cat']] % len(cat_images)]
            image_idx[p['cat']] += 1

            self.stdout.write(f"  Creating: {p['name']}...")
            
            # Download image
            image_content = self.download_image(img_url, p['name'])
            
            product = Product.objects.create(
                category=cat,
                subcategory=sub,
                name=p['name'],
                slug=slug,
                description=p['desc'],
                price=p['price'],
                original_price=p['orig'],
                stock=50,
                is_active=True,
            )
            
            if image_content:
                product.image.save(image_content.name, image_content, save=True)
                
            self.stdout.write(self.style.SUCCESS(f"    ✓ {p['name']}"))

        # Create coupons
        Coupon.objects.get_or_create(
            code='WELCOME10',
            defaults={
                'discount_percent': 10,
                'min_order_amount': 500,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=365),
            }
        )
        Coupon.objects.get_or_create(
            code='SAVE20',
            defaults={
                'discount_percent': 20,
                'min_order_amount': 2000,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=90),
            }
        )
        self.stdout.write(self.style.SUCCESS('Created coupons'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('  - 5 categories')
        self.stdout.write('  - 25 products with images')
        self.stdout.write('  - 2 coupons (WELCOME10, SAVE20)')
