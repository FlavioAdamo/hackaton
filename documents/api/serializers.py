from rest_framework import serializers
from documents.models import DocumentContent, DocumentChunk, DocumentTask


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "content",
            # "embedding",
            "index",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DocumentContentSerializer(serializers.ModelSerializer):
    # drive_file = DriveFileSerializer(read_only=True)
    chunks = DocumentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentContent
        fields = [
            "id",
            # "drive_file",
            "content",
            "chunks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DocumentTaskSerializer(serializers.ModelSerializer):
    document = DocumentContentSerializer(read_only=True)

    class Meta:
        model = DocumentTask
        fields = [
            "id",
            "document",
            "scheduled_at",
            "due_at",
            "recipient_email_list",
            "sender_email",
            "subject",
            "body",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class SimpleDocumentTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTask
        fields = [
            "id",
            "scheduled_at",
            "due_at",
            "recipient_email_list",
            "sender_email",
            "subject",
            "body",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
