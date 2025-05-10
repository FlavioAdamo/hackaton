import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoring.settings')

app = Celery('scoring')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

def check_for_reminder(file_content):
    """
    Check if the file content contains a reminder.
    """
    # Implement your logic to check for reminders in the file content
    # For example, you can look for specific keywords or patterns
    return "reminder" in file_content.lower()
