from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "default_phone_number",
        "default_country",
        "default_town_or_city",
    )
    list_filter = ("default_country", "user__date_joined")
    search_fields = ("user__username", "user__email", "default_phone_number")
    
    fieldsets = (
        ("User Information", {
            "fields": ("user",),
            "classes": ("wide",),
        }),
        ("Default Delivery Information", {
            "fields": (
                "default_phone_number",
                "default_street_address1",
                "default_street_address2",
                "default_town_or_city",
                "default_postcode",
                "default_county",
                "default_country",
            ),
        }),
    )
    
    readonly_fields = ("user",)

    def save_model(self, request, obj, form, change):
        """Validate phone number before saving"""
        try:
            obj.full_clean()
        except ValidationError as e:
            # Re-raise with proper error dictionary for admin display
            raise ValidationError(e.message_dict)
        super().save_model(request, obj, form, change)


admin.site.register(UserProfile, UserProfileAdmin)
