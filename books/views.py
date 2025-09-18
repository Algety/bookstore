from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .models import Book, Category

def all_books(request):
    books = Book.objects.all()
    query = None
    categories = None

    if request.GET:
        if 'subcategory' in request.GET and 'parent' in request.GET:
            try:
                subcategory_id = int(request.GET['subcategory'])
                parent_id = int(request.GET['parent'])
                books = books.filter(categories__id=subcategory_id, categories__parent_id=parent_id)
                categories = Category.objects.filter(id=subcategory_id)
            except ValueError:
                messages.error(request, "Invalid category selection")
                return redirect(reverse('books'))

        elif 'category' in request.GET:
            try:
                category_ids = [int(cid) for cid in request.GET['category'].split(',')]

                # Get all subcategories where parent is in category_ids
                subcategory_ids = Category.objects.filter(parent_id__in=category_ids).values_list('id', flat=True)

                # Get books tagged with any of those subcategories
                books = books.filter(categories__id__in=subcategory_ids)

                categories = Category.objects.filter(id__in=category_ids)

            except ValueError:
                messages.error(request, "Invalid category selection")
                return redirect(reverse('books'))

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "Enter the search criteria")
                return redirect(reverse('books'))

            queries = (
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(illustrators__name__icontains=query) |
                Q(authors__name__icontains=query)
            )
            books = books.filter(queries)

    active_categories = Category.objects.filter(parent=None, active=True).order_by('order')
    for category in active_categories:
        category.visible_subcategories = category.subcategories.filter(active=True).order_by('order')

    context = {
        'books': books,
        'search_term': query,
        'current_categories': categories,
        'categories': active_categories,
    }

    return render(request, 'books/books.html', context)

def book_detail(request, book_id):
    """ A view to show book details """

    book = get_object_or_404(Book, pk=book_id)

    context = {
        'book': book,
    }

    return render(request, 'books/book_detail.html', context)