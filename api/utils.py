from drf_spectacular.utils import extend_schema, OpenApiExample

def api_key_protected(summary, description, **kwargs):
    """
    Decorator that adds API key authentication information to API schema.
    """
    auth_description = (
        f"{description}\n\n"
        "**Authentication:** This endpoint requires API key authentication. "
        "Include the API key in the Authorization header as: `Authorization: Api-Key YOUR_API_KEY`"
    )
    
    return extend_schema(
        summary=summary,
        description=auth_description,
        **kwargs
    )
