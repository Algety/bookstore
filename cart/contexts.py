from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from books.models import Book

def cart_contents(request):

    cart_items = []
    total = 0
    quantity = 0
    cart = request.session.get('cart', {})

    for item_id, qty in cart.items():
        book = get_object_or_404(Book, pk=item_id)
        item_total = qty * book.price
        total += item_total
        quantity += qty
        cart_items.append({
            'item_id': item_id,
            'quantity': qty,
            'book': book,
            'total': item_total,
        })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context