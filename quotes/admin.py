from django.contrib import admin

from .models import QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "origin", "destination", "mode", "preferred_branch", "status", "created_at")
    list_filter = ("preferred_branch", "mode", "status")
    search_fields = ("full_name", "company_name", "phone_number", "email")
