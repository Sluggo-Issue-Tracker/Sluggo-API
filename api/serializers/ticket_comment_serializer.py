from rest_framework import serializers
from .user_serializer import UserSerializer
from .. models import *


class TicketCommentSerializer(serializers.ModelSerializer):
    ticket_id = serializers.ReadOnlyField(source="ticket.id")
    team_id = serializers.ReadOnlyField(source="team.id")
    owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            "id",
            "ticket_id",
            "team_id",
            "owner",
            "object_uuid",
            "content",
            "created",
            "activated",
            "deactivated",
        ]
