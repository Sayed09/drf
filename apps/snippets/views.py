from rest_framework import permissions
from apps.snippets.permissions import IsOwnerOrReadOnly
from rest_framework.viewsets import ModelViewSet
from apps.snippets.models import Snippet
from apps.snippets.serializers import SnippetSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class SnippetView(ModelViewSet):
    """
    Snippet related API endpoints
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    serializer_class = SnippetSerializer
    queryset = Snippet.objects.filter(status=True)
    http_method_names = ['get', 'post', 'patch']
    model_name = Snippet

