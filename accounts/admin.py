from django.contrib import admin

from .models import ClientProfile, StaffProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "phone_number", "sms_opt_in", "whatsapp_opt_in")
    search_fields = ("company_name", "user__username", "phone_number")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "role")
    list_filter = ("branch", "role")
