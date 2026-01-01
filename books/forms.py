from django import forms
from .models import Book, Category, BookContributor


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'authors': forms.CheckboxSelectMultiple(),
            'illustrators': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter to show only active categories
        active_categories = Category.objects.filter(active=True).order_by('parent', 'name')
        self.fields['categories'].queryset = active_categories
        
        # Filter authors and illustrators by role
        self.fields['authors'].queryset = BookContributor.objects.filter(
            role='author'
        ).order_by('name')
        
        self.fields['illustrators'].queryset = BookContributor.objects.filter(
            role='illustrator'
        ).order_by('name')

        # Apply consistent styling to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['categories', 'authors', 'illustrators']:
                field.widget.attrs['class'] = 'border-black rounded-0'

        # Custom label formatting for categories
        self.fields['categories'].label_from_instance = lambda obj: (
            f"{obj.parent.name} / {obj.name}" if obj.parent else obj.name
        )
