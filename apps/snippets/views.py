from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.shortcuts import get_object_or_404

from applibs import exceptions
from apps.snippets.permissions import IsOwnerOrReadOnly
from .models import Snippet
from .serializers import SnippetSerializer


class SnippetView(ModelViewSet):
    """
    Snippet related API endpoints
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    # model_name = Snippet

    serializer_class = SnippetSerializer
    queryset = Snippet.objects.filter(status=True)
    http_method_names = ['get', 'post', 'patch']

    def list(self, request, *args, **kwargs):
        """
            Get Snippet request:
            METHOD: GET
            URL: URI/api/v1/snippets/?type=all/active
            :param request:
            :param args:
            :param kwargs:
            :return:
        """
        snippets  = {
            "all": Snippet.objects.all().values(),
            "active": Snippet.objects.filter(status=True).values()
        }
        params = request.query_params.dict()
        return Response(snippets.get(params.get("type")), status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
            Get Specific Snippet request:
            METHOD: GET
            URL: URI/api/v1/snippets/<id>/
            :param request:
            :param args:
            :param kwargs:
            :return:
        """
        queryset = Snippet.objects.filter(status=True, id=kwargs["pk"])
        snippet_serializer = SnippetSerializer(queryset, many=True)
        return Response(snippet_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
            Create Snippet request:
            METHOD: POST
            URL: URI/api/v1/snippets
            :param request:
            {
                "title": "Motu Patlu 122",
                "owner_id": 1,
                "status": True
            }
            :param args:
            :param kwargs:
            :return:
        """
        snippet_serializer = SnippetSerializer(data=request.data)
        snippet_serializer.is_valid(raise_exception=True)
        snippet_serializer.save(code="print('Hello World')")
        return Response(data=SnippetSerializer(snippet_serializer.instance).data, status=status.HTTP_201_CREATED)
        # try:
        #     request_data = request.data
        #     Snippet.objects.create_snippet(**request_data)
        #     return Response(data={"id": 1}, status=status.HTTP_201_CREATED)
        # except Exception as error:
        #     print("Something went wrong: ", error)
        #     raise exceptions.CustomAPIException

    def partial_update(self, request, *args, **kwargs):
        """
            Update Snippet request:
            METHOD: POST
            URL: URI/api/v1/snippets/id/
            :param request:
            {
                "title": "Motu Patlu 123"
            }
            :param args:
            :param kwargs:
            :return:
        """   
        instance = get_object_or_404(Snippet, id=kwargs["pk"])
        snippet_serializer = SnippetSerializer(instance, data=request.data, partial=True)
        snippet_serializer.is_valid(raise_exception=True)
        snippet_serializer.save()
        return Response(data=SnippetSerializer(snippet_serializer.instance).data, status=status.HTTP_200_OK)
        # try:  
        #     print(request.data)
        #     request.data.update({'name': '3223'})
        #     print(request.data)
        #     Snippet.objects.update_snippet(**request.data)
        #     return Response(data={"id": kwargs["pk"]}, status=status.HTTP_201_CREATED)
        # except Exception as error:
        #     return Response(data=error)
        #     print("Something went wrong: ", error)
        #     raise exceptions.CustomAPIException

