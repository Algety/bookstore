from django.contrib import admin
from .models import Category, BookContributor, Publisher, Book

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(BookContributor)
admin.site.register(Publisher)