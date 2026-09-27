import uuid

from django.conf import settings
from django.db import models

from accounts.models import Branch


def shipment_reference():
    return f"ACS-{uuid.uuid4().hex[:8].upper()}"


class FreightMode(models.TextChoices):
    AIR = "air", "Air freight"
    SEA = "sea", "Sea freight"
    ROAD = "road", "Road freight"


class ShipmentStatus(models.TextChoices):
    BOOKED = "booked", "Booked"
    IN_TRANSIT = "in_transit", "In transit"
    AT_CUSTOMS = "at_customs", "At customs"
    CLEARED = "cleared", "Cleared"
    OUT_FOR_DELIVERY = "out_for_delivery", "Out for delivery"
    DELIVERED = "delivered", "Delivered"


class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True, default=shipment_reference, editable=False)
    client = models.ForeignKey(
        "accounts.ClientProfile", on_delete=models.PROTECT, related_name="shipments"
    )
    branch = models.CharField(max_length=20, choices=Branch.choices)
    mode = models.CharField(max_length=10, choices=FreightMode.choices)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    bill_of_lading = models.CharField(max_length=50, blank=True)
    airway_bill = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.BOOKED)
    assigned_agent = models.ForeignKey(
        "accounts.StaffProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments"
    )
    eta = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference


class StatusUpdate(models.Model):
    """Append-only history — one row per status change, drives notifications."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="status_updates")
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        "accounts.StaffProfile", on_delete=models.SET_NULL, null=True, related_name="status_updates"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.shipment.reference} → {self.status}"


class Document(models.Model):
    class DocType(models.TextChoices):
        BILL_OF_LADING = "bol", "Bill of lading"
        AIRWAY_BILL = "awb", "Airway bill"
        CUSTOMS_DECLARATION = "customs", "Customs declaration"
        INVOICE = "invoice", "Invoice"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    file = models.FileField(upload_to="shipment_documents/%Y/%m/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipment.reference} — {self.get_doc_type_display()}"
