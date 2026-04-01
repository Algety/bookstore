from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

from .models import Order, OrderLineItem
from books.models import Book
from profiles.models import UserProfile

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        )
        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "contact_email": settings.DEFAULT_FROM_EMAIL},
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        cart = intent.metadata.cart
        save_info = intent.metadata.save_info
        username = intent.metadata.username

        # Get billing details from charges if available
        billing_details = None
        if hasattr(intent, 'charges') and intent.charges.data:
            billing_details = intent.charges.data[0].billing_details

        shipping_details = intent.shipping
        grand_total = round(intent.amount / 100, 2)

        # Clean data in the shipping details
        print(f"DEBUG: Stripe shipping_details.address.country = {shipping_details.address.country}")
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
            # Convert string 'None' to actual None
            elif value == 'None':
                shipping_details.address[field] = None
        print(f"DEBUG: After cleaning, country = {shipping_details.address.country}")

        # Update profile information if save_info was checked
        profile = None
        if username != "AnonymousUser":
            try:
                profile = UserProfile.objects.get(user__username=username)
            except UserProfile.DoesNotExist:
                profile = None
            if save_info and profile:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = (
                    shipping_details.address.postal_code
                )
                profile.default_town_or_city = (
                    shipping_details.address.city
                )
                profile.default_street_address1 = (
                    shipping_details.address.line1
                )
                profile.default_street_address2 = (
                    shipping_details.address.line2 or None
                )
                profile.default_county = shipping_details.address.state or None
                profile.save()

        # Get email from billing details, fallback to metadata or User
        email = billing_details.email if billing_details else None
        if not email:
            # Fallback to metadata email
            email = intent.metadata.get("email")
        if not email and username != "AnonymousUser":
            # Fallback to User database
            try:
                user = User.objects.get(username=username)
                email = user.email
            except User.DoesNotExist:
                email = None

        order_exists = False
        attempt = 1
        
        # Print the search criteria from webhook
        search_criteria = {
            'full_name': shipping_details.name,
            'email': email,
            'phone_number': shipping_details.phone,
            'country': shipping_details.address.country,
            'postcode': shipping_details.address.postal_code,
            'town_or_city': shipping_details.address.city,
            'street_address1': shipping_details.address.line1,
            'street_address2': shipping_details.address.line2,
            'county': shipping_details.address.state,
            'grand_total': grand_total,
            'original_cart': cart[:50],  # First 50 chars of cart
            'stripe_pid': pid,
        }
        print(f"WEBHOOK SEARCH CRITERIA: {search_criteria}")
        
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                order_exists = True
                # Print the found order
                print(f"ORDER FOUND in attempt {attempt}:")
                print(f"  ID: {order.id}")
                print(f"  Full Name: {order.full_name}")
                print(f"  Email: {order.email}")
                print(f"  Phone: {order.phone_number}")
                print(f"  Country: {order.country}")
                print(f"  Postcode: {order.postcode}")
                print(f"  Town: {order.town_or_city}")
                print(f"  Street1: {order.street_address1}")
                print(f"  Street2: {order.street_address2}")
                print(f"  County: {order.county}")
                print(f"  Grand Total: {order.grand_total}")
                print(f"  Stripe PID: {order.stripe_pid}")
                break
            except Order.DoesNotExist:
                if attempt == 1:
                    print("ORDER NOT FOUND in attempt 1.")
                    print("Recent DB orders:")
                    # Print all orders to compare
                    all_orders = Order.objects.all().order_by('-id')[:5]
                    for db_order in all_orders:
                        print(
                            f"DB Order {db_order.id}: "
                            f"name='{db_order.full_name}' "
                            f"email='{db_order.email}' "
                            f"phone='{db_order.phone_number}' "
                            f"country='{db_order.country}' "
                            f"postcode='{db_order.postcode}' "
                            f"town='{db_order.town_or_city}' "
                            f"street1='{db_order.street_address1}' "
                            f"street2='{db_order.street_address2}' "
                            f"county='{db_order.county}' "
                            f"total={db_order.grand_total} "
                            f"pid={db_order.stripe_pid}"
                        )
                else:
                    print(f"ORDER NOT FOUND in attempt {attempt}")
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | SUCCESS: '
                    "Verified order already in database"
                ),
                status=200,
            )
        else:
            order = None
            try:
                print("DEBUG: Creating NEW order from webhook")
                print(f"DEBUG: Webhook country to save: {shipping_details.address.country}")
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2 or None,
                    county=shipping_details.address.state or None,
                    grand_total=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                print(f"DEBUG: Webhook order CREATED: ID={order.id}, country='{order.country}'")
                for item_id, quantity in json.loads(cart).items():
                    book = Book.objects.get(id=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        book=book,
                        quantity=quantity,
                    )
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )

        self._send_confirmation_email(order)
        return HttpResponse(
            content=(
                f'Webhook received: {event["type"]} | SUCCESS: '
                "Created order in webhook"
            ),
            status=200,
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}', status=200
        )
