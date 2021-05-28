from rest_framework import serializers
from ..models import TicketNode


class TicketNodeSerializer(serializers.ModelSerializer):
    ticket_id = serializers.ReadOnlyField()

    class Meta:
        model = TicketNode
        fields = ["ticket_id"]
