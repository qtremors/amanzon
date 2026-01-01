
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import User
from django.core import mail

class EmailVerificationTest(TestCase):
    """Tests for email verification flow."""

    def setUp(self):
        cache.clear()

    def test_registration_flow(self):
        """Test registration sends email and creates inactive user."""
        response = self.client.post(reverse('store:register'), {
            'username': 'verifyuser',
            'email': 'verify@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:verification_sent'))

        # Check user created but inactive
        user = User.objects.get(username='verifyuser')
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.verification_token)

        # Check email sent
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.verification_token, mail.outbox[0].body)
        self.assertIn('Verify your Amanzon account', mail.outbox[0].subject)

        # Verify email
        verify_url = reverse('store:verify_email', kwargs={'token': user.verification_token})
        response = self.client.get(verify_url, follow=True)
        
        # Reload user
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNone(user.verification_token)
        
        # Check user is logged in
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertContains(response, 'Email verified! You are now logged in.')

    def test_invalid_token(self):
        """Test verification with invalid token."""
        response = self.client.get(reverse('store:verify_email', kwargs={'token': 'invalid-token'}))
        self.assertEqual(response.status_code, 404)
