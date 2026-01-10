"""
Custom storage backend for Supabase Storage.
Handles file uploads for profile pictures and product images.
"""

import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from supabase import create_client


class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage.
    Uploads files to a Supabase bucket and returns public URLs.
    """

    def __init__(self):
        self.supabase_url = getattr(settings, 'SUPABASE_URL', '')
        self.supabase_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '')
        self.bucket_name = getattr(settings, 'SUPABASE_BUCKET', 'media')
        
        if self.supabase_url and self.supabase_key:
            self.client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.client = None

    def _get_storage_path(self, name):
        """Get the full path in the bucket."""
        # Normalize path separators
        return name.replace('\\', '/')

    def _save(self, name, content):
        """Save file to Supabase Storage."""
        if not self.client:
            raise Exception("Supabase client not configured")

        path = self._get_storage_path(name)
        
        # Read file content
        if hasattr(content, 'read'):
            file_bytes = content.read()
        else:
            file_bytes = content

        # Determine content type
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        if path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif path.endswith('.webp'):
            content_type = 'image/webp'
        elif path.endswith('.gif'):
            content_type = 'image/gif'

        # Upload to Supabase Storage
        self.client.storage.from_(self.bucket_name).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )

        return name

    def _open(self, name, mode='rb'):
        """Retrieve file from Supabase Storage."""
        if not self.client:
            raise Exception("Supabase client not configured")

        path = self._get_storage_path(name)
        response = self.client.storage.from_(self.bucket_name).download(path)

        return ContentFile(response)

    def delete(self, name):
        """Delete file from Supabase Storage."""
        if not self.client:
            return

        path = self._get_storage_path(name)
        try:
            self.client.storage.from_(self.bucket_name).remove([path])
        except Exception:
            pass  # Ignore deletion errors

    def exists(self, name):
        """Check if file exists in Supabase Storage."""
        if not self.client:
            return False

        path = self._get_storage_path(name)
        try:
            # Try to get file info
            self.client.storage.from_(self.bucket_name).download(path)
            return True
        except Exception:
            return False

    def url(self, name):
        """Return public URL for the file."""
        path = self._get_storage_path(name)
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{path}"

    def size(self, name):
        """Return file size (not implemented for Supabase)."""
        return 0

    def get_valid_name(self, name):
        """Return a valid filename."""
        return name.replace('\\', '/')

    def get_available_name(self, name, max_length=None):
        """Return available filename (overwrite existing with upsert)."""
        return self.get_valid_name(name)
