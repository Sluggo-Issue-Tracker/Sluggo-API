from rest_framework import serializers
from ..models import *


class TagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    created = serializers.DateTimeField(read_only=True)
    activated = serializers.DateTimeField(read_only=True)
    deactivated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            "id",
            "team_id",
            "object_uuid",
            "title",
            "created",
            "activated",
            "deactivated",
        ]
