from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    # Non-model fields for first and last name
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Order
        fields = (
            "email",
            "phone_number",
            "street_address1",
            "street_address2",
            "town_or_city",
            "postcode",
            "country",
            "county",
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "phone_number": "Phone Number",
            "country": "United Kingdom (UK delivery only)",
            "postcode": "Postal Code",
            "town_or_city": "Town or City",
            "street_address1": "Street Address 1",
            "street_address2": "Street Address 2",
            "county": "County",
        }

        self.fields["first_name"].widget.attrs["autofocus"] = True
        self.fields["first_name"].widget.attrs["required"] = True
        self.fields["first_name"].widget.attrs["autocomplete"] = "given-name"

        # Set country to UK and make it read-only
        self.fields["country"].initial = "United Kingdom"
        self.fields["country"].widget.attrs["readonly"] = True
        self.fields["country"].widget.attrs[
            "style"
        ] = "background-color: #f8f9fa; cursor: not-allowed;"

        for field in self.fields:
            if field in ["first_name", "last_name"]:
                # Handle non-model fields
                placeholder = placeholders[field]
                label_text = placeholders[field]
            else:
                placeholder = placeholders[field]
                label_text = placeholders[field]

            self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = label_text

            # Add HTML5 validation attributes
            if field == "email":
                self.fields[field].widget.attrs["type"] = "email"
                self.fields[field].widget.attrs["required"] = True
                self.fields[field].widget.attrs["autocomplete"] = "email"
            elif field == "phone_number":
                self.fields[field].widget.attrs["type"] = "tel"
                self.fields[field].widget.attrs["required"] = True
                self.fields[field].widget.attrs["autocomplete"] = "tel"
                self.fields[field].widget.attrs["inputmode"] = "tel"
            elif field == "postcode":
                self.fields[field].widget.attrs["required"] = True
                self.fields[field].widget.attrs["autocomplete"] = "postal-code"
                self.fields[field].widget.attrs["inputmode"] = "numeric"
            elif field == "town_or_city":
                self.fields[field].widget.attrs["required"] = True
                self.fields[field].widget.attrs["autocomplete"] = "address-level2"
            elif field == "street_address1":
                self.fields[field].widget.attrs["required"] = True
                self.fields[field].widget.attrs["autocomplete"] = "street-address"
            elif field == "country":
                self.fields[field].widget.attrs["required"] = True
            elif field == "last_name":
                self.fields[field].widget.attrs["autocomplete"] = "family-name"

    def clean(self):
        """
        Combine first_name and last_name into full_name
        """
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name", "").strip()
        last_name = cleaned_data.get("last_name", "").strip()

        if first_name:
            full_name = f"{first_name} {last_name}".strip()
            cleaned_data["full_name"] = full_name

        return cleaned_data

    def clean_country(self):
        """Always return United Kingdom for UK-only delivery"""
        return "United Kingdom"
