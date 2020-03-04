from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Snippet, User
from .serializers import SnippetSerializer

SNIPPETS_URL = reverse('django_everything:snippets')


class SnippetViewApiTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = "tester"
        self.password = "tester"
        self.user = User.objects.create_user(self.username, self.password)
        self.client.force_authenticate(self.user)

    def test_retrieve_snippet_list(self):
        Snippet.objects.create(title='Motu', owner_id=self.user.id)
        Snippet.objects.create(title='Patlu', owner_id=self.user.id)
        snippet_motu = Snippet.objects.get(title='Motu')
        snippet_patlu = Snippet.objects.get(title='Patlu')
        self.assertEqual(snippet_motu.get_snippet_detail(), "Motu belongs to python.")
        self.assertEqual(snippet_patlu.get_snippet_detail(), "Patlu belongs to python.")

        res = self.client.get(SNIPPETS_URL)
        snippets = Snippet.objects.all().order_by('-title')
        serializer = SnippetSerializer(snippets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
