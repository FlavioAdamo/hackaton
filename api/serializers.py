from rest_framework import serializers
from .models import DriveFolder, DriveFile

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    folder_id = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)

class CreateFolderSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=255)
    parent_folder_id = serializers.CharField(required=False, allow_blank=True)

class DriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriveFile
        fields = ['id', 'drive_id', 'name', 'mime_type', 'file_size', 'created_at', 'comment']

class DriveFolderSerializer(serializers.ModelSerializer):
    files = DriveFileSerializer(many=True, read_only=True)
    parent_id = serializers.SerializerMethodField()
    class Meta:
        model = DriveFolder
        fields = ['id', 'drive_id', 'name', 'parent_id', 'created_at', 'files']
    def get_parent_id(self, obj):
        if obj.parent_folder:
            return obj.parent_folder.id
        return None

class DriveFolderTreeSerializer(serializers.ModelSerializer):
    files = DriveFileSerializer(many=True, read_only=True)
    subfolders = serializers.SerializerMethodField()
    parent_id = serializers.SerializerMethodField()
    class Meta:
        model = DriveFolder
        fields = ['id', 'drive_id', 'name', 'parent_id', 'created_at', 'files', 'subfolders']
    def get_subfolders(self, obj):
        subfolders = obj.subfolders.all()
        return DriveFolderTreeSerializer(subfolders, many=True, context=self.context).data
    def get_parent_id(self, obj):
        if obj.parent_folder:
            return obj.parent_folder.id
        return None


from rest_framework import serializers
from .models import CalendarEvent

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = '__all__'