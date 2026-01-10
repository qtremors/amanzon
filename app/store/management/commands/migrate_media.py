"""
Management command to migrate existing local media files to Supabase Storage.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, User


class Command(BaseCommand):
    help = 'Migrate local media files to Supabase Storage'

    def handle(self, *args, **options):
        # Check if Supabase is configured
        if not getattr(settings, 'SUPABASE_URL', '') or not getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', ''):
            self.stdout.write(self.style.ERROR('Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.'))
            return

        from store.storage import SupabaseStorage
        storage = SupabaseStorage()

        migrated = 0
        failed = 0

        # Migrate product images
        self.stdout.write('Migrating product images...')
        for product in Product.objects.all():
            if product.image:
                try:
                    # Check if already a Supabase URL
                    if product.image.name and not product.image.name.startswith('http'):
                        local_path = os.path.join(settings.MEDIA_ROOT, product.image.name)
                        if os.path.exists(local_path):
                            with open(local_path, 'rb') as f:
                                file_content = f.read()
                            
                            # Upload to Supabase
                            storage._save(product.image.name, file_content)
                            self.stdout.write(self.style.SUCCESS(f'  ✓ {product.name}'))
                            migrated += 1
                        else:
                            self.stdout.write(self.style.WARNING(f'  ⚠ {product.name}: Local file not found'))
                            failed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ {product.name}: {e}'))
                    failed += 1

        # Migrate user profile pictures
        self.stdout.write('\nMigrating user profile pictures...')
        for user in User.objects.exclude(profile_picture='').exclude(profile_picture__isnull=True):
            try:
                if user.profile_picture.name and not user.profile_picture.name.startswith('http'):
                    local_path = os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            file_content = f.read()
                        
                        storage._save(user.profile_picture.name, file_content)
                        self.stdout.write(self.style.SUCCESS(f'  ✓ {user.username}'))
                        migrated += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'  ⚠ {user.username}: Local file not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ {user.username}: {e}'))
                failed += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Migration complete: {migrated} files migrated, {failed} failed'))
