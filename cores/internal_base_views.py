from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class CoreJWTView(APIView):
    """
    This core view will help to fetch data by JWT authentication
    """
    authentication_classes = (JSONWebTokenAuthentication,)
