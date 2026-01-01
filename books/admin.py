from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Category, BookContributor, Publisher, Book


# Register your models here.


class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories', 'authors', 'illustrators')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'categories':
            kwargs["queryset"] = Category.objects.filter(
                active=True
            ).order_by('parent', 'name')

            # Use the horizontal filter widget explicitly
            kwargs["widget"] = FilteredSelectMultiple(
                verbose_name="Categories",
                is_stacked=False
            )
            
            formfield = db_field.formfield(**kwargs)

            formfield.label_from_instance = lambda obj: (
                f"{obj.parent.name} / {obj.name}" if obj.parent else obj.name
            )

            return formfield
            
        elif db_field.name == 'authors':
            kwargs["queryset"] = BookContributor.objects.filter(
                role='author'
            ).order_by('name')
            
            kwargs["widget"] = FilteredSelectMultiple(
                verbose_name="Authors",
                is_stacked=False
            )
            
            return db_field.formfield(**kwargs)
            
        elif db_field.name == 'illustrators':
            kwargs["queryset"] = BookContributor.objects.filter(
                role='illustrator'
            ).order_by('name')
            
            kwargs["widget"] = FilteredSelectMultiple(
                verbose_name="Illustrators",
                is_stacked=False
            )
            
            return db_field.formfield(**kwargs)

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

    list_display = (
        'display_categories', 'title', 'sku', 'display_authors',
        'display_illustrators', 'publisher', 'language', 'price',
        'stock_quantity', 'image'
    )
    list_filter = ['publisher', 'language', 'categories']
    search_fields = ['title', 'sku', 'authors__name', 'publisher__name']
    ordering = ('sku', 'title',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'parent', 'active', 'order', 'subcategory', 'get_age_groups',
        'name', 'screen_name'
    )
    list_filter = ['subcategory', 'parent', 'active']
    list_editable = ['subcategory', 'order', 'active']
    search_fields = ['name', 'screen_name']
    ordering = ['parent', 'order', 'name']

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