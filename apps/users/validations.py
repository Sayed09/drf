from django.contrib.auth import authenticate

from applibs import exceptions
from applibs.error_codes import ERROR_CODE
from applibs.validators import is_phone_valid


def login_data_validation(func):
    """
    A simple data validation decorator
    :param func:
    :return:
    :raises:
        - if phone_number is not valid key: KEY_ERROR
        - if phone_number is not valid format: VALUE_ERROR
    """
    keys = ["phone_number"]

    def validation(request, *args, **kwargs):
        if all(key in request.data for key in keys):
            phone_number = request.data.get('phone_number')
            if not phone_number:
                raise exceptions.ValidationError(ERROR_CODE.global_codes.ALL_FIELDS_REQUIRED)
            if not is_phone_valid(phone_number=phone_number):
                raise exceptions.ValidationError(ERROR_CODE.global_codes.VALUE_ERROR)
        else:
            raise exceptions.ValidationError(ERROR_CODE.global_codes.KEY_ERROR)
        return func(request, *args, **kwargs)

    return validation


def create_user_data_validation(func):
    """
        A simple create user data validation decorator
        :param func:
        :return:
        :raises:
            - if phone_number is not valid key: KEY_ERROR
            - if phone_number is not valid format: VALUE_ERROR
        """

    keys = ["phone_number", "role"]

    def validation(request, *args, **kwargs):
        if all(key in request.data.keys() for key in keys):
            phone_number = request.data.get('phone_number')
            role = request.data.get('role')
            if not phone_number or not role:
                raise exceptions.ValidationError(ERROR_CODE.global_codes.ALL_FIELDS_REQUIRED)
            if not is_phone_valid(phone_number=phone_number):
                raise exceptions.ValidationError(ERROR_CODE.global_codes.VALUE_ERROR)
        else:
            raise exceptions.ValidationError(ERROR_CODE.global_codes.KEY_ERROR)
        return func(request, *args, **kwargs)

    return validation


def disable_data_validation(func):
    """
        A simple create user data validation decorator
        :param func:
        :return:
        :raises:
            - if phone_number or disable is not valid key: KEY_ERROR
            - if phone_number or disable is not valid format: VALUE_ERROR
        """

    keys = ["phone_number", "disable"]

    def validation(request, *args, **kwargs):
        if all(key in request.data.keys() for key in keys):
            phone_number = request.data.get('phone_number')
            disable = request.data.get('disable')
            if not phone_number:
                raise exceptions.ValidationError(ERROR_CODE.global_codes.ALL_FIELDS_REQUIRED)
            if not is_phone_valid(phone_number=phone_number) or type(disable) != bool:
                raise exceptions.ValidationError(ERROR_CODE.global_codes.VALUE_ERROR)
        else:
            raise exceptions.ValidationError(ERROR_CODE.global_codes.KEY_ERROR)
        return func(request, *args, **kwargs)

    return validation


def token_data_validation(func):
    """
    A simple login data validation decorator
    :param func:
    :return:
    """
    keys = ["username", "password"]

    def validation(request, *args, **kwargs):
        if all(key in request.data for key in keys):
            username = request.data.get('username')
            password = request.data.get('password')
            if not (username or password):
                raise exceptions.ValidationError(ERROR_CODE.authentication_codes.NO_CREDENTIALS_PROVIDED)

            user = authenticate(username=username, password=password)
            if user:
                if not user.is_service_user:
                    raise exceptions.PermissionDenied()
                if not user.is_active:
                    raise exceptions.ValidationError(ERROR_CODE.authentication_codes.USER_ACCOUNT_DEACTIVATED)
                if user.is_blocked:
                    raise exceptions.ValidationError(ERROR_CODE.authentication_codes.USER_ACCOUNT_BLOCKED)
            else:
                raise exceptions.ValidationError(ERROR_CODE.authentication_codes.USER_INVALID_CREDENTIALS)
        else:
            raise exceptions.ValidationError(ERROR_CODE.global_codes.KEY_ERROR)
        return func(request, *args, **kwargs)

    return validation


def refresh_token_data_validation(func):
    """
    A simple data validation decorator
    :param func:
    :return:
    """
    keys = ["token"]

    def validation(request, *args, **kwargs):
        if all(key in request.data for key in keys):
            token = request.data.get('token')
            if not token:
                raise exceptions.ValidationError(ERROR_CODE.global_codes.ALL_FIELDS_REQUIRED)
        else:
            raise exceptions.ValidationError(ERROR_CODE.global_codes.KEY_ERROR)
        return func(request, *args, **kwargs)

    return validation
