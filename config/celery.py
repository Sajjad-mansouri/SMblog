

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Prod')

import configurations
configurations.setup()

app = Celery('config')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()