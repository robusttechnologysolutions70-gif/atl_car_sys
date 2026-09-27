from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.tasks import notify_status_update

from .models import Shipment, StatusUpdate


@receiver(post_save, sender=StatusUpdate)
def on_status_update_created(sender, instance, created, **kwargs):
    if not created:
        return
    # Keep the shipment's denormalized status in sync for fast lookups
    Shipment.objects.filter(id=instance.shipment_id).update(status=instance.status)
    notify_status_update.delay(str(instance.id))
