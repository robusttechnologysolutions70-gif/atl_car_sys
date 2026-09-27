from django.contrib import admin

from .models import Document, Shipment, StatusUpdate


class StatusUpdateInline(admin.TabularInline):
    model = StatusUpdate
    extra = 1
    readonly_fields = ("created_at",)


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("reference", "client", "branch", "mode", "status", "eta", "created_at")
    list_filter = ("branch", "mode", "status")
    search_fields = ("reference", "bill_of_lading", "airway_bill", "client__company_name")
    inlines = [StatusUpdateInline, DocumentInline]
