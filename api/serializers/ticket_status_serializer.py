from rest_framework import serializers
from ..models import TicketStatus


class TicketStatusSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    object_uuid = serializers.ReadOnlyField()
    created = serializers.DateTimeField(read_only=True)
    activated = serializers.DateTimeField(read_only=True)
    deactivated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TicketStatus
        fields = [
            "id",
            "object_uuid",
            "title",
            "color",
            "created",
            "activated",
            "deactivated",
        ]
