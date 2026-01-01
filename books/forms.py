from django import forms
from .models import Book, Category, BookContributor


class BookForm(forms.ModelForm):
    # Separate fields for parent and child categories
    parent_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=True, active=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Parent Categories"
    )
    
    child_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(parent__isnull=False, active=True).order_by('parent__name', 'name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Child Categories"
    )

    class Meta:
        model = Book
        exclude = ['categories']  # Exclude the original categories field
        widgets = {
            'authors': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'illustrators': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
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
