from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.conf import settings
import random
import string

from api.models import Ticket, Team, Member, Tag, TicketStatus, TicketTag, TicketNode
from ..serializers import (
    UserSerializer,
    TicketStatusSerializer,
    TagSerializer,
    TicketSerializer,
    MemberSerializer,
    TeamSerializer,
)

TEAM_PK = "team_pk"

User = get_user_model()

PAGE_SIZE = settings.REST_FRAMEWORK["PAGE_SIZE"]

"""
Base class for all team related tests, querying CRUD operations
"""


# make random count random users, while ensuring we don't have any duplicates
def generateArbitraryUsers(count: int) -> list:
    emails = set()
    usernames = set()
    users = []

    for _ in range(count):
        while True:
            user = "".join(random.choice(string.ascii_letters) for _ in range(10))
            hostname = "".join(random.choice(string.ascii_letters) for _ in range(10))
            tld = "".join(random.choice(string.ascii_letters) for _ in range(3))
            email = f"{user}@{hostname}.{tld}"
            if email not in emails:
                emails.add(email)
                break

        while True:
            username = "".join(random.choice(string.ascii_letters) for _ in range(10))
            if username not in usernames:
                usernames.add(username)
                break

        first_name = "".join(random.choice(string.ascii_letters) for _ in range(10))
        last_name = "".join(random.choice(string.ascii_letters) for _ in range(10))

        users.append(
            User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
        )

        for user in users:
            user.save()

    return users


def generateArbitraryTeams(count: int) -> list:
    team_names = set()
    teams = []

    for _ in range(count):
        while True:
            team_name = "".join(random.choice(string.ascii_letters) for _ in range(10))
            if team_name not in team_names:
                team_names.add(team_name)
                break

        team = Team.objects.create(name=team_name)
        team.save()
        teams.append(team)

    return teams


class TeamRelatedCore(TestCase):
    prefix = ""
    model = None
    serializer = None

    team_dict = {"name": "bugslotics"}

    member_dict = dict(role="AD", bio="bio")

    user_dict = dict(
        username="org.sicmundus.adam",
        email="adam@sicmundus.org",
        first_name="Jonas",
        last_name="Kahnwald",
    )
    data_dict = dict()

    def setUp(self):
        self.user = User.objects.create(**self.user_dict)
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("team-list"), self.team_dict, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.team = Team.objects.get(pk=1)
        self.pk = 1

    def create(self, data):
        count = Team.objects.count()
        self.assertNotEqual(0, count)

    def list(self, expected=None):
        if not expected:
            qs = self.model.objects.get_queryset()[:PAGE_SIZE]
            expected = self.serializer(qs, many=True).data

        response = self.client.get(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], expected)

    def detail(self, expected=None):
        if not expected:
            instance = self.model.objects.get(pk=self.pk)
            expected = self.serializer(instance).data

        response = self.client.get(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def update(self, updated_dict, expected):
        response = self.client.put(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            data=updated_dict,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def delete(self):
        response = self.client.delete(
            reverse(
                self.prefix + "-detail", kwargs={"team_pk": self.team.id, "pk": self.pk}
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        qs = self.model.objects.filter(pk=self.pk)
        self.assertEqual(bool(qs), False)
