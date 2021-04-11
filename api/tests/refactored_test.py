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
            Tag.objects.create(title="to be removed", team=self.team),
            Tag.objects.create(title="to be deleted", team=self.team),
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        to_be_kept = Tag.objects.create(title="keep this", team=self.team)
        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = [
            to_be_kept.pk
        ]
        expected = TicketSerializer(ticket_instance).data
        expected["tag_list"] = [
            TagSerializer(to_be_kept).data
        ]
        self.update(extra_data, expected)

    def testRemoveAllTags(self):
        tags = [
            Tag.objects.create(title="to be kept", team=self.team),
            Tag.objects.create(title="to be deleted", team=self.team),
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = []

        expected = TicketSerializer(ticket_instance).data
        expected["tag_list"] = []
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

    admin_member_dict = {
        "bio": "asdlfkj",
        "role": "AD"
    }

    admin_user_dict = dict(username="lkajsdf", email="asdf@asdfl.c", first_name="lkajsdf", last_name="lmao")

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
        Member.objects.filter(pk=self.pk).update(role=Member.Roles.APPROVED)

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

    def testApprove(self):
        # broken. but why?
        admin_user = User.objects.create(**self.admin_user_dict)
        Member.objects.create(**self.admin_member_dict, owner=admin_user, team=self.team)
        admin_client = APIClient()
        admin_client.force_authenticate(user=admin_user)

        updated_dict = {
            "role": "AD"
        }

        response = admin_client.patch(
            reverse(self.prefix + "-detail", kwargs={TEAM_PK: self.team.id, "pk": self.pk}),
            data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_dict.get("role"), response.data.get("role"))
        self.assertEqual(response.data, MemberSerializer(Member.objects.get(pk=self.pk)).data)

    def testCreateRoleUntouched(self): # confirm that a new user can only be unapproved
        user = User.objects.create(**self.admin_user_dict)
        client = APIClient()
        client.force_authenticate(user=user)

        weird_data = {
            "bio": "biography",
            "role": "AD"
        }

        response = client.post(
            reverse(self.prefix + "-list", kwargs={TEAM_PK: self.team.id}),
            data=weird_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("role"), Member.Roles.UNAPPROVED)


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


class PinnedTicketTestCase(TestCase):
    prefix = "pinned-tickets"
    team_dict = {"name": "bugslotics", "description": "a pretty cool team"}

    user_of_interest_dict = dict(
        username="org.mungus.a",
        email="a@mungus.org",
        first_name="Adam",
        last_name="Mungus",
    )

    member_of_interest_dict = dict(
        role="AD",
        bio="Is not sus"
    )

    user_not_of_interest_dict = dict(
        username="org.mungus.impostor",
        email="impostor@mungus.org",
        first_name="Sus",
        last_name="Mungus"
    )

    member_not_of_interest_dict = dict(
        role="AD",
        bio="Sus!"
    )

    ticket_of_interest_dict = dict(
        title="Ticket Of Interest",
        description="This is a ticket of interest to us."
    )

    ticket_not_of_interest_dict = dict(
        title="Ticket not of Interest",
        description="Please ignore this!"
    )

    def setUp(self):
        # create team
        self.team = Team.objects.create(**self.team_dict)

        # setup users
        self.user_of_interest = User.objects.create(**self.user_of_interest_dict)
        self.user_not_of_interest = User.objects.create(**self.user_not_of_interest_dict)

        # setup members
        self.member_of_interest = Member.objects.create(**self.member_of_interest_dict,
                                                        owner=self.user_of_interest, team=self.team)
        self.member_not_of_interest = Member.objects.create(**self.member_not_of_interest_dict,
                                                            owner=self.user_not_of_interest, team=self.team)
        # setup clients
        self.client_of_interest = APIClient()
        self.client_of_interest.force_authenticate(user=self.user_of_interest)

        self.client_not_of_interest = APIClient()
        self.client_not_of_interest.force_authenticate(user=self.user_not_of_interest)

        self.ticket_of_interest = Ticket.objects.create(**self.ticket_of_interest_dict, team=self.team)

        self.ticket_not_of_interest = Ticket.objects.create(**self.ticket_not_of_interest_dict, team=self.team)

    def test_ticket_pin(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if accessible from a GET request
        response = self.client_of_interest.get(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check if holds correct ticket
        self.assertEqual(response.data[0].get('ticket').get('id'), self.ticket_of_interest.pk)

    def test_ticket_unpin_removes_access(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pinned_pk = response.data.get('id')

        # Now unpin
        response = self.client_of_interest.delete(
            reverse('pinned-tickets-detail', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk,
                                                     'pk': pinned_pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if accessible from a GET request
        response = self.client_of_interest.get(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_ticket_pin_does_not_cross_users(self):
        response = self.client_of_interest.post(
            reverse('pinned-tickets-list', kwargs={'team_pk': self.team.id, 'member_pk': self.member_of_interest.pk}),
            data=dict(
                ticket=self.ticket_of_interest.pk
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pinned_pk = response.data.get('id')

        response = self.client_not_of_interest.get(
            reverse('pinned-tickets-list',
                    kwargs={'team_pk': self.team.id, 'member_pk': self.member_not_of_interest.pk}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
