import uuid

from django.conf import settings
from django.db import models


class Branch(models.TextChoices):
    KAMPALA = "kampala", "Kampala"
    ENTEBBE = "entebbe", "Entebbe"


class ClientProfile(models.Model):
    """A customer who books/tracks shipments through the portal."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_profile"
    )
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20)
    whatsapp_opt_in = models.BooleanField(default=True)
    sms_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.get_username()


class StaffProfile(models.Model):
    """An Atlas Cargo employee — scoped to a branch, with a role."""

    class Role(models.TextChoices):
        CLEARING_AGENT = "clearing_agent", "Clearing agent"
        WAREHOUSE = "warehouse", "Warehouse"
        DRIVER = "driver", "Driver"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile"
    )
    branch = models.CharField(max_length=20, choices=Branch.choices)
    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_branch_display()})"
