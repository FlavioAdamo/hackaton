from django.contrib import admin
from .models import DocumentChunk, DocumentContent, DocumentTask

admin.site.register(DocumentChunk)
admin.site.register(DocumentContent)
admin.site.register(DocumentTask)
