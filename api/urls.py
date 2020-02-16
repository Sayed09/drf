from django.urls import path, include

# Put here all apps url
urlpatterns = [
    path('snippets/', include('apps.snippets.urls')),
    path('users/', include('apps.users.urls')),
]
