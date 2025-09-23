from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import OrderForm
from .models import Order, OrderLineItem
from books.models import Book
from cart.contexts import cart_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    Store cart and user info in the PaymentIntent metadata before final submission.
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'anonymous',
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, (
            "Sorry, your payment cannot be processed right now."
            "Please try again later."
        ))
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect(reverse('books'))

    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key

    try:
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
    except stripe.error.StripeError:
        messages.error(request, "There was an issue connecting to Stripe. Please try again later.")
        return redirect(reverse('view_cart'))

    if request.method == 'POST':
        form_data = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'country': request.POST.get('country'),
            'postcode': request.POST.get('postcode'),
            'town_or_city': request.POST.get('town_or_city'),
            'street_address1': request.POST.get('street_address1'),
            'street_address2': request.POST.get('street_address2'),
            'county': request.POST.get('county'),
        }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save()

            for item_id, quantity in cart.items():
                try:
                    book = Book.objects.get(id=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        book=book,
                        quantity=quantity,
                    )
                    order_line_item.save()
                except Book.DoesNotExist:
                    messages.error(request, (
                        "We couldn’t retrieve one of the products in your cart. "
                        "Please contact us for further assistance.")
                    )
                    order.delete()
                    return redirect(reverse('view_cart'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(
                request,
                "We encountered an issue with your submission. "
                "Kindly verify your information and try again."
            )
    else:
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(
            request,
            "Stripe public key is missing. "
            "Did you forget to set it in your environment?"
        )

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """ Successful checkout """

    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(request, (
        f"Order successfully processed! "
        f"Your order number is {order_number}. A confirmation "
        f"email will be sent to {order.email}."
    ))

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'order_number': order_number,
    }
    return render(request, template, context)


@csrf_exempt
def stripe_webhook(request):
    """ Stripe webhook handler """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        return HttpResponse(status=400)
    
    import json
    print("Stripe webhook received:")
    print(json.dumps(event, indent=2))

    return HttpResponse(status=200)