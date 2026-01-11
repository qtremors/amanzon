import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterForm(forms.Form):
    """User registration form."""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a username',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create a password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm your password',
    }))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        if password:
            validate_password(password)
        
        return cleaned_data


class LoginForm(forms.Form):
    """User login form."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password',
    }))


class ProfileForm(forms.ModelForm):
    """User profile update form."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_profile_picture(self):
        """Validate profile picture file size and type."""
        picture = self.cleaned_data.get('profile_picture')
        if picture and hasattr(picture, 'size'):
            # Check file size (max 2MB)
            max_size = 2 * 1024 * 1024  # 2MB
            if picture.size > max_size:
                raise forms.ValidationError('Image must be less than 2MB.')
            
            # Check content type
            content_type = getattr(picture, 'content_type', '')
            if content_type and not content_type.startswith('image/'):
                raise forms.ValidationError('File must be an image (JPEG, PNG, GIF, etc.).')
        
        return picture


class AddressForm(forms.Form):
    """Form for creating/editing saved addresses."""
    label = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g., Home, Work, Office',
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    address_line1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Street address',
    }))
    address_line2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment, suite, etc. (optional)',
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    country = forms.CharField(max_length=100, initial='India', widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    is_default = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }))


class ContactForm(forms.Form):
    """Contact page form."""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your email',
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject',
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Your message',
        'rows': 5,
    }))


class ReviewForm(forms.Form):
    """Product review form."""
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.RadioSelect(
        choices=[(i, str(i)) for i in range(1, 6)]
    ))
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Share your thoughts about this product...',
        'rows': 4,
    }))


class CheckoutForm(forms.Form):
    """Checkout billing form."""
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address',
    }))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number',
    }))
    address_line1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Street address',
    }))
    address_line2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment, suite, etc. (optional)',
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City',
    }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'State',
    }))
    country = forms.CharField(max_length=100, initial='India', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Country',
    }))
    zip_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'ZIP / Postal code',
    }))

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone', '')
        # Allow digits, spaces, dashes, plus, and parentheses
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        if not cleaned.isdigit() or len(cleaned) < 10 or len(cleaned) > 15:
            raise forms.ValidationError('Enter a valid phone number (10-15 digits).')
        return phone


class PasswordResetForm(forms.Form):
    """Password reset request form."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
    }))


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form."""
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter OTP',
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm new password',
    }))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        if new_password:
            validate_password(new_password)
        
        return cleaned_data
