from django.urls import path, include

app_name = "django_everything"

# Put here all apps url
urlpatterns = [
    path(r'snippets/', include('apps.snippets.urls'), name="snippets"),
    path('users/', include('apps.users.urls')),
]
