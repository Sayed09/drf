import requests

# generate log
from django.conf import settings

from applibs.error_codes import ERROR_CODE
from applibs import exceptions
from applibs.loggers import log_info

__all__ = [
    "SERVICE_COMMUNICATOR"
]

_session = requests.Session()


class ServiceCommunicator:

    @staticmethod
    def _post_action(path: str, data: dict, headers=None, timeout=25):
        """
        :param path:
        :param data:
        :param headers:
        :param timeout:
        :return:
        """
        try:
            with _session as session:
                response = session.post(data['service_url'] + path, json=data, headers=headers, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as err:
            log_info().error("connection error {}".format(err))
            raise exceptions.ServiceUnavailable(ERROR_CODE.http_codes.NETWORK_ERROR)

        response.raise_for_status()
        return response

    def add_user_and_permission(self, data: dict):
        try:
            response = self._post_action("/api/v1/user-permission/", data=data)
            return response.json()
        except requests.HTTPError as err:
            log_info().debug("Account added error {}".format(err))
            if 400 <= err.response.status_code <= 410:
                raise exceptions.ValidationError(err.response.json())
            raise exceptions.ServiceUnavailable(ERROR_CODE.http_codes.NETWORK_ERROR)


# Instance creation
SERVICE_COMMUNICATOR = ServiceCommunicator()
