from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import ContactMessage
from ..forms import ContactForm

def contact(request):
    """Contact page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Exclude honeypot field when creating message
            data = {k: v for k, v in form.cleaned_data.items() if k != 'website'}
            ContactMessage.objects.create(**data)
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('store:contact')
    else:
        form = ContactForm()
    
    return render(request, 'store/contact.html', {'form': form})

def about(request):
    """About page (mock)."""
    return render(request, 'store/about.html')

def faq(request):
    """FAQ page (mock)."""
    return render(request, 'store/faq.html')

def blog(request):
    """Blog page (mock)."""
    return render(request, 'store/blog.html')

def privacy(request):
    """Privacy Policy page (mock)."""
    return render(request, 'store/privacy.html')

def terms(request):
    """Terms of Service page (mock)."""
    return render(request, 'store/terms.html')
