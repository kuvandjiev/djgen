from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djtest.settings')

app = Celery('djtest')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
