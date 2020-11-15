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


class TagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    team_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=api_models.Team.objects.all()
    )
    created = serializers.ReadOnlyField()
    activated = serializers.ReadOnlyField()
    deactivated = serializers.ReadOnlyField()

    class Meta:
        model = api_models.Tag
        fields = ["id", "team_id", "title", "created", "activated", "deactivated"]

    def create(self, validated_data):

        validated_data['team'] = validated_data.pop('team_id')

        tag = api_models.Tag.objects.create(
            **validated_data
        )
        return tag


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
    team_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=api_models.Team.objects.all()
    )

    class Meta:
        model = api_models.TicketStatus
        fields = ["id", "team_id", "title", "created", "activated", "deactivated"]

    def create(self, validated_data):
        validated_data['team'] = validated_data.pop('team_id')
        status = api_models.TicketStatus.objects.create(**validated_data)
        return status


class TicketTagSerializer(serializers.ModelSerializer):
    team_id = serializers.ReadOnlyField(source="team.id")
    tag = TagSerializer(many=False, read_only=True)
    created = serializers.ReadOnlyField()

    class Meta:
        model = api_models.TicketTag
        fields = ["tag"]


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

    tag_list = TicketTagSerializer(many=True, read_only=True)
    tag_id_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(many=False, write_only=True, queryset=api_models.Tag.objects.all()),
        write_only=True,
        required=False
    )

    owner = UserSerializer(many=False, read_only=True)
    ticket_number = serializers.ReadOnlyField()
    comments = TicketCommentSerializer(many=True, required=False)

    assigned_user = UserSerializer(many=False, read_only=True)
    assigned_user_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=get_user_model().objects.all()
    )

    status = TicketStatusSerializer(many=False, read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=api_models.TicketStatus.objects.all()
    )

    created = serializers.ReadOnlyField()
    activated = serializers.ReadOnlyField()
    deactivated = serializers.ReadOnlyField()

    class Meta:
        model = api_models.Ticket
        fields = [
            "id",
            "team_id",
            "ticket_number",
            "tag_list",
            "tag_id_list",
            "owner",
            "assigned_user",
            "assigned_user_id",
            "status",
            "status_id",
            "title",
            "description",
            "comments",
            "created",
            "activated",
            "deactivated",
        ]

    def create(self, validated_data):

        validated_data['status'] = validated_data.pop('status_id', None)
        validated_data['assigned_user'] = validated_data.pop('assigned_user_id', None)
        validated_data['team'] = validated_data.pop('team_id')

        # this will remove the entry even if the call requesting using the
        # serializer does not use the tag_id_list
        validated_data.pop('tag_id_list', None)

        ticket = api_models.Ticket.objects.create(
            **validated_data
        )

        return ticket

    def update(self, instance, validated_data):
        validated_data['status'] = validated_data.pop('status_id', None)
        validated_data['assigned_user'] = validated_data.pop('assigned_user_id', None)
        validated_data.pop('tag_list_id')
        return super().update(instance, validated_data)
