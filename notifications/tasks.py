from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Notification, NotificationStatus

STATUS_MESSAGES = {
    "booked": "Your shipment {ref} has been booked with Atlas Cargo.",
    "in_transit": "Your shipment {ref} is now in transit.",
    "at_customs": "Your shipment {ref} has reached customs for clearance.",
    "cleared": "Your shipment {ref} has cleared customs.",
    "out_for_delivery": "Your shipment {ref} is out for delivery.",
    "delivered": "Your shipment {ref} has been delivered. Thank you for choosing Atlas Cargo.",
}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_status_update(self, status_update_id):
    """Fan out a StatusUpdate to every notification the client has opted into."""
    from shipments.models import StatusUpdate  # local import avoids app-loading order issues

    status_update = StatusUpdate.objects.select_related("shipment__client").get(id=status_update_id)
    shipment = status_update.shipment
    client = shipment.client
    message = STATUS_MESSAGES.get(
        status_update.status, "Your shipment {ref} status has been updated."
    ).format(ref=shipment.reference)

    channels = []
    if client.sms_opt_in:
        channels.append("sms")
    if client.whatsapp_opt_in:
        channels.append("whatsapp")

    for channel in channels:
        notification = Notification.objects.create(
            shipment=shipment,
            status_update=status_update,
            channel=channel,
            recipient=client.phone_number,
            message=message,
        )
        try:
            _send_via_provider(channel, client.phone_number, message)
            notification.delivery_status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
        except Exception as exc:  # noqa: BLE001 — log and retry via Celery
            notification.delivery_status = NotificationStatus.FAILED
            notification.save(update_fields=["delivery_status"])
            raise self.retry(exc=exc)
        notification.save(update_fields=["delivery_status", "sent_at"])


def _send_via_provider(channel: str, phone_number: str, message: str) -> None:
    """Thin wrapper so the provider can be swapped without touching the task logic."""
    import africastalking

    africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
    if channel == "sms":
        sms = africastalking.SMS
        sms.send(message, [phone_number])
    elif channel == "whatsapp":
        # Africa's Talking WhatsApp / or swap for Meta's Cloud API once approved
        raise NotImplementedError("Wire up WhatsApp Business API here")
