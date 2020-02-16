from rest_framework import serializers
from apps.snippets.models import Snippet, User


class SnippetSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), source='owner',
                                                  write_only=True)

    class Meta:
        model = Snippet
        fields = "__all__"
        extra_fields = ["owner_id"]