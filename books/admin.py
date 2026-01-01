from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from .models import Category, BookContributor, Publisher, Book


class BookAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=False, active=True).order_by('parent__name', 'name'),
        widget=FilteredSelectMultiple("Categories", is_stacked=False),
        required=False,
        label="Categories"
    )

    class Meta:
        model = Book
        fields = ['categories', 'title', 'sku', 'slug', 'description', 'cover_type', 
                  'illustration_type', 'pages', 'price', 'stock_quantity', 
                  'authors', 'illustrators', 'publisher', 'language', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter authors and illustrators by role
        self.fields['authors'].queryset = BookContributor.objects.filter(
            role='author'
        ).order_by('name')
        
        self.fields['illustrators'].queryset = BookContributor.objects.filter(
            role='illustrator'
        ).order_by('name')

        # If editing an existing book, populate the categories field
        if self.instance and self.instance.pk:
            current_categories = self.instance.categories.filter(parent__isnull=False)
            self.fields['categories'].initial = current_categories

        # Add custom labels for categories
        self.fields['categories'].label_from_instance = lambda obj: (
            f"{obj.parent.name} / {obj.name}" if obj.parent else obj.name
        )

        # Add asterisks to required fields
        required_fields = ['title', 'cover_type', 'illustration_type', 'pages', 'price', 'stock_quantity', 'language']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].label = f"{self.fields[field_name].label} *"


# Register your models here.


class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    filter_horizontal = ('authors', 'illustrators')

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