from django.contrib import admin
from home.models import ContactUsMessage


@admin.register(ContactUsMessage)
class ContactUsMessageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "author", "email", "phone", "added"]

    def has_add_permission(self, request):
        return False
