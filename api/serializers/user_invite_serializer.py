from rest_framework import serializers
from .team_serializer import TeamSerializer
from ..models import TeamInvite


class UserInviteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamInvite
        fields = ["id", "team"]
