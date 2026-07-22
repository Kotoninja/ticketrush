import os

from celery import Celery
from config.settings.celery_configuration_options import CELERY

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.local")

app = Celery("config")
app.config_from_object(CELERY)
app.autodiscover_tasks()
