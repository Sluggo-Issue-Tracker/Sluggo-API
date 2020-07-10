"""
A REST API needs to provide a way of serializing and deserializing the models created into representations such as json. We can do this by declaring serializers that work very similar to Django's forms. Create a file in the app directory named serializers.py and create your classes.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Snippet, Ticket


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer Class for the Profile model.

    The fields that are serialized and visible currently are:
        id: The id of the Profile
        user: A foriegn key to the entry in the User table corresponding to this user.
        role: Unapproved, Approved, or Admin
        bio: The bio of the user's profile
    """

    class Meta:
        model = Profile
        fields = ["id", "owner", "role", "bio"]


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer Class for the Ticket model.

    The fields that are serialized and visible currently are:
        id: The id of the Ticket
        owner: The user that created the ticket
        assigned_user: The user assigned to the ticket
        title: The title of the ticket
        description: The description of the ticket
        started: When the ticket was started
        completed: When the ticket was finished
        due_date: When the ticket is due
    """

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Ticket
        fields = [
            "id",
            "owner",
            "assigned_user",
            "title",
            "description",
            "started",
            "completed",
            "due_date",
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profiles = serializers.HyperlinkedRelatedField(
        view_name="profile-detail", read_only=True
    )

    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ["url", "id", "username", "snippets", "profiles"]


# REST TUTORIAL BELOW HERE #


from .models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(
        view_name="snippet-highlight", format="html"
    )

    class Meta:
        model = Snippet
        fields = [
            "url",
            "id",
            "owner",
            "highlight",
            "title",
            "code",
            "linenos",
            "language",
            "style",
        ]

