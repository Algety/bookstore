from django import forms
from .models import Book, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter to show only active categories
        active_categories = Category.objects.filter(active=True)
        self.fields['categories'].queryset = active_categories

        # Apply consistent styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
