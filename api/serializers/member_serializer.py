from rest_framework import serializers
from django.contrib.auth import get_user_model
from .user_serializer import UserSerializer
from ..models import Member


class MemberSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    owner = UserSerializer(many=False, read_only=True)
    object_uuid = serializers.ReadOnlyField()
    team_id = serializers.ReadOnlyField(source="team.id")
    created = serializers.DateTimeField(read_only=True)
    activated = serializers.DateTimeField(read_only=True)
    deactivated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "owner",
            "team_id",
            "object_uuid",
            "role",
            "bio",
            "pronouns",
            "created",
            "activated",
            "deactivated",
        ]
