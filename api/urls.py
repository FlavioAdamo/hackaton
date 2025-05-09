from django.urls import path
from .views import (
    HealthCheckView, 
    JWTProtectedView, 
    GoogleDriveUploadView,
    DriveFolderListView,
    DriveFolderDetailView,
    DriveFolderTreeView,
    DriveFolderCreateView,
    ListFilesView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

app_name = 'api'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt-protected/', JWTProtectedView.as_view(), name='jwt_protected_view'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('documents/upload/', GoogleDriveUploadView.as_view(), name='google-drive-upload'),
    
    # New file structure API endpoints
    path('drive/folders/', DriveFolderListView.as_view(), name='drive-folder-list'),
    path('drive/folders/<int:pk>/', DriveFolderDetailView.as_view(), name='drive-folder-detail'),
    path('drive/structure/', DriveFolderTreeView.as_view(), name='drive-folder-tree'),
    path('drive/upload/', GoogleDriveUploadView.as_view(), name='drive-upload'),
    path('drive/folders/create/', DriveFolderCreateView.as_view(), name='drive-folder-create'),
    path('drive/list/<str:folder_id>/', ListFilesView.as_view(), name='files-detail'),
    path('drive/list/<str:folder_id>', ListFilesView.as_view(), name='files-detail-no-slash'),
]
