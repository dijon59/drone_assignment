import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.project.settings')

app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
