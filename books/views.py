from django.shortcuts import render
from .models import Book

# Create your views here.
def all_books(request):
    """A view to show all books"""

    books = Book.objects.all()

    context = {
        'books': books,
    }
    return render(request, 'books/books.html', context)

def book_detail(request, book_id):
    """ A view to show book details """

    product = get_object_or_404(Book, pk=book_id)

    context = {
        'book': book,
    }

    return render(request, 'books/book_detail.html', context)