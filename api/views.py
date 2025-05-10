from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import get_object_or_404
import logging
from rest_framework import generics, mixins, viewsets

from api.gdrive_manager import GDriveManager
from api.serializers import (
    CalendarEventSerializer,
    FileUploadSerializer, 
    DriveFolderSerializer, 
    DriveFolderTreeSerializer,
    CreateFolderSerializer
)
from api.models import CalendarEvent, DriveFolder, DriveFile
# Configure logging
logger = logging.getLogger(__name__)

class HealthCheckView(APIView):
    """
    Endpoint per verificare se l'API è attiva e funzionante.
    Questo endpoint è pubblico e non richiede autenticazione.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response(
            {
                "status": "ok", 
                "message": "Service is up and running"
            }, 
            status=status.HTTP_200_OK
        )

class GoogleDriveUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FileUploadSerializer,
        responses={201: OpenApiResponse(response=dict, description='File uploaded successfully')},
        description="Upload a file to Google Drive. If folder_id is not provided, upload to root."
    )
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            folder_id = serializer.validated_data.get('folder_id')
            comment = serializer.validated_data.get('comment')
            gdrive_manager = GDriveManager()
            # If no folder_id, use root
            target_folder_id = folder_id if folder_id else '1zTvCh76LuRH52fqHthcbz3D1fhATbRA6'
            # Check if folder exists (skip if root)
            if folder_id and not gdrive_manager.check_folder_exists(folder_id):
                return Response({"error": f"Folder with id '{folder_id}' does not exist on Google Drive."}, status=status.HTTP_400_BAD_REQUEST)
            # Upload file
            uploaded_file = gdrive_manager.upload_file(file, target_folder_id)
            if uploaded_file:
                file_id = uploaded_file.get('id')
                file_size = file.size if hasattr(file, 'size') else None
                mime_type = file.content_type if hasattr(file, 'content_type') else None
                # Save file reference to DB
                # Always associate a folder (even root)
                if folder_id:
                    folder_obj, _ = DriveFolder.objects.get_or_create(drive_id=folder_id, defaults={'name': gdrive_manager.get_folder_name(folder_id)})
                else:
                    folder_obj, _ = DriveFolder.objects.get_or_create(drive_id='root', defaults={'name': 'Root'})
                # Prepare defaults for DriveFile
                file_defaults = {
                    'name': file.name,
                    'mime_type': mime_type,
                    'file_size': file_size,
                    'comment': comment,
                    'folder': folder_obj
                }
                db_file, _ = DriveFile.objects.get_or_create(
                    drive_id=file_id,
                    defaults=file_defaults
                )
                # Custom response with message and path
                return Response({
                    'message': 'File successfully uploaded',
                    'path': f"Sales > Client x > Invoices > {file.name}",
                    'file_id': file_id
                }, status=status.HTTP_201_CREATED)
            return Response({"error": "Upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWTProtectedView(APIView):
    
    """
    Endpoint protetto che richiede autenticazione JWT.
    L'autenticazione avviene tramite Bearer token nell'header Authorization.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response({"status": "jwt ok"}, status=status.HTTP_200_OK)



class DriveFolderListView(APIView):
    permission_classes = [IsAuthenticated]
    """
    API endpoint to list all drive folders and their files
    """
    @extend_schema(
        responses={200: DriveFolderSerializer(many=True)},
        description="List all folders and files stored in the database"
    )
    def get(self, request, format=None):
        folders = DriveFolder.objects.all()
        serializer = DriveFolderSerializer(folders, many=True)
        return Response(serializer.data)


class DriveFolderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    """
    API endpoint to retrieve a specific folder with its files
    """
    @extend_schema(
        responses={200: DriveFolderSerializer()},
        description="Retrieve folder details and its files"
    )
    def get(self, request, pk, format=None):
        folder = get_object_or_404(DriveFolder, pk=pk)
        serializer = DriveFolderSerializer(folder)
        return Response(serializer.data)



class DriveFolderTreeView(APIView):
    """
    API endpoint to retrieve the complete folder structure as a tree
    """
    @extend_schema(
        responses={200: DriveFolderTreeSerializer(many=True)},
        description="Retrieve the complete folder structure as a tree"
    )
    def get(self, request, format=None):
        # Only get root folders (those without parent)
        root_folders = DriveFolder.objects.filter(parent_folder=None)
        serializer = DriveFolderTreeSerializer(root_folders, many=True)
        return Response(serializer.data)


class DriveFolderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateFolderSerializer,
        responses={201: OpenApiResponse(response=dict, description='Folder created successfully')},
        description="Create a folder in Google Drive. If parent_folder_id is not provided, create in root."
    )
    def post(self, request, format=None):
        serializer = CreateFolderSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            parent_folder_id = serializer.validated_data.get('parent_folder_id')
            gdrive_manager = GDriveManager()
            parent_id = parent_folder_id if parent_folder_id else '1zTvCh76LuRH52fqHthcbz3D1fhATbRA6'
            # If parent_folder_id is provided, check existence
            if parent_folder_id and not gdrive_manager.check_folder_exists(parent_folder_id):
                return Response({"error": f"Parent folder with id '{parent_folder_id}' does not exist on Google Drive."}, status=status.HTTP_400_BAD_REQUEST)
            created, folder_data = gdrive_manager.create_folder(name=name, parent_folder=parent_id)
            if not folder_data:
                return Response({"error": "Failed to create folder"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # Save folder reference to DB
            parent_folder_obj = None
            if parent_folder_id:
                parent_folder_obj, _ = DriveFolder.objects.get_or_create(drive_id=parent_folder_id, defaults={'name': gdrive_manager.get_folder_name(parent_folder_id)})
            folder_obj, _ = DriveFolder.objects.get_or_create(
                drive_id=folder_data['id'],
                defaults={
                    'name': name,
                    'parent_folder': parent_folder_obj
                }
            )
            
            return Response({
                'message': 'Folder created successfully',
                'folder_id': folder_data['id'],
                'folder_name': name,
                'parent_folder_id': parent_folder_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ListFilesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(response=dict, description='List of files and folders')},
        description="Retrieve a list of files and folders from a specific Google Drive folder"
    )
    def get(self, request, folder_id, format=None):
        """
        Retrieve a list of files and folders from a specific Google Drive folder.
        """
        try:
            gdrive_manager = GDriveManager()
            files = gdrive_manager.list_files_and_folders(parent_folder=folder_id)
            return Response({'files': files}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()  # Fetch all calendar events
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for all actions

    def get_queryset(self):
        """
        Optionally filters the queryset by event type or date range.
        """
        queryset = super().get_queryset()
        event_type = self.request.query_params.get('event_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset