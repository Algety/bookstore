from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from .models import Category, BookContributor, Publisher, Book


class BookAdminForm(forms.ModelForm):
    # Separate fields for parent and child categories
    parent_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=True, active=True).order_by('name'),
        widget=FilteredSelectMultiple("Parent Categories", is_stacked=False),
        required=False,
        label="Parent Categories"
    )
    
    child_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=False, active=True).order_by('parent__name', 'name'),
        widget=FilteredSelectMultiple("Child Categories", is_stacked=False),
        required=False,
        label="Child Categories"
    )

    class Meta:
        model = Book
        exclude = ['categories']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter authors and illustrators by role
        self.fields['authors'].queryset = BookContributor.objects.filter(
            role='author'
        ).order_by('name')
        
        self.fields['illustrators'].queryset = BookContributor.objects.filter(
            role='illustrator'
        ).order_by('name')

        # If editing an existing book, populate the separate category fields
        if self.instance and self.instance.pk:
            current_categories = self.instance.categories.all()
            parent_cats = [cat for cat in current_categories if cat.parent is None]
            child_cats = [cat for cat in current_categories if cat.parent is not None]
            
            self.fields['parent_categories'].initial = parent_cats
            self.fields['child_categories'].initial = child_cats

        # Add custom labels for child categories
        self.fields['child_categories'].label_from_instance = lambda obj: (
            f"{obj.parent.name} / {obj.name}" if obj.parent else obj.name
        )

    def save(self, commit=True):
        book = super().save(commit=False)
        if commit:
            book.save()
            # Combine parent and child categories
            parent_categories = self.cleaned_data.get('parent_categories', [])
            child_categories = self.cleaned_data.get('child_categories', [])
            all_categories = list(parent_categories) + list(child_categories)
            book.categories.set(all_categories)
        return book


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