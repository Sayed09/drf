from django.urls import path

from apps.users.views_internal import UserCreateAPI, UserRolesAPI, UserEnableDisableAPI, UserToken, UserRefreshToken

# Put here views here
urlpatterns = [

]

internal_urls = [
    path('token/', UserToken.as_view()),
    path('refresh-token/', UserRefreshToken.as_view()),
    path("create/", UserCreateAPI.as_view()),
    path("get_role/", UserRolesAPI.as_view()),
    path("enable_disable/", UserEnableDisableAPI.as_view()),
]

urlpatterns += internal_urls
