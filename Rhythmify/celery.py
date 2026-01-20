import os
from celery import Celery
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Rhythmify.settings")
app = Celery("Rhythmify")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    logging.getLogger(__name__).debug('Request: %s', repr(self.request))