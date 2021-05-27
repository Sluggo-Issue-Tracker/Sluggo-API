from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import *


class TeamSerializer(serializers.ModelSerializer):
    # make the following fields read only
    id = serializers.ReadOnlyField()
    ticket_head = serializers.ReadOnlyField()
    object_uuid = serializers.ReadOnlyField()
    created = serializers.DateTimeField(read_only=True)
    activated = serializers.DateTimeField(read_only=True)
    deactivated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "object_uuid",
            "ticket_head",
            "created",
            "activated",
            "deactivated",
        ]
