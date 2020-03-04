from rest_framework import serializers
from .models import Snippet, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class SnippetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Snippet
        fields = ["id", "title", "owner", "owner_id"]
        # extra_fields = ["owner_id"]
