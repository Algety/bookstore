from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from cart.contexts import cart_contents

import stripe

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect(reverse('books'))
    
    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)
    
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51SA93nQ9fuUxkm6fkPRMw4FVSf0AOgTWaQd0ojSckPuR8ISBCX6rh6npijiNCIgdwkYoCVCTn9mKaYg2nT6gR7xr00iDEDTWTP',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)