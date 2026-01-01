
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from ..models import User

class SessionSecurityTest(TestCase):
    """Tests for session security."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client = Client()

    def test_session_fixation_protection(self):
        """Test that session ID changes after login."""
        # Create an anonymous session
        self.client.get(reverse('store:index'))
        pre_login_session_key = self.client.session.session_key

        # Login
        self.client.login(username='testuser', password='password')
        post_login_session_key = self.client.session.session_key

        # Verify session key changed
        self.assertNotEqual(pre_login_session_key, post_login_session_key)

    def test_session_cookie_httponly(self):
        """Test that session cookie is HttpOnly."""
        # Perform login to ensure session cookie is set
        response = self.client.post(reverse('store:login'), {
            'email': 'test@example.com', 
            'password': 'password'
        })
        
        session_cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
        self.assertIsNotNone(session_cookie, "Session cookie not set after login")
        self.assertTrue(session_cookie.get('httponly'), "Session cookie should be HttpOnly")
