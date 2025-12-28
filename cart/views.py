from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages

from books.models import Book


# Create your views here.


def view_cart(request):
    """ A view to render the cart page """

    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add the quantity of the book to the cart """

    book = get_object_or_404(Book, pk=item_id)

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})

    if item_id in list(cart.keys()):
        cart[item_id] += quantity
        messages.success(request, f'Updated {book.title} in your cart')
    else:
        cart[item_id] = quantity
        messages.success(request, f'Added {book.title} to your cart')

    request.session['cart'] = cart
    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """ Adjust the quantity of the specified book """

    book = get_object_or_404(Book, pk=item_id)

    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', {})
    from_detail = request.POST.get('from_detail', None)

    if quantity > 0:
        cart[item_id] = quantity
        if from_detail == '1':
            messages.success(request, f'Updated {book.title} in your cart')
    else:
        cart.pop(item_id, None)
        messages.success(request, f'Removed {book.title} from your cart')

    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, item_id):
    """ Remove the item from the cart """

    book = get_object_or_404(Book, pk=item_id)

    try:
        cart = request.session.get('cart', {})

        if item_id in cart:
            cart.pop(item_id)
            messages.success(request, f'Removed {book.title} from your cart')

        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
