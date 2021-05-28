from rest_framework import serializers
from .team_serializer import TeamSerializer
from ..models import TeamInvite


class TeamInviteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user_email = serializers.EmailField(source="user.email")
    team = TeamSerializer(many=False, read_only=True)

    class Meta:
        model = TeamInvite
        fields = [
            "id", "user_email", "team"
        ]
