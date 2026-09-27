from django.apps import AppConfig


class ShipmentsConfig(AppConfig):
    name = 'shipments'

    def ready(self):
        import shipments.signals  # noqa: F401
