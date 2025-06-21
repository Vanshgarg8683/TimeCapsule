from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TIMECAPSULE.settings')

app = Celery('TIMECAPSULE')

# load settings from Django settings, using CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover tasks from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
