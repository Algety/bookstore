from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated labels,
        and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_country': 'United Kingdom (UK delivery only)',
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Post Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County',
        }

        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        
        # Set country to UK and make it read-only
        self.fields['default_country'].initial = 'United Kingdom'
        self.fields['default_country'].widget.attrs['readonly'] = True
        self.fields['default_country'].widget.attrs['style'] = 'background-color: #f8f9fa; cursor: not-allowed;'
        
        for field in self.fields:
            # If you want to mark required fields with an asterisk,
            # uncomment below
            # if field != 'default_country':
            #     if self.fields[field].required:
            #         placeholder = f'{placeholders[field]} *'
            #     else:
            #         placeholder = placeholders[field]
            # else:
            #     placeholder = placeholders[field]
            placeholder = placeholders.get(field, '')
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = (
                'border-black rounded-0 profile-form-input'
            )
            self.fields[field].label = False

    def clean_default_country(self):
        """Always return United Kingdom for UK-only delivery"""
        return 'United Kingdom'
