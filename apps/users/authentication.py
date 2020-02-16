from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.encoding import smart_text

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication

from applibs.error_codes import ERROR_CODE
from applibs.exceptions import UnAuthorized
from applibs.firebase import FIREBASE_AUTH, FIREBASE

USER_SETTINGS = getattr(settings, 'FIREBASE_AUTH', None)
User = get_user_model()


class BaseFirebaseAuthentication(authentication.BaseAuthentication):
    """
    Token based authentication using firebase.
    """

    def authenticate(self, request):
        """
        With ALLOW_ANONYMOUS_REQUESTS, set request.user to an AnonymousUser,
        allowing us to configure access at the permissions level.
        """
        authorization_header = authentication.get_authorization_header(request)
        if not authorization_header:
            return AnonymousUser(), None

        """
        Returns a tuple of len(2) of `User` and the decoded firebase token if
        a valid signature has been supplied using Firebase authentication.
        """
        firebase_token = self.get_token(request)
        decoded_token = self.decode_token(firebase_token)
        firebase_user = self.authenticate_token(decoded_token)
        local_user = self.get_local_user(firebase_user)

        return local_user, firebase_token

    def get_token(self, request):
        raise NotImplementedError('get_token() has not been implemented.')

    def decode_token(self, firebase_token):
        raise NotImplementedError('decode_token() has not been implemented.')

    def authenticate_token(self, decoded_token):
        raise NotImplementedError('authenticate_token() has not been implemented.')

    def get_local_user(self, firebase_user):
        raise NotImplementedError('get_or_create_local_user() has not been implemented.')


class FirebaseAuthentication(BaseFirebaseAuthentication):
    """
    Clients should authenticate by passing the token key in the
    'Authorization' HTTP header, prepended with the string specified in the
    settings.FIREBASE_AUTH_HEADER_PREFIX setting (Default = 'JWT')
    """
    www_authenticate_realm = 'api'

    def get_token(self, request):
        """
        Parse Authorization header and retrieve JWT
        """
        authorization_header = authentication.get_authorization_header(request).split()
        # auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()
        auth_header_prefix = USER_SETTINGS.get("FIREBASE_AUTH_HEADER_PREFIX").lower()

        if not authorization_header or len(authorization_header) != 2:
            raise UnAuthorized(
                'Invalid Authorization header format, expecting: JWT <token>.'
            )

        if smart_text(authorization_header[0].lower()) != auth_header_prefix:
            raise UnAuthorized(
                'Invalid Authorization header prefix, expecting: JWT.'
            )

        return authorization_header[1]

    def decode_token(self, firebase_token):
        """
        Attempt to verify JWT from Authorization header with Firebase and
        return the decoded token
        """
        try:
            return FIREBASE_AUTH.token_verification(firebase_token)
        except ValueError:
            raise UnAuthorized(
                'JWT was found to be invalid, or the App’s project ID cannot '
                'be determined.'
            )
        except Exception:
            print("hello")
            raise UnAuthorized(ERROR_CODE.authentication_codes.TOKEN_INVALID)

    def authenticate_token(self, decoded_token):
        """
        Returns firebase user if token is authenticated
        """
        try:
            uid = decoded_token.get('uid')
            firebase_user = FIREBASE.get_user_by_uid(uid)
            return firebase_user
        except ValueError:
            raise UnAuthorized(
                'User ID is None, empty or malformed'
            )
        except Exception:
            raise UnAuthorized(
                'Error retrieving the user, or the specified user ID does not '
                'exist'
            )

    def get_local_user(self, firebase_user):
        """
        Attempts to return or create a local User from Firebase user data
        """
        try:
            user = User.objects.get(username=firebase_user.phone_number)
            if not user.is_active:
                raise UnAuthorized(ERROR_CODE.authentication_codes.USER_ACCOUNT_DEACTIVATED)
            user.last_login = timezone.now()
            user.save()
            return user
        except User.DoesNotExist:
            # TODO: Update message with error code
            raise UnAuthorized()

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        # auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()
        auth_header_prefix = USER_SETTINGS.get("FIREBASE_AUTH_HEADER_PREFIX").lower()
        return '{0} realm="{1}"'.format(auth_header_prefix, self.www_authenticate_realm)
