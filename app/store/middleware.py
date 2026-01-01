"""
Amanzon Middleware

Rate limiting and security middleware.
"""

from django.core.cache import cache
from django.http import HttpResponse


class RateLimitMiddleware:
    """
    Rate limiting middleware for sensitive endpoints.
    
    Currently limits:
    - Password reset OTP requests: 3 per 10 minutes per IP
    """
    
    # Rate limit configurations: path -> (max_requests, window_seconds)
    RATE_LIMITS = {
        '/password-reset/': (3, 600),  # 3 requests per 10 minutes
        '/login/': (5, 60),            # 5 requests per minute
        '/register/': (5, 60),         # 5 requests per minute
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only check POST requests for rate-limited paths
        if request.method == 'POST':
            for path, (max_requests, window) in self.RATE_LIMITS.items():
                if request.path == path:
                    if not self._check_rate_limit(request, path, max_requests, window):
                        return HttpResponse(
                            'Too many requests. Please try again later.',
                            status=429
                        )
        
        return self.get_response(request)
    
    def _check_rate_limit(self, request, path, max_requests, window):
        """
        Check if request is within rate limit.
        Returns True if allowed, False if rate limited.
        """
        ip = self._get_client_ip(request)
        key = f'rate_limit:{path}:{ip}'
        
        current_count = cache.get(key, 0)
        
        if current_count >= max_requests:
            return False
        
        # Increment counter
        cache.set(key, current_count + 1, window)
        return True
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
