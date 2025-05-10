from django.db import models
from pgvector.django import VectorField
from api.models import DriveFile


# Create your models here.
class DocumentContent(models.Model):
    drive_file = models.ForeignKey(
        DriveFile, on_delete=models.CASCADE, related_name="document_contents"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.drive_file.name} - {self.content[:100]}"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        DocumentContent, on_delete=models.CASCADE, related_name="chunks"
    )
    content = models.TextField()
    embedding = VectorField(
        dimensions=1536
    )  # Using 1536 dimensions which is standard for OpenAI embeddings
    index = models.IntegerField()  # To maintain order of chunks
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["index"]
        indexes = [
            models.Index(fields=["index"]),
        ]

    def __str__(self):
        return f"Chunk {self.index} of {self.document.drive_file.name}"


class DocumentTaskStatus(models.TextChoices):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DocumentTask(models.Model):
    document = models.ForeignKey(
        DocumentContent, on_delete=models.CASCADE, related_name="tasks"
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    recipient_email_list = models.JSONField(default=list, blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=DocumentTaskStatus.choices,
        default=DocumentTaskStatus.PENDING,
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
