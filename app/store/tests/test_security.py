
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

class RateLimitTest(TestCase):
    """Tests for rate limiting middleware."""

    def setUp(self):
        self.client = Client()
        # clear cache before each test
        cache.clear()

    def test_login_rate_limit(self):
        """Test login rate limiting."""
        url = reverse('store:login')
        
        # Send 5 allowed requests
        for _ in range(5):
            response = self.client.post(url, {'email': 'test@example.com', 'password': 'pass'})
            self.assertNotEqual(response.status_code, 429)
            
        # Send 6th request (should be blocked)
        response = self.client.post(url, {'email': 'test@example.com', 'password': 'pass'})
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Too many requests', status_code=429)

    def test_register_rate_limit(self):
        """Test register rate limiting."""
        url = reverse('store:register')
        
        # Send 5 allowed requests
        for _ in range(5):
            response = self.client.post(url, {})
            self.assertNotEqual(response.status_code, 429)
            
        # Send 6th request (should be blocked)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 429)
