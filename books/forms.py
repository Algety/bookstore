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
    # Separate fields for parent and child categories
    parent_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=True, active=True).order_by('name'),
        widget=forms.SelectMultiple(attrs={
            'class': 'selectpicker form-control',
            'data-live-search': 'true',
            'data-actions-box': 'true',
            'title': 'Choose parent categories...'
        }),
        required=False,
        label="Parent Categories"
    )
    
    child_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=False, active=True).order_by('parent__name', 'name'),
        widget=forms.SelectMultiple(attrs={
            'class': 'selectpicker form-control',
            'data-live-search': 'true',
            'data-actions-box': 'true',
            'title': 'Choose child categories...'
        }),
        required=False,
        label="Child Categories"
    )

    class Meta:
        model = Book
        exclude = ['categories']
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

        # Apply consistent styling to most fields
        for field_name, field in self.fields.items():
            if field_name not in ['parent_categories', 'child_categories', 'authors', 'illustrators']:
                field.widget.attrs['class'] = 'border-black rounded-0'

        # If editing an existing book, populate the separate category fields
        if self.instance and self.instance.pk:
            current_categories = self.instance.categories.all()
            parent_cats = [cat for cat in current_categories if cat.parent is None]
            child_cats = [cat for cat in current_categories if cat.parent is not None]
            
            self.fields['parent_categories'].initial = parent_cats
            self.fields['child_categories'].initial = child_cats

        # Add custom labels for child categories showing parent/child format
        child_choices = []
        for category in self.fields['child_categories'].queryset:
            label = f"{category.parent.name} / {category.name}" if category.parent else category.name
            child_choices.append((category.pk, label))
        
        self.fields['child_categories'].choices = child_choices

    def save(self, commit=True):
        book = super().save(commit=False)
        if commit:
            book.save()
            # Combine parent and child categories and save to the book's categories
            parent_categories = self.cleaned_data.get('parent_categories', [])
            child_categories = self.cleaned_data.get('child_categories', [])
            all_categories = list(parent_categories) + list(child_categories)
            book.categories.set(all_categories)
        return book
