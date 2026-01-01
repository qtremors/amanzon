from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import ContactMessage
from ..forms import ContactForm

def contact(request):
    """Contact page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(**form.cleaned_data)
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('store:contact')
    else:
        form = ContactForm()
    
    return render(request, 'store/contact.html', {'form': form})
