from django import template

register = template.Library()

STATUS_COLORS = {
    "booked": "secondary",
    "in_transit": "info",
    "at_customs": "warning",
    "cleared": "success",
    "out_for_delivery": "success",
    "delivered": "dark",
    "new": "secondary",
    "reviewed": "info",
    "converted": "success",
    "declined": "danger",
}


STATUS_LABELS = {
    "booked": "Booked",
    "in_transit": "In transit",
    "at_customs": "At customs",
    "cleared": "Cleared",
    "out_for_delivery": "Out for delivery",
    "delivered": "Delivered",
}


@register.filter
def status_color(value):
    return STATUS_COLORS.get(value, "secondary")


@register.filter
def status_label(value):
    return STATUS_LABELS.get(value, value)
