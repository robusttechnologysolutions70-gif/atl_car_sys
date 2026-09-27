from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("shipment", "channel", "recipient", "delivery_status", "created_at", "sent_at")
    list_filter = ("channel", "delivery_status")
    search_fields = ("recipient", "shipment__reference")
