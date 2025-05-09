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


