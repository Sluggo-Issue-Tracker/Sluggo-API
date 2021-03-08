from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.conf import settings

from api.models import (Ticket, Team, Member, Tag, TicketStatus, TicketTag, TicketNode)
from ..serializers import UserSerializer, TicketStatusSerializer, TagSerializer, TicketSerializer, MemberSerializer, \
    TeamSerializer

TEAM_PK = "team_pk"

User = get_user_model()

PAGE_SIZE = settings.REST_FRAMEWORK["PAGE_SIZE"]


class TeamRelatedCore(TestCase):
    prefix = ""
    model = None
    serializer = None

    team_dict = {"name": "bugslotics", "description": "a pretty cool team"}

    member_dict = dict(
        role="AD",
        bio="bio"
    )

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
        response = self.client.post(
            reverse("team-list"), self.team_dict, format="json"
        )

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
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], expected)

    def detail(self, expected=None):
        if not expected:
            instance = self.model.objects.get(pk=self.pk)
            expected = self.serializer(instance).data

        response = self.client.get(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def update(self, updated_dict, expected):
        response = self.client.put(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def delete(self):
        response = self.client.delete(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        qs = self.model.objects.filter(pk=self.pk)
        self.assertEqual(bool(qs), False)


class TeamTestCase(TeamRelatedCore):
    prefix = "team"
    model = Team
    serializer = TeamSerializer

    def testCreate(self):
        count = Team.objects.count()
        self.assertNotEqual(0, count)

    def testList(self):
        response = self.client.get(
            reverse("team-list"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDetail(self):
        response = self.client.get(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testUpdate(self):
        updated_team_dict = self.team_dict
        updated_team_dict["description"] = "not cool"
        response = self.client.put(
            reverse("team-detail", kwargs={"pk": self.team.id}), data=updated_team_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testDelete(self):
        response = self.client.delete(
            reverse("team-detail", kwargs={"pk": self.team.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TicketTestCase(TeamRelatedCore):
    data_dict = {
        "title": "ticket",
        "description": "ticket test"
    }

    prefix = "team-tickets"
    model = Ticket
    serializer = TicketSerializer

    def setUp(self):
        super().setUp()
        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            data=self.data_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = self.data_dict
        updated_dict["description"] = "alskdjf"

        s_instance = TicketSerializer(self.model.objects.get(pk=self.pk))
        expected = s_instance.data
        expected["description"] = updated_dict["description"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()

    def testTagOnCreate(self):
        extra_data = dict(self.data_dict)

        ticket_status = TicketStatus.objects.create(title="status", team=self.team)
        extra_data["status"] = ticket_status.id

        tag_instance = Tag.objects.create(title="wine", team=self.team)
        extra_data["tag_list"] = [
            tag_instance.id
        ]

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=extra_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testRemoveTagOnUpdate(self):
        tags = [
            Tag.objects.create(title="to be kept", team=self.team),
            Tag.objects.create(title="to be deleted", team=self.team),
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = [
            tags[0].pk
        ]
        expected = TicketSerializer(ticket_instance).data
        expected["tag_list"] = [
            TagSerializer(Tag.objects.get(pk=tags[0].pk)).data
        ]
        self.update(extra_data, expected)


class WrongTeamTestCase(TicketTestCase):
    other_user = dict(
        username="org.org.org",
        email="asdf@sicmundus.org",
        first_name="Jonas",
        last_name="Kahnwald",
    )

    def setUp(self):
        super().setUp()

        user_instance = User.objects.create(**self.other_user)
        self.client = APIClient()
        self.client.force_authenticate(user=user_instance)

    # TODO: regularized error messages
    def list(self, expected=None):
        response = self.client.get(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def detail(self, expected=None):
        response = self.client.get(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def update(self, updated_dict, expected=None):
        response = self.client.put(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def delete(self):
        response = self.client.delete(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testTagOnCreate(self):
        extra_data = dict(self.data_dict)

        ticket_status = TicketStatus.objects.create(title="status", team=self.team)
        extra_data["status"] = ticket_status.id

        tag_instance = Tag.objects.create(title="wine", team=self.team)
        extra_data["tag_list"] = [
            tag_instance.id
        ]

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=extra_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MemberTestCase(TeamRelatedCore):
    prefix = "team-members"

    model = Member
    serializer = MemberSerializer

    data_dict = {
        "bio": "biography"
    }

    normal_user_dict = dict(
        username="gov.wnpp.Claudia",
        email="Claudia@wnpp.gov",
        first_name="Claudia",
        last_name="Tiedemann",
    )

    def setUp(self):
        super().setUp()
        self.normal_user = User.objects.create(**self.normal_user_dict)
        self.client = APIClient()
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=self.data_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

        # force approve the member
        Member.objects.filter(pk=self.pk).update(role=Member.Roles.ADMIN)

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = self.data_dict
        updated_dict["bio"] = "alsdfkj"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["bio"] = updated_dict["bio"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()


class TagTestCase(TeamRelatedCore):
    prefix = "team-tags"
    serializer = TagSerializer

    data_dict = {
        "title": "wine"
    }

    model = Tag

    def setUp(self):
        super().setUp()
        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            data=self.data_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = self.data_dict
        updated_dict["title"] = "alsdkfj"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["title"] = updated_dict["title"]

        self.update(updated_dict, expected)

    def testDelete(self):
        self.delete()


class StatusTestCase(TeamRelatedCore):
    prefix = "team-statuses"
    model = TicketStatus
    serializer = TicketStatusSerializer

    data_dict = {
        "title": "in progress",
        "color": "#F5F225"
    }

    def setUp(self):
        super().setUp()
        response = self.client.post(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            data=self.data_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.pk = response.data.get("id")

    def testCreate(self):
        self.create(self.data_dict)

    def testList(self):
        self.list()

    def testDetail(self):
        self.detail()

    def testUpdate(self):
        updated_dict = dict(self.data_dict)
        updated_dict["title"] = "alsdkfj"
        updated_dict["color"] = "#F39617"

        expected = self.serializer(self.model.objects.get(pk=self.pk)).data
        expected["title"] = updated_dict["title"]
        expected["color"] = updated_dict["color"]

        self.update(updated_dict, expected)

    def testBadColor(self):
        updated_dict = dict(self.data_dict)
        updated_dict["color"] = "bad"

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.put(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)

    def testDelete(self):
        self.delete()
