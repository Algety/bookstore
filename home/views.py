from django.shortcuts import render

# Create your views here.

def index(request):
    """ A view to return an index page """
    return render(request, "books/books.html")
