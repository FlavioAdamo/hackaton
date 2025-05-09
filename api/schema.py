from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class ApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Adds API Key Authentication scheme to the OpenAPI schema.
    This allows API clients to understand how to authenticate with API Key.
    """
    target_class = 'rest_framework_api_key.permissions.HasAPIKey'
    name = 'ApiKeyAuth'

    def get_security_definition(self, auto_schema):
        """
        Define the security scheme for API Key authentication
        """
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'API key authorization. Format: "Api-Key YOUR_API_KEY"'
        }


class HasAPIKeyOrIsAuthenticatedScheme(OpenApiAuthenticationExtension):
    """
    Adds combined authentication scheme to the OpenAPI schema.
    """
    target_class = 'api.permissions.HasAPIKeyOrIsAuthenticated'
    name = 'ApiKeyOrSessionAuth'
    
    def get_security_requirement(self, auto_schema):
        return [{'ApiKeyAuth': []}]
    
    def get_security_definition(self, auto_schema):
        return {}  # Reuse the ApiKeyAuth definition
