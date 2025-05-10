from django.db import models
from django.utils import timezone

class DriveFolder(models.Model):
    """Model to store Google Drive folder references"""
    drive_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.drive_id})"
    
    class Meta:
        ordering = ['name']

class DriveFile(models.Model):
    """Model to store Google Drive file references"""
    drive_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(DriveFolder, on_delete=models.CASCADE, related_name='files')
    mime_type = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.drive_id})"
    
    class Meta:
        ordering = ['name']



from datetime import timedelta

from django.db import models

# Create your models here.
from django.db import models

class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('REMINDER', 'Reminder')
    ]

    title = models.CharField(max_length=255, help_text="Title of the event")
    description = models.TextField(blank=True, null=True, help_text="Additional details about the event")
    start_date = models.DateField(help_text="Start date of the event")
    end_date = models.DateField(blank=True, null=True, help_text="End date of the event (optional)")
    is_full_day = models.BooleanField(default=True, help_text="Indicates if the event spans the entire day")
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='REMINDER',
        help_text="Type of the event (holiday, meeting, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the event was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the event was last updated")
    



