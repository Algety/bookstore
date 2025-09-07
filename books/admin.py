from django.contrib import admin
from .models import Category, BookContributor, Publisher, Book

# Register your models here.
class BookAdmin(admin.ModelAdmin):
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = 'Categories'

    def display_authors(self, obj):
        return ", ".join([c.name for c in obj.authors.all()])
    display_authors.short_description = 'Authors'

    def display_illustrators(self, obj):
        return ", ".join([c.name for c in obj.illustrators.all()])
    display_illustrators.short_description = 'Illustrators'

    list_display = ('display_categories','title', 'display_authors', 'display_illustrators',
                     'publisher', 'language', 'price', 'stock_quantity','image')
    ordering = ('title',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

class BookContributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'photo')

class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(BookContributor, BookContributorAdmin)
admin.site.register(Publisher, PublisherAdmin)