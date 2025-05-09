from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated

class HasAPIKeyOrIsAuthenticated(HasAPIKey):
    def has_permission(self, request, view):
        has_api_key = super().has_permission(request, view)
        is_authenticated = IsAuthenticated().has_permission(request, view)
        return has_api_key or is_authenticated
