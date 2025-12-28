from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from books.models import Book, Category
import re


def index(request):
    books = Book.objects.all()
    query = None
    categories = None

    if request.GET:
        if 'subcategory' in request.GET and 'parent' in request.GET:
            try:
                subcategory_id = int(request.GET['subcategory'])
                parent_id = int(request.GET['parent'])
                books = books.filter(
                    categories__id=subcategory_id,
                    categories__parent_id=parent_id
                )
                categories = Category.objects.filter(id=subcategory_id)
            except ValueError:
                messages.error(request, "Invalid category selection")
                return redirect(reverse('books'))

        elif 'category' in request.GET:
            try:
                category_ids = [
                    int(cid) for cid in request.GET['category'].split(',')
                ]

                # Get all subcategories where parent is in category_ids
                subcategory_ids = Category.objects.filter(
                    parent_id__in=category_ids
                ).values_list('id', flat=True)

                # Get books tagged with any of those subcategories
                books = books.filter(categories__id__in=subcategory_ids)

                categories = Category.objects.filter(id__in=category_ids)

            except ValueError:
                messages.error(request, "Invalid category selection")
                return redirect(reverse('books'))

        if 'q' in request.GET:
            query = request.GET['q']
            if not query.strip():
                messages.error(request, "Enter the search criteria")
                return redirect(reverse('books'))

            # Split query into individual words
            words = query.strip().split()
            words = re.findall(r'\w+', query.lower())

            # Build a combined Q object that requires each word to match
            # at least one field
            for word in words:
                word_queries = (
                    Q(title__icontains=word) |
                    Q(description__icontains=word) |
                    Q(authors__name__icontains=word) |
                    Q(publisher__name__icontains=word)
                )

                books = books.filter(word_queries)

    sort_option = request.GET.get('sort')

    if sort_option == 'price_asc':
        books = books.order_by('price')
    elif sort_option == 'price_desc':
        books = books.order_by('-price')

    language = request.GET.get('language')
    if language in ['ukr', 'eng']:
        books = books.filter(language=language)

    active_categories = Category.objects.filter(
        parent=None, active=True
    ).order_by('order')
    for category in active_categories:
        category.visible_subcategories = (
            category.subcategories.filter(active=True).order_by('order')
        )

    context = {
        'books': books,
        'search_term': query,
        'current_categories': categories,
        'categories': active_categories,
        'sort_option': sort_option,
        'language': language,
        'show_carousel': True,
    }

    return render(request, 'home/index.html', context)
