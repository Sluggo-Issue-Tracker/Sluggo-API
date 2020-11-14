"""
A REST API needs to provide a way of serializing and deserializing the models created into representations such as json.
We can do this by declaring serializers that work very similar to Django's forms. Create a file in the app directory
named serializers.py and create your classes.
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model
from rest_framework.utils import model_meta

from django.conf import settings
from . import models as api_models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name"]


class TeamSerializer(serializers.ModelSerializer):
    # make the following fields read only
    id = serializers.ReadOnlyField()
    ticket_head = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    activated = serializers.ReadOnlyField()
    deactivated = serializers.ReadOnlyField()

    class Meta:
        model = api_models.Team
        fields = [
            "id",
            "name",
            "description",
            "ticket_head",
            "created",
            "activated",
            "deactivated",
        ]


class MemberSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    owner = UserSerializer(many=False, read_only=True)
    team_id = serializers.ReadOnlyField(source="team.id")
    role = serializers.ReadOnlyField()
    created = serializers.ReadOnlyField()
    activated = serializers.ReadOnlyField()
    deactivated = serializers.ReadOnlyField()

    class Meta:
        model = api_models.Member
        fields = [
            "id",
            "owner",
            "team_id",
            "role",
            "bio",
            "created",
            "activated",
            "deactivated",
        ]


class TicketCommentSerializer(serializers.ModelSerializer):
    """
    Serialzier for comments. to be used with tickets
    """

    class Meta:
        model = api_models.TicketComment
        ticket_id = serializers.ReadOnlyField(source="ticket.id")
        team_id = serializers.ReadOnlyField(source="team.id")
        owner = UserSerializer(many=False, read_only=True)

        fields = [
            "id",
            "ticket_id",
            "team_id",
            "owner",
            "content",
            "created",
            "activated",
            "deactivated",
        ]


class TicketStatusSerializer(serializers.ModelSerializer):
    team_id = serializers.ReadOnlyField(source="team.id")

    class Meta:
        model = api_models.TicketStatus
        fields = ["id", "team_id", "title", "created", "activated", "deactivated"]


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer Class for the Ticket model.

    The fields that are serialized and visible currently are:
        id: The id of the Ticket
        team_id: id of owner team
        owner: The user that created the ticket
        assigned_user: The user assigned to the ticket
        title: The title of the ticket
        description: The description of the ticket
        comments: The comments associated with this ticket
    """

    id = serializers.ReadOnlyField()
    team_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=api_models.Team.objects.all()
    )
    owner = UserSerializer(many=False, read_only=True)
    ticket_number = serializers.ReadOnlyField()

    comments = TicketCommentSerializer(many=True, required=False)
    assigned_user = UserSerializer(many=False, read_only=True)
    status = TicketStatusSerializer(many=False, read_only=True)

    created = serializers.ReadOnlyField()
    activated = serializers.ReadOnlyField()
    deactivated = serializers.ReadOnlyField()

    class Meta:
        model = api_models.Ticket
        fields = [
            "id",
            "team_id",
            "ticket_number",
            "owner",
            "assigned_user",
            "status",
            "title",
            "description",
            "comments",
            "created",
            "activated",
            "deactivated",
        ]

        # definition of fields that will be present only on writes
        extra_kwargs = {
            'assigned_user_id': {'write_only': True},
            'status_id': {'write_only': True}
        }

    def parse_fields(self, validated_data):
        assigned_user_id = validated_data.pop('assigned_user_id', None)
        status_id = validated_data.pop('status_id', None)
        assigned_user = None
        status = None

        if assigned_user_id:
            assigned_user = get_user_model().objects.get(pk=assigned_user_id)
        if status_id:
            status = api_models.TicketStatus.objects.get(pk=status_id)

        return assigned_user, status

    def create(self, validated_data):

        assigned_user, status = self.parse_fields(validated_data)
        validated_data['team'] = validated_data.pop('team_id')

        ticket = api_models.Ticket.objects.create(
            **validated_data, assigned_user=assigned_user, status=status
        )
        return ticket

    def update(self, instance, validated_data):
        assigned_user, status = self.parse_fields(validated_data)
        instance.assigned_user = assigned_user
        instance.status = status
        return super().update(instance, validated_data)


