from django.contrib import admin
from .models import Category, BookContributor, Publisher, Book

# Register your models here.
class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'categories':
            kwargs["queryset"] = Category.objects.filter(active=True).order_by('parent__name', 'name')

            formfield = db_field.formfield(**kwargs)

            formfield.label_from_instance = lambda obj: (
                f"{obj.parent.name} / {obj.name}" if obj.parent else obj.name
            )

            return formfield

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def display_categories(self, obj):
        return ", ".join([
            f"{c.parent.name} / {c.name}" if c.parent else c.name
            for c in obj.categories.all()
        ])
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
    list_display = ('parent', 'active', 'order', 'subcategory', 'get_age_groups', 'name', 'screen_name')
    list_filter = ['subcategory', 'parent', 'active']
    list_editable = ['subcategory', 'order', 'active']
    search_fields = ['name', 'screen_name']

    def get_age_groups(self, obj):
        return ", ".join(obj.get_age_group_labels())

    get_age_groups.short_description = 'Age Groups'


class BookContributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'photo')

class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(BookContributor, BookContributorAdmin)
admin.site.register(Publisher, PublisherAdmin)