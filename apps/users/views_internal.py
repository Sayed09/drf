from collections import Counter

from django.contrib.auth.models import Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler, RefreshJSONWebToken

from applibs.error_codes import ERROR_CODE
from applibs.success_codes import SUCCESS_CODE
from cores.internal_base_views import CoreJWTView
from apps.users.models import User
from apps.users.utils import mapping_value
from apps.users.validations import refresh_token_data_validation, create_user_data_validation, disable_data_validation, \
    token_data_validation


class UserToken(ObtainJSONWebToken):
    """
    A custom class for JWT Token
        URL: /api/v1/users/token/
        Method: POST
    """
    @method_decorator(token_data_validation)
    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        :raises
            - KEY_ERROR: mistake spelling username or password
            - NO_CREDENTIALS_PROVIDED: provided empty credential
            - USER_INVALID_CREDENTIALS: provided wrong credential
            - USER_ACCOUNT_BLOCKED: if user blocked
            - USER_ACCOUNT_DEACTIVATED: if user account is deactivated
        """

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)

            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True)
            return response

        return Response(ERROR_CODE.global_codes.VALUE_ERROR, status=401)


class UserRefreshToken(RefreshJSONWebToken):
    """
    A custom class for JWT Refresh Token
        URL: /api/v1/users/refresh-token/
        Method: POST
    """

    @method_decorator(refresh_token_data_validation)
    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        :raises
            - KEY_ERROR: token keyword is not provided or spelling mistake
            - ALL_FIELDS_REQUIRED: empty token field
        """

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)

            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (timezone.now() + api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True)
            return response
        return Response(ERROR_CODE.global_codes.VALUE_ERROR, status=401)


class UserCreateAPI(CoreJWTView):
    """
        URL: /api/v1/users/create/
        Method: POST
        data:
        {
            "phone_number": "+8801XXXXXXXXXX",
            "role": "Admin/Staff/Reader"
        }
    """
    model_name = User

    @method_decorator(create_user_data_validation)
    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        :raises
            - KEY_ERROR: If key is not valid
            - VALUE_ERROR: If value is not valid
        """
        phone_number = request.data.get('phone_number')
        role_name = request.data.get('role').capitalize()
        password = request.data.get('password')

        user = User.objects.filter(username=phone_number)
        if user:
            user[0].groups.clear()
            group = Group.objects.get(name=role_name)
            user[0].groups.add(group)
            return Response(SUCCESS_CODE.global_codes.REQUEST_SUCCESS, status=status.HTTP_200_OK)

        user = User.objects.create_user(username=phone_number, password=password)
        group = Group.objects.get(name=role_name)
        user.groups.add(group)
        return Response(SUCCESS_CODE.global_codes.REQUEST_SUCCESS, status=status.HTTP_200_OK)


class UserEnableDisableAPI(CoreJWTView):
    """
        URL: /api/v1/users/enable_disable/
        Method: POST
        data:
        {
            "phone_number": "+8801XXXXXXXXXX",
            "disable": true/false
        }
    """
    model_name = User

    @method_decorator(disable_data_validation)
    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        :raises
            - KEY_ERROR: If key is not valid
            - VALUE_ERROR: If value is not valid
        """
        phone_number = request.data.get('phone_number')
        disable = request.data.get('disable')
        if disable:
            User.objects.filter(username=phone_number).update(is_active=False)
            return Response(SUCCESS_CODE.global_codes.REQUEST_SUCCESS, status=status.HTTP_200_OK)
        User.objects.filter(username=phone_number).update(is_active=True)
        return Response(SUCCESS_CODE.global_codes.REQUEST_SUCCESS, status=status.HTTP_200_OK)


class UserRolesAPI(CoreJWTView):
    """
        URL: /api/v1/users/role_group/
        Method: GET
    """
    model_name = User

    def get(self, request):
        """
        :param request:
        :return: all role group with permissions list
        """

        responses = Group.objects.annotate(
            permission_list=ArrayAgg(F("permissions__codename")),
            app_name=ArrayAgg(F("permissions__content_type__app_label"))
        ).values()

        res_list = []
        for response in responses:
            permission_list = response['permission_list']
            app_list = response['app_name']
            role_name = response['name']
            app_values = list(Counter(app_list).values())
            app_keys = list(Counter(app_list).keys())
            permissions = []
            prev = 0
            for app, value in zip(app_keys, app_values):
                value = value + prev
                perms_list = permission_list[prev:value]
                prev = value
                permission = list(Counter([mapping_value(x) for x in perms_list]).keys())
                permissions.append({"module_name": app, "operations": permission})
            res_list.append({"name": role_name, 'permissions': permissions})

        data = {"data": res_list, "service_id": 1}
        data.update(SUCCESS_CODE.global_codes.REQUEST_SUCCESS)

        return Response(data, status=status.HTTP_200_OK)
