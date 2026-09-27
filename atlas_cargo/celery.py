import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlas_cargo.settings")

app = Celery("atlas_cargo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
