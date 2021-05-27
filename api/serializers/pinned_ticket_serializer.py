from rest_framework import serializers
from ..models import Ticket, PinnedTicket
from .fields.primary_key_serialized_field import PrimaryKeySerializedField
from .ticket_serializer import TicketSerializer


class PinnedTicketSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    ticket = PrimaryKeySerializedField(many=False,
                                       required=True,
                                       queryset=Ticket.objects.all(),
                                       serializer=TicketSerializer)
    created = serializers.DateTimeField(read_only=True)
    object_uuid = serializers.ReadOnlyField()

    class Meta:
        model = PinnedTicket
        fields = ["ticket", "pinned", "object_uuid", "created", "id"]
