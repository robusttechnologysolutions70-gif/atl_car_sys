import uuid

from django.db import models


class NotificationChannel(models.TextChoices):
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "Email"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class Notification(models.Model):
    """One row per outbound message — created by a Celery task off a StatusUpdate."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "shipments.Shipment", on_delete=models.CASCADE, related_name="notifications"
    )
    status_update = models.ForeignKey(
        "shipments.StatusUpdate", on_delete=models.CASCADE, related_name="notifications"
    )
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    recipient = models.CharField(max_length=32)  # phone number
    message = models.CharField(max_length=320)
    delivery_status = models.CharField(
        max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.PENDING
    )
    provider_message_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.channel} to {self.recipient} — {self.delivery_status}"
