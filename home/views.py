from django.shortcuts import render
from books.models import Book

def index(request):
    books = Book.objects.all()
    context = {
        'books': books,
        # 'banners': ['banner1.jpg', 'banner2.jpg'],
    }
    return render(request, 'home/index.html', context)