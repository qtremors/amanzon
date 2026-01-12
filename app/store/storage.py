"""
Custom storage backend for Supabase Storage.
Handles file uploads for profile pictures and product images.
"""

import logging
import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from supabase import create_client

logger = logging.getLogger(__name__)


class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage.
    Uploads files to a Supabase bucket and returns public URLs.
    Uses lazy initialization for faster app startup.
    """

    def __init__(self):
        self.supabase_url = getattr(settings, 'SUPABASE_URL', '')
        self.supabase_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '')
        self.bucket_name = getattr(settings, 'SUPABASE_BUCKET', 'media')
        self._client = None  # Lazy initialization

    @property
    def client(self):
        """Lazy-load Supabase client on first use."""
        if self._client is None and self.supabase_url and self.supabase_key:
            self._client = create_client(self.supabase_url, self.supabase_key)
        return self._client

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
        except Exception as e:
            logger.warning(f"Failed to delete file from Supabase Storage: {path} - {e}")

    def exists(self, name):
        """Check if file exists in Supabase Storage using paginated list API."""
        if not self.client:
            return False

        path = self._get_storage_path(name)
        try:
            folder = '/'.join(path.split('/')[:-1]) or ''
            filename = path.split('/')[-1]
            
            # Paginate through all files in folder to find match
            limit = 100
            offset = 0
            while True:
                result = self.client.storage.from_(self.bucket_name).list(
                    folder, {"limit": limit, "offset": offset, "search": filename}
                )
                if not result:
                    break
                if any(item.get('name') == filename for item in result):
                    return True
                if len(result) < limit:
                    break
                offset += limit
            return False
        except Exception:
            return False

    def url(self, name):
        """Return public URL for the file."""
        path = self._get_storage_path(name)
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{path}"

    def size(self, name):
        """Return file size from Supabase metadata."""
        if not self.client:
            return 0
            
        try:
            path = self._get_storage_path(name)
            folder = '/'.join(path.split('/')[:-1]) or ''
            filename = path.split('/')[-1]
            
            # Paginate through all files in folder to find match
            limit = 100
            offset = 0
            while True:
                result = self.client.storage.from_(self.bucket_name).list(
                    folder, {"limit": limit, "offset": offset, "search": filename}
                )
                if not result:
                    break
                for item in result:
                    if item.get('name') == filename:
                        return item.get('metadata', {}).get('size', 0)
                if len(result) < limit:
                    break
                offset += limit
            return 0
        except Exception:
            return 0

    def get_valid_name(self, name):
        """Return a valid filename."""
        return name.replace('\\', '/')

    def get_available_name(self, name, max_length=None):
        """Return available filename (overwrite existing with upsert)."""
        return self.get_valid_name(name)
