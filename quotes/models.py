import uuid

from django.db import models

from accounts.models import Branch
from shipments.models import FreightMode


class QuoteRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        CONVERTED = "converted", "Converted to shipment"
        DECLINED = "declined", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    mode = models.CharField(max_length=10, choices=FreightMode.choices)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    cargo_description = models.CharField(max_length=255)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume_cbm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_branch = models.CharField(max_length=20, choices=Branch.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.origin} → {self.destination}"
