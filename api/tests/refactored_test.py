from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from api.models import (Ticket, Team, Member, Tag, TicketStatus, TicketTag, TicketNode)
from ..serializers import UserSerializer, TicketStatusSerializer, TicketTagSerializer

TEAM_PK = "team_pk"

User = get_user_model()


class TeamRelatedCore(TestCase):
    prefix = ""

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

    def list(self):
        response = self.client.get(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def detail(self):
        response = self.client.get(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def update(self, updated_dict):
        response = self.client.put(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), data=updated_dict, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def delete(self):
        response = self.client.delete(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TeamTestCase(TeamRelatedCore):
    prefix = "team"

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
        self.update(updated_dict)

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
            Tag.objects.create(title="to be deleted", team=self.team),
            Tag.objects.create(title="to be kept", team=self.team)
        ]
        ticket_instance = Ticket.objects.get(pk=self.pk)
        for tag in tags:
            TicketTag.objects.create(ticket=ticket_instance, team=self.team, tag=tag)

        extra_data = dict(self.data_dict)
        extra_data["tag_list"] = [
            tags[0].pk
        ]
        self.update(extra_data)


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

    def list(self):
        response = self.client.get(
            reverse(self.prefix + "-list", kwargs={"team_pk": self.team.id}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def detail(self):
        response = self.client.get(
            reverse(self.prefix + "-detail", kwargs={
                "team_pk": self.team.id,
                "pk": self.pk
            }), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def update(self, updated_dict):
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
        self.update(updated_dict)

    def testDelete(self):
        self.delete()


class TagTestCase(TeamRelatedCore):
    prefix = "team-tags"

    data_dict = {
        "title": "wine"
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
        updated_dict = self.data_dict
        updated_dict["title"] = "alsdkfj"
        self.update(updated_dict)

    def testDelete(self):
        self.delete()


class StatusTestCase(TeamRelatedCore):
    prefix = "team-statuses"

    data_dict = {
        "title": "in progress"
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
        updated_dict = self.data_dict
        updated_dict["title"] = "alsdkfj"
        self.update(updated_dict)

    def testDelete(self):
        self.delete()


class StatusColorTestCase(TeamRelatedCore):
    prefix = "team-statuses"

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
        updated_dict = self.data_dict
        updated_dict["color"] = "#F39617"
        self.update(updated_dict)

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

        self.ticket_of_interest = Ticket.objects.create(**self.ticket_of_interest_dict, team=self.team,
                                                        owner=self.user_of_interest)
        self.ticket_not_of_interest = Ticket.objects.create(**self.ticket_not_of_interest_dict, team=self.team,
                                                            owner=self.user_not_of_interest)

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
        self.assertEqual(response.data.get('count'), 1)

        # Check if holds correct ticket
        self.assertEqual(response.data.get('results')[0].get('ticket').get('id'), self.ticket_of_interest.pk)

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
        self.assertEqual(response.data.get('count'), 0)

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
        self.assertEqual(response.data.get('count'), 0)
