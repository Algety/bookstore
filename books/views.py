from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .models import Book, Category

def all_books(request):
    """A view to show all books"""
    books = Book.objects.all()
    query = None
    categories = None

    if request.GET:
        # print("Request GET:", request.GET)  # Shows all query parameters

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            books = books.filter(categories__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "Enter the search criteria")
                return redirect(reverse('books'))

            queries = Q(title__icontains=query) | Q(description__icontains=query) | Q(illustrators__name__icontains=query) | Q(authors__name__icontains=query)
            books = books.filter(queries)

    context = {
        'books': books,
        'search_term': query,
        'current_categories': categories,
    }

    return render(request, 'books/books.html', context)

def book_detail(request, book_id):
    """ A view to show book details """

    book = get_object_or_404(Book, pk=book_id)

    context = {
        'book': book,
    }

    return render(request, 'books/book_detail.html', context)