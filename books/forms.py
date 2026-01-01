from django import forms
from .models import Book, Category, BookContributor


class MultiSelectDropdownWidget(forms.CheckboxSelectMultiple):
    """Custom widget that renders as a dropdown with checkboxes"""
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-select-multiple-checkbox'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap-select@1.14.0-beta3/dist/css/bootstrap-select.min.css',)
        }
        js = ('https://cdn.jsdelivr.net/npm/bootstrap-select@1.14.0-beta3/dist/js/bootstrap-select.min.js',)


class BookForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=False, active=True).order_by('parent__name', 'name'),
        widget=forms.SelectMultiple(attrs={
            'class': 'selectpicker form-control',
            'data-live-search': 'true',
            'data-actions-box': 'true',
            'title': 'Choose categories...'
        }),
        required=False,
        label="Categories"
    )

    class Meta:
        model = Book
        fields = ['categories', 'title', 'sku', 'slug', 'description', 'cover_type', 
                  'illustration_type', 'pages', 'price', 'stock_quantity',
                  'authors', 'illustrators', 'publisher', 'language', 'image']
        widgets = {
            'authors': forms.SelectMultiple(attrs={
                'class': 'selectpicker form-control',
                'data-live-search': 'true',
                'data-actions-box': 'true',
                'title': 'Choose authors...'
            }),
            'illustrators': forms.SelectMultiple(attrs={
                'class': 'selectpicker form-control', 
                'data-live-search': 'true',
                'data-actions-box': 'true',
                'title': 'Choose illustrators...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter authors and illustrators by role
        self.fields['authors'].queryset = BookContributor.objects.filter(
            role='author'
        ).order_by('name')
        
        self.fields['illustrators'].queryset = BookContributor.objects.filter(
            role='illustrator'
        ).order_by('name')

        # Apply consistent styling to non-dropdown fields
        for field_name, field in self.fields.items():
            if field_name not in ['categories', 'authors', 'illustrators']:
                field.widget.attrs['class'] = 'border-black rounded-0'

        # Add asterisks to required fields
        required_fields = ['title', 'cover_type', 'illustration_type', 'pages', 'price', 'stock_quantity', 'language']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].label = f"{self.fields[field_name].label} *"
