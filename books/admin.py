from django.contrib import admin
from .models import Category, BookContributor, Publisher, Book


# Register your models here.


class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'categories':
            kwargs["queryset"] = Category.objects.filter(
                active=True
            ).order_by('parent__name', 'name')

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

    list_display = (
        'display_categories', 'title', 'sku', 'display_authors',
        'display_illustrators', 'publisher', 'language', 'price',
        'stock_quantity', 'image'
    )
    ordering = ('sku', 'title',)

# `parent_display` is used as the first non-editable column to be used
# as the link field to solve the problem of not saving inline edits

class CategoryAdmin(admin.ModelAdmin):

    def parent_display(self, obj):
        """Safe, non-editable display of parent category."""
        return obj.parent.name if obj.parent else ""
    parent_display.short_description = "Parent new"

    def get_age_groups(self, obj):
        return ", ".join(obj.get_age_group_labels())
    get_age_groups.short_description = 'Age Groups'

    def get_changelist_formset(self, request, **kwargs):
        kwargs['exclude'] = ('age_groups',)
        return super().get_changelist_formset(request, **kwargs)
    
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if request.method == "POST":
            formset = response.context_data["cl"].formset
            if formset and formset.errors:
                print("FORMSET ERRORS:", formset.errors)
        return response


    # List configuration
    list_display = (
        'parent_display',   # link column
        'active',
        'order',
        'subcategory',
        'get_age_groups',
        'name',
        'screen_name',
    )

    # Make the first column the link
    list_display_links = ('parent_display',)

    # Inline editable fields
    list_editable = ['active']

    exclude = ('age_groups',)

    # Filters and search
    list_filter = ['subcategory', 'active']
    search_fields = ['name', 'screen_name']
    ordering = ()


class BookContributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'photo')


class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(BookContributor, BookContributorAdmin)
admin.site.register(Publisher, PublisherAdmin)
