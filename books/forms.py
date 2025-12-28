from django import forms
from .models import Book, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize category choices with screen names if available
        categories = Category.objects.all()
        category_labels = [
            (c.id, c.get_screen_name() or c.name) for c in categories
        ]
        self.fields['categories'].choices = category_labels

        # Apply consistent styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
