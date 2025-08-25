import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ERP_CORE.settings')

app = Celery('ERP_CORE')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
