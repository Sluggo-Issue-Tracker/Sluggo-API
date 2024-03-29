from rest_framework import serializers
from .fields.primary_key_serialized_field import PrimaryKeySerializedField
from .ticket_comment_serializer import TicketCommentSerializer
from .tag_serializer import TagSerializer
from .member_serializer import MemberSerializer
from .ticket_status_serializer import TicketStatusSerializer
from .team_serializer import TeamSerializer
from ..models import Ticket, Tag, Member, TicketStatus, TicketTag


class TicketSerializer(serializers.ModelSerializer):
    """
    On writes,\n
    - tag_list expects a list of primary keys\n
    - status expects a primary key\n
    On reads,\n
    - tag_list is a list of serialized tag objects\n
    - status is a serialized status object\n

    The autogenerated documentation does not account for this
    """

    id = serializers.ReadOnlyField()

    tag_list = PrimaryKeySerializedField(
        many=True, required=False, queryset=Tag.objects.all(), serializer=TagSerializer
    )

    parent_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    object_uuid = serializers.ReadOnlyField()

    ticket_number = serializers.ReadOnlyField()
    comments = TicketCommentSerializer(many=True, required=False)

    assigned_user = PrimaryKeySerializedField(
        many=False,
        required=False,
        allow_null=True,
        queryset=Member.objects.all(),
        serializer=MemberSerializer,
    )

    status = PrimaryKeySerializedField(
        many=False,
        required=False,
        allow_null=True,
        queryset=TicketStatus.objects.all(),
        serializer=TicketStatusSerializer,
    )

    created = serializers.DateTimeField(read_only=True)
    activated = serializers.DateTimeField(read_only=True)
    deactivated = serializers.DateTimeField(read_only=True)
    team = TeamSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "tag_list",
            "parent_id",
            "object_uuid",
            "assigned_user",
            "status",
            "title",
            "team",
            "description",
            "comments",
            "due_date",
            "created",
            "activated",
            "deactivated",
        ]

    # this creates a record from the json, modifying the keys
    def create(self, validated_data):
        tag_list = validated_data.pop("tag_list", None)

        ticket = Ticket.objects.create(**validated_data)

        TicketTag.create_all(tag_list, ticket)

        return ticket

    # update the instance with validated_data
    def update(self, instance: Ticket, validated_data):
        tag_list = validated_data.pop("tag_list", None)

        TicketTag.delete_difference(tag_list, instance)

        return super().update(instance, validated_data)
