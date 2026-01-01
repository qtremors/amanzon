import secrets
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from ..models import User
from ..forms import RegisterForm, LoginForm, ProfileForm, PasswordResetForm, PasswordResetConfirmForm

def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('store:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Look up user by email first, then authenticate by username
            email = form.cleaned_data['email']
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=form.cleaned_data['password']
                )
            except User.DoesNotExist:
                user = None
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'store:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:index')


def register(request):
    """Registration page."""
    if request.user.is_authenticated:
        return redirect('store:index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            # Deactivate user until verified
            user.is_active = False
            user.verification_token = str(uuid.uuid4())
            user.save()
            
            # Send verification email
            verification_link = request.build_absolute_uri(
                reverse('store:verify_email', kwargs={'token': user.verification_token})
            )
            
            send_mail(
                'Verify your Amanzon account',
                f'Click the link to verify your email: {verification_link}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            return redirect('store:verification_sent')
    else:
        form = RegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})


def verification_sent(request):
    """Email verification sent page."""
    return render(request, 'auth/verification_sent.html')


def verify_email(request, token):
    """Verify email address."""
    user = get_object_or_404(User, verification_token=token)
    
    if not user.is_active:
        user.is_active = True
        user.verification_token = None
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, 'Email verified! You are now logged in.')
        return redirect('store:index')
    else:
        messages.info(request, 'Email already verified.')
        return redirect('store:login')


@login_required
def profile(request):
    """User profile page."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('store:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'store/profile.html', {'form': form})


def password_reset(request):
    """Password reset request page."""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                
                # Send email
                send_mail(
                    'Amanzon - Password Reset OTP',
                    f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                request.session['reset_email'] = email
                messages.success(request, 'OTP sent to your email.')
                return redirect('store:password_reset_confirm')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'auth/password_reset.html', {'form': form})


def password_reset_confirm(request):
    """Password reset confirmation page."""
    email = request.session.get('reset_email')
    if not email:
        return redirect('store:password_reset')
    
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=email)
                
                # Check OTP
                if user.otp != form.cleaned_data['otp']:
                    messages.error(request, 'Invalid OTP.')
                    return render(request, 'auth/password_reset_confirm.html', {'form': form})
                
                # Check OTP expiry (10 minutes)
                if user.otp_created_at and (timezone.now() - user.otp_created_at).total_seconds() > 600:
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return redirect('store:password_reset')
                
                # Set new password
                user.set_password(form.cleaned_data['new_password'])
                user.otp = None
                user.otp_created_at = None
                user.save()
                
                del request.session['reset_email']
                messages.success(request, 'Password changed successfully! Please login.')
                return redirect('store:login')
                
            except User.DoesNotExist:
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('store:password_reset')
    else:
        form = PasswordResetConfirmForm()
    
    return render(request, 'auth/password_reset_confirm.html', {'form': form, 'email': email})
