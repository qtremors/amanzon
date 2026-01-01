
from django.test import TestCase, override_settings
from django.core import mail
from django.conf import settings

class EmailSettingsTest(TestCase):
    """Test email sender configuration."""

    @override_settings(DEFAULT_FROM_EMAIL='Amanzon Support <support@amanzon.com>')
    def test_default_from_email_used(self):
        """Test that DEFAULT_FROM_EMAIL is used as the sender."""
        # Send a test email
        mail.send_mail(
            'Subject',
            'Body',
            settings.DEFAULT_FROM_EMAIL,
            ['to@example.com'],
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'Amanzon Support <support@amanzon.com>')
