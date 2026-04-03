from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    # Non-model fields for User model data
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated labels,
        and set autofocus on first field
        """
        super().__init__(*args, **kwargs)

        # Pre-fill user fields from the User model
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "default_country": "United Kingdom (UK delivery only)",
            "default_phone_number": "Phone Number",
            "default_postcode": "Post Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_county": "County",
        }

        self.fields["first_name"].widget.attrs["autofocus"] = True

        # Set country to UK and make it read-only
        self.fields["default_country"].initial = "United Kingdom"
        self.fields["default_country"].widget.attrs["readonly"] = True
        self.fields["default_country"].widget.attrs[
            "style"
        ] = "background-color: #f8f9fa; cursor: not-allowed;"

        for field in self.fields:
            placeholder = placeholders.get(field, "")
            self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs[
                "class"
            ] = "border-black rounded-0 profile-form-input"
            # Show labels with proper text
            label_text = placeholders.get(
                field, field.replace("default_", "").replace("_", " ").title()
            )
            self.fields[field].label = label_text

    def clean_default_country(self):
        """Always return United Kingdom for UK-only delivery"""
        return "United Kingdom"
