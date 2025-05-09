from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io

class GDriveManager:
    _creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/drive']
    )
    _drive_service = build('drive', 'v3', credentials=_creds)
    _GDRIVE_BASE_DIRECTORY_ID = "1zTvCh76LuRH52fqHthcbz3D1fhATbRA6"

    def check_folder_exists(self, folder_id: str):
        """
        Check if a folder exists on Google Drive by its ID
        """
        try:
            self._drive_service.files().get(
                fileId=folder_id,
                fields='id,name,mimeType',
                supportsAllDrives=True
            ).execute()
            return True
        except Exception:
            # Folder does not exist or no permission to access
            return False
            
    def get_folder_name(self, folder_id: str):
        """
        Get the name of a folder by its ID
        """
        try:
            folder = self._drive_service.files().get(
                fileId=folder_id,
                fields='name',
                supportsAllDrives=True
            ).execute()
            return folder.get('name', 'Unknown Folder')
        except Exception:
            return 'Unknown Folder'

    def find_folder_by_name(self, folder_name: str, parent: str = None):
        """
        Find a folder by its name under a specific parent
        Returns the folder data if found, otherwise None
        """
        parent_folder = parent or self._GDRIVE_BASE_DIRECTORY_ID
        query = f"name = '{folder_name}' and '{parent_folder}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        
        response = self._drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)',
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        
        folders = response.get('files', [])
        return folders[0] if folders else None

    def create_folder(self, name: str, parent_folder: str = None):
        parent_folder = parent_folder or self._GDRIVE_BASE_DIRECTORY_ID
        
        #Check if folder already exist
        query = f"name = '{name}' and parents = '{parent_folder}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        response = self._drive_service.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True).execute()
        existing_folders = response.get('files', [])

        if existing_folders:
            return False, existing_folders[0]
        
        folder_metadata = {
            'name': name,
            'parents': [f'{parent_folder}'],
            'mimeType': "application/vnd.google-apps.folder",
        }
        
        folder = self._drive_service.files().create(
            body=folder_metadata,
            fields='id',
            supportsAllDrives=True,
        ).execute()
        return True, folder


    def upload_file(self, file, folder_id):
        file_metadata = {
            'name': file.name,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype=file.content_type)
        uploaded_file = self._drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
        ).execute()
        return uploaded_file

    def list_files(self, parent_folder: str):
        parent_folder = parent_folder
        query = f"parents = '{parent_folder}'"
        response = self._drive_service.files().list(q=query, includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
        files = response.get('files', [])
        next_page_token = response.get('nextPageToken', None)

        while next_page_token:
            response = self._drive_service.files().list(q=query, includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
            files = response.get('files', [])
            next_page_token = response.get('nextPageToken', None)

        return files

    def list_files_and_folders(self, parent_folder: str):
        query = f"'{parent_folder}' in parents and trashed = false"
        response = self._drive_service.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)"
        ).execute()
        items = response.get('files', [])
        next_page_token = response.get('nextPageToken')

        # Ciclo per ottenere tutti i file e le cartelle presenti direttamente
        while next_page_token:
            response = self._drive_service.files().list(
                q=query,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            items.extend(response.get('files', []))
            next_page_token = response.get('nextPageToken')

        return items

    def move_file(self, file_id: str, new_folder_id: str):
        # Get the file's current parents
        file = self._drive_service.files().get(
            fileId=file_id,
            fields='parents',
            supportsAllDrives=True
        ).execute()
        previous_parents = ",".join(file.get('parents', []))

        # Move the file to the new folder
        file = self._drive_service.files().update(
            fileId=file_id,
            addParents=new_folder_id,
            removeParents=previous_parents,
            supportsAllDrives=True,
            fields='id, parents, name'
        ).execute()
        return file