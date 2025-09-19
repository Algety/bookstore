from books.models import Book, Category
from django.db.models import Q
import re

def get_filtered_books(request):
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
                return books.none(), query, categories

        elif 'category' in request.GET:
            try:
                category_ids = [int(cid) for cid in request.GET['category'].split(',')]
                subcategory_ids = Category.objects.filter(parent_id__in=category_ids).values_list('id', flat=True)
                books = books.filter(categories__id__in=subcategory_ids)
                categories = Category.objects.filter(id__in=category_ids)
            except ValueError:
                return books.none(), query, categories

        if 'q' in request.GET:
            query = request.GET['q']
            if query.strip():
                words = re.findall(r'\w+', query.lower())
                for word in words:
                    word_queries = (
                        Q(title__icontains=word) |
                        Q(description__icontains=word) |
                        Q(authors__name__icontains=word) |
                        Q(publisher__name__icontains=word)
                    )
                    books = books.filter(word_queries)

    return books, query, categories