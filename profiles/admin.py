from django.contrib import admin
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


admin.site.register(UserProfile, UserProfileAdmin)
