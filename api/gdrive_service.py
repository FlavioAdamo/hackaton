from gdrive_manager import GDriveManager
from django.conf import settings


class GDriveService:
    _manager = GDriveManager()

    def create_folder(self, name: str, parent_folder: str):
        return self._manager.create_folder(
            name= f"{name}",
            parent_folder=parent_folder
        )

    def create_project_folder(self, project_code: str, project_name: str):
        return self._manager.create_folder(
            name= f"{project_code}/{project_name}",
            parent_folder=settings.GDRIVE_PROJECT_DIRECTORY_ID
        )

    def create_lead_folder(self, name: str):
        return self._manager.create_folder(
            name= f"{name}",
            parent_folder= settings.GDRIVE_LEAD_DIRECTORY_ID
        )