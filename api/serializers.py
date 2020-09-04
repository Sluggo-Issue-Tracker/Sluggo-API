"""
A REST API needs to provide a way of serializing and deserializing the models created into representations such as json.
We can do this by declaring serializers that work very similar to Django's forms. Create a file in the app directory
named serializers.py and create your classes.
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model

from django.conf import settings
from . import models as api_models


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.ReadOnlyField(source="get_full_name")

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "fullname"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Team
        fields = [
            "id",
            "name",
            "description",
            "ticket_head",
            "created",
            "deactivated"
        ]


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    team_id = serializers.ReadOnlyField(source="team.id")

    class Meta:
        model = api_models.Member
        fields = [
            "id",
            "user",
            "team_id",
            "role",
            "bio",
            "created",
            "activated",
            "deactivated"
        ]


class TicketCommentSerializer(serializers.ModelSerializer):
    """
    Serialzier for comments. to be used with tickets
    """

    class Meta:
        model = api_models.TicketComment
        ticket_id = serializers.ReadOnlyField(source="ticket.id")
        team_id = serializers.ReadOnlyField(source="team.id")
        author = UserSerializer(many=False)

        fields = [
            "id",
            "ticket_id",
            "team_id",
            "author",
            "content",
            "created",
            "activated",
            "deactivated"
        ]


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
        started: When the ticket was started
        completed: When the ticket was finished
        due_date: When the ticket is due
    """

    team_id = serializers.ReadOnlyField(source="team.id")
    owner = serializers.ReadOnlyField(source="owner.email")
    comments = TicketCommentSerializer(many=True, required=False)
    assigned_user = UserSerializer()

    class Meta:
        model = api_models.Ticket
        fields = [
            "id",
            "team_id",
            "ticket_number",
            "owner",
            "assigned_user",
            "title",
            "description",
            "comments",
            "activated",
            "deactivated"
        ]


class TicketStatusSerializer(serializers.ModelSerializer):
    team_id = serializers.ReadOnlyField(source="team.id")

    class Meta:
        model = api_models.TicketStatus
        fields = [
            "id",
            "team_id",
            "title",
            "created",
            "activated",
            "deactivated"
        ]
