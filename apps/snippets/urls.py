from rest_framework import routers

from apps.snippets.views import SnippetView

router = routers.DefaultRouter()
router.register(r'', SnippetView)

urlpatterns = []

urlpatterns += router.urls
