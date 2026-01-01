"""
Management command to create superuser from environment variables.
Used for deployment on platforms without shell access (e.g., Render free tier).
"""
import os
from django.core.management.base import BaseCommand
from store.models import User


class Command(BaseCommand):
    help = 'Create superuser from environment variables if not exists'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'tremors')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'tremors@amanzon.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD not set, skipping superuser creation'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists'))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
